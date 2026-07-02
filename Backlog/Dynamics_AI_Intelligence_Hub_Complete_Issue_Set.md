# Dynamics AI Intelligence Hub — Complete GitHub Issue Set

> Single-file consolidation of the entire issue backlog: the master
> index (with the per-milestone workload tally, ADR register and
> dependency chains) followed by all 87 full-spec, copy-paste-ready
> issues.
>
> **How this file is organised.** The index below is the navigation hub —
> its register table lists every issue by ID (1.1 -> 12.8) with its story
> points, milestone and originating tier. The issues themselves then
> follow, grouped by tier exactly as drafted. To work in epic order,
> read the index table top-to-bottom and jump to the matching section.
>
> Tier map: Tier 1 = cross-cutting high-risk features - Tier 2 = Epic 3/4
> (Dataverse & OpenF1) - Tier 3 = coverage-gap stories - Tier 4 = Epic
> 1/2 (Foundation & Python) - Tier 5 = Epic 5/6 (FastF1 & Data Eng) -
> Tier 6 = Epic 7 (ML) - Tier 7 = Epic 8 (GenAI) - Tier 8 = Epic 9/10
> (RAG & Agents) - Tier 9 = Epic 11/12 (Security & Capstone).




========================================================================


# Dynamics AI Intelligence Hub — Backlog Issue Index

> Master index of the complete issue set (70 items) across all tiers.
> Every story/spike in backlog v0.3 now has a full-spec, copy-paste-ready
> issue. Use this as the checklist when creating GitHub Issues and to
> read the per-milestone workload.
>
> **Files:**
> - Tier 1 — `GitHub_Issue_Drafts_High_Risk_Features.md`
> - Tier 2 — `GitHub_Issue_Drafts_Tier2_Dataverse_OpenF1.md`
> - Tier 3 — `GitHub_Issue_Drafts_Tier3_Coverage_Gaps.md`
> - Tier 4 — `GitHub_Issue_Drafts_Tier4_Foundation_Python.md`
> - Tier 5 — `GitHub_Issue_Drafts_Tier5_FastF1_DataEng.md`
> - Tier 6 — `GitHub_Issue_Drafts_Tier6_MachineLearning.md`
> - Tier 7 — `GitHub_Issue_Drafts_Tier7_GenerativeAI.md`
> - Tier 8 — `GitHub_Issue_Drafts_Tier8_RAG_Agents.md`
> - Tier 9 — `GitHub_Issue_Drafts_Tier9_Security_Capstone.md`

------------------------------------------------------------------------
# Full issue register
------------------------------------------------------------------------

| ID | Title | Type | Pts | Milestone | Tier |
|----|-------|------|-----|-----------|------|
| 1.1 | Configure workstation and project skeleton | Story | 3 | M1 | 4 |
| 1.2 | Repository governance and templates | Story | 3 | M1 | 4 |
| 1.3 | Documentation scaffolding and ADR log | Story | 2 | M1 | 4 |
| 1.4 | Local secrets and config management | Story | 2 | M1 | 4 |
| CI | CI pipeline (lint/type/test/coverage) | Story | 5 | M1 | 1 |
| IaC | Select primary IaC tool (ADR-0002) | Spike | 2 | M1 | 1 |
| 2.1 | Python fundamentals + tested utils | Story | 5 | M1 | 4 |
| 2.2 | Build the reusable REST client | Story | 5 | M1 | 4 |
| 2.3 | Testing patterns and coverage discipline | Story | 3 | M1 | 4 |
| 2.A | Build the shared utilities package | Story | 3 | M1 | 3 |
| 2.B | Build reusable resilience utilities | Story | 3 | M1 | 3 |
| 3.1 | Design the generic CRM ERD | Story | 3 | M2 | 2 |
| 3.2 | Create Dataverse tables and relationships | Story | 5 | M2 | 2 |
| 3.3 | Configure forms and views | Story | 3 | M2 | 2 |
| 3.4 | Build the model-driven app | Story | 5 | M2 | 2 |
| 3.5 | Configure security roles and teams | Story | 3 | M2 | 2 |
| 3.6 | Enable auditing and BPF history | Story | 2 | M2 | 2 |
| 3.7 | Generate and seed sample CRM data | Story | 5 | M2 | 2 |
| DVAPI | Dataverse API access from Python | Story | 8 | M2 | 1 |
| FnPlat | Serverless platform foundation | Story | 5 | M2 | 1 |
| 4.1 | Build the OpenF1 ingestion client | Story | 5 | M2 | 2 |
| 4.2 | Add resilience and rate limiting | Story | 3 | M2 | 2 |
| 4.3 | Validate OpenF1 responses (Pydantic) | Story | 3 | M2 | 2 |
| 4.4 | Persist OpenF1 data to Dataverse | Story | 5 | M2 | 2 |
| 4.5 | Schedule ingestion (timer Function) | Story | 3 | M2 | 2 |
| 4.6 | Ingestion observability | Story | 2 | M2 | 2 |
| 5.1 | Configure FastF1 and cache | Story | 2 | M3 | 5 |
| 5.2 | Lap-telemetry notebook | Story | 3 | M3 | 5 |
| 5.3 | Driver/stint comparison notebook | Story | 3 | M3 | 5 |
| 5.4 | Extract reusable telemetry helpers | Story | 3 | M3 | 5 |
| 5.5 | Publish summaries to Dataverse | Story | 3 | M3 | 5 |
| 6.1 | Clean and normalise datasets | Story | 5 | M3 | 5 |
| 6.2 | Profile datasets + quality checks | Story | 3 | M3 | 5 |
| 6.3 | Export trusted datasets to Parquet | Story | 2 | M3 | 5 |
| 6.4 | Visualise ingestion + CRM trends | Story | 3 | M3 | 5 |
| 6.5 | Audit: actor/entity change patterns | Story | 3 | M3 | 5 |
| 6.6 | Audit: temporal patterns | Story | 3 | M3 | 5 |
| 6.7 | Audit: features for anomaly detection | Story | 3 | M3 | 5 |
| 6.8 | Reusable notebook templates | Story | 2 | M3 | 5 |
| 7.1 | Engineer feature sets for models | Story | 5 | M4 | 6 |
| 7.2 | Lap-time regression model | Story | 5 | M4 | 6 |
| 7.3 | Strategy classification model | Story | 5 | M4 | 6 |
| 7.4 | Clustering analysis | Story | 3 | M4 | 6 |
| 7.5 | Audit anomaly detection model | Story | 5 | M4 | 6 |
| 7.6 | Model evaluation and comparison | Story | 3 | M4 | 6 |
| 7.7 | Experiment tracking + model cards | Story | 3 | M4 | 6 |
| 7.8 | Package + serve model via Function | Story | 5 | M4 | 6 |
| 8.1 | Azure OpenAI / Foundry integration | Story | 3 | M5 | 7 |
| 8.2 | Prompt engineering + prompt library | Story | 3 | M5 | 7 |
| 8.3 | Structured outputs | Story | 3 | M5 | 7 |
| 8.4 | Function calling + ADR-0006 | Story | 5 | M5 | 7 |
| 8.5 | AI summaries | Story | 3 | M5 | 7 |
| 8.6 | CRM assistant scaffolding | Story | 5 | M5 | 7 |
| 8.7 | Ground the assistant with RAG | Story | 3 | M5 | 7 |
| 8.8 | Guarded CRM action tools | Story | 5 | M5 | 7 |
| 8.9 | Prompt and response logging | Story | 3 | M5 | 7 |
| 8.10 | GenAI output evaluation harness | Story | 3 | M5 | 7 |
| 9.1 | Document ingestion and chunking | Story | 5 | M5 | 8 |
| 9.2 | Generate embeddings | Story | 3 | M5 | 8 |
| 9.3 | Azure AI Search index | Story | 5 | M5 | 8 |
| 9.4 | Hybrid search retrieval | Story | 3 | M5 | 8 |
| 9.5 | Permission-aware retrieval | Story | 5 | M5 | 8 |
| 9.6 | Citations and grounding | Story | 3 | M5 | 8 |
| 9.7 | RAG evaluation | Story | 3 | M5 | 8 |
| 9.Z | Assemble end-to-end RAG assistant | Story | 8 | M5 | 3 |
| 10.1 | Choose agent framework (ADR-0007) | Spike | 2 | M5 | 8 |
| 10.2 | Build the four core agents | Story | 8 | M5 | 8 |
| 10.3 | Tool registry | Story | 3 | M5 | 8 |
| 10.4 | Human-in-the-loop approval | Story | 3 | M5 | 8 |
| 10.5 | Agent telemetry and tracing | Story | 3 | M5 | 8 |
| 10.6 | Agent safety and guardrails | Story | 3 | M5 | 8 |
| 10.Z | Orchestrate multi-agent workflow | Story | 8 | M5 | 3 |
| 11.A | Audit-logging policy + audit | Story | 3 | M6 | 3 |
| 11.B | Responsible AI (NIST AI RMF) | Story | 5 | M6 | 3 |
| 11.C | Key Vault + Managed Identity | Story | 5 | M6 | 3 |
| 11.D | Observability consolidation | Story | 3 | M6 | 3 |
| 11.E | Threat model (STRIDE) | Story | 5 | M6 | 9 |
| 11.F | Prompt-injection test suite | Story | 5 | M6 | 9 |
| 11.G | Cost monitoring + dashboard | Story | 3 | M6 | 9 |
| 12.1 | Ingestion + analytics in the app | Story | 5 | M6 | 9 |
| 12.2 | RAG assistant in the front end | Story | 5 | M6 | 9 |
| 12.3 | Agent workflow triggerable | Story | 5 | M6 | 9 |
| 12.4 | AI logging visible in Dataverse | Story | 3 | M6 | 9 |
| 12.5 | IaC for all Azure resources | Story | 8 | M6 | 9 |
| 12.6 | Deployment CI/CD | Story | 5 | M6 | 9 |
| 12.7 | Architecture documentation pack | Story | 5 | M6 | 9 |
| 12.8 | Demo walkthrough + portfolio | Story | 3 | M6 | 9 |

**Total: 87 issues** (85 stories + 2 spikes — the IaC-tool spike and the
agent-framework spike; the DVAPI/FnPlat/CI rows are stories).

------------------------------------------------------------------------
# Per-milestone points tally (workload check)
------------------------------------------------------------------------

| Milestone | Items | Story points | Assessment |
|-----------|-------|--------------|------------|
| M1 — Python & API Foundations | 11 | 36 | Full but front-loaded config; manageable |
| **M2 — Dataverse & Dynamics** | 15 | **60** | **Overloaded — the pressure point** |
| M3 — Data Engineering & Analytics | 13 | 38 | Balanced |
| M4 — Machine Learning | 8 | 34 | Balanced |
| **M5 — GenAI, RAG & Agents** | 25 | **101** | **Severely overloaded** |
| M6 — Governance, Deployment & Portfolio | 15 | 68 | Heavy and end-loaded |
| **Total** | **87** | **337** | ~30–45 pts/month sustainable; M2, M5 & M6 exceed it |

### What the tally tells you

For a solo learner also new to Python, a sustainable pace is roughly
30–45 points a month. **Month 5 (101 pts) is not deliverable as scheduled**
— it packs all of Epics 8, 9 and 10 including four 8-point items (9.Z,
10.2, 10.Z) plus the assistant, RAG pipeline and agent building blocks
into one month. **Month 2 (60 pts)** is the second pressure point, and
**Month 6 (68 pts)** is heavier than it looks because deployment,
governance and the portfolio all land together at the end.

### Suggested rebalancing (no scope cut)

1. **Split Month 5 across Months 5 and 6**, or spread Epics 8–10 from
   mid-Month 4. Concretely: move Epic 8 (GenAI, ~36 pts) to start in
   Month 4 once ML is underway, leaving RAG + Agents in Month 5.
2. **Push OpenF1 (Epic 4, ~26 pts) into early Month 3.** Month 3 (37 pts)
   has room; Month 2 does not. Dataverse (Epic 3) + the two Tier-1
   prerequisites already fill Month 2.
3. **Treat the assembly stories (9.Z, 10.Z) and their dependencies as the
   Month 5 critical path** — everything else in M5 can slip; these
   cannot, because Epic 12 depends on them.

------------------------------------------------------------------------
# ADR register
------------------------------------------------------------------------

| ADR | Decision | Raised in |
|-----|----------|-----------|
| ADR-0001 | Repository conventions | 1.3 |
| ADR-0002 | Primary IaC tool (Bicep vs Terraform) | IaC spike (Tier 1) |
| ADR-0003 | Dataverse auth (service principal → MI) | DVAPI (Tier 1); may be superseded by 11.C |
| ADR-0004 | Azure Functions hosting model | FnPlat (Tier 1) |
| ADR-0005 | Generic CRM schema approach | 3.1 |
| ADR-0006 | Function-calling vs agent-orchestration boundary | 8.4 |
| ADR-0007 | Agent orchestration framework | 10.1 |

------------------------------------------------------------------------
# Critical dependency chains (schedule around these)
------------------------------------------------------------------------

1. **2.A → 2.B → 2.2** — shared utils and resilience gate the REST
   client, which gates OpenF1.
2. **DVAPI (Dataverse API) → 4.4, 5.5, 8.5/8.6, 8.9** — Python
   write-access is the silent prerequisite for all persistence and
   logging.
3. **3.5 security roles → 9.5 permission-aware retrieval → 9.Z → 12.2** —
   the permission-aware RAG thread.
4. **3.6 auditing → 3.7 seeding → 6.5/6.6 → 6.7 → 7.5** — the audit-data
   thread feeding the anomaly model.
5. **8.4 tool layer → 10.3 registry → 10.2 agents → 10.Z → 12.3** — the
   agent thread; 9.Z also feeds 10.Z (researcher uses RAG).
6. **12.5 IaC → 12.6 deployment CI**, and **11.C secrets** depends on
   deployed services.

------------------------------------------------------------------------
# Labels used across the set
------------------------------------------------------------------------

`epic`, `feature`, `story`, `spike`, `task`, `python`, `azure`,
`dataverse`, `dynamics`, `openf1`, `fastf1`, `ml`, `rag`, `agent`, `ai`,
`security`, `governance`, `observability`, `documentation`,
`architecture`, `portfolio`, `foundation`, `api`, `blocked`,
`good-first-task`

> Note: `ai`, `observability`, `foundation` and `api` were used in issue
> drafts beyond the original recommended label set. Add them when
> configuring labels in issue 1.2, or relabel to the original set if you
> prefer to keep it tight.



========================================================================


# Dynamics AI Intelligence Hub — GitHub Issue Drafts

> Copy-paste-ready issue bodies for the four highest-risk new features
> introduced in backlog v0.2. Each is self-contained. Paste the body
> into a new GitHub Issue, apply the listed labels and milestone, and
> set the Story Points / Priority project fields.
>
> **Sequencing:** ADR-0002 (IaC) → CI/CD → Serverless Platform → Dataverse
> API Access is the safest order, but CI/CD and the IaC ADR can run in
> parallel with early Month-1 work. Dataverse API Access must land before
> Epics 4, 5 and 8 begin.

------------------------------------------------------------------------

## Issue 1 — Story: Dataverse API access from Python

**Type:** Story
**Epic:** Epic 3 — Dynamics & Dataverse
**Feature:** Dataverse API Access from Python
**Story Points:** 8
**Priority:** High (critical dependency)
**Milestone:** Month 2 — Dataverse and Dynamics Foundation
**Labels:** `story`, `dataverse`, `dynamics`, `python`, `azure`, `security`
**Suggested branch:** `feat/dataverse-api-client`
**Suggested PR title:** `feat(dataverse): reusable Dataverse Web API client with service principal auth`

### User Story

As a learner, I want a reusable, authenticated Python client for the
Dataverse Web API so that ingestion, analytics and AI features can read
and write CRM records without duplicating auth or HTTP logic.

### Goal

Deliver `src/dataverse/` — a tested Python package that authenticates to
a Dataverse dev environment and performs create, read, update, upsert
and batch operations.

### Business Value

Every downstream feature (OpenF1 persistence, FastF1 summaries, AI
request/response logging) depends on writing to Dataverse. A single
governed access layer prevents scattered, insecure auth code.

### Learning Value

Service principal / OAuth client-credentials flow, the Dataverse Web
API, `$batch` semantics, and secure secret handling — core skills for a
Dynamics-aligned AI architect.

### Dependencies

- **Blocks:** Epic 4 (OpenF1 persistence), Epic 5 (publish summaries),
  Epic 8 (AI request/response logging)
- **Requires:** Epic 3 tables exist (at least Account, Contact,
  AI Request, AI Response); Epic 1 secrets management

### Description

Register an Entra ID app registration, grant it an application user in
the Dataverse environment with an appropriate security role, and build a
thin, well-tested client wrapping the Web API. The client must acquire
tokens via the client-credentials flow, refresh on expiry, and expose
typed methods for CRUD, upsert (by alternate key) and batch. All secrets
come from environment/Key Vault, never source.

### Tasks

- [ ] Register Entra ID app registration and create a client secret
- [ ] Create an application user in the Dataverse environment and assign
      a least-privilege security role
- [ ] Implement token acquisition (client-credentials) with refresh
- [ ] Implement `create`, `retrieve`, `retrieve_multiple`, `update`,
      `delete`
- [ ] Implement `upsert` by alternate key
- [ ] Implement `$batch` for bulk writes
- [ ] Load credentials from environment (`.env` locally, secrets in CI)
- [ ] Add structured logging and typed exceptions
- [ ] Write unit tests (mocked HTTP) — target ≥ 20
- [ ] Write one integration test against the dev environment (guarded
      behind an env flag)
- [ ] Draft ADR-0003 (auth approach: service principal now, path to
      managed identity later)
- [ ] Update README with setup and usage

### SMART Acceptance Criteria

- [ ] **Specific:** `src/dataverse` exposes CRUD, upsert and batch
      methods against the Dataverse Web API.
- [ ] **Measurable:** ≥ 20 unit tests pass with ≥ 90% coverage of the
      client module; one integration test creates and deletes a record
      in the dev environment.
- [ ] **Achievable:** Uses only the client-credentials flow and the REST
      Web API (no plugin/SDK compilation).
- [ ] **Relevant:** Every later persistence feature imports this client.
- [ ] **Time-bound:** Complete within the first two weeks of Month 2.

### Definition of Ready

- [ ] Dataverse dev environment available
- [ ] Target entities and alternate keys agreed
- [ ] Secret storage mechanism (Epic 1) in place

### Definition of Done

- [ ] Code merged with green CI
- [ ] Unit + integration tests pass
- [ ] No secrets in source or history
- [ ] ADR-0003 recorded
- [ ] README usage section added

### Deliverables

- `src/dataverse/` package
- `tests/dataverse/`
- `docs/decisions/ADR-0003-dataverse-auth.md`

### Learning Resources

- **Microsoft Learn — Dataverse Web API (Use the Web API):** reference
  for entity URLs, CRUD verbs, `$batch` and query options — use while
  implementing the client methods.
- **Microsoft Learn — OAuth client-credentials flow (Microsoft identity
  platform):** use when implementing app-only token acquisition.
- **Microsoft Learn — Create an application user in Dataverse:** use
  when wiring the service principal into the environment.
- **MSAL for Python documentation:** use for the token acquisition and
  refresh implementation.

------------------------------------------------------------------------

## Issue 2 — Story: Serverless platform foundation (Azure Functions)

**Type:** Story
**Epic:** Epic 4 — OpenF1 Integration
**Feature:** Serverless Platform Foundation
**Story Points:** 5
**Priority:** High (cross-cutting dependency)
**Milestone:** Month 2 — Dataverse and Dynamics Foundation
**Labels:** `story`, `azure`, `python`, `architecture`, `foundation`
**Suggested branch:** `feat/azure-functions-foundation`
**Suggested PR title:** `feat(functions): establish Azure Functions Python project and local dev`

### User Story

As a learner, I want a working Azure Functions Python project with local
run and deploy proven once, so that ingestion, AI orchestration and
inference can all reuse the same serverless foundation.

### Goal

Stand up `src/azure_functions/` with one timer trigger and one HTTP
trigger, runnable locally and deployable to Azure, with the hosting
model chosen and recorded.

### Business Value

Establishes the serverless runtime that Epics 4, 8 and 10 depend on.
Doing it once, well, avoids three inconsistent function apps later.

### Learning Value

Functions programming model (v2 Python), triggers/bindings, local Core
Tools workflow, and hosting-plan trade-offs.

### Dependencies

- **Blocks:** Epic 4 scheduled ingestion, Epic 8 AI orchestration,
  Epic 7 model inference, Epic 10 agents
- **Requires:** Epic 1 environment; a decision on hosting plan

### Description

Scaffold a single Functions app using the Python v2 model. Add a
timer-triggered function (placeholder for ingestion) and an
HTTP-triggered function (placeholder for AI/health). Prove `func start`
locally and a deploy smoke test to a dev Function App. Record the
hosting-model decision in an ADR.

### Tasks

- [ ] Install Azure Functions Core Tools
- [ ] Scaffold Python v2 Functions project in `src/azure_functions`
- [ ] Add a timer-triggered function (placeholder)
- [ ] Add an HTTP-triggered function (health/echo)
- [ ] Configure `local.settings.json` (gitignored) and settings template
- [ ] Wire structured logging via Application Insights bindings
- [ ] Run locally with `func start` and verify both triggers
- [ ] Deploy to a dev Function App and smoke test
- [ ] Draft ADR-0004 (hosting model: Consumption vs Flex Consumption)
- [ ] Document local dev + deploy in README

### SMART Acceptance Criteria

- [ ] **Specific:** A single Python v2 Functions app with one timer and
      one HTTP trigger exists in `src/azure_functions`.
- [ ] **Measurable:** Both triggers run locally via `func start`; the
      HTTP trigger returns 200 from the deployed dev Function App.
- [ ] **Achievable:** Placeholder logic only — no business logic yet.
- [ ] **Relevant:** Later epics add functions to this same app.
- [ ] **Time-bound:** Complete within one week of Month 2.

### Definition of Ready

- [ ] Azure subscription and resource group available
- [ ] Hosting-plan options understood

### Definition of Done

- [ ] Both triggers run locally and the HTTP trigger is reachable when
      deployed
- [ ] No secrets committed
- [ ] ADR-0004 recorded
- [ ] README dev/deploy section added
- [ ] Green CI

### Deliverables

- `src/azure_functions/` project
- `docs/decisions/ADR-0004-functions-hosting-model.md`

### Learning Resources

- **Microsoft Learn — Azure Functions Python developer guide:** use as
  the primary reference for the v2 programming model, triggers and
  bindings.
- **Microsoft Learn — Work with Azure Functions Core Tools:** use for
  local scaffolding, `func start` and deployment.
- **Microsoft Learn — Azure Functions hosting options:** use when
  choosing between Consumption and Flex Consumption for ADR-0004.

------------------------------------------------------------------------

## Issue 3 — Story: CI pipeline (lint, type, test, coverage gate)

**Type:** Story
**Epic:** Epic 1 — Foundation
**Feature:** CI/CD Pipeline
**Story Points:** 5
**Priority:** High
**Milestone:** Month 1 — Python and API Foundations
**Labels:** `story`, `python`, `documentation`, `foundation`
**Suggested branch:** `feat/ci-pipeline`
**Suggested PR title:** `ci: add lint, type-check, test and coverage-gated GitHub Actions workflow`

### User Story

As a learner, I want a GitHub Actions workflow that runs formatting,
lint, type checks and tests with a coverage gate on every push and PR,
so that quality is enforced automatically from day one.

### Goal

A green, required CI workflow that blocks merges when checks fail, with
status badges on the README.

### Business Value

Automated quality gates are table stakes for a credible portfolio and
prevent regressions as the codebase grows across 12 epics.

### Learning Value

GitHub Actions workflow syntax, matrix/caching, and integrating Ruff,
Black, MyPy and pytest-cov into CI.

### Dependencies

- **Requires:** Epic 1 environment (tools installed), a repository with
  at least one testable module
- **Precedes:** effectively gates all later merges

### Description

Author `.github/workflows/ci.yml` running on push and pull_request. It
sets up Python 3.12, installs dependencies with caching, runs Black
`--check`, Ruff, MyPy and pytest with coverage, and fails below a
coverage threshold. Add branch protection requiring the workflow to
pass, and add badges to the README.

### Tasks

- [ ] Create `.github/workflows/ci.yml`
- [ ] Set up Python 3.12 and dependency caching
- [ ] Add Black `--check` step
- [ ] Add Ruff lint step
- [ ] Add MyPy type-check step
- [ ] Add pytest with `--cov` and a `--cov-fail-under` threshold
- [ ] Upload coverage as an artifact
- [ ] Configure branch protection to require the CI check
- [ ] Add CI and coverage badges to README
- [ ] Document how to run the same checks locally

### SMART Acceptance Criteria

- [ ] **Specific:** A single workflow runs format, lint, type and test
      steps on push and PR.
- [ ] **Measurable:** The workflow fails the build when coverage is
      below the configured threshold (initially 80%); a passing badge
      renders on the README.
- [ ] **Achievable:** Uses standard `actions/setup-python` and pip
      caching — no bespoke infrastructure.
- [ ] **Relevant:** Every subsequent PR is gated by this workflow.
- [ ] **Time-bound:** Complete within the first week of Month 1.

### Definition of Ready

- [ ] Repository exists with a testable module and `pyproject.toml`
- [ ] Tooling (Ruff, Black, MyPy, pytest) configured

### Definition of Done

- [ ] Workflow green on `main`
- [ ] Branch protection requires the check
- [ ] Coverage gate demonstrably fails on an under-covered branch
- [ ] Badges added to README

### Deliverables

- `.github/workflows/ci.yml`
- README badges and "running checks locally" section

### Learning Resources

- **GitHub Docs — Building and testing Python (Actions):** use as the
  template for the workflow structure and Python setup.
- **GitHub Docs — Managing branch protection rules:** use when making
  the CI check required for merges.
- **Ruff and pytest-cov documentation:** use when configuring the lint
  and coverage-gate steps.

------------------------------------------------------------------------

## Issue 4 — Spike: Select the primary Infrastructure-as-Code tool (ADR-0002)

**Type:** Spike
**Epic:** Epic 1 — Foundation (decision consumed by Epic 12)
**Feature:** Documentation Scaffolding / Azure Deployment & IaC
**Story Points:** 2
**Priority:** Medium-High (must precede any Azure provisioning)
**Milestone:** Month 1 — Python and API Foundations
**Labels:** `spike`, `architecture`, `azure`, `documentation`
**Suggested branch:** `spike/iac-tool-adr`
**Suggested PR title:** `docs(adr): ADR-0002 select primary Infrastructure-as-Code tool`

### Goal

Decide and record whether Bicep or Terraform is the project's primary
IaC tool, and prune the repository to a single approach.

### Business Value

The repo ships both `infrastructure/bicep/` and `infrastructure/terraform/`.
Maintaining two IaC toolchains as a solo learner is wasted effort and a
portfolio inconsistency; one clear choice reads as deliberate.

### Learning Value

Comparative evaluation of Azure IaC tooling and the discipline of
recording an architectural decision with trade-offs.

### Dependencies

- **Blocks:** all Azure provisioning (Epic 4 Functions deploy, Epic 12
  deployment)
- **Requires:** nothing beyond the repo

### Description

A time-boxed decision spike. Compare Bicep and Terraform for this
project against the criteria below, pick one, record ADR-0002, and
either remove the unused folder or clearly mark it out of scope. Bicep
is the Microsoft-aligned default and is the recommended starting
position unless a specific reason favours Terraform.

**Decision criteria:** Microsoft alignment / portfolio signal, learning
curve for a solo learner, Azure resource coverage, state management
overhead, and community/tooling maturity.

### Tasks

- [ ] Summarise Bicep vs Terraform against the decision criteria
- [ ] Draft a minimal proof snippet for the leading option (e.g. a
      resource group + storage account)
- [ ] Make the decision
- [ ] Write ADR-0002 using the project ADR format
- [ ] Remove or clearly deprecate the unused `infrastructure/` subfolder
- [ ] Update README/backlog to reference the chosen tool

### SMART Acceptance Criteria

- [ ] **Specific:** ADR-0002 names one primary IaC tool with rationale
      and trade-offs.
- [ ] **Measurable:** Exactly one active IaC folder remains under
      `infrastructure/`; the other is removed or marked deprecated.
- [ ] **Achievable:** Time-boxed to a single focused session (≤ 4 hours).
- [ ] **Relevant:** Unblocks all later Azure deployment work.
- [ ] **Time-bound:** Complete within Month 1.

### Definition of Ready

- [ ] Decision criteria agreed
- [ ] ADR template available in `docs/decisions`

### Definition of Done

- [ ] ADR-0002 merged (status Accepted)
- [ ] Repository reflects the single chosen tool
- [ ] Backlog/README updated

### Deliverables

- `docs/decisions/ADR-0002-iac-tool.md`
- Pruned `infrastructure/` tree

### ADR-0002 skeleton

```markdown
# ADR-0002: Primary Infrastructure-as-Code tool
## Status
Proposed
## Context
The repository currently contains both Bicep and Terraform folders.
A solo learner cannot maintain two IaC toolchains credibly.
## Decision
<Bicep | Terraform> is the primary IaC tool for this project.
## Options Considered
1. Bicep — Microsoft-native, no state files, strong Azure alignment.
2. Terraform — multi-cloud, mature ecosystem, explicit state management.
3. Both — rejected: duplicate effort, inconsistent portfolio signal.
## Consequences
Positive: single toolchain, clearer portfolio narrative.
Negative: <e.g. less multi-cloud transferability if Bicep chosen>.
## Follow-up Actions
- [ ] Remove the unused infrastructure subfolder
- [ ] Author baseline IaC for the dev Function App (Epic 12)
```

### Learning Resources

- **Microsoft Learn — What is Bicep?:** use when evaluating the
  Microsoft-native option and drafting the proof snippet.
- **Azure Architecture Center — Infrastructure as Code:** use for the
  comparative framing and best practices.
- **HashiCorp — Terraform on Azure (azurerm provider) docs:** use if
  evaluating Terraform seriously.



========================================================================


# Dynamics AI Intelligence Hub — GitHub Issue Drafts (Tier 2)

> Copy-paste-ready issue bodies for Epic 3 (Dynamics & Dataverse) and
> Epic 4 (OpenF1 Integration). Paste each body into a new GitHub Issue,
> apply the listed labels and milestone, and set the Story Points /
> Priority project fields.
>
> **Already drafted elsewhere (Tier 1 file):** *Dataverse API access
> from Python* (Epic 3) and *Serverless platform foundation* (Epic 4).
> Those are prerequisites referenced below.
>
> **Suggested build order:** 3.1 → 3.2 → 3.3 → 3.4 → 3.5 → 3.6 → 3.7,
> then Epic 4 (which also needs the Tier-1 Dataverse API and Functions
> stories in place). 4.1 → 4.3 → 4.2 → 4.4 → 4.5 → 4.6.

------------------------------------------------------------------------
------------------------------------------------------------------------

# EPIC 3 — DYNAMICS & DATAVERSE

------------------------------------------------------------------------

## Issue 3.1 — Story: Design the generic CRM ERD

**Type:** Story
**Feature:** Data Model & ERD
**Story Points:** 3
**Priority:** High
**Milestone:** Month 2 — Dataverse and Dynamics Foundation
**Labels:** `story`, `dataverse`, `dynamics`, `architecture`, `documentation`
**Suggested branch:** `feat/crm-erd`
**Suggested PR title:** `docs(dataverse): generic CRM entity-relationship diagram and schema notes`

### User Story

As a learner, I want a documented, client-agnostic CRM data model so
that every table, relationship and key is agreed before I build
anything in Dataverse.

### Goal

Produce an ERD and schema notes covering the generic CRM entities, with
relationships, keys and the AI-specific tables.

### Business Value

A design-first artefact prevents costly rework of tables and
relationships and reads as deliberate architecture in the portfolio.

### Learning Value

Dataverse relationship types (1:N, N:N), alternate keys, and modelling
an audit + AI-logging schema.

### Dependencies

- **Blocks:** 3.2 (Create tables)
- **Requires:** nothing beyond the repo

### Description

Model the entities: Account, Contact, Lead, Opportunity, Case, Activity,
Product, Knowledge Article, Document, Audit Event, AI Request, AI
Response. Define relationships, primary and alternate keys, and the
link between AI Request and AI Response and the records they act on.
Deliver as a Mermaid ERD plus a short schema note, and record an ADR for
the schema approach.

### Tasks

- [ ] List entities and their key attributes
- [ ] Define relationships (1:N, N:N) and cascade behaviour
- [ ] Define primary names and alternate keys (needed for upsert)
- [ ] Model AI Request / AI Response and their links to CRM records
- [ ] Author the ERD in Mermaid under `docs/diagrams`
- [ ] Write a schema note under `docs/architecture`
- [ ] Draft ADR-0005 (generic CRM schema approach)

### SMART Acceptance Criteria

- [ ] **Specific:** A Mermaid ERD covers all 12 entities with typed
      relationships and named keys.
- [ ] **Measurable:** Every entity has at least one alternate key
      defined where upsert is expected; the ERD renders in GitHub.
- [ ] **Achievable:** Design only — no Dataverse build in this story.
- [ ] **Relevant:** Directly drives table creation in 3.2.
- [ ] **Time-bound:** Complete within two days of starting Month 2.

### Definition of Ready

- [ ] Allowed generic entity list confirmed
- [ ] ADR template available

### Definition of Done

- [ ] ERD and schema note merged
- [ ] ADR-0005 recorded
- [ ] ERD renders correctly on GitHub

### Deliverables

- `docs/diagrams/crm-erd.md` (Mermaid)
- `docs/architecture/crm-schema-notes.md`
- `docs/decisions/ADR-0005-crm-schema.md`

### Learning Resources

- **Microsoft Learn — Dataverse table relationships:** use when
  defining 1:N and N:N relationships and cascade behaviour.
- **Microsoft Learn — Alternate keys for Dataverse tables:** use when
  choosing keys that support upsert from Python.
- **Mermaid ER diagram syntax:** use when authoring the ERD.

------------------------------------------------------------------------

## Issue 3.2 — Story: Create Dataverse tables and relationships

**Type:** Story
**Feature:** Dataverse Tables & Relationships
**Story Points:** 5
**Priority:** High
**Milestone:** Month 2 — Dataverse and Dynamics Foundation
**Labels:** `story`, `dataverse`, `dynamics`
**Suggested branch:** `feat/dataverse-tables`
**Suggested PR title:** `feat(dataverse): create generic CRM tables, columns and relationships`

### User Story

As a learner, I want the generic CRM tables built in a Dataverse
solution so that data can be stored, related and later accessed from
Python.

### Goal

Create all entities from the ERD as tables in a managed-friendly
unmanaged solution, with columns, relationships and alternate keys.

### Business Value

The data layer that every downstream feature reads from and writes to.

### Learning Value

Solution-based development, column data types, relationship
configuration and publishing.

### Dependencies

- **Blocks:** 3.3 Forms & Views, 3.7 Sample data, Tier-1 Dataverse API
  access
- **Requires:** 3.1 ERD

### Description

Create a dedicated unmanaged solution and add the tables from the ERD.
Configure columns with correct data types, set primary names, add
alternate keys, and create the relationships. Publish and export the
solution to source control.

### Tasks

- [ ] Create a publisher and unmanaged solution
- [ ] Create each table with its columns and data types
- [ ] Set primary name columns
- [ ] Add alternate keys per the ERD
- [ ] Create relationships (1:N, N:N)
- [ ] Create the AI Request / AI Response tables
- [ ] Publish all customisations
- [ ] Export the unmanaged solution into the repo

### SMART Acceptance Criteria

- [ ] **Specific:** All 12 entities exist as tables in one solution with
      relationships matching the ERD.
- [ ] **Measurable:** Every alternate key defined in 3.1 exists; the
      exported solution is committed under `dataverse/solutions`.
- [ ] **Achievable:** Uses maker portal + solution export; no code.
- [ ] **Relevant:** Enables forms, app, API access and seeding.
- [ ] **Time-bound:** Complete within the first week of Month 2.

### Definition of Ready

- [ ] 3.1 ERD merged
- [ ] Dataverse dev environment available

### Definition of Done

- [ ] Tables, columns, keys and relationships created and published
- [ ] Solution exported and committed
- [ ] Spot-check: a record can be created manually in each table

### Deliverables

- Dataverse tables in the dev environment
- Exported unmanaged solution in the repo (`dataverse/solutions/`)

### Learning Resources

- **Microsoft Learn — Create and edit tables in Dataverse:** use for
  table and column creation.
- **Microsoft Learn — Solutions overview (Power Platform):** use for
  solution-based development and export.

------------------------------------------------------------------------

## Issue 3.3 — Story: Configure forms and views

**Type:** Story
**Feature:** Forms & Views
**Story Points:** 3
**Priority:** Medium
**Milestone:** Month 2 — Dataverse and Dynamics Foundation
**Labels:** `story`, `dataverse`, `dynamics`
**Suggested branch:** `feat/forms-and-views`
**Suggested PR title:** `feat(dataverse): main forms and primary views for core entities`

### User Story

As a learner, I want usable forms and views on the core entities so that
records are readable and the model-driven app has something to render.

### Goal

Configure a main form and at least one useful view for each core entity.

### Dependencies

- **Blocks:** 3.4 Model-driven app
- **Requires:** 3.2 Tables

### Tasks

- [ ] Configure main forms for Account, Contact, Lead, Opportunity,
      Case, Activity, Product, Knowledge Article
- [ ] Configure a default and one custom view per core entity
- [ ] Add quick-find columns
- [ ] Publish and export into the solution

### SMART Acceptance Criteria

- [ ] **Specific:** Each core entity has a main form and ≥ 2 views.
- [ ] **Measurable:** Quick-find returns results on the primary name
      column for each core entity.
- [ ] **Achievable:** Maker-portal configuration only.
- [ ] **Relevant:** Feeds the model-driven app.
- [ ] **Time-bound:** Complete within Month 2.

### Definition of Done

- [ ] Forms and views published and exported to the solution
- [ ] Committed to the repo

### Deliverables

- Updated solution with forms and views

### Learning Resources

- **Microsoft Learn — Create and design forms:** use when building main
  forms.
- **Microsoft Learn — Create or edit views:** use when configuring views
  and quick-find.

------------------------------------------------------------------------

## Issue 3.4 — Story: Build the model-driven app

**Type:** Story
**Feature:** Model-Driven App
**Story Points:** 5
**Priority:** Medium
**Milestone:** Month 2 — Dataverse and Dynamics Foundation
**Labels:** `story`, `dynamics`, `dataverse`, `portfolio`
**Suggested branch:** `feat/model-driven-app`
**Suggested PR title:** `feat(dynamics): generic CRM model-driven app with sitemap`

### User Story

As a learner, I want a model-driven app exposing the core entities so
that the portfolio has a usable Dynamics front end.

### Goal

Create a model-driven app with a coherent sitemap over the core
entities.

### Dependencies

- **Requires:** 3.3 Forms & Views
- **Blocks:** later demo/capstone

### Tasks

- [ ] Create the model-driven app
- [ ] Add core entities to the sitemap grouped logically
- [ ] Configure navigation areas/groups
- [ ] Validate and publish the app
- [ ] Capture screenshots for the portfolio
- [ ] Export into the solution

### SMART Acceptance Criteria

- [ ] **Specific:** One model-driven app surfaces all core entities via
      a grouped sitemap.
- [ ] **Measurable:** The app opens and each entity list loads without
      error; ≥ 3 screenshots captured.
- [ ] **Achievable:** App designer only.
- [ ] **Relevant:** Portfolio-visible Dynamics front end.
- [ ] **Time-bound:** Complete within Month 2.

### Definition of Done

- [ ] App published and exported to the solution
- [ ] Screenshots saved under `portfolio/`
- [ ] Committed to the repo

### Deliverables

- Model-driven app in the solution
- Screenshots in `portfolio/`

### Learning Resources

- **Microsoft Learn — Build your first model-driven app:** use for app
  and sitemap creation.

------------------------------------------------------------------------

## Issue 3.5 — Story: Configure security roles and teams

**Type:** Story
**Feature:** Security Roles & Teams
**Story Points:** 3
**Priority:** High
**Milestone:** Month 2 — Dataverse and Dynamics Foundation
**Labels:** `story`, `dataverse`, `dynamics`, `security`, `governance`
**Suggested branch:** `feat/security-roles`
**Suggested PR title:** `feat(dataverse): security roles and teams for permission-aware access`

### User Story

As a learner, I want security roles and teams configured so that
permission-aware retrieval (Epic 9) has real access boundaries to
enforce.

### Goal

Define least-privilege security roles and at least two teams that create
a meaningful access boundary for later RAG filtering.

### Business Value

Security is designed in from Month 2, not retrofitted; enables the
permission-aware RAG demo.

### Learning Value

Dataverse security model: business units, teams, roles, and privilege
depth.

### Dependencies

- **Requires:** 3.2 Tables
- **Blocks:** Epic 9 permission-aware retrieval, Tier-1 Dataverse API
  application user role

### Tasks

- [ ] Define 2–3 security roles with differentiated table privileges
- [ ] Create at least two teams
- [ ] Assign roles to teams
- [ ] Document the access model
- [ ] Export role definitions into the solution

### SMART Acceptance Criteria

- [ ] **Specific:** ≥ 2 roles and ≥ 2 teams exist with differentiated
      access to at least one entity (e.g. Knowledge Article / Document).
- [ ] **Measurable:** A test user in one team can access a record another
      team's user cannot.
- [ ] **Achievable:** Configuration only.
- [ ] **Relevant:** Directly enables Epic 9 filtering.
- [ ] **Time-bound:** Complete within Month 2.

### Definition of Done

- [ ] Roles/teams created, documented and exported
- [ ] Access boundary verified with two test users
- [ ] Committed to the repo

### Deliverables

- Security roles/teams in the solution
- `docs/security/access-model.md`

### Learning Resources

- **Microsoft Learn — Security roles and privileges (Dataverse):** use
  when defining roles and privilege depth.
- **Microsoft Learn — Manage teams in Dataverse:** use when creating
  teams and assigning roles.

------------------------------------------------------------------------

## Issue 3.6 — Story: Enable auditing and Business Process Flow history

**Type:** Story
**Feature:** Auditing & Business Process Flow History
**Story Points:** 2
**Priority:** Medium
**Milestone:** Month 2 — Dataverse and Dynamics Foundation
**Labels:** `story`, `dataverse`, `dynamics`, `governance`
**Suggested branch:** `feat/enable-auditing`
**Suggested PR title:** `feat(dataverse): enable auditing and BPF history for audit analytics`

### User Story

As a learner, I want auditing and Business Process Flow history enabled
so that Epic 6 has a real enterprise-style audit dataset to analyse.

### Goal

Enable environment and table-level auditing on core entities and turn on
BPF history capture.

### Dependencies

- **Requires:** 3.2 Tables
- **Blocks:** Epic 6 audit history analytics

### Tasks

- [ ] Enable auditing at the environment level
- [ ] Enable auditing on core entities and key columns
- [ ] Enable Business Process Flow and its history
- [ ] Generate a few changes to confirm audit records appear
- [ ] Document what is audited

### SMART Acceptance Criteria

- [ ] **Specific:** Auditing is enabled on all core entities and BPF
      history is captured.
- [ ] **Measurable:** Editing a record produces a retrievable audit
      entry; a BPF stage change is recorded.
- [ ] **Achievable:** Configuration only.
- [ ] **Relevant:** Supplies the Epic 6 dataset.
- [ ] **Time-bound:** Complete within Month 2.

### Definition of Done

- [ ] Auditing and BPF history enabled and verified
- [ ] `docs/architecture/auditing.md` written
- [ ] Committed to the repo

### Deliverables

- Auditing/BPF configuration
- `docs/architecture/auditing.md`

### Learning Resources

- **Microsoft Learn — Manage Dataverse auditing:** use when enabling and
  scoping auditing.
- **Microsoft Learn — Business process flows overview:** use when
  enabling BPF and its history.

------------------------------------------------------------------------

## Issue 3.7 — Story: Generate and seed sample CRM data

**Type:** Story
**Feature:** Sample CRM Data & Seeding
**Story Points:** 5
**Priority:** High (dependency for Epics 6–7)
**Milestone:** Month 2 — Dataverse and Dynamics Foundation
**Labels:** `story`, `dataverse`, `python`, `dynamics`
**Suggested branch:** `feat/sample-crm-seeder`
**Suggested PR title:** `feat(dataverse): client-agnostic sample CRM data generator and seeder`

### User Story

As a learner, I want a repeatable generator that seeds realistic,
client-agnostic CRM data (including audit history) so that analytics and
ML have data to work with.

### Goal

A Python seeder that creates synthetic Accounts, Contacts, Leads,
Opportunities, Cases and Activities via the Dataverse API, plus enough
record churn to produce meaningful audit history.

### Business Value

Unblocks Epics 6–7; makes the whole solution demonstrable without any
customer data.

### Learning Value

Synthetic data generation (e.g. Faker), idempotent seeding, and driving
the Dataverse API at volume.

### Dependencies

- **Requires:** 3.2 Tables, 3.6 Auditing enabled, Tier-1 Dataverse API
  client
- **Blocks:** Epic 6 (analytics), Epic 7 (ML)

### Description

Build a seeder under `src/dataverse` (or `datasets/sample-crm`
generator) that produces plausible, fully synthetic records with no
reference to any real person, employer or domain. Include a controlled
number of updates to seeded records so auditing produces a usable
history. Make it idempotent and parameterised by volume.

### Tasks

- [ ] Choose a synthetic-data approach (e.g. Faker) and document it
- [ ] Generate Accounts, Contacts, Leads
- [ ] Generate Opportunities, Cases, Activities linked to the above
- [ ] Apply a controlled set of updates to generate audit history
- [ ] Make the seeder idempotent (safe to re-run)
- [ ] Parameterise record volumes via config/CLI args
- [ ] Add unit tests for the generators (deterministic with a seed)
- [ ] Document how to run the seeder

### SMART Acceptance Criteria

- [ ] **Specific:** Running the seeder populates all six operational
      entities with linked, synthetic records and generates audit
      history.
- [ ] **Measurable:** A default run creates ≥ 200 records across entities
      and ≥ 50 audit entries; re-running does not duplicate records.
- [ ] **Achievable:** Uses the existing Dataverse client and a synthetic
      data library.
- [ ] **Relevant:** Provides the dataset for Epics 6–7.
- [ ] **Time-bound:** Complete within the second week of Month 2.

### Definition of Ready

- [ ] Tier-1 Dataverse API client merged
- [ ] Auditing enabled (3.6)

### Definition of Done

- [ ] Seeder runs idempotently and populates the environment
- [ ] Unit tests pass; green CI
- [ ] No real personal/client data anywhere
- [ ] README seeding section added

### Deliverables

- `src/dataverse/seed/` (or equivalent) generator
- `tests/dataverse/test_seed.py`
- README seeding instructions

### Learning Resources

- **Faker documentation:** use for generating synthetic names,
  companies and contact details.
- **Microsoft Learn — Dataverse Web API (batch/create):** use for
  efficient bulk seeding.

------------------------------------------------------------------------
------------------------------------------------------------------------

# EPIC 4 — OPENF1 INTEGRATION

> Prerequisites already drafted in Tier 1: *Serverless platform
> foundation* (used by 4.5) and *Dataverse API access from Python*
> (used by 4.4). Epic 2's reusable REST client underpins 4.1.

------------------------------------------------------------------------

## Issue 4.1 — Story: Build the OpenF1 ingestion client

**Type:** Story
**Feature:** Ingestion Client
**Story Points:** 5
**Priority:** High
**Milestone:** Month 2 — Dataverse and Dynamics Foundation
**Labels:** `story`, `openf1`, `python`, `api`
**Suggested branch:** `feat/openf1-client`
**Suggested PR title:** `feat(openf1): OpenF1 ingestion client for sessions, drivers and laps`

### User Story

As a learner, I want an OpenF1 client built on my reusable REST client
so that I can pull public F1 sessions, drivers and laps in a consistent,
tested way.

### Goal

`src/openf1/` client exposing typed methods to fetch sessions, drivers
and laps from the OpenF1 API.

### Business Value

The first real-world public data source flowing into the platform;
proves the Epic 2 REST client in anger.

### Learning Value

Consuming a public REST API, query parameters, pagination and mapping
JSON to typed models.

### Dependencies

- **Requires:** Epic 2 REST client
- **Blocks:** 4.2, 4.3, 4.4

### Tasks

- [ ] Wrap the Epic 2 REST client with an OpenF1 base URL
- [ ] Implement `get_sessions`, `get_drivers`, `get_laps`
- [ ] Support query filters (e.g. by session key, driver number)
- [ ] Add structured logging of requests
- [ ] Unit tests with mocked responses (≥ 15)
- [ ] Document usage

### SMART Acceptance Criteria

- [ ] **Specific:** Client fetches sessions, drivers and laps with
      filter support.
- [ ] **Measurable:** ≥ 15 unit tests pass; a manual run returns real
      data for a known session.
- [ ] **Achievable:** Read-only public API, no auth required.
- [ ] **Relevant:** Feeds validation and persistence.
- [ ] **Time-bound:** Complete within Month 2.

### Definition of Ready

- [ ] Epic 2 REST client merged

### Definition of Done

- [ ] Client merged with green CI and passing tests
- [ ] README usage section added

### Deliverables

- `src/openf1/` client
- `tests/openf1/`

### Learning Resources

- **OpenF1 API documentation:** use as the endpoint and query-parameter
  reference for sessions, drivers and laps.
- **Python requests / httpx docs:** use for query params and response
  handling (whichever your Epic 2 client wraps).

------------------------------------------------------------------------

## Issue 4.2 — Story: Add resilience and rate limiting

**Type:** Story
**Feature:** Resilience & Rate Limiting
**Story Points:** 3
**Priority:** Medium
**Milestone:** Month 2 — Dataverse and Dynamics Foundation
**Labels:** `story`, `openf1`, `python`, `api`
**Suggested branch:** `feat/openf1-resilience`
**Suggested PR title:** `feat(openf1): retries, backoff and pagination for ingestion`

### User Story

As a learner, I want the OpenF1 ingestion to handle retries, backoff and
pagination so that large imports complete reliably.

### Goal

Add resilient request handling and full pagination to the ingestion
client.

### Dependencies

- **Requires:** 4.1 Ingestion client

### Tasks

- [ ] Add exponential backoff with jitter on transient failures
- [ ] Handle HTTP 429 / rate limiting explicitly
- [ ] Implement pagination to retrieve full result sets
- [ ] Add tests simulating 429s and multi-page responses
- [ ] Document behaviour and limits

### SMART Acceptance Criteria

- [ ] **Specific:** The client retries transient errors and paginates
      through all pages.
- [ ] **Measurable:** Tests prove a simulated 429 is retried and a
      multi-page response is fully collected.
- [ ] **Achievable:** Builds on the Epic 2 resilience primitives.
- [ ] **Relevant:** Required for reliable scheduled ingestion.
- [ ] **Time-bound:** Complete within Month 2.

### Definition of Done

- [ ] Resilience + pagination merged with passing tests
- [ ] Green CI

### Deliverables

- Updated `src/openf1/` client + tests

### Learning Resources

- **OpenF1 API documentation:** confirm rate-limit and pagination
  behaviour.
- **tenacity documentation:** use for retry/backoff decorators if
  adopted.

------------------------------------------------------------------------

## Issue 4.3 — Story: Validate OpenF1 responses with Pydantic

**Type:** Story
**Feature:** Data Validation
**Story Points:** 3
**Priority:** Medium
**Milestone:** Month 2 — Dataverse and Dynamics Foundation
**Labels:** `story`, `openf1`, `python`
**Suggested branch:** `feat/openf1-validation`
**Suggested PR title:** `feat(openf1): Pydantic models validating API responses before persistence`

### User Story

As a learner, I want OpenF1 responses validated against typed models so
that malformed or unexpected data is caught before it reaches Dataverse.

### Goal

Pydantic models for session, driver and lap payloads with validation on
ingest.

### Dependencies

- **Requires:** 4.1 Ingestion client
- **Blocks:** 4.4 Persistence

### Tasks

- [ ] Define Pydantic models for session, driver, lap
- [ ] Parse and validate responses in the client
- [ ] Handle and log validation failures without crashing a run
- [ ] Unit tests for valid and invalid payloads
- [ ] Document the validation contract

### SMART Acceptance Criteria

- [ ] **Specific:** All three payload types are validated via Pydantic
      before use.
- [ ] **Measurable:** Tests cover valid parsing and at least three
      invalid-payload cases; invalid records are logged and skipped.
- [ ] **Achievable:** Pydantic v2 models only.
- [ ] **Relevant:** Protects the Dataverse layer.
- [ ] **Time-bound:** Complete within Month 2.

### Definition of Done

- [ ] Models + validation merged with passing tests
- [ ] Green CI

### Deliverables

- `src/openf1/models.py`
- Tests

### Learning Resources

- **Pydantic documentation:** use for model definition and validation.

------------------------------------------------------------------------

## Issue 4.4 — Story: Persist OpenF1 data to Dataverse

**Type:** Story
**Feature:** Dataverse Persistence
**Story Points:** 5
**Priority:** High
**Milestone:** Month 2 — Dataverse and Dynamics Foundation
**Labels:** `story`, `openf1`, `dataverse`, `python`
**Suggested branch:** `feat/openf1-persistence`
**Suggested PR title:** `feat(openf1): map and upsert OpenF1 data into Dataverse`

### User Story

As a learner, I want validated OpenF1 data mapped and upserted into
Dataverse so that public F1 data is queryable alongside the CRM model.

### Goal

Map validated models to Dataverse tables and upsert them via the Tier-1
Dataverse client, idempotently.

### Business Value

First end-to-end pipeline: public API → validation → Dataverse.

### Dependencies

- **Requires:** 4.3 Validation, Tier-1 Dataverse API client, dedicated
  OpenF1 tables (extend Epic 3 solution or a separate solution)
- **Blocks:** 4.5 Scheduled ingestion

### Tasks

- [ ] Confirm/create Dataverse tables for sessions, drivers, laps
- [ ] Map Pydantic models to Dataverse entities
- [ ] Upsert by alternate key (idempotent)
- [ ] Batch writes for laps
- [ ] Integration test creating then re-running without duplicates
- [ ] Document the mapping

### SMART Acceptance Criteria

- [ ] **Specific:** Validated sessions, drivers and laps are upserted to
      Dataverse.
- [ ] **Measurable:** A full run for one session populates the tables;
      re-running produces no duplicates (verified by count).
- [ ] **Achievable:** Uses the existing Dataverse client's upsert/batch.
- [ ] **Relevant:** Enables scheduled ingestion and later analytics.
- [ ] **Time-bound:** Complete within Month 2.

### Definition of Ready

- [ ] OpenF1 tables exist with alternate keys
- [ ] Tier-1 Dataverse client merged

### Definition of Done

- [ ] End-to-end run persists data idempotently
- [ ] Integration test passes; green CI
- [ ] Mapping documented

### Deliverables

- `src/openf1/persistence.py`
- OpenF1 tables in a Dataverse solution
- `docs/architecture/openf1-mapping.md`

### Learning Resources

- **Microsoft Learn — Dataverse Web API upsert and $batch:** use for
  idempotent bulk writes.

------------------------------------------------------------------------

## Issue 4.5 — Story: Schedule ingestion via a timer-triggered Function

**Type:** Story
**Feature:** Scheduled Ingestion (Azure Functions)
**Story Points:** 3
**Priority:** Medium
**Milestone:** Month 2 — Dataverse and Dynamics Foundation
**Labels:** `story`, `openf1`, `azure`, `python`
**Suggested branch:** `feat/openf1-scheduled-ingestion`
**Suggested PR title:** `feat(openf1): timer-triggered Function running the ingestion pipeline`

### User Story

As a learner, I want ingestion to run on a schedule in Azure Functions
so that the pipeline operates unattended and demonstrates serverless
orchestration.

### Goal

A timer-triggered function that runs the OpenF1 → Dataverse pipeline
idempotently.

### Dependencies

- **Requires:** 4.4 Persistence, Tier-1 Serverless platform foundation
- **Blocks:** none

### Tasks

- [ ] Add a timer-triggered function to the Functions app
- [ ] Invoke the ingestion + persistence pipeline
- [ ] Ensure idempotent re-runs
- [ ] Read config/secrets from app settings (not source)
- [ ] Local run + deploy smoke test
- [ ] Document schedule and configuration

### SMART Acceptance Criteria

- [ ] **Specific:** A timer trigger runs the full pipeline on a defined
      schedule.
- [ ] **Measurable:** A manual local invocation and one deployed run both
      populate Dataverse without duplicates.
- [ ] **Achievable:** Reuses 4.4 pipeline and the Tier-1 Functions app.
- [ ] **Relevant:** Demonstrates serverless orchestration.
- [ ] **Time-bound:** Complete within Month 2.

### Definition of Done

- [ ] Function runs locally and when deployed
- [ ] No secrets in source
- [ ] Green CI; schedule documented

### Deliverables

- Timer function in `src/azure_functions`
- Config documentation

### Learning Resources

- **Microsoft Learn — Timer trigger for Azure Functions:** use for the
  CRON schedule and binding.

------------------------------------------------------------------------

## Issue 4.6 — Story: Add ingestion observability

**Type:** Story
**Feature:** Ingestion Observability
**Story Points:** 2
**Priority:** Medium
**Milestone:** Month 2 — Dataverse and Dynamics Foundation
**Labels:** `story`, `openf1`, `azure`, `observability`, `governance`
**Suggested branch:** `feat/openf1-observability`
**Suggested PR title:** `feat(openf1): structured logging, run metrics and failure alerts`

### User Story

As a learner, I want ingestion runs logged with metrics and alerting so
that failures are visible and the pipeline is operable.

### Goal

Structured logging and basic metrics (records processed, failures,
duration) emitted to Application Insights, with an alert on failures.

### Dependencies

- **Requires:** 4.5 Scheduled ingestion

### Tasks

- [ ] Emit structured logs (run id, counts, duration)
- [ ] Emit custom metrics to Application Insights
- [ ] Log validation and persistence failures with context
- [ ] Configure a basic alert rule on failed runs
- [ ] Document the observability approach

### SMART Acceptance Criteria

- [ ] **Specific:** Each run logs counts, duration and outcome, and
      emits metrics.
- [ ] **Measurable:** A forced failure produces a log entry and triggers
      the alert rule.
- [ ] **Achievable:** Uses App Insights bindings from the Tier-1
      Functions app.
- [ ] **Relevant:** Operability + early governance signal.
- [ ] **Time-bound:** Complete within Month 2.

### Definition of Done

- [ ] Logs and metrics visible in App Insights
- [ ] Alert rule verified
- [ ] `docs/architecture/observability.md` written

### Deliverables

- Logging/metrics in the ingestion function
- Alert rule
- `docs/architecture/observability.md`

### Learning Resources

- **Microsoft Learn — Monitor Azure Functions with Application
  Insights:** use for logging, custom metrics and alerts.



========================================================================


# Dynamics AI Intelligence Hub — GitHub Issue Drafts (Tier 3: Coverage Gaps)

> Copy-paste-ready issue bodies for the gap-closing stories identified in
> the v0.3 coverage review. Grouped as: Epic 2 shared foundations, the
> Epic 9 / Epic 10 assembly stories, and the reworked Epic 11
> policy-layer stories. Paste each body into a new GitHub Issue.

------------------------------------------------------------------------
# EPIC 2 — SHARED FOUNDATIONS
------------------------------------------------------------------------

## Issue 2.A — Story: Build the shared utilities package

**Type:** Story
**Feature:** Packaging & Shared Utilities
**Story Points:** 3
**Priority:** High (imported by every later epic)
**Milestone:** Month 1 — Python and API Foundations
**Labels:** `story`, `python`, `foundation`
**Suggested branch:** `feat/shared-utilities`
**Suggested PR title:** `feat(shared): config loader, logging setup and exception hierarchy`

### User Story

As a learner, I want an importable internal `shared` package so that
config loading, structured logging and common exceptions are defined
once and reused everywhere.

### Goal

`src/shared` providing a config loader, structured-logging setup and a
common exception hierarchy, importable as `shared` across the codebase.

### Business Value

Eliminates copy-pasted config/logging code across ingestion, Dataverse,
AI and agent modules; a single place to change cross-cutting behaviour.

### Learning Value

Python packaging, environment-driven configuration, and structured
logging patterns.

### Dependencies

- **Requires:** Epic 1 environment
- **Blocks (soft):** cleaner implementation of REST client, Dataverse
  client, ingestion, AI modules

### Tasks

- [ ] Implement a config loader (environment variables + typed defaults)
- [ ] Implement structured logging setup (JSON-friendly, correlation id)
- [ ] Define a common exception hierarchy
- [ ] Configure packaging so modules `import shared` cleanly
- [ ] Unit tests for config precedence and logging setup
- [ ] Document usage in README

### SMART Acceptance Criteria

- [ ] **Specific:** `shared` exposes config, logging and exceptions.
- [ ] **Measurable:** ≥ 90% coverage of the package; another module
      imports and uses it in a test.
- [ ] **Achievable:** Standard library + minimal deps.
- [ ] **Relevant:** Consumed by every subsequent epic.
- [ ] **Time-bound:** Complete within Week 2 of Month 1.

### Definition of Ready

- [ ] Repo skeleton and tooling in place

### Definition of Done

- [ ] Package merged with green CI and ≥ 90% coverage
- [ ] README usage section added

### Deliverables

- `src/shared/` (config, logging, exceptions)
- `tests/shared/`

### Learning Resources

- **Python Packaging User Guide — packaging projects:** use for making
  `shared` importable.
- **Python `logging` HOWTO:** use for the structured-logging setup.

------------------------------------------------------------------------

## Issue 2.B — Story: Build reusable resilience utilities

**Type:** Story
**Feature:** Error Handling & Resilience
**Story Points:** 3
**Priority:** High
**Milestone:** Month 1 — Python and API Foundations
**Labels:** `story`, `python`, `api`, `foundation`
**Suggested branch:** `feat/resilience-utilities`
**Suggested PR title:** `feat(shared): reusable timeout, backoff and retry utilities`

### User Story

As a learner, I want reusable timeout and retry-with-backoff utilities in
one place so that the REST client and OpenF1 ingestion share the same
resilience behaviour instead of reimplementing it.

### Goal

A tested resilience module in `src/shared` providing a timeout wrapper
and a configurable exponential-backoff-with-jitter retry decorator.

### Business Value

Single source of truth for retry behaviour; removes the triple
duplication flagged between Epic 2 REST client, this feature, and OpenF1
4.2.

### Learning Value

Retry semantics, jitter, transient-vs-permanent error classification.

### Dependencies

- **Requires:** 2.A shared package (for logging/exceptions)
- **Consumed by:** Epic 2 REST client story, OpenF1 4.2

### Tasks

- [ ] Implement a timeout wrapper
- [ ] Implement a retry decorator (exponential backoff + jitter, max
      attempts)
- [ ] Support configurable retry predicates (which errors are transient)
- [ ] Emit structured logs on retry/give-up via `shared` logging
- [ ] Unit tests: retry-on-transient, give-up-after-N, no-retry-on-
      permanent
- [ ] Document the contract and reference it from 4.2

### SMART Acceptance Criteria

- [ ] **Specific:** A retry decorator and timeout wrapper live in
      `src/shared/resilience.py`.
- [ ] **Measurable:** Tests prove a simulated transient error is retried
      and a permanent error is not; retries stop after the configured
      maximum.
- [ ] **Achievable:** Either hand-rolled or via `tenacity` (record the
      choice).
- [ ] **Relevant:** Directly consumed by the REST client and OpenF1
      ingestion.
- [ ] **Time-bound:** Complete within Week 2 of Month 1.

### Definition of Ready

- [ ] 2.A shared package merged

### Definition of Done

- [ ] Module merged with passing tests; green CI
- [ ] REST client story updated to consume it (or a follow-up task
      created)
- [ ] Documented and referenced from OpenF1 4.2

### Deliverables

- `src/shared/resilience.py`
- `tests/shared/test_resilience.py`

### Learning Resources

- **tenacity documentation:** use if adopting a library for
  retry/backoff.

------------------------------------------------------------------------
# EPIC 9 / EPIC 10 — ASSEMBLY (GLUE) STORIES
------------------------------------------------------------------------

## Issue 9.Z — Story: Assemble the end-to-end RAG assistant

**Type:** Story
**Feature:** End-to-End RAG Assistant (assembly)
**Story Points:** 8
**Priority:** High (portfolio deliverable for Epic 9)
**Milestone:** Month 5 — Generative AI, RAG and Agents
**Labels:** `story`, `rag`, `azure`, `python`, `portfolio`, `security`
**Suggested branch:** `feat/rag-assistant-e2e`
**Suggested PR title:** `feat(rag): end-to-end permission-aware RAG assistant with citations`

### User Story

As a learner, I want the RAG pipeline assembled into a single callable
assistant so that the portfolio shows a working, grounded,
permission-aware question-answering capability — not just isolated
parts.

### Goal

One entrypoint that runs retrieval (hybrid + permission-aware) →
generation → cited answer, respecting the caller's Dataverse role.

### Business Value

This is the demonstrable RAG capability; the individual pipeline features
have no portfolio value until assembled.

### Learning Value

Composing a retrieval-augmented generation flow end to end and enforcing
access boundaries at query time.

### Dependencies

- **Requires:** Epic 9 ingestion, embeddings, Azure AI Search, hybrid
  search, permission-aware retrieval, citations; Epic 3 security roles;
  Azure OpenAI integration (Epic 8)
- **Blocks:** Epic 8 "Ground the assistant with RAG"; Epic 12 RAG
  integration story

### Tasks

- [ ] Compose hybrid + permission-aware retrieval into one query path
- [ ] Pass retrieved context into the generation call
- [ ] Return the answer with citations to sources
- [ ] Enforce the caller's Dataverse role in retrieval filtering
- [ ] Add an end-to-end test where two users with different roles get
      different (correctly filtered) results
- [ ] Log prompt/response (ties to Epic 8 logging)
- [ ] Document the assistant API and limitations

### SMART Acceptance Criteria

- [ ] **Specific:** A single entrypoint answers a question with
      citations, filtered by the caller's role.
- [ ] **Measurable:** For a seeded question, the answer cites ≥ 1 correct
      source; a restricted user provably cannot retrieve a document an
      authorised user can.
- [ ] **Achievable:** Reuses existing Epic 9 components; no new
      retrieval tech.
- [ ] **Relevant:** The headline RAG deliverable.
- [ ] **Time-bound:** Complete within Month 5.

### Definition of Ready

- [ ] All referenced Epic 9 features merged
- [ ] Security roles (Epic 3) configured

### Definition of Done

- [ ] End-to-end test passes (including the two-user access test)
- [ ] Citations verified correct on sample questions
- [ ] Prompt/response logged
- [ ] Documented; green CI

### Deliverables

- `src/rag/assistant.py` (or equivalent entrypoint)
- End-to-end test
- `docs/architecture/rag-assistant.md`

### Learning Resources

- **Microsoft Learn — Retrieval Augmented Generation with Azure AI
  Search:** use for the end-to-end RAG pattern.
- **Microsoft Learn — Azure AI Search security filters / document-level
  access:** use for permission-aware filtering.

------------------------------------------------------------------------

## Issue 10.Z — Story: Orchestrate the multi-agent workflow

**Type:** Story
**Feature:** End-to-End Multi-Agent Workflow (assembly)
**Story Points:** 8
**Priority:** High (portfolio deliverable for Epic 10)
**Milestone:** Month 5 — Generative AI, RAG and Agents
**Labels:** `story`, `agent`, `azure`, `python`, `portfolio`, `governance`
**Suggested branch:** `feat/agent-workflow-e2e`
**Suggested PR title:** `feat(agents): orchestrated planner→researcher→reviewer→reporter workflow`

### User Story

As a learner, I want the four agents assembled into one orchestrated
workflow so that the portfolio shows a working agentic capability with
tooling, approval and telemetry.

### Goal

A workflow that takes a goal and runs planner → researcher → reviewer →
reporter, using the tool registry (reusing Epic 8 tools and Epic 9 RAG),
with an approval gate on writes and full telemetry.

### Business Value

The demonstrable agentic capability; the individual agents have no
portfolio value until orchestrated together.

### Learning Value

Multi-agent orchestration, tool reuse across a single-model tool layer,
human-in-the-loop approval and agent tracing.

### Dependencies

- **Requires:** Epic 10 orchestration framework (ADR), four agents, tool
  registry, approval workflow, telemetry; Epic 8 tool layer (ADR-0006
  boundary); Epic 9 RAG assistant (9.Z)
- **Blocks:** Epic 12 agent integration story

### Tasks

- [ ] Compose the four agents into one orchestrated run
- [ ] Route tool use through the registry, reusing Epic 8 tools
- [ ] Have the researcher use the Epic 9 RAG assistant
- [ ] Insert a human approval gate before any write action
- [ ] Emit agent telemetry/traces for the whole run
- [ ] End-to-end test producing a report from a sample goal
- [ ] Document the workflow and its guardrails

### SMART Acceptance Criteria

- [ ] **Specific:** A single workflow runs all four agents to produce a
      report from a goal.
- [ ] **Measurable:** A sample goal yields a report; a write action is
      blocked pending approval; telemetry captures each agent step.
- [ ] **Achievable:** Reuses the Epic 8 tool layer and Epic 9 RAG; no new
      model plumbing.
- [ ] **Relevant:** The headline agent deliverable.
- [ ] **Time-bound:** Complete within Month 5.

### Definition of Ready

- [ ] Orchestration framework ADR accepted
- [ ] Four agents and tool registry merged
- [ ] RAG assistant (9.Z) available

### Definition of Done

- [ ] End-to-end test passes and produces a report
- [ ] Approval gate verified on a write action
- [ ] Telemetry visible for the run
- [ ] Documented; green CI

### Deliverables

- `src/agents/workflow.py` (or equivalent entrypoint)
- End-to-end test
- `docs/architecture/agent-workflow.md`

### Learning Resources

- **Microsoft Learn — Semantic Kernel agents / orchestration** (or the
  framework chosen in the Epic 10 ADR): use for the orchestration
  pattern.

------------------------------------------------------------------------
# EPIC 11 — POLICY-LAYER STORIES (reworked)
------------------------------------------------------------------------

> These replace the earlier duplicate "implement logging/observability/
> secrets" stories. They govern and consolidate capabilities built in
> earlier epics rather than rebuilding them.

## Issue 11.A — Story: Define and audit the audit-logging policy

**Type:** Story
**Feature:** Audit Logging (governance)
**Story Points:** 3
**Priority:** Medium
**Milestone:** Month 6 — Governance, Deployment and Portfolio
**Labels:** `story`, `governance`, `security`, `documentation`
**Suggested branch:** `feat/audit-logging-policy`
**Suggested PR title:** `docs(governance): audit-logging policy and completeness audit`

### Goal

Define what must be logged and for how long, then audit the existing
logging (Dataverse 3.6, ingestion 4.6, prompt/response Epic 8) for gaps.

### Description

This is governance, not a new logging build. Produce a policy document,
then check each implemented logging surface against it and raise
follow-up tasks for any gaps.

### Tasks

- [ ] Write the audit-logging policy (scope, fields, retention)
- [ ] Audit Dataverse auditing (3.6) against the policy
- [ ] Audit ingestion logging (4.6) against the policy
- [ ] Audit prompt/response logging (Epic 8) against the policy
- [ ] Raise follow-up tasks for any gaps

### SMART Acceptance Criteria

- [ ] **Specific:** A policy exists and each of the three logging
      surfaces is assessed against it.
- [ ] **Measurable:** A gap report lists each surface as compliant or
      with a linked remediation task.
- [ ] **Achievable:** Review + documentation, minimal new code.
- [ ] **Relevant:** Governance credibility for the portfolio.
- [ ] **Time-bound:** Complete within Month 6.

### Definition of Done

- [ ] Policy merged; gap report produced; remediation tasks linked

### Deliverables

- `docs/security/audit-logging-policy.md`
- Gap report / linked issues

### Learning Resources

- **Microsoft Learn — Dataverse auditing:** confirm what auditing
  captures when assessing coverage.

------------------------------------------------------------------------

## Issue 11.B — Story: Responsible AI assessment mapped to NIST AI RMF

**Type:** Story
**Feature:** Responsible AI
**Story Points:** 5
**Priority:** Medium
**Milestone:** Month 6 — Governance, Deployment and Portfolio
**Labels:** `story`, `governance`, `documentation`, `architecture`
**Suggested branch:** `feat/responsible-ai-assessment`
**Suggested PR title:** `docs(governance): Responsible AI assessment mapped to NIST AI RMF`

### Goal

Assess the solution against the NIST AI Risk Management Framework and
document findings and mitigations.

### Tasks

- [ ] Map the solution to the NIST AI RMF functions (Govern, Map,
      Measure, Manage)
- [ ] Identify risks (hallucination, injection, data exposure, bias)
- [ ] Record existing mitigations (permission-aware retrieval, approval
      gates, logging) and gaps
- [ ] Produce a Responsible AI note for the portfolio

### SMART Acceptance Criteria

- [ ] **Specific:** Each NIST AI RMF function is addressed with concrete
      references to solution features.
- [ ] **Measurable:** ≥ 5 risks documented, each with a mitigation or a
      logged gap.
- [ ] **Achievable:** Assessment/documentation task.
- [ ] **Relevant:** Strong architect-level portfolio signal.
- [ ] **Time-bound:** Complete within Month 6.

### Definition of Done

- [ ] Assessment merged and referenced from the README/portfolio

### Deliverables

- `docs/security/responsible-ai.md`

### Learning Resources

- **NIST AI Risk Management Framework (AI RMF 1.0):** use as the
  assessment structure.
- **Microsoft — Responsible AI Standard / resources:** use for practical
  mitigations relevant to Azure AI.

------------------------------------------------------------------------

## Issue 11.C — Story: Move production secrets to Key Vault + Managed Identity

**Type:** Story
**Feature:** Identity & Secrets Management (authoritative)
**Story Points:** 5
**Priority:** High
**Milestone:** Month 6 — Governance, Deployment and Portfolio
**Labels:** `story`, `security`, `azure`, `governance`
**Suggested branch:** `feat/managed-identity-key-vault`
**Suggested PR title:** `feat(security): Key Vault secrets and Managed Identity for Azure services`

### Goal

Make this the authoritative production secret/identity implementation:
Key Vault for secrets, Managed Identity for service-to-service auth,
removing inline secrets. Epic 1 covered local `.env` only.

### Dependencies

- **Requires:** Azure services deployed (Functions, AI Search, Azure
  OpenAI); Tier-1 Dataverse auth (candidate to migrate from client
  secret to Managed Identity)

### Tasks

- [ ] Provision Key Vault (via the chosen IaC tool)
- [ ] Enable Managed Identity on Functions/app services
- [ ] Grant least-privilege access to Key Vault and resources
- [ ] Migrate application config off inline secrets to Key Vault
      references
- [ ] Where possible, replace client secrets with Managed Identity
- [ ] Update ADR-0003 (Dataverse auth) if the auth approach changes
- [ ] Verify services run with no secrets in config or source

### SMART Acceptance Criteria

- [ ] **Specific:** Production secrets are in Key Vault; services use
      Managed Identity where supported.
- [ ] **Measurable:** No secret values appear in app settings, source or
      history; services start and function using Key Vault references /
      Managed Identity.
- [ ] **Achievable:** Standard Azure identity patterns.
- [ ] **Relevant:** Core enterprise security requirement.
- [ ] **Time-bound:** Complete within Month 6.

### Definition of Done

- [ ] Secrets in Key Vault; Managed Identity in use where supported
- [ ] No secrets in config/source (verified)
- [ ] ADR updated if auth changed; green CI

### Deliverables

- IaC for Key Vault + identity assignments
- Updated app configuration
- ADR update if applicable

### Learning Resources

- **Microsoft Learn — Managed identities for Azure resources:** use for
  service-to-service auth.
- **Microsoft Learn — Use Key Vault references in app settings:** use for
  wiring secrets without exposing values.

------------------------------------------------------------------------

## Issue 11.D — Story: Consolidate observability into one standard and dashboard

**Type:** Story
**Feature:** Observability & Telemetry (consolidation)
**Story Points:** 3
**Priority:** Medium
**Milestone:** Month 6 — Governance, Deployment and Portfolio
**Labels:** `story`, `observability`, `azure`, `governance`
**Suggested branch:** `feat/observability-consolidation`
**Suggested PR title:** `feat(observability): unified telemetry standard and dashboard`

### Goal

Define one observability standard and consolidate the ingestion (4.6) and
agent (Epic 10) telemetry into a single dashboard with baseline alerting.

### Tasks

- [ ] Define the observability standard (log fields, metrics, traces)
- [ ] Ensure ingestion and agent telemetry conform to it
- [ ] Build a single Application Insights dashboard
- [ ] Configure baseline alert rules (failures, latency, cost signals)
- [ ] Document the standard and dashboard

### SMART Acceptance Criteria

- [ ] **Specific:** One dashboard covers ingestion and agent runs against
      a documented standard.
- [ ] **Measurable:** The dashboard shows both sources; a forced failure
      raises an alert.
- [ ] **Achievable:** Consolidates existing telemetry; minimal new
      instrumentation.
- [ ] **Relevant:** Operability + governance signal.
- [ ] **Time-bound:** Complete within Month 6.

### Definition of Done

- [ ] Dashboard live; alerts verified; standard documented

### Deliverables

- Application Insights dashboard
- `docs/architecture/observability-standard.md`

### Learning Resources

- **Microsoft Learn — Application Insights dashboards and alerts:** use
  for the consolidated dashboard and alert rules.



========================================================================


# GitHub Issue Drafts (Tier 4: Epic 1 & 2 completion)

> Full-spec, copy-paste-ready issues completing Epic 1 (Foundation) and
> Epic 2 (Python Engineering). CI/CD and the IaC spike live in Tier 1;
> the shared-utilities and resilience stories live in Tier 3.

------------------------------------------------------------------------
# EPIC 1 — FOUNDATION
------------------------------------------------------------------------

## Issue 1.1 — Story: Configure the workstation and project skeleton

**Type:** Story
**Feature:** Development Environment
**Story Points:** 3
**Priority:** High
**Milestone:** Month 1 — Python and API Foundations
**Labels:** `story`, `python`, `foundation`
**Suggested branch:** `feat/dev-environment`
**Suggested PR title:** `chore(setup): reproducible Python dev environment and project skeleton`

### User Story

As a learner, I want a fully reproducible Python development environment
and repo skeleton so that every later story starts from a clean,
tool-enforced baseline.

### Goal

A working local environment (Python 3.12+, venv, Ruff, Black, PyTest,
MyPy, Git, VS Code) and the repository skeleton from the agreed
structure, with a clean build verified.

### Business Value

Removes environment friction and inconsistency from day one; a
reproducible setup is the precondition for CI and every feature.

### Learning Value

Modern Python tooling, virtual environments, and editor/linter
integration.

### Dependencies

- **Requires:** nothing
- **Blocks:** effectively everything

### Description

Install and configure the toolchain, create the GitHub repository, lay
down the folder structure (`src/`, `tests/`, `docs/`, etc.), add
`pyproject.toml` with tool config, and prove the environment runs tests,
lint and format cleanly.

### Tasks

- [ ] Install Python 3.12+ and create a virtual environment
- [ ] Install Ruff, Black, PyTest, MyPy
- [ ] Configure VS Code (interpreter, format-on-save, test discovery)
- [ ] Configure Git and create the GitHub repository
- [ ] Create the project skeleton per the agreed structure
- [ ] Add `pyproject.toml` with tool configuration
- [ ] Add a trivial module + test to prove the pipeline
- [ ] Document setup in README

### SMART Acceptance Criteria

- [ ] **Specific:** The repo contains the agreed folder structure and a
      configured toolchain.
- [ ] **Measurable:** `pytest`, `ruff`, `black --check` and `mypy` all
      run clean locally on a fresh clone.
- [ ] **Achievable:** Standard tooling, no bespoke setup.
- [ ] **Relevant:** Baseline for all later work.
- [ ] **Time-bound:** Complete within Week 1 of Month 1.

### Definition of Ready

- [ ] GitHub account and local Git available

### Definition of Done

- [ ] Fresh clone builds and all four tools pass
- [ ] README setup section written

### Deliverables

- Configured repository skeleton
- `pyproject.toml`
- README setup section

### Learning Resources

- **Python Packaging User Guide — creating a project:** use for the
  `pyproject.toml` layout.
- **Ruff, Black, MyPy, pytest docs:** use when configuring each tool.

------------------------------------------------------------------------

## Issue 1.2 — Story: Repository governance and templates

**Type:** Story
**Feature:** Repository Governance & Templates
**Story Points:** 3
**Priority:** High
**Milestone:** Month 1 — Python and API Foundations
**Labels:** `story`, `documentation`, `foundation`
**Suggested branch:** `feat/repo-governance`
**Suggested PR title:** `chore(github): labels, milestones, project board, issue/PR templates`

### User Story

As a learner, I want the GitHub project scaffolding (labels, milestones,
board, templates, CODEOWNERS, conventions) so that every issue and PR is
classified and consistent from the start.

### Goal

A configured GitHub Project with the full label set, six milestones,
custom fields, issue/PR templates, CODEOWNERS and documented conventions.

### Business Value

Makes the backlog navigable and the portfolio read as professionally
managed; enables filtering and reporting across 12 epics.

### Learning Value

GitHub Projects, issue forms, and repository governance conventions.

### Dependencies

- **Requires:** 1.1 repository exists
- **Blocks:** clean creation of all subsequent issues

### Tasks

- [ ] Create the label set (epic, feature, story, spike, task, python,
      azure, dataverse, dynamics, openf1, fastf1, ml, rag, agent,
      security, governance, documentation, architecture, portfolio,
      observability, blocked, good-first-task)
- [ ] Create the six monthly milestones
- [ ] Configure the GitHub Project board and custom fields (Type, Story
      Points, Priority, Milestone)
- [ ] Add issue templates (epic, feature, story, spike, task, bug)
- [ ] Add the pull request template
- [ ] Add CODEOWNERS
- [ ] Document branch naming and commit message conventions

### SMART Acceptance Criteria

- [ ] **Specific:** All labels, milestones, fields and templates exist.
- [ ] **Measurable:** A test issue can be created from a template and
      assigned Type/Points/Priority/Milestone on the board.
- [ ] **Achievable:** GitHub configuration only.
- [ ] **Relevant:** Underpins the whole backlog.
- [ ] **Time-bound:** Complete within Week 1 of Month 1.

### Definition of Ready

- [ ] Repository created (1.1)

### Definition of Done

- [ ] Labels, milestones, board, templates, CODEOWNERS committed
- [ ] Conventions documented in CONTRIBUTING

### Deliverables

- `.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md`
- `CODEOWNERS`
- Configured Project board and labels/milestones
- Conventions in `CONTRIBUTING.md`

### Learning Resources

- **GitHub Docs — Planning and tracking with Projects:** use for board
  and custom fields.
- **GitHub Docs — Configuring issue templates:** use for the template
  forms.

------------------------------------------------------------------------

## Issue 1.3 — Story: Documentation scaffolding and ADR log

**Type:** Story
**Feature:** Documentation Scaffolding
**Story Points:** 2
**Priority:** Medium
**Milestone:** Month 1 — Python and API Foundations
**Labels:** `story`, `documentation`, `architecture`, `foundation`
**Suggested branch:** `feat/docs-scaffolding`
**Suggested PR title:** `docs: README, CONTRIBUTING, CHANGELOG, LICENSE, docs tree and ADR-0001`

### User Story

As a learner, I want the documentation tree and ADR log in place so that
decisions and guides have a home from the first commit.

### Goal

Authored README/CONTRIBUTING/CHANGELOG/LICENSE, the `docs/` tree, an ADR
log with ADR-0001 (repository conventions), and optional GitHub Pages.

### Dependencies

- **Requires:** 1.1 repository
- **Blocks:** every later doc/ADR deliverable

### Tasks

- [ ] Author README, CONTRIBUTING, CHANGELOG, LICENSE
- [ ] Create the `docs/` tree (architecture, backlog, decisions,
      diagrams, learning, security, retrospectives)
- [ ] Establish the ADR log and record ADR-0001 (repository conventions)
- [ ] (Optional) Configure GitHub Pages

### SMART Acceptance Criteria

- [ ] **Specific:** Core docs and the `docs/` tree exist with ADR-0001.
- [ ] **Measurable:** ADR-0001 follows the project ADR format; README
      renders with project overview and setup.
- [ ] **Achievable:** Markdown only.
- [ ] **Relevant:** Portfolio credibility and decision traceability.
- [ ] **Time-bound:** Complete within Week 1 of Month 1.

### Definition of Done

- [ ] Docs merged; ADR-0001 recorded; tree in place

### Deliverables

- `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `LICENSE`
- `docs/` tree
- `docs/decisions/ADR-0001-repository-conventions.md`

### Learning Resources

- **GitHub Docs — About READMEs:** use for structure.
- **adr.github.io (ADR patterns):** use as the ADR-log reference.

------------------------------------------------------------------------

## Issue 1.4 — Story: Local secrets and config management

**Type:** Story
**Feature:** Secrets & Config Management (local development)
**Story Points:** 2
**Priority:** High
**Milestone:** Month 1 — Python and API Foundations
**Labels:** `story`, `security`, `python`, `foundation`
**Suggested branch:** `feat/local-secrets`
**Suggested PR title:** `chore(security): .env handling, CI secrets and pre-commit hooks`

### User Story

As a learner, I want local secret handling and pre-commit safeguards so
that credentials never reach source, before any API work begins.

### Goal

`.env`/`.env.example` handling, CI secrets configured, and pre-commit
hooks for secret scanning, lint and format. **Scope:** local dev only —
production secrets are Epic 11 (11.C).

### Dependencies

- **Requires:** 1.1, 1.2
- **Blocks:** any story that reads credentials locally

### Tasks

- [ ] Add `.env` handling (via the `shared` config loader) and
      `.env.example`
- [ ] Add `.env` to `.gitignore`
- [ ] Configure GitHub Actions secrets for CI
- [ ] Add pre-commit hooks: secret scanning, Ruff, Black
- [ ] Document the local secrets workflow

### SMART Acceptance Criteria

- [ ] **Specific:** `.env` is git-ignored; `.env.example` documents
      required keys; pre-commit blocks secrets and lint/format issues.
- [ ] **Measurable:** A committed test secret is caught by the hook; CI
      reads its secret from GitHub Actions secrets.
- [ ] **Achievable:** Standard pre-commit + dotenv patterns.
- [ ] **Relevant:** Security from day one.
- [ ] **Time-bound:** Complete within Week 2 of Month 1.

### Definition of Done

- [ ] Hooks active; `.env.example` committed; workflow documented
- [ ] No real secrets in source

### Deliverables

- `.env.example`, `.pre-commit-config.yaml`
- README secrets section

### Learning Resources

- **pre-commit documentation:** use for hook configuration.
- **GitHub Docs — Encrypted secrets for Actions:** use for CI secrets.

------------------------------------------------------------------------
# EPIC 2 — PYTHON ENGINEERING
------------------------------------------------------------------------

## Issue 2.1 — Story: Python fundamentals with a tested utilities module

**Type:** Story
**Feature:** Core Language
**Story Points:** 5
**Priority:** High
**Milestone:** Month 1 — Python and API Foundations
**Labels:** `story`, `python`, `foundation`
**Suggested branch:** `feat/python-basics`
**Suggested PR title:** `feat(python): fundamentals exercises and tested utility module`

### User Story

As a learner new to Python, I want structured fundamentals practice
producing a tested utility module so that I build real fluency, not just
notes.

### Goal

A `python_basics` package covering the core language surface, backed by
exercises with high coverage.

### Business Value

Establishes the Python fluency every later epic assumes.

### Learning Value

Variables, functions, classes, dataclasses, collections, file IO, JSON,
logging, exceptions, type hints, packaging, unit tests.

### Dependencies

- **Requires:** 1.1 environment
- **Blocks (soft):** all Python-heavy stories

### Tasks

- [ ] Work through progressively harder exercises (target ~30)
- [ ] Build a small utility module exercising each concept
- [ ] Add type hints throughout and pass MyPy
- [ ] Write unit tests
- [ ] Document what was learned in `docs/learning`

### SMART Acceptance Criteria

- [ ] **Specific:** A `python_basics` module covers the listed concepts.
- [ ] **Measurable:** ~30 exercises complete with ≥ 90% coverage on the
      utility module; MyPy passes.
- [ ] **Achievable:** Solo learner over two weeks.
- [ ] **Relevant:** Foundational fluency.
- [ ] **Time-bound:** Complete within two weeks of Month 1.

### Definition of Done

- [ ] Module + tests merged; green CI; ≥ 90% coverage
- [ ] Learning note written

### Deliverables

- `src/python_basics/`, `tests/python_basics/`
- `docs/learning/python-basics.md`

### Learning Resources

- **The Python Tutorial (official docs):** primary reference for the
  language surface.
- **Real Python — type checking / dataclasses guides:** use for hints
  and dataclasses.

------------------------------------------------------------------------

## Issue 2.2 — Story: Build the reusable REST client

**Type:** Story
**Feature:** REST API Client
**Story Points:** 5
**Priority:** High
**Milestone:** Month 1 — Python and API Foundations
**Labels:** `story`, `python`, `api`, `foundation`
**Suggested branch:** `feat/rest-client`
**Suggested PR title:** `feat(api): reusable REST client with retries, timeouts and logging`

### User Story

As a learner, I want a reusable REST client that consumes the shared
resilience utilities so that OpenF1 ingestion and any future API work
share one battle-tested HTTP layer.

### Goal

`src/api` — a configurable client with timeout handling, retry via the
`shared` resilience decorator, structured logging and a typed error
model.

### Business Value

The foundation for OpenF1 ingestion (Epic 4) and any REST integration;
avoids per-integration HTTP boilerplate.

### Learning Value

HTTP client design, dependency reuse, and testing with mocked responses.

### Dependencies

- **Requires:** 2.A shared package, 2.B resilience utilities
- **Blocks:** Epic 4 OpenF1 client

### Tasks

- [ ] Base client with configurable base URL and headers
- [ ] Timeout handling
- [ ] Retry via the `shared` resilience decorator (no reimplementation)
- [ ] Structured logging via `shared`
- [ ] Typed error/exception model
- [ ] Unit tests with mocked responses (≥ 20)
- [ ] Document usage

### SMART Acceptance Criteria

- [ ] **Specific:** A reusable client exposes GET/POST with timeout,
      retry and logging.
- [ ] **Measurable:** ≥ 20 unit tests pass; a simulated transient error
      is retried via the shared decorator (not a local copy).
- [ ] **Achievable:** Builds on 2.A/2.B.
- [ ] **Relevant:** Directly consumed by Epic 4.
- [ ] **Time-bound:** Complete within Week 2 of Month 1.

### Definition of Ready

- [ ] 2.A and 2.B merged

### Definition of Done

- [ ] Client merged with ≥ 20 tests; green CI
- [ ] Consumes shared resilience (verified in a test)
- [ ] README usage section

### Deliverables

- `src/api/`, `tests/api/`

### Learning Resources

- **httpx / requests documentation:** use for the transport layer.
- **pytest — monkeypatch / responses libraries:** use for mocking HTTP.

------------------------------------------------------------------------

## Issue 2.3 — Story: Establish testing patterns and coverage discipline

**Type:** Story
**Feature:** Testing & Quality
**Story Points:** 3
**Priority:** Medium
**Milestone:** Month 1 — Python and API Foundations
**Labels:** `story`, `python`, `foundation`
**Suggested branch:** `feat/testing-patterns`
**Suggested PR title:** `test: shared pytest fixtures, parametrisation and coverage discipline`

### User Story

As a learner, I want reusable pytest patterns and a coverage habit so
that every later module is tested consistently.

### Goal

Shared fixtures, parametrised-test examples, mocking patterns and a
documented coverage discipline that the CI gate (Tier-1 Issue 3)
enforces.

### Dependencies

- **Requires:** 1.1 environment; complements CI (Tier-1 Issue 3)

### Tasks

- [ ] Establish `conftest.py` with shared fixtures
- [ ] Add parametrised-test examples
- [ ] Document mocking patterns (monkeypatch / fakes)
- [ ] Configure coverage reporting and a local `make test` / task
- [ ] Write a short testing guide

### SMART Acceptance Criteria

- [ ] **Specific:** Shared fixtures and documented patterns exist.
- [ ] **Measurable:** At least one parametrised and one mocked test run
      green; coverage report generates locally and in CI.
- [ ] **Achievable:** pytest + pytest-cov only.
- [ ] **Relevant:** Consistency across all later tests.
- [ ] **Time-bound:** Complete within Week 2 of Month 1.

### Definition of Done

- [ ] Patterns merged; testing guide written; CI coverage report visible

### Deliverables

- `tests/conftest.py`
- `docs/learning/testing-guide.md`

### Learning Resources

- **pytest documentation — fixtures and parametrize:** use for the
  patterns.
- **pytest-cov documentation:** use for coverage reporting.



========================================================================


# GitHub Issue Drafts (Tier 5: Epic 5 FastF1 & Epic 6 Data Engineering)

> Full-spec, copy-paste-ready issues for FastF1 analytics and data
> engineering. All Month 3. Depends on Epic 3 seeded data (3.7) and
> Epic 4 ingestion for real inputs.

------------------------------------------------------------------------
# EPIC 5 — FASTF1 ANALYTICS
------------------------------------------------------------------------

## Issue 5.1 — Story: Configure FastF1 and its cache

**Type:** Story
**Feature:** Environment & Caching
**Story Points:** 2
**Priority:** Medium
**Milestone:** Month 3 — Data Engineering and Analytics
**Labels:** `story`, `fastf1`, `python`
**Suggested branch:** `feat/fastf1-setup`
**Suggested PR title:** `feat(fastf1): configure FastF1 and persistent cache`

### User Story

As a learner, I want FastF1 installed with a working cache so that
telemetry notebooks load quickly and reproducibly.

### Goal

FastF1 configured with a persistent local cache and a verified data load
for one session.

### Business Value

Fast, reproducible telemetry access underpins every Epic 5 notebook.

### Learning Value

FastF1 setup, caching, and session data loading.

### Dependencies

- **Requires:** 1.1 environment
- **Blocks:** 5.2, 5.3, 5.4

### Tasks

- [ ] Install FastF1
- [ ] Configure a persistent cache directory (git-ignored)
- [ ] Load one session and confirm data returns
- [ ] Document setup and cache location

### SMART Acceptance Criteria

- [ ] **Specific:** FastF1 is configured with a persistent cache.
- [ ] **Measurable:** A session loads from cache on the second run
      (measurably faster / offline).
- [ ] **Achievable:** Library configuration only.
- [ ] **Relevant:** Prerequisite for all telemetry work.
- [ ] **Time-bound:** Complete within Week 1 of Month 3.

### Definition of Done

- [ ] Cache configured and verified; setup documented

### Deliverables

- FastF1 config in `src/fastf1_analytics`
- README/setup note

### Learning Resources

- **FastF1 documentation — getting started and cache:** use for install
  and cache configuration.

------------------------------------------------------------------------

## Issue 5.2 — Story: Lap-telemetry notebook for one session

**Type:** Story
**Feature:** Telemetry Notebooks
**Story Points:** 3
**Priority:** Medium
**Milestone:** Month 3 — Data Engineering and Analytics
**Labels:** `story`, `fastf1`, `python`, `portfolio`
**Suggested branch:** `feat/lap-telemetry-notebook`
**Suggested PR title:** `feat(fastf1): lap telemetry notebook with speed/throttle/brake traces`

### User Story

As a learner, I want a telemetry notebook for one session so that the
portfolio shows real F1 data analysis with narrative.

### Goal

A reproducible notebook loading one session and plotting speed, throttle
and brake traces for a chosen lap, with commentary.

### Dependencies

- **Requires:** 5.1
- **Blocks:** 5.4 (helper extraction)

### Tasks

- [ ] Load a chosen session and lap
- [ ] Plot speed, throttle and brake traces
- [ ] Add narrative commentary explaining the plots
- [ ] Ensure the notebook re-runs top-to-bottom from cache
- [ ] Save to `notebooks/`

### SMART Acceptance Criteria

- [ ] **Specific:** One notebook plots three telemetry channels for a
      chosen lap.
- [ ] **Measurable:** Notebook re-runs cleanly end-to-end; ≥ 3 charts
      with written interpretation.
- [ ] **Achievable:** Uses FastF1 + matplotlib.
- [ ] **Relevant:** Portfolio-visible analysis.
- [ ] **Time-bound:** Complete within Week 1 of Month 3.

### Definition of Done

- [ ] Notebook merged and re-runnable; commentary included

### Deliverables

- `notebooks/lap-telemetry.ipynb`

### Learning Resources

- **FastF1 documentation — telemetry and plotting:** use for channels
  and lap selection.

------------------------------------------------------------------------

## Issue 5.3 — Story: Driver and stint comparison notebook

**Type:** Story
**Feature:** Driver / Stint Comparison
**Story Points:** 3
**Priority:** Medium
**Milestone:** Month 3 — Data Engineering and Analytics
**Labels:** `story`, `fastf1`, `python`
**Suggested branch:** `feat/driver-stint-comparison`
**Suggested PR title:** `feat(fastf1): driver and stint comparison analysis`

### User Story

As a learner, I want to compare drivers and analyse stints so that the
analytics go beyond a single lap.

### Goal

A notebook comparing two drivers over a session and analysing stint pace
degradation.

### Dependencies

- **Requires:** 5.1, 5.2

### Tasks

- [ ] Compare two drivers' lap times across a session
- [ ] Segment laps into stints and analyse pace over each stint
- [ ] Visualise degradation / delta
- [ ] Add interpretation
- [ ] Save to `notebooks/`

### SMART Acceptance Criteria

- [ ] **Specific:** The notebook compares ≥ 2 drivers and ≥ 2 stints.
- [ ] **Measurable:** Produces delta and degradation charts with written
      reading; re-runs cleanly.
- [ ] **Achievable:** FastF1 lap data.
- [ ] **Relevant:** Deeper analytical portfolio content.
- [ ] **Time-bound:** Complete within Week 2 of Month 3.

### Definition of Done

- [ ] Notebook merged and re-runnable

### Deliverables

- `notebooks/driver-stint-comparison.ipynb`

### Learning Resources

- **FastF1 documentation — laps and results:** use for lap/stint data.

------------------------------------------------------------------------

## Issue 5.4 — Story: Extract reusable telemetry/plot helpers

**Type:** Story
**Feature:** Reusable Analysis Utilities
**Story Points:** 3
**Priority:** Medium
**Milestone:** Month 3 — Data Engineering and Analytics
**Labels:** `story`, `fastf1`, `python`
**Suggested branch:** `feat/fastf1-helpers`
**Suggested PR title:** `refactor(fastf1): extract reusable load/plot helpers with tests`

### User Story

As a learner, I want common load/plot logic extracted into a tested
module so that notebooks stay thin and Epic 6 templates can reuse it.

### Goal

A `fastf1_analytics` helper module (load session, prepare telemetry,
standard plots) with unit tests, imported by the notebooks.

### Dependencies

- **Requires:** 5.2, 5.3
- **Blocks (soft):** Epic 6 notebook templates

### Tasks

- [ ] Identify duplicated logic across 5.2/5.3
- [ ] Extract load/prepare/plot helpers into `src/fastf1_analytics`
- [ ] Refactor the notebooks to import the helpers
- [ ] Unit tests (≥ 10) with small fixtures
- [ ] Document the helper API

### SMART Acceptance Criteria

- [ ] **Specific:** A helper module provides load and plot functions.
- [ ] **Measurable:** ≥ 10 unit tests pass; both notebooks import the
      module rather than duplicating code.
- [ ] **Achievable:** Refactor of existing code.
- [ ] **Relevant:** Enables reuse in Epic 6.
- [ ] **Time-bound:** Complete within Week 2 of Month 3.

### Definition of Done

- [ ] Module + tests merged; notebooks refactored; green CI

### Deliverables

- `src/fastf1_analytics/`, `tests/fastf1_analytics/`

### Learning Resources

- **FastF1 documentation:** confirm stable APIs to wrap.
- **pytest fixtures:** use for lightweight test data.

------------------------------------------------------------------------

## Issue 5.5 — Story: Publish analysis summaries to Dataverse

**Type:** Story
**Feature:** Publish Summaries to Dataverse
**Story Points:** 3
**Priority:** Medium
**Milestone:** Month 3 — Data Engineering and Analytics
**Labels:** `story`, `fastf1`, `dataverse`, `python`
**Suggested branch:** `feat/publish-summaries`
**Suggested PR title:** `feat(fastf1): publish analysis summaries to Dataverse`

### User Story

As a learner, I want analysis summaries written back to Dataverse so
that insights surface in the model-driven app, not only in notebooks.

### Goal

A routine that writes per-session summary records to Dataverse via the
Tier-1 access layer.

### Dependencies

- **Requires:** 5.4, Tier-1 Dataverse API client, target summary table
  (extend Epic 3 solution)

### Tasks

- [ ] Define/confirm a Dataverse summary table
- [ ] Compute per-session summary metrics
- [ ] Upsert summaries via the Dataverse client (idempotent)
- [ ] Integration test writing and re-writing without duplicates
- [ ] Document the mapping

### SMART Acceptance Criteria

- [ ] **Specific:** Session summaries are upserted to Dataverse.
- [ ] **Measurable:** A run creates summary records; re-running produces
      no duplicates.
- [ ] **Achievable:** Reuses the Dataverse client's upsert.
- [ ] **Relevant:** Surfaces analytics in the app.
- [ ] **Time-bound:** Complete within Week 3 of Month 3.

### Definition of Done

- [ ] Summaries visible in Dataverse; integration test passes; green CI

### Deliverables

- `src/fastf1_analytics/publish.py`
- Summary table in the solution

### Learning Resources

- **Microsoft Learn — Dataverse Web API upsert:** use for idempotent
  writes.

------------------------------------------------------------------------
# EPIC 6 — DATA ENGINEERING
------------------------------------------------------------------------

## Issue 6.1 — Story: Clean and normalise the datasets

**Type:** Story
**Feature:** Data Cleaning & Normalisation
**Story Points:** 5
**Priority:** High
**Milestone:** Month 3 — Data Engineering and Analytics
**Labels:** `story`, `python`, `openf1`
**Suggested branch:** `feat/data-cleaning`
**Suggested PR title:** `feat(data): clean and normalise OpenF1 and CRM datasets`

### User Story

As a learner, I want cleaning and normalisation routines so that raw
ingested and seeded data becomes consistent inputs for analytics and ML.

### Goal

Reusable Pandas routines that clean and normalise the OpenF1 and seeded
CRM datasets into consistent schemas.

### Dependencies

- **Requires:** Epic 4 ingestion, Epic 3 seeded data (3.7)
- **Blocks:** 6.2, 6.3, Epic 7

### Tasks

- [ ] Load raw datasets into Pandas
- [ ] Handle missing values, types and duplicates
- [ ] Normalise column names and units to a consistent schema
- [ ] Unit tests on cleaning functions with sample frames
- [ ] Document the cleaning rules

### SMART Acceptance Criteria

- [ ] **Specific:** Cleaning routines output consistent, typed frames.
- [ ] **Measurable:** Tests cover null-handling, dedup and type coercion;
      output schema documented.
- [ ] **Achievable:** Pandas only.
- [ ] **Relevant:** Precondition for trusted analytics/ML.
- [ ] **Time-bound:** Complete within Week 1 of Month 3.

### Definition of Done

- [ ] Routines + tests merged; rules documented; green CI

### Deliverables

- `src/` cleaning module + `tests/`
- `docs/architecture/data-cleaning.md`

### Learning Resources

- **pandas User Guide — working with missing data / merging:** use for
  cleaning operations.

------------------------------------------------------------------------

## Issue 6.2 — Story: Profile datasets and add quality checks

**Type:** Story
**Feature:** Data Quality & Profiling
**Story Points:** 3
**Priority:** Medium
**Milestone:** Month 3 — Data Engineering and Analytics
**Labels:** `story`, `python`, `governance`
**Suggested branch:** `feat/data-quality`
**Suggested PR title:** `feat(data): profiling and validation to separate cleaned from trusted`

### User Story

As a learner, I want profiling and validation checks so that "cleaned"
data is provably "trusted" before ML uses it.

### Goal

A profiling report plus validation checks (ranges, nullability,
uniqueness) that gate a dataset as trusted.

### Dependencies

- **Requires:** 6.1

### Tasks

- [ ] Generate a profiling summary (distributions, nulls, cardinality)
- [ ] Define validation rules per dataset
- [ ] Implement checks that pass/fail a dataset
- [ ] Unit tests for the checks
- [ ] Document the quality gate

### SMART Acceptance Criteria

- [ ] **Specific:** Profiling + rule-based validation exist per dataset.
- [ ] **Measurable:** A deliberately corrupted frame fails validation; a
      clean frame passes.
- [ ] **Achievable:** Pandas + a lightweight validation approach.
- [ ] **Relevant:** Trust boundary for ML.
- [ ] **Time-bound:** Complete within Week 2 of Month 3.

### Definition of Done

- [ ] Checks + tests merged; quality gate documented

### Deliverables

- Profiling notebook/report + validation module + tests

### Learning Resources

- **pandas — descriptive statistics:** use for profiling.
- **Pandera or Great Expectations docs:** use if adopting a validation
  library (record the choice).

------------------------------------------------------------------------

## Issue 6.3 — Story: Export trusted datasets to Parquet

**Type:** Story
**Feature:** Storage Layer
**Story Points:** 2
**Priority:** Medium
**Milestone:** Month 3 — Data Engineering and Analytics
**Labels:** `story`, `python`
**Suggested branch:** `feat/parquet-export`
**Suggested PR title:** `feat(data): export trusted datasets to partitioned Parquet`

### User Story

As a learner, I want trusted datasets exported to Parquet so that
analytics and ML read efficient, columnar, versioned inputs.

### Goal

Export validated datasets to Parquet under `datasets/`, partitioned
sensibly.

### Dependencies

- **Requires:** 6.2

### Tasks

- [ ] Export cleaned/validated frames to Parquet
- [ ] Choose partitioning (e.g. by season/entity)
- [ ] Add a small read helper
- [ ] Test round-trip (write then read equals input)
- [ ] Document the storage layout

### SMART Acceptance Criteria

- [ ] **Specific:** Trusted datasets are written to Parquet.
- [ ] **Measurable:** A write→read round-trip test passes; files land
      under `datasets/`.
- [ ] **Achievable:** pandas/pyarrow.
- [ ] **Relevant:** Efficient inputs for Epic 7.
- [ ] **Time-bound:** Complete within Week 2 of Month 3.

### Definition of Done

- [ ] Export + read helper + round-trip test merged

### Deliverables

- Parquet files under `datasets/`
- Export/read helper + tests

### Learning Resources

- **pandas — IO tools (Parquet):** use for read/write and partitioning.

------------------------------------------------------------------------

## Issue 6.4 — Story: Visualise ingestion and CRM trends

**Type:** Story
**Feature:** Visualisation & Trend Analysis
**Story Points:** 3
**Priority:** Medium
**Milestone:** Month 3 — Data Engineering and Analytics
**Labels:** `story`, `python`, `portfolio`
**Suggested branch:** `feat/trend-visualisation`
**Suggested PR title:** `feat(data): trend visualisation notebook across OpenF1 and CRM`

### User Story

As a learner, I want a trends notebook so that the portfolio shows
insight across both the F1 and CRM datasets.

### Goal

A notebook charting ≥ 3 trends (e.g. lap-time distribution, case volume
over time, opportunity value by stage), each with a one-paragraph
reading.

### Dependencies

- **Requires:** 6.3

### Tasks

- [ ] Load trusted Parquet datasets
- [ ] Produce ≥ 3 trend charts across both domains
- [ ] Write a one-paragraph reading per chart
- [ ] Ensure clean re-run
- [ ] Save to `notebooks/`

### SMART Acceptance Criteria

- [ ] **Specific:** ≥ 3 trends across OpenF1 and CRM are charted.
- [ ] **Measurable:** Each chart has written interpretation; notebook
      re-runs cleanly.
- [ ] **Achievable:** pandas + matplotlib.
- [ ] **Relevant:** Portfolio insight.
- [ ] **Time-bound:** Complete within Week 3 of Month 3.

### Definition of Done

- [ ] Notebook merged and re-runnable

### Deliverables

- `notebooks/trends.ipynb`

### Learning Resources

- **pandas — visualization:** use for charting.

------------------------------------------------------------------------

## Issue 6.5 — Story: Analyse actor and entity change patterns (audit)

**Type:** Story
**Feature:** Audit History Analytics
**Story Points:** 3
**Priority:** High (portfolio piece)
**Milestone:** Month 3 — Data Engineering and Analytics
**Labels:** `story`, `python`, `governance`, `portfolio`
**Suggested branch:** `feat/audit-actor-entity`
**Suggested PR title:** `feat(audit): actor and entity change-pattern analysis`

### User Story

As a learner, I want an audit-history analysis by actor and entity so
that the enterprise-style dataset produces real governance insight.

### Goal

A notebook summarising changes by actor, entity and operation type over
a defined window, with tables and charts.

### Dependencies

- **Requires:** Epic 3 audit history (3.6, 3.7)
- **Blocks (soft):** 6.7 feature extraction

### Tasks

- [ ] Load the seeded audit history
- [ ] Aggregate changes by actor, entity, operation
- [ ] Chart top actors/entities and operation mix
- [ ] Interpret findings
- [ ] Save to `notebooks/`

### SMART Acceptance Criteria

- [ ] **Specific:** Changes are summarised by actor, entity and
      operation.
- [ ] **Measurable:** ≥ 3 tables/charts with interpretation; notebook
      re-runs cleanly.
- [ ] **Achievable:** pandas over the audit dataset.
- [ ] **Relevant:** Headline governance analytics.
- [ ] **Time-bound:** Complete within Week 3 of Month 3.

### Definition of Done

- [ ] Notebook merged and re-runnable

### Deliverables

- `notebooks/audit-actor-entity.ipynb`

### Learning Resources

- **pandas — groupby / pivot tables:** use for the aggregations.

------------------------------------------------------------------------

## Issue 6.6 — Story: Analyse temporal audit patterns

**Type:** Story
**Feature:** Audit History Analytics
**Story Points:** 3
**Priority:** Medium
**Milestone:** Month 3 — Data Engineering and Analytics
**Labels:** `story`, `python`, `governance`
**Suggested branch:** `feat/audit-temporal`
**Suggested PR title:** `feat(audit): temporal pattern analysis (bursts, gaps, time-of-day)`

### User Story

As a learner, I want temporal audit analysis so that time-based anomalies
(bursts, off-hours activity, gaps) become visible.

### Goal

A notebook visualising activity by hour/day, detecting bursts and unusual
gaps.

### Dependencies

- **Requires:** 3.6/3.7 audit history
- **Blocks (soft):** 6.7, Epic 7 anomaly model

### Tasks

- [ ] Parse timestamps and build time series
- [ ] Chart activity by hour and day-of-week
- [ ] Flag bursts and unusual gaps
- [ ] Interpret findings
- [ ] Save to `notebooks/`

### SMART Acceptance Criteria

- [ ] **Specific:** Time-based patterns are visualised.
- [ ] **Measurable:** ≥ 2 temporal charts plus a burst/gap summary;
      notebook re-runs cleanly.
- [ ] **Achievable:** pandas time-series.
- [ ] **Relevant:** Feeds anomaly detection.
- [ ] **Time-bound:** Complete within Week 3 of Month 3.

### Definition of Done

- [ ] Notebook merged and re-runnable

### Deliverables

- `notebooks/audit-temporal.ipynb`

### Learning Resources

- **pandas — time series / resampling:** use for temporal aggregation.

------------------------------------------------------------------------

## Issue 6.7 — Story: Extract audit features for anomaly detection

**Type:** Story
**Feature:** Audit History Analytics
**Story Points:** 3
**Priority:** High (blocks Epic 7 anomaly model)
**Milestone:** Month 3 — Data Engineering and Analytics
**Labels:** `story`, `python`, `ml`, `governance`
**Suggested branch:** `feat/audit-features`
**Suggested PR title:** `feat(audit): feature table for anomaly detection`

### User Story

As a learner, I want an audit feature table so that the Epic 7 anomaly
model has a documented, ready-to-use input.

### Goal

A documented feature table (per actor / per entity change frequencies,
recency, diversity) exported to Parquet for Epic 7.

### Dependencies

- **Requires:** 6.5, 6.6
- **Blocks:** Epic 7 anomaly detection (7.5)

### Tasks

- [ ] Define features (change frequency, recency, entity diversity, etc.)
- [ ] Compute the feature table
- [ ] Export to `datasets/audit-history/features.parquet`
- [ ] Document each feature's definition
- [ ] Unit tests on feature computations

### SMART Acceptance Criteria

- [ ] **Specific:** A documented feature table is exported.
- [ ] **Measurable:** ≥ 5 features defined and tested; Parquet file
      produced and readable.
- [ ] **Achievable:** pandas aggregations.
- [ ] **Relevant:** Direct input to the anomaly model.
- [ ] **Time-bound:** Complete within Week 4 of Month 3.

### Definition of Done

- [ ] Feature table exported; features documented; tests pass; green CI

### Deliverables

- `datasets/audit-history/features.parquet`
- Feature notebook + `docs/architecture/audit-features.md`

### Learning Resources

- **pandas — groupby aggregation:** use for feature computation.

------------------------------------------------------------------------

## Issue 6.8 — Story: Build reusable notebook templates

**Type:** Story
**Feature:** Reusable Notebook Templates
**Story Points:** 2
**Priority:** Low
**Milestone:** Month 3 — Data Engineering and Analytics
**Labels:** `story`, `python`, `documentation`
**Suggested branch:** `feat/notebook-templates`
**Suggested PR title:** `feat(data): reusable analysis notebook templates`

### User Story

As a learner, I want notebook templates so that new analyses start
consistently and reuse the Epic 5 helpers.

### Goal

One or two starter notebook templates (setup, load trusted data, plot,
interpret) importing the shared helpers.

### Dependencies

- **Requires:** 5.4 helpers, 6.3 Parquet layer

### Tasks

- [ ] Create a template notebook with standard sections
- [ ] Wire in `fastf1_analytics` helpers and Parquet loading
- [ ] Document how to start a new analysis from the template

### SMART Acceptance Criteria

- [ ] **Specific:** A reusable template notebook exists.
- [ ] **Measurable:** A new analysis can be started from it in < 5
      minutes; it imports the shared helpers.
- [ ] **Achievable:** Documentation/scaffolding.
- [ ] **Relevant:** Consistency and reuse.
- [ ] **Time-bound:** Complete within Week 4 of Month 3.

### Definition of Done

- [ ] Template + usage note merged

### Deliverables

- `notebooks/_template.ipynb`
- Usage note

### Learning Resources

- **Jupyter documentation:** use for notebook structure conventions.



========================================================================


# GitHub Issue Drafts (Tier 6: Epic 7 Machine Learning)

> Full-spec, copy-paste-ready issues for the ML epic. All Month 4.
> Depends on Epic 6 trusted datasets (6.3) and the audit feature table
> (6.7). Inference serving reuses the Tier-1 Azure Functions platform.

------------------------------------------------------------------------

## Issue 7.1 — Story: Engineer feature sets for the portfolio models

**Type:** Story
**Feature:** Feature Engineering
**Story Points:** 5
**Priority:** High
**Milestone:** Month 4 — Machine Learning and Evaluation
**Labels:** `story`, `ml`, `python`
**Suggested branch:** `feat/ml-feature-engineering`
**Suggested PR title:** `feat(ml): documented feature sets for lap, strategy and audit models`

### User Story

As a learner, I want documented feature sets tied to each model so that
training is reproducible and the features are defensible.

### Goal

Three documented feature sets: lap/stint features (lap prediction),
race-context features (strategy classification), and audit
change-frequency/recency features (consuming Epic 6's 6.7 export).

### Business Value

Well-specified features are the difference between a toy model and a
credible one; documentation is a portfolio signal.

### Learning Value

Feature engineering, leakage avoidance, and feature documentation.

### Dependencies

- **Requires:** 6.3 trusted datasets, 6.7 audit features
- **Blocks:** 7.2, 7.3, 7.5

### Tasks

- [ ] Derive lap/stint features for lap prediction
- [ ] Derive race-context features for strategy classification
- [ ] Load audit features from 6.7
- [ ] Check for and prevent target leakage
- [ ] Document each feature and its rationale
- [ ] Unit tests on feature computations

### SMART Acceptance Criteria

- [ ] **Specific:** Three named feature sets exist, each documented.
- [ ] **Measurable:** Each set has ≥ 5 documented features; a leakage
      check is described per set.
- [ ] **Achievable:** pandas/scikit-learn transformers.
- [ ] **Relevant:** Feeds all three models.
- [ ] **Time-bound:** Complete within Week 1 of Month 4.

### Definition of Ready

- [ ] Trusted datasets (6.3) and audit features (6.7) available

### Definition of Done

- [ ] Feature modules + tests merged; features documented; green CI

### Deliverables

- `src/ai/features/` (or `src/ml/features/`) + tests
- `docs/architecture/ml-features.md`

### Learning Resources

- **scikit-learn — preprocessing and pipelines:** use for feature
  transformers.
- **scikit-learn — common pitfalls (data leakage):** use for the leakage
  checks.

------------------------------------------------------------------------

## Issue 7.2 — Story: Lap-time regression model

**Type:** Story
**Feature:** Supervised Learning
**Story Points:** 5
**Priority:** High
**Milestone:** Month 4 — Machine Learning and Evaluation
**Labels:** `story`, `ml`, `python`, `fastf1`, `portfolio`
**Suggested branch:** `feat/lap-regression`
**Suggested PR title:** `feat(ml): lap-time regression model with baseline comparison`

### User Story

As a learner, I want a lap-time regression model so that the portfolio
shows a supervised regression workflow end to end.

### Goal

A trained regression model predicting lap time from the lap/stint
features, compared against a naive baseline, with metrics logged.

### Dependencies

- **Requires:** 7.1; experiment tracking (7.7) recommended in parallel
- **Blocks (soft):** 7.6 evaluation, 7.8 packaging

### Tasks

- [ ] Split data (train/validation/test) without leakage
- [ ] Establish a naive baseline
- [ ] Train a regression model (e.g. gradient boosting)
- [ ] Evaluate on held-out data (MAE/RMSE/R²)
- [ ] Log the run (ties to 7.7)
- [ ] Document results and limitations

### SMART Acceptance Criteria

- [ ] **Specific:** A regression model predicts lap time and beats a
      baseline.
- [ ] **Measurable:** Test-set MAE/RMSE reported and lower than the
      baseline; run logged.
- [ ] **Achievable:** scikit-learn.
- [ ] **Relevant:** Core supervised deliverable.
- [ ] **Time-bound:** Complete within Week 2 of Month 4.

### Definition of Done

- [ ] Model trained, evaluated and beating baseline; run logged; results
      documented; green CI

### Deliverables

- Training script/notebook + `docs/architecture/lap-regression.md`

### Learning Resources

- **scikit-learn — supervised learning / model selection:** use for
  training and splits.
- **scikit-learn — regression metrics:** use for evaluation.

------------------------------------------------------------------------

## Issue 7.3 — Story: Strategy classification model

**Type:** Story
**Feature:** Supervised Learning
**Story Points:** 5
**Priority:** Medium
**Milestone:** Month 4 — Machine Learning and Evaluation
**Labels:** `story`, `ml`, `python`, `fastf1`
**Suggested branch:** `feat/strategy-classification`
**Suggested PR title:** `feat(ml): race-strategy classification model`

### User Story

As a learner, I want a strategy classification model so that the
portfolio includes a supervised classification workflow.

### Goal

A classifier predicting a race-strategy label from race-context
features, with appropriate metrics.

### Dependencies

- **Requires:** 7.1

### Tasks

- [ ] Define the classification target and encode labels
- [ ] Split data without leakage
- [ ] Train a classifier and a baseline
- [ ] Evaluate (accuracy, precision/recall, F1, confusion matrix)
- [ ] Log the run
- [ ] Document results

### SMART Acceptance Criteria

- [ ] **Specific:** A classifier predicts the strategy label.
- [ ] **Measurable:** F1 and a confusion matrix reported; beats a
      majority-class baseline.
- [ ] **Achievable:** scikit-learn.
- [ ] **Relevant:** Classification deliverable.
- [ ] **Time-bound:** Complete within Week 2 of Month 4.

### Definition of Done

- [ ] Model trained, evaluated, beating baseline; run logged; documented

### Deliverables

- Training script/notebook + doc

### Learning Resources

- **scikit-learn — classification metrics:** use for F1/confusion
  matrix.

------------------------------------------------------------------------

## Issue 7.4 — Story: Clustering analysis

**Type:** Story
**Feature:** Unsupervised Learning
**Story Points:** 3
**Priority:** Low
**Milestone:** Month 4 — Machine Learning and Evaluation
**Labels:** `story`, `ml`, `python`
**Suggested branch:** `feat/clustering`
**Suggested PR title:** `feat(ml): clustering analysis with cluster interpretation`

### User Story

As a learner, I want a clustering analysis so that the portfolio shows
an unsupervised workflow with interpreted clusters.

### Goal

Cluster a suitable dataset (e.g. driver/stint profiles), choose k with a
principled method, and interpret the clusters.

### Dependencies

- **Requires:** 6.3 / 7.1 features

### Tasks

- [ ] Select and scale features
- [ ] Choose k (elbow/silhouette)
- [ ] Fit clustering and assign labels
- [ ] Interpret and visualise clusters
- [ ] Document findings

### SMART Acceptance Criteria

- [ ] **Specific:** Clusters are produced and interpreted.
- [ ] **Measurable:** k justified by a metric; ≥ 1 visualisation with
      written interpretation.
- [ ] **Achievable:** scikit-learn.
- [ ] **Relevant:** Unsupervised deliverable.
- [ ] **Time-bound:** Complete within Week 3 of Month 4.

### Definition of Done

- [ ] Clustering + interpretation merged

### Deliverables

- Notebook + doc

### Learning Resources

- **scikit-learn — clustering:** use for algorithms and k selection.

------------------------------------------------------------------------

## Issue 7.5 — Story: Audit anomaly detection model

**Type:** Story
**Feature:** Anomaly Detection
**Story Points:** 5
**Priority:** High (headline portfolio piece)
**Milestone:** Month 4 — Machine Learning and Evaluation
**Labels:** `story`, `ml`, `python`, `governance`, `portfolio`
**Suggested branch:** `feat/audit-anomaly`
**Suggested PR title:** `feat(ml): audit anomaly detection on change-behaviour features`

### User Story

As a learner, I want an audit anomaly detector so that the enterprise
audit dataset yields a governance-relevant ML capability.

### Goal

An unsupervised anomaly detector (e.g. Isolation Forest) over the 6.7
audit features, surfacing and explaining flagged anomalies.

### Dependencies

- **Requires:** 6.7 audit feature table, 7.1
- **Blocks (soft):** Epic 12 integration, Epic 11 responsible AI

### Tasks

- [ ] Load the audit feature table
- [ ] Fit an anomaly detector
- [ ] Rank and inspect the top anomalies
- [ ] Explain why flagged records are anomalous
- [ ] Log the run and document limitations (no labels → qualitative eval)

### SMART Acceptance Criteria

- [ ] **Specific:** An anomaly detector flags unusual audit behaviour.
- [ ] **Measurable:** Top-N anomalies surfaced with per-record
      explanation; run logged.
- [ ] **Achievable:** scikit-learn Isolation Forest / LOF.
- [ ] **Relevant:** Governance-relevant headline model.
- [ ] **Time-bound:** Complete within Week 3 of Month 4.

### Definition of Done

- [ ] Detector + explanations merged; run logged; limitations documented

### Deliverables

- Training script/notebook + `docs/architecture/audit-anomaly.md`

### Learning Resources

- **scikit-learn — outlier / novelty detection:** use for the detector.

------------------------------------------------------------------------

## Issue 7.6 — Story: Model evaluation and comparison

**Type:** Story
**Feature:** Model Evaluation & Metrics
**Story Points:** 3
**Priority:** Medium
**Milestone:** Month 4 — Machine Learning and Evaluation
**Labels:** `story`, `ml`, `python`, `documentation`
**Suggested branch:** `feat/model-evaluation`
**Suggested PR title:** `feat(ml): consistent evaluation harness and model comparison`

### User Story

As a learner, I want a consistent evaluation harness so that models are
compared fairly and results are reproducible.

### Goal

A shared evaluation routine producing standard metrics and a comparison
table across the trained models.

### Dependencies

- **Requires:** 7.2, 7.3 (and 7.5 qualitatively)

### Tasks

- [ ] Implement a reusable evaluation function per task type
- [ ] Produce a comparison table (model vs baseline)
- [ ] Add cross-validation where appropriate
- [ ] Document metric choices and their meaning

### SMART Acceptance Criteria

- [ ] **Specific:** One harness evaluates regression and classification
      models consistently.
- [ ] **Measurable:** A comparison table covers each model vs its
      baseline with the same metrics.
- [ ] **Achievable:** scikit-learn metrics + CV.
- [ ] **Relevant:** Credible, comparable results.
- [ ] **Time-bound:** Complete within Week 4 of Month 4.

### Definition of Done

- [ ] Harness + comparison table merged; metric choices documented

### Deliverables

- `src/` evaluation module + comparison notebook

### Learning Resources

- **scikit-learn — cross-validation and metrics:** use for the harness.

------------------------------------------------------------------------

## Issue 7.7 — Story: Experiment tracking and reproducibility

**Type:** Story
**Feature:** Experiment Tracking & Reproducibility
**Story Points:** 3
**Priority:** High (architect signal)
**Milestone:** Month 4 — Machine Learning and Evaluation
**Labels:** `story`, `ml`, `python`, `architecture`
**Suggested branch:** `feat/experiment-tracking`
**Suggested PR title:** `feat(ml): experiment tracking, fixed seeds and model cards`

### User Story

As a learner, I want experiment tracking, fixed seeds and model cards so
that every result is reproducible and explainable.

### Goal

Logged runs (params, metrics, artefacts), documented seed policy, and a
model card per portfolio model.

### Dependencies

- **Requires:** at least one model (7.2)
- **Enhances:** 7.2, 7.3, 7.5

### Tasks

- [ ] Choose a tracking approach (MLflow or structured logs) — record it
- [ ] Log params, metrics and artefacts per run
- [ ] Fix and document random seeds
- [ ] Produce a model card per model
- [ ] Document how to reproduce a run

### SMART Acceptance Criteria

- [ ] **Specific:** Runs are logged and each model has a card.
- [ ] **Measurable:** ≥ 2 runs logged with params/metrics; re-running
      with the fixed seed reproduces the metric within tolerance.
- [ ] **Achievable:** MLflow local or structured logging.
- [ ] **Relevant:** Reproducibility is a key architect signal.
- [ ] **Time-bound:** Complete within Week 4 of Month 4.

### Definition of Done

- [ ] Tracking in use; seeds fixed; model cards written

### Deliverables

- Tracking setup + `docs/architecture/model-cards/`

### Learning Resources

- **MLflow documentation — tracking:** use if adopting MLflow.
- **Model Cards (Google / Hugging Face guidance):** use for the card
  structure.

------------------------------------------------------------------------

## Issue 7.8 — Story: Package and serve a model via Azure Function

**Type:** Story
**Feature:** Model Packaging & Inference
**Story Points:** 5
**Priority:** Medium
**Milestone:** Month 4 — Machine Learning and Evaluation
**Labels:** `story`, `ml`, `azure`, `python`
**Suggested branch:** `feat/model-inference-function`
**Suggested PR title:** `feat(ml): serialise a model and serve inference via Azure Function`

### User Story

As a learner, I want a trained model served behind an HTTP Function so
that inference is callable from the app and agents.

### Goal

Serialise a chosen model and expose an HTTP-triggered inference endpoint
on the Tier-1 Functions platform.

### Dependencies

- **Requires:** a trained model (7.2), Tier-1 Serverless platform
- **Blocks (soft):** Epic 12 integration

### Tasks

- [ ] Serialise the model (with version metadata)
- [ ] Add an HTTP-triggered inference function
- [ ] Validate inputs and return typed predictions
- [ ] Handle load-once/reuse of the model in the function
- [ ] Test locally and deployed
- [ ] Document the endpoint contract

### SMART Acceptance Criteria

- [ ] **Specific:** An HTTP function returns predictions from the
      serialised model.
- [ ] **Measurable:** A sample request returns a valid prediction locally
      and when deployed; invalid input returns a clear error.
- [ ] **Achievable:** Reuses the Tier-1 Functions app.
- [ ] **Relevant:** Bridges ML into the deployed solution.
- [ ] **Time-bound:** Complete within Week 4 of Month 4.

### Definition of Done

- [ ] Endpoint works locally and deployed; contract documented; green CI

### Deliverables

- Serialised model artefact + inference function
- `docs/architecture/inference-endpoint.md`

### Learning Resources

- **scikit-learn — model persistence:** use for serialisation caveats.
- **Microsoft Learn — Azure Functions HTTP trigger (Python):** use for
  the endpoint.



========================================================================


# GitHub Issue Drafts (Tier 7: Epic 8 Generative AI)

> Full-spec, copy-paste-ready issues for the GenAI epic. All Month 5.
> Depends on Epic 3 AI Request/Response entities and the Tier-1
> serverless platform. The three CRM-assistant stories (8.6–8.8) were
> split from one oversized story in the v0.3 review.

------------------------------------------------------------------------

## Issue 8.1 — Story: Azure OpenAI / Foundry integration

**Type:** Story
**Feature:** Azure OpenAI / Microsoft Foundry Integration
**Story Points:** 3
**Priority:** High
**Milestone:** Month 5 — Generative AI, RAG and Agents
**Labels:** `story`, `ai`, `azure`, `python`
**Suggested branch:** `feat/azure-openai-integration`
**Suggested PR title:** `feat(ai): Azure OpenAI client wrapper with config and logging`

### User Story

As a learner, I want a configured Azure OpenAI client wrapper so that
every LLM feature calls the model through one governed entrypoint.

### Goal

A `src/ai` client wrapping Azure OpenAI (chat + embeddings) with config,
retries via `shared`, and structured logging.

### Business Value

One governed LLM entrypoint; prevents scattered SDK calls and eases later
logging and cost control.

### Learning Value

Azure OpenAI SDK, deployment/model config, and safe client design.

### Dependencies

- **Requires:** 2.A shared, 2.B resilience; an Azure OpenAI resource
- **Blocks:** 8.2–8.10, Epic 9 generation

### Tasks

- [ ] Provision/confirm an Azure OpenAI deployment
- [ ] Wrap chat completion and embeddings calls
- [ ] Load endpoint/deployment config from `shared` (no inline secrets)
- [ ] Add retry (via `shared`) and structured logging
- [ ] Unit tests with mocked responses
- [ ] Document usage

### SMART Acceptance Criteria

- [ ] **Specific:** A wrapper exposes chat and embeddings calls.
- [ ] **Measurable:** A live call returns a completion; tests pass with
      mocks; no secrets in source.
- [ ] **Achievable:** Azure OpenAI SDK.
- [ ] **Relevant:** Foundation for all LLM features.
- [ ] **Time-bound:** Complete within Week 1 of Month 5.

### Definition of Done

- [ ] Wrapper merged; live smoke test passes; green CI; no secrets

### Deliverables

- `src/ai/client.py`, `tests/ai/`

### Learning Resources

- **Microsoft Learn — Azure OpenAI Service quickstart (Python):** use
  for client setup and calls.

------------------------------------------------------------------------

## Issue 8.2 — Story: Prompt engineering patterns and prompt library

**Type:** Story
**Feature:** Prompt Engineering
**Story Points:** 3
**Priority:** Medium
**Milestone:** Month 5 — Generative AI, RAG and Agents
**Labels:** `story`, `ai`, `python`, `documentation`
**Suggested branch:** `feat/prompt-library`
**Suggested PR title:** `feat(ai): reusable prompt templates and prompt-engineering notes`

### User Story

As a learner, I want a small prompt library and documented patterns so
that prompts are versioned and reusable rather than ad hoc.

### Goal

Reusable, parameterised prompt templates for the summary and assistant
use cases, with a short patterns note.

### Dependencies

- **Requires:** 8.1

### Tasks

- [ ] Define parameterised prompt templates (system + user)
- [ ] Cover summarisation and CRM Q&A cases
- [ ] Document prompt-engineering patterns used
- [ ] Add tests that templates render with expected variables

### SMART Acceptance Criteria

- [ ] **Specific:** A prompt library with ≥ 3 templates exists.
- [ ] **Measurable:** Templates render deterministically in tests; a
      patterns note is written.
- [ ] **Achievable:** Templating only.
- [ ] **Relevant:** Reused by summaries and the assistant.
- [ ] **Time-bound:** Complete within Week 1 of Month 5.

### Definition of Done

- [ ] Library + tests + note merged; green CI

### Deliverables

- `src/ai/prompts/` + `docs/learning/prompt-engineering.md`

### Learning Resources

- **Microsoft Learn — Prompt engineering techniques (Azure OpenAI):**
  use for the patterns.

------------------------------------------------------------------------

## Issue 8.3 — Story: Structured outputs

**Type:** Story
**Feature:** Structured Outputs
**Story Points:** 3
**Priority:** Medium
**Milestone:** Month 5 — Generative AI, RAG and Agents
**Labels:** `story`, `ai`, `python`
**Suggested branch:** `feat/structured-outputs`
**Suggested PR title:** `feat(ai): schema-constrained structured outputs with validation`

### User Story

As a learner, I want the model to return schema-validated structured
output so that downstream code consumes reliable JSON, not free text.

### Goal

A pattern that requests structured output and validates it against a
Pydantic schema, with graceful handling of invalid responses.

### Dependencies

- **Requires:** 8.1

### Tasks

- [ ] Define output schemas (Pydantic) for a chosen task
- [ ] Request structured output from the model
- [ ] Validate and, on failure, retry/repair or raise a typed error
- [ ] Unit tests for valid and invalid model outputs

### SMART Acceptance Criteria

- [ ] **Specific:** Model output is validated against a schema.
- [ ] **Measurable:** Valid output parses; an invalid output is caught
      and handled (tested).
- [ ] **Achievable:** Pydantic + Azure OpenAI structured output.
- [ ] **Relevant:** Reliable inputs for function calling and the app.
- [ ] **Time-bound:** Complete within Week 1 of Month 5.

### Definition of Done

- [ ] Pattern + tests merged; green CI

### Deliverables

- `src/ai/structured.py` + tests

### Learning Resources

- **Microsoft Learn — Structured outputs (Azure OpenAI):** use for the
  request format.
- **Pydantic documentation:** use for schema validation.

------------------------------------------------------------------------

## Issue 8.4 — Story: Function calling, tool routing and ADR-0006

**Type:** Story
**Feature:** Function Calling & Tool Routing
**Story Points:** 5
**Priority:** High
**Milestone:** Month 5 — Generative AI, RAG and Agents
**Labels:** `story`, `ai`, `python`, `architecture`
**Suggested branch:** `feat/function-calling`
**Suggested PR title:** `feat(ai): single-model function calling and tool routing (ADR-0006)`

### User Story

As a learner, I want a single-model function-calling layer so that the
assistant can invoke tools, and I want the Epic 8/10 boundary recorded so
agents reuse this layer rather than duplicating it.

### Goal

A tool-routing layer that lets one model call registered tools, plus
ADR-0006 defining the boundary (Epic 8 = single-model calling; Epic 10 =
orchestration reusing this layer).

### Business Value

The tool layer both the assistant and the agents depend on; the ADR
prevents duplicated tool plumbing.

### Learning Value

Function/tool calling, schema-described tools, and safe dispatch.

### Dependencies

- **Requires:** 8.1, 8.3
- **Blocks:** 8.8 CRM actions, Epic 10 agents

### Tasks

- [ ] Define a tool interface (name, schema, handler)
- [ ] Implement model-driven tool selection and dispatch
- [ ] Validate tool arguments before execution
- [ ] Add 1–2 read-only sample tools
- [ ] Unit tests for routing and argument validation
- [ ] Record ADR-0006 (function-calling vs agent-orchestration boundary)

### SMART Acceptance Criteria

- [ ] **Specific:** The model can select and call a registered tool with
      validated arguments.
- [ ] **Measurable:** A test prompt triggers the correct tool with
      correct args; ADR-0006 is accepted.
- [ ] **Achievable:** Azure OpenAI tool calling.
- [ ] **Relevant:** Shared foundation for assistant and agents.
- [ ] **Time-bound:** Complete within Week 2 of Month 5.

### Definition of Done

- [ ] Routing + tests merged; ADR-0006 recorded; green CI

### Deliverables

- `src/ai/tools/` routing layer + tests
- `docs/decisions/ADR-0006-function-calling-boundary.md`

### Learning Resources

- **Microsoft Learn — Function calling with Azure OpenAI:** use for the
  tool-calling mechanics.

------------------------------------------------------------------------

## Issue 8.5 — Story: AI summaries

**Type:** Story
**Feature:** AI Summaries
**Story Points:** 3
**Priority:** Medium
**Milestone:** Month 5 — Generative AI, RAG and Agents
**Labels:** `story`, `ai`, `python`, `dataverse`
**Suggested branch:** `feat/ai-summaries`
**Suggested PR title:** `feat(ai): generate CRM record summaries with logging`

### User Story

As a learner, I want AI-generated summaries of CRM records so that the
app can surface concise overviews of accounts/cases.

### Goal

A summarisation routine over CRM records using the prompt library, with
prompt/response logging.

### Dependencies

- **Requires:** 8.1, 8.2; Dataverse access layer
- **Ties to:** 8.9 logging

### Tasks

- [ ] Fetch record context via the Dataverse layer
- [ ] Generate a summary using a prompt template
- [ ] Log prompt/response (ties to 8.9)
- [ ] Handle long context (truncation/chunking)
- [ ] Tests with mocked model responses

### SMART Acceptance Criteria

- [ ] **Specific:** A routine summarises a CRM record.
- [ ] **Measurable:** Produces a summary for a seeded account/case;
      prompt/response logged.
- [ ] **Achievable:** Uses the client + prompt library.
- [ ] **Relevant:** Visible AI value in the app.
- [ ] **Time-bound:** Complete within Week 2 of Month 5.

### Definition of Done

- [ ] Summaries generated and logged; tests pass; green CI

### Deliverables

- `src/ai/summaries.py` + tests

### Learning Resources

- **Microsoft Learn — Azure OpenAI completions best practices:** use for
  summarisation prompting.

------------------------------------------------------------------------

## Issue 8.6 — Story: CRM assistant scaffolding

**Type:** Story
**Feature:** Generic CRM Assistant
**Story Points:** 5
**Priority:** High
**Milestone:** Month 5 — Generative AI, RAG and Agents
**Labels:** `story`, `ai`, `python`, `dataverse`, `portfolio`
**Suggested branch:** `feat/crm-assistant-scaffolding`
**Suggested PR title:** `feat(ai): conversational CRM assistant over Dataverse data`

### User Story

As a learner, I want a conversational assistant over the generic CRM so
that users can ask questions answered from Dataverse data.

### Goal

An assistant that answers questions from Dataverse via the access layer,
with prompt/response logging enabled.

### Dependencies

- **Requires:** 8.1, 8.2, Dataverse access layer
- **Blocks (soft):** 8.7 grounding, 8.8 actions

### Tasks

- [ ] Build a conversation loop with system/context prompts
- [ ] Retrieve relevant CRM data via the Dataverse layer
- [ ] Answer questions grounded in that data
- [ ] Enable prompt/response logging (8.9)
- [ ] Tests with mocked model + data
- [ ] Document the assistant

### SMART Acceptance Criteria

- [ ] **Specific:** The assistant answers CRM questions from Dataverse
      data.
- [ ] **Measurable:** Answers a seeded question correctly; every
      interaction is logged.
- [ ] **Achievable:** Client + Dataverse layer.
- [ ] **Relevant:** Portfolio-visible assistant.
- [ ] **Time-bound:** Complete within Week 3 of Month 5.

### Definition of Done

- [ ] Assistant answers grounded questions; logging on; tests pass

### Deliverables

- `src/ai/assistant/` + tests
- `docs/architecture/crm-assistant.md`

### Learning Resources

- **Microsoft Learn — Build a chat app with Azure OpenAI:** use for the
  conversation pattern.

------------------------------------------------------------------------

## Issue 8.7 — Story: Ground the assistant with RAG

**Type:** Story
**Feature:** Generic CRM Assistant
**Story Points:** 3
**Priority:** High
**Milestone:** Month 5 — Generative AI, RAG and Agents
**Labels:** `story`, `ai`, `rag`, `python`, `portfolio`
**Suggested branch:** `feat/assistant-rag-grounding`
**Suggested PR title:** `feat(ai): ground CRM assistant answers in RAG with citations`

### User Story

As a learner, I want the assistant grounded in RAG retrieval so that
answers cite knowledge sources instead of relying on model memory.

### Goal

Connect the assistant to the Epic 9 RAG assistant (9.Z) so answers are
grounded and cited.

### Dependencies

- **Requires:** 8.6, Epic 9 assembly (9.Z)

### Tasks

- [ ] Call the RAG assistant for knowledge-grounded questions
- [ ] Merge retrieved, cited context into the answer
- [ ] Fall back gracefully when retrieval returns nothing
- [ ] Tests covering grounded vs ungrounded paths
- [ ] Document the grounding behaviour

### SMART Acceptance Criteria

- [ ] **Specific:** Knowledge questions are answered with citations from
      RAG.
- [ ] **Measurable:** A seeded knowledge question returns an answer with
      ≥ 1 citation; a no-hit query degrades gracefully.
- [ ] **Achievable:** Reuses 9.Z.
- [ ] **Relevant:** Trustworthy, cited answers.
- [ ] **Time-bound:** Complete within Week 3 of Month 5.

### Definition of Done

- [ ] Grounded answers with citations; tests pass; documented

### Deliverables

- Updated assistant + tests

### Learning Resources

- **Microsoft Learn — RAG with Azure AI Search:** use for the grounding
  pattern.

------------------------------------------------------------------------

## Issue 8.8 — Story: Add guarded CRM action tools

**Type:** Story
**Feature:** Generic CRM Assistant
**Story Points:** 5
**Priority:** Medium
**Milestone:** Month 5 — Generative AI, RAG and Agents
**Labels:** `story`, `ai`, `python`, `dataverse`, `security`
**Suggested branch:** `feat/assistant-actions`
**Suggested PR title:** `feat(ai): guarded CRM action tools with write approval`

### User Story

As a learner, I want the assistant to perform guarded actions (e.g.
create a follow-up activity) so that it moves from answering to doing —
safely.

### Goal

A small set of function-calling tools (via the 8.4 layer) for CRM
lookups and writes, with human approval required on write actions.

### Dependencies

- **Requires:** 8.4 tool layer, 8.6 assistant, Dataverse access layer

### Tasks

- [ ] Implement a read tool (look up a record)
- [ ] Implement a write tool (create a follow-up activity)
- [ ] Require explicit approval before any write executes
- [ ] Log tool invocations
- [ ] Tests: read works; write is blocked without approval
- [ ] Document the tools and the approval gate

### SMART Acceptance Criteria

- [ ] **Specific:** The assistant can look up records and create an
      activity via tools.
- [ ] **Measurable:** A write is blocked until approved (tested); reads
      return correct data.
- [ ] **Achievable:** Reuses the 8.4 routing layer.
- [ ] **Relevant:** Safe, actionable assistant.
- [ ] **Time-bound:** Complete within Week 4 of Month 5.

### Definition of Done

- [ ] Tools work; write approval enforced; tests pass; documented

### Deliverables

- Assistant tools + tests

### Learning Resources

- **Microsoft Learn — Function calling with Azure OpenAI:** use for the
  tools.

------------------------------------------------------------------------

## Issue 8.9 — Story: Prompt and response logging

**Type:** Story
**Feature:** Prompt & Response Logging
**Story Points:** 3
**Priority:** High (governance from the start)
**Milestone:** Month 5 — Generative AI, RAG and Agents
**Labels:** `story`, `ai`, `dataverse`, `governance`
**Suggested branch:** `feat/prompt-response-logging`
**Suggested PR title:** `feat(ai): log prompts/responses to Dataverse and link to audit trail`

### User Story

As a learner, I want prompts and responses logged to Dataverse so that
AI interactions are auditable — governance built in, not bolted on.

### Goal

Every LLM interaction recorded in the AI Request / AI Response entities
and linked to the audit trail.

### Business Value

Auditability of AI behaviour; the data that Epic 11's audit-logging
policy (11.A) later governs.

### Dependencies

- **Requires:** 8.1, Epic 3 AI Request/Response entities, Dataverse layer
- **Governed by:** 11.A

### Tasks

- [ ] Persist request (prompt, model, params) to AI Request
- [ ] Persist response (output, tokens, latency) to AI Response
- [ ] Link records to the acting user / related CRM record
- [ ] Ensure no sensitive secrets are logged
- [ ] Tests verifying records are written
- [ ] Document the logging schema

### SMART Acceptance Criteria

- [ ] **Specific:** Interactions are written to AI Request/Response.
- [ ] **Measurable:** A call produces linked request+response records;
      verified in a test.
- [ ] **Achievable:** Reuses the Dataverse layer.
- [ ] **Relevant:** Core governance capability.
- [ ] **Time-bound:** Complete within Week 2 of Month 5 (early, so later
      stories log by default).

### Definition of Done

- [ ] Logging active across LLM features; tests pass; schema documented

### Deliverables

- `src/ai/logging.py` + tests
- `docs/architecture/ai-logging.md`

### Learning Resources

- **Microsoft Learn — Dataverse Web API create:** use for writing log
  records.

------------------------------------------------------------------------

## Issue 8.10 — Story: GenAI output evaluation harness

**Type:** Story
**Feature:** GenAI Output Evaluation
**Story Points:** 3
**Priority:** Medium
**Milestone:** Month 5 — Generative AI, RAG and Agents
**Labels:** `story`, `ai`, `python`, `governance`
**Suggested branch:** `feat/genai-eval`
**Suggested PR title:** `feat(ai): evaluation harness for summaries and assistant answers`

### User Story

As a learner, I want an evaluation harness for GenAI output so that
summary and answer quality is measured, not assumed.

### Goal

A small evaluation set and harness scoring summaries and assistant
answers (e.g. groundedness, relevance) with documented criteria.

### Dependencies

- **Requires:** 8.5, 8.6

### Tasks

- [ ] Build a small labelled/reference evaluation set
- [ ] Implement scoring (rule-based and/or LLM-as-judge — record choice)
- [ ] Score summaries and assistant answers
- [ ] Report results and known weaknesses
- [ ] Document the evaluation method

### SMART Acceptance Criteria

- [ ] **Specific:** A harness scores GenAI outputs against criteria.
- [ ] **Measurable:** ≥ 10 evaluation cases scored; a results summary is
      produced.
- [ ] **Achievable:** Small eval set + scoring.
- [ ] **Relevant:** Quality evidence for the portfolio.
- [ ] **Time-bound:** Complete within Week 4 of Month 5.

### Definition of Done

- [ ] Harness + results + method doc merged; green CI

### Deliverables

- `src/ai/evaluation/` + eval set + results note

### Learning Resources

- **Microsoft Learn — Evaluate generative AI applications (Azure AI):**
  use for evaluation approaches.



========================================================================


# GitHub Issue Drafts (Tier 8: Epic 9 RAG & Epic 10 Agents)

> Full-spec, copy-paste-ready issues for the RAG pipeline features and
> the agent building blocks. All Month 5. The assembly stories (9.Z RAG
> assistant, 10.Z multi-agent workflow) live in Tier 3 and depend on
> these.

------------------------------------------------------------------------
# EPIC 9 — RAG (pipeline features)
------------------------------------------------------------------------

## Issue 9.1 — Story: Document ingestion and chunking

**Type:** Story
**Feature:** Document Ingestion & Chunking
**Story Points:** 5
**Priority:** High
**Milestone:** Month 5 — Generative AI, RAG and Agents
**Labels:** `story`, `rag`, `python`
**Suggested branch:** `feat/rag-ingestion-chunking`
**Suggested PR title:** `feat(rag): document ingestion and chunking pipeline`

### User Story

As a learner, I want documents ingested and chunked so that the RAG
pipeline has clean, appropriately sized units to embed.

### Goal

An ingestion routine that loads the knowledge sources and splits them
into overlapping chunks with metadata.

### Business Value

The entry point to retrieval quality; chunking choices drive downstream
answer quality.

### Learning Value

Document loading, chunking strategies, and metadata design for
retrieval.

### Dependencies

- **Requires:** knowledge sources available (F1 regs, CRM docs, product
  docs, knowledge articles)
- **Blocks:** 9.2, 9.3, 9.Z

### Tasks

- [ ] Load each knowledge source type
- [ ] Chunk with a chosen size/overlap (record the choice)
- [ ] Attach metadata (source, section, access tag for 9.5)
- [ ] Unit tests on chunk boundaries and metadata
- [ ] Document the ingestion/chunking approach

### SMART Acceptance Criteria

- [ ] **Specific:** Sources are ingested into chunks with metadata.
- [ ] **Measurable:** Chunk count and average size reported; each chunk
      carries source + access-tag metadata (tested).
- [ ] **Achievable:** Standard chunking libraries or custom.
- [ ] **Relevant:** Foundation for retrieval.
- [ ] **Time-bound:** Complete within Week 1 of Month 5.

### Definition of Done

- [ ] Pipeline + tests merged; approach documented; green CI

### Deliverables

- `src/rag/ingestion.py` + tests
- `docs/architecture/rag-ingestion.md`

### Learning Resources

- **Microsoft Learn — Chunk documents for RAG (Azure AI Search):** use
  for chunking guidance.

------------------------------------------------------------------------

## Issue 9.2 — Story: Generate embeddings

**Type:** Story
**Feature:** Embeddings
**Story Points:** 3
**Priority:** High
**Milestone:** Month 5 — Generative AI, RAG and Agents
**Labels:** `story`, `rag`, `ai`, `python`
**Suggested branch:** `feat/rag-embeddings`
**Suggested PR title:** `feat(rag): embedding generation for chunks`

### User Story

As a learner, I want chunk embeddings generated so that documents can be
retrieved by semantic similarity.

### Goal

An embedding routine using the Azure OpenAI embeddings model (via the
8.1 client), batched and idempotent.

### Dependencies

- **Requires:** 9.1, 8.1
- **Blocks:** 9.3, 9.4

### Tasks

- [ ] Embed chunks in batches via the 8.1 client
- [ ] Attach embeddings to chunk metadata
- [ ] Make re-embedding idempotent (skip unchanged chunks)
- [ ] Tests with mocked embeddings
- [ ] Document the model and dimensions used

### SMART Acceptance Criteria

- [ ] **Specific:** Chunks are embedded and stored with their vectors.
- [ ] **Measurable:** All chunks embedded; re-run skips unchanged chunks
      (tested).
- [ ] **Achievable:** Azure OpenAI embeddings.
- [ ] **Relevant:** Enables vector search.
- [ ] **Time-bound:** Complete within Week 1 of Month 5.

### Definition of Done

- [ ] Embedding routine + tests merged; green CI

### Deliverables

- `src/rag/embeddings.py` + tests

### Learning Resources

- **Microsoft Learn — Azure OpenAI embeddings:** use for the embeddings
  API.

------------------------------------------------------------------------

## Issue 9.3 — Story: Azure AI Search index

**Type:** Story
**Feature:** Azure AI Search Index
**Story Points:** 5
**Priority:** High
**Milestone:** Month 5 — Generative AI, RAG and Agents
**Labels:** `story`, `rag`, `azure`, `python`
**Suggested branch:** `feat/ai-search-index`
**Suggested PR title:** `feat(rag): Azure AI Search index with vector and keyword fields`

### User Story

As a learner, I want an Azure AI Search index so that chunks are
searchable by both vector and keyword.

### Goal

A defined index (vector + text + metadata fields, including the access
tag) populated from embedded chunks.

### Dependencies

- **Requires:** 9.2; an Azure AI Search resource
- **Blocks:** 9.4, 9.5, 9.Z

### Tasks

- [ ] Define the index schema (vector, content, source, access tag)
- [ ] Create the index (via SDK/IaC)
- [ ] Upload embedded chunks
- [ ] Verify a basic vector and keyword query
- [ ] Document the schema

### SMART Acceptance Criteria

- [ ] **Specific:** An index with vector + text + metadata fields exists
      and is populated.
- [ ] **Measurable:** A vector query and a keyword query each return
      relevant chunks.
- [ ] **Achievable:** Azure AI Search SDK.
- [ ] **Relevant:** The retrieval backbone.
- [ ] **Time-bound:** Complete within Week 2 of Month 5.

### Definition of Done

- [ ] Index created, populated and queryable; schema documented; no
      secrets in source

### Deliverables

- `src/rag/index.py` + index schema definition
- `docs/architecture/search-index.md`

### Learning Resources

- **Microsoft Learn — Create a vector index (Azure AI Search):** use for
  schema and upload.

------------------------------------------------------------------------

## Issue 9.4 — Story: Hybrid search retrieval

**Type:** Story
**Feature:** Hybrid Search / Retrieval
**Story Points:** 3
**Priority:** High
**Milestone:** Month 5 — Generative AI, RAG and Agents
**Labels:** `story`, `rag`, `azure`, `python`
**Suggested branch:** `feat/hybrid-search`
**Suggested PR title:** `feat(rag): hybrid (vector + keyword) retrieval with ranking`

### User Story

As a learner, I want hybrid retrieval so that queries benefit from both
semantic and keyword matching.

### Goal

A retrieval function combining vector and keyword search with sensible
ranking, returning top-k chunks with metadata.

### Dependencies

- **Requires:** 9.3
- **Blocks:** 9.5, 9.Z

### Tasks

- [ ] Implement hybrid query (vector + keyword)
- [ ] Return top-k with scores and metadata
- [ ] Tune k and ranking on sample queries
- [ ] Tests with a small seeded index
- [ ] Document the retrieval contract

### SMART Acceptance Criteria

- [ ] **Specific:** Hybrid retrieval returns ranked top-k chunks.
- [ ] **Measurable:** For seeded queries, relevant chunks appear in
      top-k (tested).
- [ ] **Achievable:** Azure AI Search hybrid query.
- [ ] **Relevant:** Feeds generation.
- [ ] **Time-bound:** Complete within Week 2 of Month 5.

### Definition of Done

- [ ] Retrieval + tests merged; contract documented; green CI

### Deliverables

- `src/rag/retrieval.py` + tests

### Learning Resources

- **Microsoft Learn — Hybrid search (Azure AI Search):** use for the
  query pattern.

------------------------------------------------------------------------

## Issue 9.5 — Story: Permission-aware retrieval

**Type:** Story
**Feature:** Permission-Aware Retrieval
**Story Points:** 5
**Priority:** High
**Milestone:** Month 5 — Generative AI, RAG and Agents
**Labels:** `story`, `rag`, `security`, `azure`, `python`
**Suggested branch:** `feat/permission-aware-retrieval`
**Suggested PR title:** `feat(rag): permission-aware retrieval filtered by Dataverse roles`

### User Story

As a learner, I want retrieval filtered by the caller's Dataverse role
so that users only see documents they are authorised to see.

### Goal

Retrieval that applies security filters based on the caller's Dataverse
security role, enforcing document-level boundaries. Implementation lives
here; the policy is governed by Epic 11 (11.B access boundaries).

### Business Value

The differentiating enterprise capability; makes the RAG demo
credible for regulated contexts.

### Learning Value

Security-trimmed retrieval and mapping identity to document access.

### Dependencies

- **Requires:** 9.4, Epic 3 security roles (3.5), access-tag metadata
  from 9.1
- **Blocks:** 9.Z, 11.B verification

### Tasks

- [ ] Map the caller's Dataverse role to allowed access tags
- [ ] Apply a security filter to the search query
- [ ] Enforce document-level boundaries in results
- [ ] Tests: two roles get correctly different result sets
- [ ] Document the filtering model

### SMART Acceptance Criteria

- [ ] **Specific:** Retrieval results are filtered by the caller's role.
- [ ] **Measurable:** A restricted user provably cannot retrieve a
      document an authorised user can (tested with two users).
- [ ] **Achievable:** Search filters + role mapping.
- [ ] **Relevant:** Headline enterprise capability.
- [ ] **Time-bound:** Complete within Week 3 of Month 5.

### Definition of Done

- [ ] Filtering enforced; two-user test passes; model documented; green CI

### Deliverables

- Updated `src/rag/retrieval.py` + tests
- `docs/security/permission-aware-retrieval.md`

### Learning Resources

- **Microsoft Learn — Security filters / document-level access (Azure AI
  Search):** use for security trimming.

------------------------------------------------------------------------

## Issue 9.6 — Story: Citations and grounding

**Type:** Story
**Feature:** Citations & Grounding
**Story Points:** 3
**Priority:** High
**Milestone:** Month 5 — Generative AI, RAG and Agents
**Labels:** `story`, `rag`, `ai`, `python`
**Suggested branch:** `feat/rag-citations`
**Suggested PR title:** `feat(rag): grounded generation with source citations`

### User Story

As a learner, I want generated answers to cite their sources so that
answers are verifiable and trustworthy.

### Goal

A generation step that produces answers grounded in retrieved chunks,
each answer carrying source citations.

### Dependencies

- **Requires:** 9.4 (retrieval), 8.1 (generation)
- **Blocks:** 9.Z

### Tasks

- [ ] Pass retrieved chunks as grounding context
- [ ] Prompt the model to cite sources it used
- [ ] Return structured citations (source, chunk id)
- [ ] Tests verifying citations map to retrieved chunks
- [ ] Document the citation format

### SMART Acceptance Criteria

- [ ] **Specific:** Answers include citations to retrieved sources.
- [ ] **Measurable:** For a seeded question, ≥ 1 citation resolves to a
      retrieved chunk (tested).
- [ ] **Achievable:** Prompting + structured output.
- [ ] **Relevant:** Trust and verifiability.
- [ ] **Time-bound:** Complete within Week 3 of Month 5.

### Definition of Done

- [ ] Cited answers produced; tests pass; format documented

### Deliverables

- `src/rag/generation.py` + tests

### Learning Resources

- **Microsoft Learn — Grounding and citations in RAG:** use for the
  citation pattern.

------------------------------------------------------------------------

## Issue 9.7 — Story: RAG evaluation

**Type:** Story
**Feature:** RAG Evaluation
**Story Points:** 3
**Priority:** Medium
**Milestone:** Month 5 — Generative AI, RAG and Agents
**Labels:** `story`, `rag`, `python`, `governance`
**Suggested branch:** `feat/rag-evaluation`
**Suggested PR title:** `feat(rag): retrieval and answer quality evaluation`

### User Story

As a learner, I want to evaluate retrieval and answer quality so that RAG
performance is measured, not assumed.

### Goal

An evaluation set and metrics for retrieval (hit rate) and answer quality
(groundedness/relevance).

### Dependencies

- **Requires:** 9.6

### Tasks

- [ ] Build an evaluation set of questions with expected sources
- [ ] Measure retrieval hit rate / recall
- [ ] Measure answer groundedness/relevance (rule-based or LLM-judge)
- [ ] Report results and weaknesses
- [ ] Document the method

### SMART Acceptance Criteria

- [ ] **Specific:** Retrieval and answer metrics are produced.
- [ ] **Measurable:** ≥ 10 questions evaluated; hit rate and a quality
      score reported.
- [ ] **Achievable:** Small eval set.
- [ ] **Relevant:** Quality evidence.
- [ ] **Time-bound:** Complete within Week 4 of Month 5.

### Definition of Done

- [ ] Evaluation + results + method doc merged

### Deliverables

- `src/rag/evaluation/` + results note

### Learning Resources

- **Microsoft Learn — Evaluate RAG / generative AI (Azure AI):** use for
  metrics.

------------------------------------------------------------------------
# EPIC 10 — AI AGENTS (building blocks)
------------------------------------------------------------------------

## Issue 10.1 — Spike: Choose the agent orchestration framework

**Type:** Spike
**Feature:** Agent Orchestration Framework
**Story Points:** 2
**Priority:** High
**Milestone:** Month 5 — Generative AI, RAG and Agents
**Labels:** `spike`, `agent`, `architecture`, `documentation`
**Suggested branch:** `spike/agent-framework-adr`
**Suggested PR title:** `docs(adr): ADR-0007 agent orchestration framework selection`

### Goal

Decide and record the agent orchestration framework (Semantic Kernel /
AutoGen / custom) before building agents.

### Business Value

Prevents building four agents against a framework you later abandon.

### Learning Value

Comparative evaluation of agent frameworks against project needs.

### Dependencies

- **Requires:** 8.4 tool layer understanding
- **Blocks:** 10.2, 10.Z

### Tasks

- [ ] Compare Semantic Kernel, AutoGen and a custom loop against
      criteria (tool reuse with 8.4, approval hooks, telemetry, learning
      curve)
- [ ] Build a tiny proof (single agent calling one tool)
- [ ] Decide and record ADR-0007
- [ ] Note implications for 10.2–10.Z

### SMART Acceptance Criteria

- [ ] **Specific:** ADR-0007 names one framework with rationale.
- [ ] **Measurable:** A minimal single-agent proof runs; ADR accepted.
- [ ] **Achievable:** Time-boxed (≤ 1 day).
- [ ] **Relevant:** Unblocks the agent build.
- [ ] **Time-bound:** Complete within Week 1 of Month 5.

### Definition of Done

- [ ] ADR-0007 merged; proof committed or discarded with notes

### Deliverables

- `docs/decisions/ADR-0007-agent-framework.md`

### Learning Resources

- **Microsoft Learn — Semantic Kernel overview:** use when evaluating
  the Microsoft-aligned option.
- **AutoGen documentation:** use when evaluating AutoGen.

------------------------------------------------------------------------

## Issue 10.2 — Story: Build the four core agents

**Type:** Story
**Feature:** Core Agents
**Story Points:** 8
**Priority:** High
**Milestone:** Month 5 — Generative AI, RAG and Agents
**Labels:** `story`, `agent`, `ai`, `python`
**Suggested branch:** `feat/core-agents`
**Suggested PR title:** `feat(agents): planner, researcher, reviewer and reporter agents`

### User Story

As a learner, I want the four role agents built so that the orchestration
story (10.Z) has real components to assemble.

### Goal

Planner, Researcher, Reviewer and Reporter agents on the chosen
framework, each individually testable.

### Dependencies

- **Requires:** 10.1 ADR, 8.4 tool layer
- **Blocks:** 10.Z

### Tasks

- [ ] Implement the Planner (goal → plan)
- [ ] Implement the Researcher (uses tools / RAG)
- [ ] Implement the Reviewer (checks outputs)
- [ ] Implement the Reporter (produces a report)
- [ ] Unit tests per agent with mocked model/tools
- [ ] Document each agent's contract

### SMART Acceptance Criteria

- [ ] **Specific:** Four agents exist, each with a defined input/output.
- [ ] **Measurable:** Each agent has passing unit tests in isolation.
- [ ] **Achievable:** On the 10.1 framework.
- [ ] **Relevant:** Building blocks for 10.Z.
- [ ] **Time-bound:** Complete within Week 2 of Month 5.

### Definition of Done

- [ ] Four agents + tests merged; contracts documented; green CI

### Deliverables

- `src/agents/{planner,researcher,reviewer,reporter}.py` + tests

### Learning Resources

- **Microsoft Learn — Semantic Kernel agents** (or chosen framework):
  use for the agent abstractions.

------------------------------------------------------------------------

## Issue 10.3 — Story: Tool registry

**Type:** Story
**Feature:** Tool Registry
**Story Points:** 3
**Priority:** High
**Milestone:** Month 5 — Generative AI, RAG and Agents
**Labels:** `story`, `agent`, `python`, `architecture`
**Suggested branch:** `feat/tool-registry`
**Suggested PR title:** `feat(agents): tool registry reusing the Epic 8 tool layer`

### User Story

As a learner, I want a tool registry so that agents discover and invoke
tools consistently, reusing the Epic 8 function-calling layer.

### Goal

A registry that exposes the 8.4 tools (plus RAG) to agents with metadata
and allow-listing hooks.

### Dependencies

- **Requires:** 8.4 tool layer, 9.Z RAG assistant
- **Blocks:** 10.Z, 10.6 guardrails

### Tasks

- [ ] Define registry entries (name, schema, handler, allow-list flag)
- [ ] Register the Epic 8 tools and the RAG assistant
- [ ] Provide lookup/dispatch for agents
- [ ] Tests for registration and dispatch
- [ ] Document how to add a tool

### SMART Acceptance Criteria

- [ ] **Specific:** A registry exposes tools to agents.
- [ ] **Measurable:** An agent invokes a registered tool via the registry
      (tested).
- [ ] **Achievable:** Wraps 8.4.
- [ ] **Relevant:** Central to orchestration and guardrails.
- [ ] **Time-bound:** Complete within Week 2 of Month 5.

### Definition of Done

- [ ] Registry + tests merged; extension documented; green CI

### Deliverables

- `src/agents/registry.py` + tests

### Learning Resources

- **Microsoft Learn — Semantic Kernel plugins/functions** (or chosen
  framework): use for tool registration patterns.

------------------------------------------------------------------------

## Issue 10.4 — Story: Human-in-the-loop approval workflow

**Type:** Story
**Feature:** Human-in-the-Loop / Approval
**Story Points:** 3
**Priority:** High
**Milestone:** Month 5 — Generative AI, RAG and Agents
**Labels:** `story`, `agent`, `python`, `governance`
**Suggested branch:** `feat/agent-approval`
**Suggested PR title:** `feat(agents): approval gate for write/irreversible actions`

### User Story

As a learner, I want an approval gate so that agents cannot perform
write or irreversible actions without explicit human sign-off.

### Goal

An approval mechanism that pauses before flagged actions and requires
confirmation to proceed.

### Dependencies

- **Requires:** 10.3 registry
- **Blocks:** 10.Z

### Tasks

- [ ] Flag tools/actions that require approval
- [ ] Pause execution and surface the pending action
- [ ] Proceed only on explicit approval; otherwise abort cleanly
- [ ] Tests: a write action is blocked without approval
- [ ] Document the approval flow

### SMART Acceptance Criteria

- [ ] **Specific:** Flagged actions require approval before executing.
- [ ] **Measurable:** A write action is blocked pending approval and
      proceeds only after it (tested).
- [ ] **Achievable:** Registry hook + gate.
- [ ] **Relevant:** Core agent safety.
- [ ] **Time-bound:** Complete within Week 3 of Month 5.

### Definition of Done

- [ ] Approval gate + tests merged; flow documented

### Deliverables

- `src/agents/approval.py` + tests

### Learning Resources

- **Microsoft Learn — Responsible AI / human oversight patterns:** use
  for the approval rationale.

------------------------------------------------------------------------

## Issue 10.5 — Story: Agent telemetry and tracing

**Type:** Story
**Feature:** Agent Telemetry & Tracing
**Story Points:** 3
**Priority:** Medium
**Milestone:** Month 5 — Generative AI, RAG and Agents
**Labels:** `story`, `agent`, `azure`, `observability`
**Suggested branch:** `feat/agent-telemetry`
**Suggested PR title:** `feat(agents): per-step telemetry and tracing`

### User Story

As a learner, I want per-step agent telemetry so that a workflow run is
observable and debuggable — and later consolidated by Epic 11 (11.D).

### Goal

Structured traces for each agent step (inputs, tool calls, outputs,
timing) emitted to Application Insights.

### Dependencies

- **Requires:** 10.2 agents
- **Consolidated by:** 11.D

### Tasks

- [ ] Emit a trace per agent step (start/end, tool used, tokens, timing)
- [ ] Correlate steps under one run id
- [ ] Send to Application Insights
- [ ] Tests verifying traces are emitted
- [ ] Document the telemetry schema (aligns with 11.D standard)

### SMART Acceptance Criteria

- [ ] **Specific:** Each agent step emits a correlated trace.
- [ ] **Measurable:** A run produces traces for every step under one run
      id (verified).
- [ ] **Achievable:** App Insights bindings.
- [ ] **Relevant:** Observability for agents.
- [ ] **Time-bound:** Complete within Week 3 of Month 5.

### Definition of Done

- [ ] Telemetry emitted and correlated; tests pass; schema documented

### Deliverables

- Telemetry in `src/agents/` + schema note

### Learning Resources

- **Microsoft Learn — Application Insights custom telemetry:** use for
  traces/metrics.

------------------------------------------------------------------------

## Issue 10.6 — Story: Agent safety and guardrails

**Type:** Story
**Feature:** Agent Safety & Guardrails
**Story Points:** 3
**Priority:** High
**Milestone:** Month 5 — Generative AI, RAG and Agents
**Labels:** `story`, `agent`, `security`, `python`
**Suggested branch:** `feat/agent-guardrails`
**Suggested PR title:** `feat(agents): tool allow-lists and injection resistance`

### User Story

As a learner, I want tool allow-lists and injection resistance so that
agents cannot be steered into unauthorised tool use — verified later by
Epic 11 (11.F).

### Goal

Per-agent tool allow-lists enforced by the registry, plus basic
prompt-injection resistance in agent inputs.

### Dependencies

- **Requires:** 10.3 registry
- **Verified by:** 11.F prompt-injection suite

### Tasks

- [ ] Enforce per-agent tool allow-lists in the registry
- [ ] Sanitise / constrain untrusted inputs to agents
- [ ] Reject tool calls outside the allow-list
- [ ] Tests: an off-list tool call is refused; a basic injection is
      resisted
- [ ] Document the guardrails (link to Epic 11)

### SMART Acceptance Criteria

- [ ] **Specific:** Agents can only call allow-listed tools.
- [ ] **Measurable:** An off-list tool call is refused and a basic
      injection attempt does not escalate tool access (tested).
- [ ] **Achievable:** Registry enforcement + input handling.
- [ ] **Relevant:** Core agent safety.
- [ ] **Time-bound:** Complete within Week 4 of Month 5.

### Definition of Done

- [ ] Allow-lists enforced; injection tests pass; guardrails documented

### Deliverables

- Guardrail enforcement in `src/agents/` + tests

### Learning Resources

- **OWASP — Top 10 for LLM Applications:** use for injection and tool
  misuse risks.



========================================================================


# GitHub Issue Drafts (Tier 9: Epic 11 remainder & Epic 12 Capstone)

> Full-spec, copy-paste-ready issues for the three Epic 11 stories not
> covered in Tier 3 (threat modelling, prompt-injection testing, cost
> monitoring) and all of Epic 12. All Month 6. Epic 11's audit-logging
> (11.A), responsible AI (11.B), secrets (11.C) and observability (11.D)
> live in Tier 3; the IaC ADR spike lives in Tier 1.

------------------------------------------------------------------------
# EPIC 11 — SECURITY & GOVERNANCE (remaining)
------------------------------------------------------------------------

## Issue 11.E — Story: Threat model the end-to-end solution

**Type:** Story
**Feature:** Threat Modelling
**Story Points:** 5
**Priority:** High
**Milestone:** Month 6 — Governance, Deployment and Portfolio
**Labels:** `story`, `security`, `governance`, `architecture`
**Suggested branch:** `feat/threat-model`
**Suggested PR title:** `docs(security): STRIDE threat model of the end-to-end solution`

### User Story

As a learner, I want a documented threat model so that the solution's
security posture is analysed, not assumed — a strong architect signal.

### Goal

A STRIDE (or equivalent) threat model covering ingestion, Dataverse,
the LLM features, RAG, agents and Azure hosting, with mitigations.

### Business Value

Demonstrates security-architect thinking; surfaces risks before
deployment.

### Learning Value

Threat modelling methodology and trust-boundary analysis.

### Dependencies

- **Requires:** the architecture is largely defined (Epics 3–10)
- **Feeds:** 11.B responsible AI, 11.F injection tests

### Tasks

- [ ] Draw the solution data-flow with trust boundaries
- [ ] Apply STRIDE per component
- [ ] Record threats, likelihood/impact and mitigations (existing or
      planned)
- [ ] Raise follow-up issues for unmitigated high risks
- [ ] Document the model

### SMART Acceptance Criteria

- [ ] **Specific:** A STRIDE model covers all major components and trust
      boundaries.
- [ ] **Measurable:** ≥ 10 threats documented, each with a mitigation or
      a linked follow-up.
- [ ] **Achievable:** Analysis + documentation.
- [ ] **Relevant:** Core governance/portfolio piece.
- [ ] **Time-bound:** Complete within Week 1 of Month 6.

### Definition of Done

- [ ] Threat model merged; follow-ups raised for high risks

### Deliverables

- `docs/security/threat-model.md` + data-flow diagram

### Learning Resources

- **Microsoft — Threat modelling / STRIDE guidance:** use as the method.
- **OWASP — Top 10 for LLM Applications:** use for LLM-specific threats.

------------------------------------------------------------------------

## Issue 11.F — Story: Prompt-injection test suite

**Type:** Story
**Feature:** LLM Security / Prompt Injection Testing
**Story Points:** 5
**Priority:** High
**Milestone:** Month 6 — Governance, Deployment and Portfolio
**Labels:** `story`, `security`, `ai`, `agent`, `python`
**Suggested branch:** `feat/prompt-injection-tests`
**Suggested PR title:** `test(security): prompt-injection suite against assistant and agents`

### User Story

As a learner, I want an automated prompt-injection suite so that the
assistant and agents are proven resistant to common attacks.

### Goal

A test suite of injection attempts against the assistant (8.6–8.8) and
agents (10.x), verifying guardrails and allow-lists hold.

### Dependencies

- **Requires:** 8.6–8.8 assistant, 10.6 guardrails
- **Verifies:** 10.6 allow-lists

### Tasks

- [ ] Assemble a catalogue of injection patterns (ignore-instructions,
      tool-coercion, data-exfiltration, role-override)
- [ ] Run them against the assistant and agents
- [ ] Assert guardrails/allow-lists hold and no unauthorised tool runs
- [ ] Record any bypasses and raise follow-ups
- [ ] Document the suite and results

### SMART Acceptance Criteria

- [ ] **Specific:** An automated suite exercises injection patterns
      against assistant and agents.
- [ ] **Measurable:** ≥ 10 attack cases run; each asserts a guardrail
      holds or logs a tracked bypass.
- [ ] **Achievable:** pytest + the existing surfaces.
- [ ] **Relevant:** LLM security evidence.
- [ ] **Time-bound:** Complete within Week 2 of Month 6.

### Definition of Done

- [ ] Suite merged and green (or bypasses tracked); results documented

### Deliverables

- `tests/security/test_prompt_injection.py`
- `docs/security/prompt-injection-results.md`

### Learning Resources

- **OWASP — Top 10 for LLM Applications (prompt injection):** use for
  attack patterns.

------------------------------------------------------------------------

## Issue 11.G — Story: Cost monitoring and spend dashboard

**Type:** Story
**Feature:** Cost Monitoring
**Story Points:** 3
**Priority:** Medium
**Milestone:** Month 6 — Governance, Deployment and Portfolio
**Labels:** `story`, `azure`, `governance`, `observability`
**Suggested branch:** `feat/cost-monitoring`
**Suggested PR title:** `feat(governance): cost alerts and spend dashboard for Azure AI services`

### User Story

As a learner, I want cost alerts and a spend dashboard so that Azure
OpenAI, Search and Functions usage stays visible and bounded.

### Goal

Budget alerts and a cost dashboard covering the main paid services.

### Dependencies

- **Requires:** Azure services deployed

### Tasks

- [ ] Configure a budget with alert thresholds
- [ ] Build a cost view/dashboard for OpenAI, Search, Functions
- [ ] Document expected cost drivers and how to reduce them
- [ ] Verify an alert fires at a low test threshold

### SMART Acceptance Criteria

- [ ] **Specific:** Budget alerts and a spend view exist for the paid
      services.
- [ ] **Measurable:** A low test threshold triggers an alert; the
      dashboard shows per-service spend.
- [ ] **Achievable:** Azure Cost Management.
- [ ] **Relevant:** Operational governance.
- [ ] **Time-bound:** Complete within Week 2 of Month 6.

### Definition of Done

- [ ] Alerts + dashboard live; cost drivers documented

### Deliverables

- Cost alerts + dashboard
- `docs/architecture/cost-monitoring.md`

### Learning Resources

- **Microsoft Learn — Azure Cost Management budgets and alerts:** use
  for setup.

------------------------------------------------------------------------
# EPIC 12 — CAPSTONE
------------------------------------------------------------------------

## Issue 12.1 — Story: Ingestion + analytics visible in the app

**Type:** Story
**Feature:** End-to-End Integration
**Story Points:** 5
**Priority:** High
**Milestone:** Month 6 — Governance, Deployment and Portfolio
**Labels:** `story`, `dynamics`, `dataverse`, `portfolio`
**Suggested branch:** `feat/capstone-ingestion-analytics`
**Suggested PR title:** `feat(capstone): surface ingested data and analytics in the app`

### User Story

As a learner, I want ingested OpenF1 data and FastF1 summaries visible in
the model-driven app so that the pipeline's output is demonstrable.

### Goal

Ingested data and published summaries surfaced through app views/forms.

### Dependencies

- **Requires:** Epic 4 persistence, 5.5 summaries, Epic 3 app (3.4)

### Tasks

- [ ] Confirm ingested + summary data lands in the right tables
- [ ] Add/adjust app views and forms to surface it
- [ ] Verify end-to-end from ingestion run to app display
- [ ] Capture screenshots for the portfolio
- [ ] Document the flow

### SMART Acceptance Criteria

- [ ] **Specific:** Ingested data and summaries appear in the app.
- [ ] **Measurable:** After an ingestion run, the new data is visible in
      app views; screenshots captured.
- [ ] **Achievable:** Reuses existing tables/app.
- [ ] **Relevant:** Demonstrable integration slice.
- [ ] **Time-bound:** Complete within Week 1 of Month 6.

### Definition of Done

- [ ] Data visible in the app; screenshots + flow doc merged

### Deliverables

- App view/form updates + screenshots + flow note

### Learning Resources

- **Microsoft Learn — Model-driven app views:** use for surfacing data.

------------------------------------------------------------------------

## Issue 12.2 — Story: RAG assistant wired into the front end

**Type:** Story
**Feature:** End-to-End Integration
**Story Points:** 5
**Priority:** High
**Milestone:** Month 6 — Governance, Deployment and Portfolio
**Labels:** `story`, `rag`, `dynamics`, `portfolio`, `security`
**Suggested branch:** `feat/capstone-rag-frontend`
**Suggested PR title:** `feat(capstone): expose the RAG assistant from the app`

### User Story

As a learner, I want the RAG assistant reachable from the app so that
users get grounded, permission-aware answers in context.

### Goal

The Epic 9 assistant (9.Z) exposed from the app or a linked surface,
respecting the caller's role.

### Dependencies

- **Requires:** 9.Z RAG assistant, app (3.4), permission-aware retrieval
  (9.5)

### Tasks

- [ ] Expose the assistant via an HTTP endpoint (Functions)
- [ ] Surface it from the app or a linked page
- [ ] Pass the caller's identity/role for filtering
- [ ] Verify grounded, cited, role-appropriate answers in context
- [ ] Screenshots + docs

### SMART Acceptance Criteria

- [ ] **Specific:** The assistant is callable from the app front end.
- [ ] **Measurable:** A question returns a cited answer; two users see
      role-appropriate results.
- [ ] **Achievable:** Reuses 9.Z + Functions.
- [ ] **Relevant:** Headline integration.
- [ ] **Time-bound:** Complete within Week 1 of Month 6.

### Definition of Done

- [ ] Assistant reachable from the app; role filtering verified;
      documented

### Deliverables

- Front-end integration + endpoint + screenshots

### Learning Resources

- **Microsoft Learn — Embed/extend model-driven apps:** use for the
  surface.

------------------------------------------------------------------------

## Issue 12.3 — Story: Agent workflow triggerable end-to-end

**Type:** Story
**Feature:** End-to-End Integration
**Story Points:** 5
**Priority:** Medium
**Milestone:** Month 6 — Governance, Deployment and Portfolio
**Labels:** `story`, `agent`, `dynamics`, `portfolio`, `governance`
**Suggested branch:** `feat/capstone-agent-trigger`
**Suggested PR title:** `feat(capstone): trigger the multi-agent workflow from a user action`

### User Story

As a learner, I want to trigger the multi-agent workflow from the app so
that the agentic capability is demonstrable end to end.

### Goal

A user action triggers the Epic 10 workflow (10.Z) and its report output
is viewable, with the approval gate intact.

### Dependencies

- **Requires:** 10.Z workflow, app (3.4)

### Tasks

- [ ] Expose the workflow via an endpoint
- [ ] Trigger it from a user action in/near the app
- [ ] Surface the produced report
- [ ] Verify the approval gate blocks writes until approved
- [ ] Screenshots + docs

### SMART Acceptance Criteria

- [ ] **Specific:** A user action runs the workflow and shows a report.
- [ ] **Measurable:** A sample goal yields a report; a write is blocked
      pending approval.
- [ ] **Achievable:** Reuses 10.Z.
- [ ] **Relevant:** Demonstrable agentic slice.
- [ ] **Time-bound:** Complete within Week 2 of Month 6.

### Definition of Done

- [ ] Workflow triggerable; report visible; approval verified; documented

### Deliverables

- Trigger integration + endpoint + screenshots

### Learning Resources

- **Microsoft Learn — Azure Functions HTTP trigger:** use for the
  endpoint.

------------------------------------------------------------------------

## Issue 12.4 — Story: AI request/response logging visible in Dataverse

**Type:** Story
**Feature:** End-to-End Integration
**Story Points:** 3
**Priority:** Medium
**Milestone:** Month 6 — Governance, Deployment and Portfolio
**Labels:** `story`, `dataverse`, `ai`, `governance`, `portfolio`
**Suggested branch:** `feat/capstone-ai-logging-visible`
**Suggested PR title:** `feat(capstone): surface AI request/response logs and audit links`

### User Story

As a learner, I want AI interactions visible in Dataverse so that the
governance story is demonstrable, not just implemented.

### Goal

AI Request / AI Response records surfaced in the app and linked to the
audit trail.

### Dependencies

- **Requires:** 8.9 logging, app (3.4), auditing (3.6)

### Tasks

- [ ] Add app views for AI Request / AI Response
- [ ] Show the link between AI interactions and audit entries
- [ ] Verify a live interaction appears with its audit link
- [ ] Screenshots + docs

### SMART Acceptance Criteria

- [ ] **Specific:** AI logs are viewable in the app with audit links.
- [ ] **Measurable:** A live interaction produces a visible, audit-linked
      record.
- [ ] **Achievable:** Views over existing tables.
- [ ] **Relevant:** Governance demonstrability.
- [ ] **Time-bound:** Complete within Week 2 of Month 6.

### Definition of Done

- [ ] Logs visible and audit-linked; screenshots + doc merged

### Deliverables

- App views + screenshots + note

### Learning Resources

- **Microsoft Learn — Dataverse auditing:** use for the audit linkage.

------------------------------------------------------------------------

## Issue 12.5 — Story: Author Infrastructure as Code for all Azure resources

**Type:** Story
**Feature:** Azure Deployment & Infrastructure as Code
**Story Points:** 8
**Priority:** High
**Milestone:** Month 6 — Governance, Deployment and Portfolio
**Labels:** `story`, `azure`, `architecture`
**Suggested branch:** `feat/iac-all-resources`
**Suggested PR title:** `feat(iac): parameterised IaC for all Azure resources`

### User Story

As a learner, I want all Azure resources defined as code so that the
environment is reproducible and the portfolio shows IaC discipline.

### Goal

IaC (in the tool chosen by ADR-0002, Tier-1) provisioning Functions,
Azure OpenAI, AI Search, Key Vault, Application Insights and storage,
parameterised per environment.

### Dependencies

- **Requires:** ADR-0002 (Tier-1 IaC spike); resources understood from
  Epics 4/8/9
- **Blocks:** 12.6 deployment CI

### Tasks

- [ ] Author IaC for each Azure resource
- [ ] Parameterise per environment (dev/prod)
- [ ] Wire Key Vault + Managed Identity references (11.C)
- [ ] Validate a clean deploy to a dev environment
- [ ] Document the IaC and parameters

### SMART Acceptance Criteria

- [ ] **Specific:** IaC provisions all required Azure resources.
- [ ] **Measurable:** A clean dev deploy stands up the full environment
      from code; parameters switch environments.
- [ ] **Achievable:** Single IaC tool (ADR-0002).
- [ ] **Relevant:** Reproducibility + portfolio signal.
- [ ] **Time-bound:** Complete within Week 3 of Month 6.

### Definition of Done

- [ ] Dev environment deploys cleanly from IaC; documented; no secrets in
      source

### Deliverables

- `infrastructure/<chosen-tool>/` templates + parameters
- `docs/architecture/infrastructure.md`

### Learning Resources

- **Microsoft Learn — Bicep** (or Terraform azurerm, per ADR-0002): use
  for authoring the templates.

------------------------------------------------------------------------

## Issue 12.6 — Story: Deployment CI/CD

**Type:** Story
**Feature:** Deployment CI/CD
**Story Points:** 5
**Priority:** High
**Milestone:** Month 6 — Governance, Deployment and Portfolio
**Labels:** `story`, `azure`, `architecture`
**Suggested branch:** `feat/deployment-cicd`
**Suggested PR title:** `ci: deployment workflow for infrastructure and application`

### User Story

As a learner, I want a deployment pipeline so that infra and app promote
to Azure automatically and repeatably — distinct from the build CI.

### Goal

A GitHub Actions workflow that deploys the IaC and the application, with
environment promotion.

### Dependencies

- **Requires:** 12.5 IaC, Tier-1 build CI
- **Distinct from:** Epic 1 build CI

### Tasks

- [ ] Author a deploy workflow (infra then app)
- [ ] Authenticate to Azure via OIDC / federated credentials (no stored
      secrets)
- [ ] Add environment promotion (dev → prod) with a gate
- [ ] Run a full deploy to dev via the pipeline
- [ ] Document the pipeline

### SMART Acceptance Criteria

- [ ] **Specific:** A pipeline deploys infra and app to an environment.
- [ ] **Measurable:** A pipeline run stands up dev end to end; promotion
      to prod is gated.
- [ ] **Achievable:** GitHub Actions + Azure login (OIDC).
- [ ] **Relevant:** Deployment automation.
- [ ] **Time-bound:** Complete within Week 3 of Month 6.

### Definition of Done

- [ ] Deploy pipeline green to dev; promotion gate in place; documented;
      no stored cloud secrets

### Deliverables

- `.github/workflows/deploy.yml`
- `docs/architecture/deployment.md`

### Learning Resources

- **GitHub Docs — Deploying to Azure / OIDC login:** use for
  secretless auth.
- **Microsoft Learn — Deploy Bicep/Terraform with GitHub Actions:** use
  for the deploy steps.

------------------------------------------------------------------------

## Issue 12.7 — Story: Architecture documentation pack

**Type:** Story
**Feature:** Architecture Documentation Pack
**Story Points:** 5
**Priority:** High
**Milestone:** Month 6 — Governance, Deployment and Portfolio
**Labels:** `story`, `documentation`, `architecture`, `portfolio`
**Suggested branch:** `feat/architecture-docs`
**Suggested PR title:** `docs(architecture): consolidated architecture pack with diagrams`

### User Story

As a learner, I want a consolidated architecture pack so that a reviewer
can understand the whole solution quickly — the portfolio centrepiece.

### Goal

A cohesive architecture document set with context/container/component
views (Mermaid), key flows, and an ADR index.

### Dependencies

- **Requires:** most epics complete
- **Consumes:** all prior ADRs and per-feature docs

### Tasks

- [ ] Write a solution overview (context and containers)
- [ ] Diagram key flows (ingestion, RAG, agents) in Mermaid
- [ ] Compile an ADR index (0001–0007)
- [ ] Summarise security, governance and cost posture
- [ ] Cross-link the per-feature docs

### SMART Acceptance Criteria

- [ ] **Specific:** An architecture pack with diagrams and an ADR index
      exists.
- [ ] **Measurable:** ≥ 3 Mermaid diagrams render; every ADR is indexed;
      a reviewer can trace each capability to a doc.
- [ ] **Achievable:** Documentation consolidation.
- [ ] **Relevant:** Portfolio centrepiece.
- [ ] **Time-bound:** Complete within Week 4 of Month 6.

### Definition of Done

- [ ] Pack merged; diagrams render; ADR index complete

### Deliverables

- `docs/architecture/overview.md` + diagrams + ADR index

### Learning Resources

- **Azure Architecture Center:** use for diagram conventions and
  reference patterns.
- **Mermaid documentation:** use for the diagrams.

------------------------------------------------------------------------

## Issue 12.8 — Story: Demo walkthrough and portfolio packaging

**Type:** Story
**Feature:** Demo Walkthrough & Portfolio Packaging
**Story Points:** 3
**Priority:** High
**Milestone:** Month 6 — Governance, Deployment and Portfolio
**Labels:** `story`, `documentation`, `portfolio`
**Suggested branch:** `feat/demo-portfolio`
**Suggested PR title:** `docs(portfolio): demo walkthrough and portfolio packaging`

### User Story

As a learner, I want a demo walkthrough and packaged portfolio so that
the six-month project reads as a credible, hireable body of work.

### Goal

A scripted demo (with a recording or annotated screenshots) and a
`/portfolio` package summarising outcomes, skills and links.

### Dependencies

- **Requires:** 12.1–12.7

### Tasks

- [ ] Script an end-to-end demo (ingestion → analytics → RAG → agents →
      governance)
- [ ] Record it or capture annotated screenshots
- [ ] Write a portfolio summary (capabilities, skills, architecture, ADRs)
- [ ] Link everything from the README
- [ ] Package under `/portfolio`

### SMART Acceptance Criteria

- [ ] **Specific:** A demo walkthrough and portfolio package exist.
- [ ] **Measurable:** The walkthrough covers all headline capabilities;
      the README links to the portfolio, architecture and demo.
- [ ] **Achievable:** Documentation + capture.
- [ ] **Relevant:** The hireability payload.
- [ ] **Time-bound:** Complete within Week 4 of Month 6.

### Definition of Done

- [ ] Demo + portfolio merged and linked from README

### Deliverables

- `portfolio/` package + demo assets
- README portfolio section

### Learning Resources

- **GitHub Docs — About READMEs / GitHub Pages:** use for presenting the
  portfolio publicly.
