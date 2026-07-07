# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Current state

This repository is **under active implementation** — substantial code exists across `src/`, `tests/`, `docs/`, and `scripts/`. The GenAI (Epic 8), RAG (Epic 9), and Agents (Epic 10) pillars are built and live-verified, alongside the Dataverse client, OpenF1 ingestion, and the Paddock Club predictions game. Still verify what's actually on disk before assuming — the "Repository structure" section below marks what is implemented vs. still a placeholder.

**The backlog lives in GitHub — that is canonical:** GitHub Issues + Project #2 (`synchsys/dynamics-ai-intelligence-hub`), organised Epic → Feature → Story → Task via sub-issues, with Milestones and `type:`/`priority:`/`effort:` labels. When asked to "build X" or "start on Y", find the issue there and follow its User Story / tasks / Definition of Done / suggested branch / labels. Managed via the `github-backlog-management` skills.

The two Markdown documents under `Backlog/` are the **original input** (now migrated to GitHub — treat as read-only source, not the live tracker):

- `Backlog/Dynamics_AI_Intelligence_Hub_Backlog_v0_4.md` — the narrative backlog: vision, roadmap, milestones, dependency risks, and the Epic → Feature → Story → Task breakdown.
- `Backlog/Dynamics_AI_Intelligence_Hub_Complete_Issue_Set.md` — the original issue register (87 issues, IDs 1.1 → 12.8), plus later Paddock Club rework additions (Epic 13). Note the GitHub issue **numbers** differ from these source IDs.

## Live environment

Azure resources are provisioned (dev; secrets in git-ignored `.env`, **rotate before anything public**; Managed Identity is Epic 11):

- **Dataverse** `racy-dev` with the `racy_` schema (F1 + Paddock + AI-logging tables), via a service principal.
- **Azure OpenAI** `racy-openai-dev` (uksouth) — `gpt-5-mini` chat + `text-embedding-3-small`; Entra auth reusing the Dataverse SP. Note: the gpt-4o generation is deprecated — use GPT-5-family models, which reject an explicit `temperature`.
- **Azure AI Search** `racy-search-dev` (Free tier) — vector + keyword; dev uses the admin key.

`scripts/**/verify_*.py` are live smoke tests for each capability (they create + clean up their own data).

## What is being built

**Dynamics AI Intelligence Hub** — a portfolio-grade, production-style reference implementation for a six-month transition from Microsoft Solution Architect to AI & ML Solution Architect. It combines: professional Python, Azure AI + Azure Functions, Dynamics 365 & Dataverse, a client-agnostic CRM domain model, REST integration (OpenF1/FastF1 F1 data), Pandas data engineering, ML, RAG, AI agents, Azure AI Search, and security/governance/observability.

## Repository structure

Packages under `src/` (✅ = implemented + tested, live-verified; 🚧 = placeholder `__init__.py` only, not yet built):

- ✅ `src/shared` — config loader, structured logging, exception hierarchy, **resilience** (timeout + exponential-backoff-with-jitter retry). Consumed by every other module — do not reimplement retry logic elsewhere.
- ✅ `src/api` — reusable REST client (retries, timeouts, structured logging) on `src/shared`.
- ✅ `src/dataverse` — authenticated Dataverse Web API client (read/write, upsert, atomic `$batch`).
- ✅ `src/openf1` — OpenF1 ingestion on `src/api`, persisting to Dataverse.
- ✅ `src/ai` — Azure OpenAI client, prompt library, structured outputs, **the function-calling tool layer**, prompt/response logging (`prompt_log`), guarded CRM action tools, and the CRM assistant (`assistant/`).
- ✅ `src/rag` — ingestion/chunking, embeddings, Azure AI Search index, hybrid + permission-aware retrieval, cited generation, the assembled `RagAssistant`, and an evaluation harness.
- ✅ `src/agents` — the `Agent` primitive, the four core agents (planner → researcher → reviewer → reporter), and the `MultiAgentWorkflow`. **Layered above both `ai` and `rag`** (imports either freely; neither imports `agents`) — reuses the `ai` tool layer (ADR-0006) and wraps the RAG assistant as a researcher tool.
- ✅ `src/paddock` — the Paddock Club predictions game (Epic 13): odds pricing, the settlement registry + deterministic grading, wager lock + settlement engine, and the LLM free-text `intake`. (Not in the original backlog structure; added in the 2026-07 rework.)
- 🚧 `src/fastf1_analytics` — telemetry analysis helpers (placeholder).
- 🚧 `src/azure_functions` — serverless timer/HTTP triggers to host ingestion, the assistant, and the agent workflow (placeholder).

Supporting trees: `tests/` (mirrors `src/`), `scripts/` (per-capability live `verify_*.py` + Dataverse schema tooling), `docs/` (`architecture/`, `decisions/` for ADRs, `security/`, `learning/`), `infrastructure/` (`bicep/`, `terraform/`, `environments/`), plus `notebooks/`, `datasets/`, `portfolio/`.

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

- **Python 3.12+.** Tooling is configured in `pyproject.toml`: **Ruff** (lint, `E/F/I/UP/B/SIM`; `scripts/` excluded) + **Black** (line-length 100) + **mypy** `--strict` (pydantic plugin) + **pytest** + **pytest-cov**. Every gate must be clean before a PR: `ruff check . && black --check . && mypy src tests && pytest`. Coverage is deliberately **not** in `addopts` (it breaks editor test discovery) — run it explicitly: `pytest --cov=src --cov-fail-under=80`; the practice in this repo is **100% coverage on new `src/` code** (inject SDKs/gateways/loggers so units test hermetically). **CI** (`.github/workflows/ci.yml`, story #9) runs all four gates + the coverage threshold on every push and PR.
- **Branch naming:** `feat/<area>-<short-desc>` (e.g. `feat/dataverse-api-client`), per the "Suggested branch" line in each issue.
- **PR titles:** Conventional Commits scoped by area, e.g. `feat(dataverse): reusable Dataverse Web API client with service principal auth`.
- **Response validation:** external API responses are validated with **Pydantic** models before persistence.
- **ADRs** live in `docs/decisions/`. Recorded: **0002** IaC tool (Bicep primary; Terraform tree retired), **0003** Dataverse auth (service principal now → Managed Identity in Epic 11), **0004** Functions hosting (Flex Consumption; deploy root = `src/`), **0005** generic CRM schema (native Dataverse standard tables; custom `racy_` only for AI logging), **0006** function-calling vs agent-orchestration boundary, **0007** agent framework (custom orchestration over the `ai` tool layer), **0008** odds/settlement (multi-source, void-don't-guess, virtual credits), **0009** experience surface + business-logic placement. No major decisions currently open. (Historical note: an early draft mislabeled the experience-surface decision as "ADR-0007"; that slot is the agent-framework ADR, and the experience decision is 0009.)
- **Secrets:** local development uses `.env` / `.env.example` only. Production secrets/identity (Key Vault + Managed Identity) are owned by Epic 11 — do not hardcode production credentials into feature code.

## Workload note

The backlog is costed at 337 story points and treats six months as the aggressive case. Months 5 (GenAI/RAG/Agents) and 2 (Dataverse) are the pressure points. When work must slip, the backlog's guidance is to defer lower-priority items (clustering model, notebook templates, parts of Epic 11 hardening) rather than the end-to-end **assembly stories** (RAG assistant, multi-agent workflow) or the governance spine — those are the portfolio's differentiators.

**Status:** both headline differentiators are **delivered and live-verified** — the end-to-end RAG assistant (Epic 9) and the multi-agent workflow (Epic 10), alongside the GenAI/assistant spine (Epic 8) and the Paddock Club game (Epic 13). Remaining major work is platform/experience (Azure Functions #10/#20, model-driven app UI #11/#12), Epic 11 hardening, Epic 7 ML, and the Epic 12 capstone assembly.
