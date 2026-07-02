# Dynamics AI Intelligence Hub

## Six-Month AI & ML Solution Architect Backlog

> **Version:** 0.4 (Workload-rebalanced)
>
> This document is the product backlog for a six-month transition from
> experienced Microsoft Solution Architect to AI & ML Solution
> Architect. It is organised for GitHub Projects and follows an
> Epic → Feature → Story → Task hierarchy.
>
> **Changes since v0.3 (workload rebalance):**
> - The full issue set was costed: **87 issues, 337 story points**. The
>   per-milestone tally exposed overload — M5 at 101 pts, M6 at 68, M2 at
>   60 — against a sustainable solo pace of ~30–45 pts/month.
> - **Rebalanced the roadmap** (no scope cut): OpenF1 ingestion (Epic 4)
>   moves into early Month 3; Azure OpenAI foundations (Epic 8.1–8.4)
>   begin in Month 4 alongside ML, leaving RAG + Agents as the Month 5
>   focus. See the new *Workload & Scheduling* section for the tally and
>   critical path.
> - Adjusted the *Suggested milestone* on Epic 4 (Month 3, early) and
>   Epic 8 (Month 4–5) to match.
> - Added four labels used across the issue drafts to the label set:
>   `ai`, `observability`, `foundation`, `api`.
>
> **Changes since v0.2 (coverage review):**
> - Added stories to features that had none: Epic 2 *Packaging & Shared
>   Utilities* and *Error Handling & Resilience*; Epic 5 *Reusable
>   Analysis Utilities*.
> - Recast **Epic 11** as a policy + final-hardening layer over
>   capabilities implemented in earlier epics, removing duplicate
>   implementation stories (audit logging, observability, secrets).
> - Scoped Epic 1 *Secrets & Config* to local development only;
>   production secrets/identity are owned by Epic 11.
> - Decomposed Epic 12 *End-to-End Integration* into discrete integration
>   stories.
> - Added assembly ("glue") stories to Epic 9 (end-to-end RAG assistant)
>   and Epic 10 (end-to-end multi-agent workflow).
> - Expanded Epic 6 *Audit History Analytics* and split Epic 8 *Generic
>   CRM Assistant* into scaffolding / grounding / actions.
> - Tightened vague one-liner stories (telemetry, visualisation, feature
>   engineering) into dataset-specific, measurable stories.
> - Added ADR-0006 to define the function-calling vs agent-orchestration
>   boundary (Epic 8 vs Epic 10).
>
> **Changes in v0.2:** Added the Feature layer to every epic; introduced
> previously-absent features (repository governance, CI/CD, Dataverse API
> access, Azure Functions platform, IaC, permission-aware retrieval,
> experiment tracking, prompt/response logging); promoted Azure Functions
> and IaC to first-class features; added dependency-risk callouts.

------------------------------------------------------------------------

# Vision

Build a portfolio-grade, production-style reference implementation
demonstrating:

-   Professional Python engineering
-   Azure AI & Azure Functions
-   Dynamics 365 & Dataverse
-   Generic CRM domain modelling
-   REST API integration
-   OpenF1 and FastF1 data ingestion
-   Data engineering with Pandas
-   Machine Learning
-   Retrieval-Augmented Generation (RAG)
-   AI Agents
-   Azure AI Search
-   Security, governance and observability

------------------------------------------------------------------------

# Product Goals

1.  Become productive in Python.
2.  Learn modern AI engineering practices.
3.  Build reusable Azure-native components.
4.  Demonstrate enterprise architecture skills.
5.  Produce a public GitHub portfolio.

------------------------------------------------------------------------

# Repository Structure

``` text
dynamics-ai-intelligence-hub/
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── .github/
│   ├── workflows/
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
├── docs/
│   ├── architecture/
│   ├── backlog/
│   ├── decisions/
│   ├── diagrams/
│   ├── learning/
│   ├── security/
│   └── retrospectives/
├── src/
│   ├── api/
│   ├── dataverse/
│   ├── openf1/
│   ├── fastf1_analytics/
│   ├── ai/
│   ├── rag/
│   ├── agents/
│   ├── azure_functions/
│   └── shared/
├── notebooks/
├── datasets/
│   ├── openf1/
│   ├── audit-history/
│   └── sample-crm/
├── infrastructure/
│   ├── bicep/
│   ├── terraform/
│   └── environments/
├── tests/
└── portfolio/
```

------------------------------------------------------------------------

# Six-Month Roadmap

  Month   Focus              Deliverable
  ------- ------------------ ------------------------------------------
  1       Python & Tooling   REST client, GitHub workflows, CI/CD
  2       Dataverse & APIs   Generic CRM app, Dataverse API access, Azure Functions + IaC foundation
  3       Data Engineering   OpenF1 ingestion (from M2), analytics notebooks, audit reporting, data quality
  4       Machine Learning   Predictive models, anomaly detection, experiment tracking, begin Azure OpenAI foundations
  5       LLM Engineering    RAG, agents, assistant grounding & actions, permission-aware retrieval
  6       Enterprise AI      Governance, deployment CI/CD, portfolio

------------------------------------------------------------------------

# Milestones

-   Month 1 — Python and API Foundations
-   Month 2 — Dataverse and Dynamics Foundation
-   Month 3 — Data Engineering and Analytics
-   Month 4 — Machine Learning and Evaluation
-   Month 5 — Generative AI, RAG and Agents
-   Month 6 — Governance, Deployment and Portfolio

------------------------------------------------------------------------

# Dependency Risks (read before scheduling)

1.  **Dataverse write-access from Python** (Epic 3 → *Dataverse API Access*)
    is a silent prerequisite for Epics 4, 5 and 8. Schedule it early in
    Month 2 or those epics stall.
2.  **Sample CRM data generation** (Epic 3 → *Sample CRM Data & Seeding*)
    must precede Epics 6–7 analytics and ML work.
3.  **Azure Functions platform** (Epic 4 → *Serverless Platform Foundation*)
    is referenced by Epics 4, 8 and 10 but must be established once,
    early, and reused.
4.  **IaC tool decision** (Epic 1 → ADR-0002) should be made before any
    Azure resource is provisioned; the repo ships both `bicep/` and
    `terraform/` and only one should be primary.

------------------------------------------------------------------------

# Workload & Scheduling (read before committing to dates)

The full issue set costs **87 issues / 337 story points**. Costed by
milestone as originally mapped:

  Milestone   Items   Points   Assessment
  ----------- ------- -------- --------------------------------------------
  M1          11      36       Full but front-loaded config; manageable
  M2          15      60       Overloaded — first pressure point
  M3          13      38       Balanced
  M4          8       34       Balanced
  M5          25      101      Severely overloaded
  M6          15      68       Heavy and end-loaded

A sustainable solo pace — for someone also learning Python — is roughly
**30–45 points a month**. As mapped, M5 is ~2–3× that, and M2 and M6 also
exceed it. The rebalance below spreads the load **without cutting scope**:

1.  **Move OpenF1 (Epic 4, ~21 pts) into early Month 3.** M3 (38) has
    room; M2 (60) does not. Epic 4 can only start once Dataverse API
    access lands anyway, so late-M2/early-M3 is its natural slot. This
    takes M2 down toward ~40 and lifts M3 toward ~55.
2.  **Start Azure OpenAI foundations (Epic 8.1–8.4, ~14 pts) in Month 4**
    alongside ML, leaving the assistant, RAG and agents for Month 5. This
    takes M5 down toward ~80 and lifts M4 toward ~48.
3.  **Protect the Month 5 critical path.** Even rebalanced, M5 is the
    tightest month. The non-negotiable chain is the assembly stories and
    their inputs: permission-aware retrieval (9.5) → RAG assembly (9.Z),
    and the tool layer (8.4) → agents (10.2) → agent workflow (10.Z),
    with 9.Z feeding 10.Z. Everything else in M5 can slip a week; these
    cannot, because Epic 12 depends on them.

Even after rebalancing, treat **six months as the aggressive case**. If
progress slips, the honest levers are: defer the lower-priority models
(7.4 clustering), the notebook templates (6.8), and parts of Epic 11's
hardening into a Month 7 — rather than dropping the assembly stories or
the governance spine, which are the portfolio's differentiators.

------------------------------------------------------------------------

# Epic 1 -- Foundation

**Suggested milestone:** Month 1
**Goal:** Establish a reproducible, governed, automated engineering base
before any feature work begins.

## Feature -- Development Environment

### Story -- Configure Workstation

**SMART Objective**

Within one week, create a fully reproducible Python development
environment capable of running unit tests, linting, formatting and
GitHub Actions.

### Tasks

-   Install Python 3.12+
-   Configure virtual environments
-   Install Ruff, Black, PyTest and MyPy
-   Configure VS Code
-   Configure Git
-   Create GitHub repository
-   Create project skeleton
-   Document setup
-   Verify clean build

**Definition of Done**

-   Repository builds successfully
-   Tests execute
-   Lint passes
-   Formatting passes

## Feature -- Repository Governance & Templates

Establish the GitHub project scaffolding defined in the project
instructions.

Stories:

-   Create label set (epic, feature, story, spike, task, python, azure,
    dataverse, dynamics, openf1, fastf1, ml, rag, agent, ai, security,
    governance, observability, documentation, architecture, portfolio,
    foundation, api, blocked, good-first-task)
-   Create six monthly milestones
-   Configure GitHub Project board and custom fields (Type, Story
    Points, Priority, Milestone)
-   Add issue templates (epic, feature, story, spike, task, bug)
-   Add pull request template
-   Add CODEOWNERS
-   Document branch naming and commit message conventions

## Feature -- CI/CD Pipeline

Promote GitHub Actions from a single task to a first-class capability
(build/lint/type/coverage gates). Deployment CI is handled separately in
Epic 12.

Stories:

-   Create CI workflow (lint, format check, type check, tests)
-   Enforce minimum test coverage gate
-   Add status badges to README
-   Add branch protection rules

## Feature -- Documentation Scaffolding

Stories:

-   Author README, CONTRIBUTING, CHANGELOG, LICENSE
-   Create `docs/` tree
-   Establish ADR log and record ADR-0001 (repository conventions)
-   (Optional) Configure GitHub Pages

## Feature -- Secrets & Config Management (local development)

**Scope:** local development only. Production secrets and identity
(Managed Identity + Key Vault) are owned by Epic 11 to avoid duplication.

Stories:

-   Establish `.env` handling and `.env.example`
-   Configure GitHub Actions secrets for CI
-   Add pre-commit hooks (secret scanning, lint, format)

------------------------------------------------------------------------

# Epic 2 -- Python Engineering

**Suggested milestone:** Month 1
**Goal:** Build professional Python foundations and the reusable
primitives consumed by later epics.

## Feature -- Core Language

### Story -- Learn Python

**SMART Objective**

Complete 30 progressively harder exercises over two weeks with at least
90% test coverage for personal utility modules.

### Tasks

-   Variables
-   Functions
-   Classes
-   Dataclasses
-   Collections
-   File IO
-   JSON
-   Logging
-   Exceptions
-   Type hints
-   Packaging
-   Unit tests

Deliverables:

-   `/src/python_basics`
-   `/tests/python_basics`

## Feature -- REST API Client

Reusable HTTP client that becomes the foundation for OpenF1 ingestion
(Epic 4).

### Story -- Build reusable REST client

**SMART Objective**

By the end of Week 2, implement a reusable Python REST client with
retries, timeout handling, structured logging and at least 20 passing
unit tests.

Tasks:

-   Base client with configurable base URL and headers
-   Timeout handling
-   Retry with exponential backoff
-   Structured logging
-   Error/exception model
-   Unit tests with mocked responses

Deliverable: `/src/api`

## Feature -- Testing & Quality

Stories:

-   Establish pytest patterns and fixtures
-   Mocking and parametrised tests
-   Coverage reporting and discipline

## Feature -- Packaging & Shared Utilities

Populates `/src/shared` (config loader, logging setup, common
exceptions) reused across every epic.

### Story -- Build the shared utilities package

**SMART Objective**

By the end of Week 2, publish an importable internal `shared` package
containing a config loader, structured-logging setup and a common
exception hierarchy, with ≥ 90% test coverage.

Tasks:

-   Config loader (environment + defaults)
-   Structured logging setup
-   Common exception hierarchy
-   Package metadata so modules import `shared` cleanly
-   Unit tests

Deliverable: `/src/shared`, `/tests/shared`

## Feature -- Error Handling & Resilience

Single, authoritative home for retry/backoff primitives. The REST client
(Epic 2) and OpenF1 resilience (Epic 4.2) **consume** these rather than
reimplementing them.

### Story -- Build reusable resilience utilities

**SMART Objective**

Implement a reusable timeout + exponential-backoff-with-jitter retry
decorator in `src/shared`, with tests proving retry-on-transient and
give-up-after-N behaviour; consumed by the REST client and OpenF1
ingestion.

Tasks:

-   Timeout wrapper
-   Retry decorator with exponential backoff + jitter
-   Configurable retry predicates (which errors are transient)
-   Unit tests (simulated transient failures, exhausted retries)
-   Document the contract so 4.2 references it

Deliverable: `/src/shared/resilience.py`, tests

------------------------------------------------------------------------

# Epic 3 -- Dynamics & Dataverse

**Suggested milestone:** Month 2
**Goal:** Create a completely client-agnostic CRM solution and the
Python access layer that later epics depend on.

Entities:

-   Account
-   Contact
-   Lead
-   Opportunity
-   Case
-   Activity
-   Product
-   Knowledge Article
-   Document
-   Audit Event
-   AI Request
-   AI Response

## Feature -- Data Model & ERD

Design-first artefact produced before any table is created.

Stories:

-   Design ERD
-   Document entity relationships and keys
-   Record ADR for schema approach

## Feature -- Dataverse Tables & Relationships

Stories:

-   Create Dataverse tables
-   Configure columns and relationships
-   Configure alternate keys

## Feature -- Forms & Views

Stories:

-   Configure forms
-   Configure views

## Feature -- Model-Driven App

Stories:

-   Create model-driven app
-   Configure sitemap and navigation

## Feature -- Security Roles & Teams

Stories:

-   Configure security roles
-   Configure teams and business units

## Feature -- Auditing & Business Process Flow History

Stories:

-   Enable auditing
-   Enable and capture Business Process Flow history

## Feature -- Sample CRM Data & Seeding

**Dependency:** blocks Epics 6–7.

Stories:

-   Build a client-agnostic sample data generator
-   Seed Accounts, Contacts, Leads, Opportunities, Cases, Activities
-   Generate synthetic audit history for analytics

## Feature -- Dataverse API Access from Python

**Critical dependency:** required by Epics 4, 5 and 8.

Stories:

-   Register app / service principal authentication
-   Implement Dataverse Web API client (read/write)
-   Implement upsert and batch operations
-   Unit/integration tests against a dev environment
-   Record ADR for auth approach (service principal vs managed identity)

Deliverable: `/src/dataverse`

------------------------------------------------------------------------

# Epic 4 -- OpenF1 Integration

**Suggested milestone:** Month 3 (early); may begin late Month 2 if
capacity allows and Dataverse API access is ready
**Goal:** Ingest public F1 data into Dataverse using resilient,
observable, scheduled pipelines.

**Depends on:** Epic 2 (REST client), Epic 3 (Dataverse API access).

## Feature -- Serverless Platform Foundation

**Cross-cutting dependency:** established once here, reused by Epics 8
and 10.

Stories:

-   Install Azure Functions Core Tools and configure local dev
-   Choose and document hosting model (Consumption vs Flex) via ADR
-   Establish trigger patterns (timer, HTTP) and project layout
-   Local run + deploy smoke test

Deliverable: `/src/azure_functions`

## Feature -- Ingestion Client

Stories:

-   Build reusable OpenF1 client on top of the Epic 2 REST client
-   Authenticate where required
-   Import sessions
-   Import drivers
-   Import laps

## Feature -- Resilience & Rate Limiting

Stories:

-   Handle retries
-   Handle rate limiting and pagination

## Feature -- Data Validation

Stories:

-   Validate API responses with Pydantic models before persistence

## Feature -- Dataverse Persistence

Stories:

-   Map OpenF1 entities to Dataverse tables
-   Store ingested data via the Dataverse access layer

## Feature -- Scheduled Ingestion (Azure Functions)

Stories:

-   Timer-triggered ingestion function
-   Idempotent re-runs

## Feature -- Ingestion Observability

Stories:

-   Log imports
-   Emit run metrics and failure alerts

------------------------------------------------------------------------

# Epic 5 -- FastF1 Analytics

**Suggested milestone:** Month 3
**Goal:** Produce telemetry analysis notebooks and publish summaries to
Dataverse.

## Feature -- Environment & Caching

Stories:

-   Configure FastF1
-   Configure the FastF1 cache

## Feature -- Telemetry Notebooks

### Story -- Build a lap-telemetry notebook for one session

**SMART Objective**

Produce a notebook that loads one race session via FastF1 and plots
speed, throttle and brake traces for a chosen lap, with narrative
commentary and reproducible output.

## Feature -- Driver / Stint Comparison

Stories:

-   Compare drivers
-   Analyse stints

## Feature -- Reusable Analysis Utilities

Shared plotting/analysis helpers that feed Epic 6 notebook templates.

### Story -- Extract reusable telemetry/plot helpers

**SMART Objective**

Refactor common load/plot logic out of the telemetry notebooks into a
tested `fastf1_analytics` helper module that Epic 6 notebook templates
import, with ≥ 10 unit tests.

Deliverable: `/src/fastf1_analytics`, tests

## Feature -- Publish Summaries to Dataverse

Stories:

-   Publish summaries to Dataverse (via Epic 3 access layer)

------------------------------------------------------------------------

# Epic 6 -- Data Engineering

**Suggested milestone:** Month 3
**Goal:** Turn raw ingested and sample data into trusted, reusable
analytical assets.

## Feature -- Data Cleaning & Normalisation

Stories:

-   Clean datasets
-   Normalise schemas

## Feature -- Data Quality & Profiling

Stories:

-   Profile datasets
-   Add validation and quality checks (separating "cleaned" from
    "trusted")

## Feature -- Storage Layer

Stories:

-   Export Parquet

## Feature -- Visualisation & Trend Analysis

### Story -- Visualise ingestion and CRM trends

**SMART Objective**

Produce a notebook charting at least three trends across the ingested
OpenF1 and seeded CRM data (e.g. lap-time distribution, case volume over
time, opportunity value by stage), each with a one-paragraph reading.

## Feature -- Audit History Analytics

Enterprise-style audit dataset — a headline portfolio piece and the
input to the Epic 7 anomaly model. Broken into concrete stories.

### Story -- Analyse actor and entity change patterns

**SMART Objective**

From the seeded audit history, produce a notebook summarising changes by
actor, entity and operation type, with tables and charts, over a defined
window.

### Story -- Analyse temporal audit patterns

**SMART Objective**

Identify and visualise time-based patterns in the audit history
(activity by hour/day, bursts, unusual gaps) as a reproducible notebook.

### Story -- Extract audit features for anomaly detection

**SMART Objective**

Produce a documented feature table (per actor / per entity change
frequencies, recency, diversity) exported for direct use by the Epic 7
audit-anomaly model.

Deliverable: `datasets/audit-history/features.parquet` + notebook

## Feature -- Reusable Notebook Templates

Stories:

-   Build reusable notebook templates

------------------------------------------------------------------------

# Epic 7 -- Machine Learning

**Suggested milestone:** Month 4
**Goal:** Build and evaluate portfolio-grade models with reproducible
experiments.

## Feature -- Feature Engineering

### Story -- Engineer features for the portfolio models

**SMART Objective**

Produce documented feature sets tied to each portfolio model: lap/stint
features for lap prediction, race-context features for strategy
classification, and (consuming Epic 6) change-frequency/recency features
for audit anomaly detection.

Stories:

-   Lap/stint features (lap prediction)
-   Race-context features (strategy classification)
-   Audit change features (from Epic 6 export)

## Feature -- Supervised Learning

Stories:

-   Regression (lap prediction)
-   Classification (strategy classification)

## Feature -- Unsupervised Learning

Stories:

-   Clustering

## Feature -- Anomaly Detection

Stories:

-   Audit anomaly detection

## Feature -- Model Evaluation & Metrics

Stories:

-   Model Evaluation

## Feature -- Experiment Tracking & Reproducibility

Stories:

-   Track experiments and log runs
-   Fix random seeds and document reproducibility
-   Produce model cards

## Feature -- Model Packaging & Inference

Stories:

-   Serialise trained models
-   Serve inference via an Azure Function

------------------------------------------------------------------------

# Epic 8 -- Generative AI

**Suggested milestone:** Month 4–5 (begin foundational stories 8.1–8.4 in
Month 4 alongside ML; assistant, grounding and actions in Month 5)
**Goal:** Add LLM capabilities with governance wired in from the start.

**Depends on:** Epic 3 (AI Request/Response entities), Epic 4
(serverless platform).

## Feature -- Azure OpenAI / Microsoft Foundry Integration

Stories:

-   Azure OpenAI integration

## Feature -- Prompt Engineering

Stories:

-   Prompt engineering

## Feature -- Structured Outputs

Stories:

-   Structured outputs

## Feature -- Function Calling & Tool Routing

Defines single-model tool invocation. The Epic 8 / Epic 10 boundary is
recorded in **ADR-0006**: Epic 8 = single-model function calling; Epic
10 = multi-agent orchestration that *reuses* this tool layer.

Stories:

-   Function calling
-   Tool routing
-   Record ADR-0006 (function-calling vs agent-orchestration boundary)

## Feature -- AI Summaries

Stories:

-   AI summaries

## Feature -- Generic CRM Assistant

Split into scaffolding, grounding and actions rather than one oversized
story.

### Story -- Assistant scaffolding

**SMART Objective**

Stand up a conversational assistant over the generic CRM that answers
questions from Dataverse data via the Dataverse access layer, with
prompt/response logging enabled.

### Story -- Ground the assistant with RAG

**SMART Objective**

Connect the assistant to the Epic 9 RAG retrieval so answers are grounded
in knowledge sources with citations (depends on Epic 9 assembly story).

### Story -- Add CRM action tools

**SMART Objective**

Give the assistant a small set of guarded function-calling tools (e.g.
create a follow-up activity, look up a record) using the Epic 8 tool
layer, with approval on write actions.

## Feature -- Prompt & Response Logging

Governance starts here, not in Epic 11.

Stories:

-   Log prompts and responses to the AI Request / AI Response entities
-   Link AI interactions to the audit trail

## Feature -- GenAI Output Evaluation

Stories:

-   Build an evaluation harness for summaries and assistant answers

------------------------------------------------------------------------

# Epic 9 -- RAG

**Suggested milestone:** Month 5
**Goal:** Deliver grounded, permission-aware retrieval over public and
generic knowledge sources.

Knowledge sources:

-   Public F1 regulations
-   Generic CRM documentation
-   Product documentation
-   Knowledge articles

## Feature -- Document Ingestion & Chunking

Stories:

-   Document ingestion
-   Chunking

## Feature -- Embeddings

Stories:

-   Embeddings

## Feature -- Azure AI Search Index

Stories:

-   Azure AI Search

## Feature -- Hybrid Search / Retrieval

Stories:

-   Hybrid search

## Feature -- Permission-Aware Retrieval

Implementation lives here; governance policy is tracked in Epic 11.

Stories:

-   Filter retrieval results by Dataverse security roles
-   Enforce document-level access boundaries

## Feature -- Citations & Grounding

Stories:

-   Citation support

## Feature -- RAG Evaluation

Stories:

-   Evaluation

## Feature -- End-to-End RAG Assistant (assembly)

Assembles the pipeline features into a working, callable capability — the
actual portfolio deliverable.

### Story -- Assemble the end-to-end RAG assistant

**SMART Objective**

Wire ingestion → embeddings → hybrid + permission-aware retrieval →
generation → cited answer into a single callable RAG assistant, and
demonstrate it answering a grounded question with correct citations and
role-appropriate filtering.

Tasks:

-   Compose retrieval (hybrid + permission-aware) into one query path
-   Pass retrieved context to the generation call
-   Return answer with citations
-   Enforce the caller's Dataverse role in retrieval
-   End-to-end test with two users seeing different results

Deliverable: `/src/rag` assistant entrypoint + test

------------------------------------------------------------------------

# Epic 10 -- AI Agents

**Suggested milestone:** Month 5
**Goal:** Orchestrate multi-agent workflows with tooling, approval and
guardrails.

## Feature -- Agent Orchestration Framework

Stories:

-   Spike: choose framework (Semantic Kernel / AutoGen / custom) and
    record ADR

## Feature -- Core Agents

Stories:

-   Planner
-   Researcher
-   Reviewer
-   Reporter

## Feature -- Tool Registry

Stories:

-   Tool registry

## Feature -- Human-in-the-Loop / Approval

Stories:

-   Approval workflow

## Feature -- Agent Telemetry & Tracing

Stories:

-   Agent telemetry

## Feature -- Agent Safety & Guardrails

Stories:

-   Tool allow-lists
-   Injection resistance (links to Epic 11)

## Feature -- End-to-End Multi-Agent Workflow (assembly)

Assembles the individual agents into one orchestrated workflow — the
portfolio deliverable for this epic.

### Story -- Orchestrate the planner→researcher→reviewer→reporter workflow

**SMART Objective**

Run all four agents as a single workflow that takes a goal, plans,
researches (via the tool registry, reusing the Epic 8 tool layer and
Epic 9 RAG), reviews, and produces a report, with an approval gate on
any write action and full agent telemetry.

Tasks:

-   Compose the four agents into one orchestrated run
-   Route tool use through the registry (reusing Epic 8 tools)
-   Insert human approval before write actions
-   Emit agent telemetry/traces for the full run
-   End-to-end test producing a report from a sample goal

Deliverable: `/src/agents` workflow entrypoint + test

------------------------------------------------------------------------

# Epic 11 -- Security & Governance

**Suggested milestone:** Month 6 (policies apply continuously from
Month 1).
**Goal:** Make security, responsible AI and observability first-class.
This epic is the **policy + final-hardening layer**: most capabilities
are *implemented* in earlier epics; the stories here define the policy,
consolidate scattered implementations, and perform a hardening pass.
This avoids duplicating work already scheduled elsewhere.

## Feature -- Threat Modelling

New implementation work (not owned elsewhere).

Stories:

-   Threat model the end-to-end solution (STRIDE or similar)

## Feature -- LLM Security / Prompt Injection Testing

New implementation work.

Stories:

-   Build a prompt-injection test suite against the assistant and agents
-   Verify agent tool allow-lists (Epic 10 guardrails) hold under attack

## Feature -- Audit Logging (governance)

**Implemented in:** Dataverse auditing (3.6), ingestion logging (4.6),
prompt/response logging (Epic 8). This feature owns the *policy* and a
completeness check, not a fresh logging build.

Stories:

-   Define the audit-logging policy (what must be logged, retention)
-   Completeness audit across 3.6 / 4.6 / Epic 8; close any gaps

## Feature -- Permission-Aware Access & Data Boundaries (policy)

**Implemented in:** Epic 9 permission-aware retrieval, Epic 3 security
roles.

Stories:

-   Define the access-boundary policy
-   Verify enforcement end-to-end with multi-user tests

## Feature -- Responsible AI

New assessment work. Map explicitly to the NIST AI Risk Management
Framework.

Stories:

-   Responsible AI assessment mapped to NIST AI RMF functions

## Feature -- Identity & Secrets Management (authoritative)

**Owns the production implementation.** Epic 1 secrets management covers
local `.env` only; this feature moves production secrets/identity to
Azure.

Stories:

-   Managed Identity for Azure services (replace client secrets where
    possible)
-   Key Vault for all production secrets
-   Migrate function/app configuration off inline secrets

## Feature -- Cost Monitoring

New implementation work.

Stories:

-   Configure cost alerts and a spend dashboard (Azure OpenAI, Search,
    Functions)

## Feature -- Observability & Telemetry (consolidation)

**Implemented in:** ingestion observability (4.6), agent telemetry (Epic
10). This feature consolidates them into one standard and dashboard.

Stories:

-   Define the observability standard (logs, metrics, traces)
-   Consolidate ingestion + agent telemetry into a single dashboard and
    alerting baseline

------------------------------------------------------------------------

# Epic 12 -- Capstone

**Suggested milestone:** Month 6
**Goal:** Deliver a production-style Dynamics application that ties
everything together.

## Feature -- End-to-End Integration

Decomposed into discrete integration stories rather than one blob. Each
produces a demonstrable slice.

### Story -- Ingestion + analytics visible in the app

**SMART Objective**

Show ingested OpenF1 data and FastF1 summaries surfaced inside the
model-driven app.

### Story -- RAG assistant wired into the front end

**SMART Objective**

Expose the Epic 9 RAG assistant from the app (or a linked surface),
answering grounded, permission-aware questions.

### Story -- Agent workflow triggerable end-to-end

**SMART Objective**

Trigger the Epic 10 multi-agent workflow from a user action and view its
report output.

### Story -- AI request/response logging visible in Dataverse

**SMART Objective**

Demonstrate AI interactions recorded in the AI Request / AI Response
tables and linked to the audit trail.

## Feature -- Azure Deployment & Infrastructure as Code

**Decision required:** ADR-0002 selects the primary IaC tool (Bicep is
the Microsoft-aligned default); the repo currently ships both `bicep/`
and `terraform/`.

Stories:

-   Record ADR-0002 (primary IaC tool)
-   Author IaC for all Azure resources
-   Parameterise environments

## Feature -- Deployment CI/CD

Distinct from Epic 1's build CI.

Stories:

-   Build deployment workflow (infra + app)
-   Environment promotion

## Feature -- Architecture Documentation Pack

Stories:

-   Architecture documentation
-   Diagrams (Mermaid)

## Feature -- Demo Walkthrough & Portfolio Packaging

Stories:

-   Demo walkthrough
-   Portfolio packaging in `/portfolio`

------------------------------------------------------------------------

# Continuous Backlog

Weekly:

-   Journal
-   Git commits
-   Refactoring
-   Architecture notes

Fortnightly:

-   Technical blog
-   ADR

Monthly:

-   Release
-   Retrospective
-   Roadmap review

------------------------------------------------------------------------

# Definition of Success

At the end of six months the repository should contain:

-   Production-quality code
-   Architecture diagrams
-   ADRs
-   Azure deployment
-   Automated CI/CD
-   AI portfolio
-   Documentation
-   Demo walkthrough
-   Public GitHub project
