# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Current state

This repository is at the **planning stage — there is no code yet.** The only content is a product backlog under `Backlog/` (a `files.zip` plus two extracted Markdown files). Do not assume any `src/`, `tests/`, tooling, or git history exists until you have verified it; the structure below is the *target*, not the current reality.

The two backlog documents are the source of truth:

- `Backlog/Dynamics_AI_Intelligence_Hub_Backlog_v0_4.md` — the narrative backlog: vision, product goals, six-month roadmap, milestones, dependency risks, workload analysis, and the Epic → Feature → Story → Task breakdown.
- `Backlog/Dynamics_AI_Intelligence_Hub_Complete_Issue_Set.md` — the full issue register: all 87 GitHub issues (85 stories + 2 spikes, 337 story points) with IDs (1.1 → 12.8), story points, milestones, the ADR register, critical dependency chains, and copy-paste-ready issue bodies.

When asked to "build X" or "start on Y", locate the corresponding issue ID in the register first and follow its User Story / tasks / Definition of Done, its suggested branch name, and its labels.

## What is being built

**Dynamics AI Intelligence Hub** — a portfolio-grade, production-style reference implementation for a six-month transition from Microsoft Solution Architect to AI & ML Solution Architect. It combines: professional Python, Azure AI + Azure Functions, Dynamics 365 & Dataverse, a client-agnostic CRM domain model, REST integration (OpenF1/FastF1 F1 data), Pandas data engineering, ML, RAG, AI agents, Azure AI Search, and security/governance/observability.

## Target repository structure

Create directories under `src/` as their owning epic is worked; each maps to a deliverable in the backlog:

- `src/shared` — config loader, structured logging, exception hierarchy, **resilience** (timeout + exponential-backoff-with-jitter retry). Consumed by every other module — build this first and do not reimplement retry logic elsewhere.
- `src/api` — reusable REST client (retries, timeouts, structured logging) built on `src/shared`; foundation for OpenF1.
- `src/dataverse` — authenticated Dataverse Web API client (read/write, upsert, batch). **Silent prerequisite for OpenF1, FastF1 publishing, and the GenAI assistant** — schedule early.
- `src/openf1` — OpenF1 ingestion on top of `src/api`, persisting to Dataverse via `src/dataverse`.
- `src/fastf1_analytics` — telemetry analysis helpers feeding notebook templates.
- `src/ai` — Azure OpenAI integration, prompt engineering, structured outputs, function calling, CRM assistant.
- `src/rag` — document ingestion/chunking, embeddings, Azure AI Search, hybrid + permission-aware retrieval, cited answers.
- `src/agents` — multi-agent orchestration (planner → researcher → reviewer → reporter) reusing the `src/ai` tool layer and `src/rag`.
- `src/azure_functions` — serverless platform foundation (timer/HTTP triggers); **established once and reused** by OpenF1, GenAI, and agents.

Supporting trees: `tests/` (mirrors `src/`), `notebooks/`, `datasets/` (`openf1/`, `audit-history/`, `sample-crm/`), `docs/` (`architecture/`, `decisions/` for ADRs, `diagrams/`, `learning/`, `security/`, `retrospectives/`), `infrastructure/` (`bicep/`, `terraform/`, `environments/`), `portfolio/`.

## Architecture: dependencies and layering

The build order is driven by dependency chains, not epic numbering. The critical ones (see the "Critical dependency chains" section of the issue set):

1. `src/shared` utils + resilience → REST client (`src/api`) → OpenF1 (`src/openf1`).
2. Dataverse API access (`src/dataverse`) gates all persistence and AI logging (OpenF1 persistence, FastF1 publishing, assistant, prompt/response logging).
3. Dataverse security roles → permission-aware retrieval (`src/rag`) → end-to-end RAG assistant → capstone front end.
4. Dataverse auditing → sample-data seeding → audit analytics notebooks → audit-anomaly ML model.
5. GenAI tool/function-calling layer → agent tool registry → agents → multi-agent workflow → capstone.

**Function-calling vs agents (ADR-0006):** `src/ai` owns single-model function calling; `src/agents` owns multi-agent orchestration that *reuses* that tool layer. Do not duplicate tool routing across the two.

**Governance is wired in from the start, not bolted on:** prompt/response logging (to the AI Request / AI Response Dataverse entities), ingestion observability, and permission-aware retrieval are *implemented* in their feature epics. Epic 11 (Security & Governance) is a **policy + consolidation + hardening layer** over those — it defines policy and closes gaps, it does not re-implement logging or access control.

### Domain model

The CRM is deliberately **client-agnostic** (no customer-specific naming). Entities: Account, Contact, Lead, Opportunity, Case, Activity, Product, Knowledge Article, Document, Audit Event, AI Request, AI Response. F1 (OpenF1/FastF1) data is public sample data ingested *into* this model — it is not the domain itself.

## Conventions

These come from the backlog and issue drafts — follow them when scaffolding:

- **Python 3.12+.** Tooling target: **Ruff** (lint) + **Black** (format) + **pytest** (test) + **mypy** (types). None of this is configured yet; when you set it up, wire it into a CI workflow (lint, format check, type check, tests) with a coverage gate. Reusable utility modules target ≥ 90% coverage.
- **Branch naming:** `feat/<area>-<short-desc>` (e.g. `feat/dataverse-api-client`), per the "Suggested branch" line in each issue.
- **PR titles:** Conventional Commits scoped by area, e.g. `feat(dataverse): reusable Dataverse Web API client with service principal auth`.
- **Response validation:** external API responses are validated with **Pydantic** models before persistence.
- **ADRs** live in `docs/decisions/`. Open decisions tracked in the ADR register: IaC tool (Bicep vs Terraform — Bicep is the Microsoft-aligned default; both trees currently planned, only one should be primary), Dataverse auth (service principal → Managed Identity), Functions hosting model, CRM schema approach, plus ADR-0006/0007 above.
- **Secrets:** local development uses `.env` / `.env.example` only. Production secrets/identity (Key Vault + Managed Identity) are owned by Epic 11 — do not hardcode production credentials into feature code.

## Workload note

The backlog is costed at 337 story points and treats six months as the aggressive case. Months 5 (GenAI/RAG/Agents) and 2 (Dataverse) are the pressure points. When work must slip, the backlog's guidance is to defer lower-priority items (clustering model, notebook templates, parts of Epic 11 hardening) rather than the end-to-end **assembly stories** (RAG assistant, multi-agent workflow) or the governance spine — those are the portfolio's differentiators.
