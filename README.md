# dynamics-ai-intelligence-hub

[![CI](https://github.com/synchsys/dynamics-ai-intelligence-hub/actions/workflows/ci.yml/badge.svg)](https://github.com/synchsys/dynamics-ai-intelligence-hub/actions/workflows/ci.yml)
[![coverage gate: 80%](https://img.shields.io/badge/coverage%20gate-80%25-brightgreen)](#running-checks-locally)
[![python: 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](pyproject.toml)

Portfolio-grade reference implementation for an AI & ML Solution Architect
transition: professional Python, Azure AI + Azure Functions, Dynamics 365 &
Dataverse, a client-agnostic CRM domain model, REST integration (OpenF1/FastF1),
Pandas data engineering, ML, RAG, AI agents, and security/governance/observability.

The backlog lives in GitHub Issues and the linked Project (Epic → Feature →
Story → Task). See `CLAUDE.md` for the target architecture and conventions.

## Prerequisites

- **Python 3.12+** (`python3.12 --version`)
- **Git** and a GitHub account
- Recommended: VS Code with the extensions in `.vscode/extensions.json`

## Environment setup

```bash
# 1. Create and activate a virtual environment (Python 3.12+)
python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Upgrade pip and install the project with dev tooling
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Dependency management uses **pip + `pyproject.toml`** (editable install). Runtime
dependencies live under `[project.dependencies]`; the lint/format/type/test
toolchain lives under the `dev` optional-dependency group. The ML & data pillar
(FastF1, pandas, …) lives under the **`analytics`** extra — install it with
`pip install -e ".[dev,analytics]"` (this is what CI installs). FastF1 caches
telemetry to `datasets/fastf1-cache/` (git-ignored) so sessions load fast and
reproducibly on repeat runs.

## Running checks locally

These are the exact gates [CI](.github/workflows/ci.yml) runs on every push and
pull request — run them before pushing:

```bash
ruff check .              # lint (pycodestyle, pyflakes, isort, pyupgrade, bugbear, simplify)
black --check .           # formatting
mypy src tests            # static types (strict)
pytest                    # tests (fast; editor-friendly, no coverage)
pytest --cov=src --cov-report=term-missing --cov-fail-under=80   # tests + coverage gate
```

Coverage is intentionally kept out of pytest's `addopts` so VS Code's Test
Explorer and debugger work; run the `--cov` command explicitly. The gate is 80%,
but the practice in this repo is **100% coverage on new `src/` code** — SDKs,
gateways and loggers are injected so units test hermetically without network or
credentials. Each capability also has a live smoke test under `scripts/**/verify_*.py`
that runs against the real Azure services and cleans up after itself.

## Project layout

```
src/            # source packages (src-layout, importable after editable install)
  shared/       # config, logging, exceptions, resilience
  api/          # reusable REST client
  dataverse/    # Dataverse Web API client
  openf1/       # OpenF1 ingestion
  ai/           # Azure OpenAI: client, prompts, structured outputs, tool layer, CRM assistant
  rag/          # retrieval-augmented generation (ingest → retrieve → cited answers)
  agents/       # multi-agent orchestration (planner → researcher → reviewer → reporter)
  paddock/      # Paddock Club predictions game (odds, settlement, LLM intake)
  fastf1_analytics/   # placeholder — not yet implemented
  azure_functions/    # placeholder — not yet implemented
tests/          # mirrors src/
scripts/        # live verify_*.py smoke tests + Dataverse schema tooling
docs/           # architecture, decisions (ADRs), learning, security
infrastructure/ # bicep, terraform, environments
notebooks/  datasets/  portfolio/
```

## Shared utilities (`src/shared`)

Cross-cutting primitives imported by every later module — a single place for
configuration, logging and errors (resilience/retry arrives in story #23).

**Configuration** — typed, environment-driven settings (`HUB_` prefix;
precedence: environment > `.env` > typed defaults). Invalid values raise
`ConfigError`.

```python
from shared import get_settings

settings = get_settings()          # cached; HUB_ENVIRONMENT, HUB_LOG_LEVEL, ...
if settings.environment == "prod":
    ...
```

**Structured logging** — JSON-friendly records with a context-bound
correlation id that flows across async/Functions calls.

```python
from shared import bind_correlation_id, configure_logging, get_logger

configure_logging(level=get_settings().log_level, json_output=True)
bind_correlation_id()              # or pass an id from an inbound request
log = get_logger(__name__)
log.info("processing request")     # -> {"level": "INFO", ..., "correlation_id": "..."}
```

**Exceptions** — catch the base `SharedError`; downstream clients subclass
`ExternalServiceError`, `ValidationError`, `ConfigError`.

```python
from shared import SharedError

try:
    ...
except SharedError:
    ...
```

**Resilience** — a `retry` decorator (exponential backoff + full jitter, with a
transient/permanent predicate) and a `run_with_timeout` wrapper. Hand-rolled
(no `tenacity`) so behaviour is explicit and testable. The REST client
(story #35) and OpenF1 ingestion (story 4.2) consume these rather than
reimplementing retry/backoff. Retries and give-ups log via `shared.logging`.

```python
from shared import retry, run_with_timeout

@retry(max_attempts=3, retry_on=ConnectionError)   # only retries transient errors
def fetch() -> bytes:
    ...

result = run_with_timeout(fetch, timeout=5.0)       # caller-side deadline
```

## REST client (`src/api`)

A resilient, typed HTTP client (built on `httpx`) that consumes the `shared`
resilience + logging utilities. It adds timeouts, retry-with-backoff for
transient failures (connection errors, timeouts, `429`/`5xx`) and a typed error
model. On `429`, the server's `Retry-After` header is honoured over the default
backoff. Foundation for OpenF1 ingestion (Epic 4) and any future REST work.

```python
from api import RestClient, ApiStatusError

with RestClient("https://api.openf1.org/v1", timeout=10.0, max_attempts=3) as client:
    try:
        resp = client.get("/sessions", params={"year": 2024})
        data = resp.json()
    except ApiStatusError as err:
        # 4xx raise immediately; 429/5xx are retried first, then surface here
        print(err.status_code, err.body)
```

Errors derive from `shared.ExternalServiceError` → `ApiError` →
`ApiConnectionError` / `ApiTimeoutError` / `ApiStatusError`.

## OpenF1 ingestion client (`src/openf1`)

A typed client over the public OpenF1 API, built on the REST client above (so it
inherits timeouts, retry and logging). It is the **settlement source of truth**
for the Paddock Club predictions game (ADR-0008). Methods return raw `list[dict]`
(Pydantic validation is story 4.3). Rate limiting is handled by the REST client
(honours `Retry-After`); large imports are chunked with `collect(...)`.

```python
from openf1 import OpenF1Client

with OpenF1Client() as f1:
    results = f1.get_session_result(session_key=9158)      # settlement backbone
    grid    = f1.get_starting_grid(session_key=9158)
    laps    = f1.get_laps(session_key=9158, driver_number=1)
```

Filters are pass-through query params. A **qualifying** `session_key` uses the
same methods as a race, so qualifying markets settle on the same path. For large
imports, chunk the query on a natural key (OpenF1 returns the full array per
request — no offset paging):

```python
laps = f1.collect("laps", over="driver_number", values=[1, 44, 16], session_key=9158)
```

**Endpoint → settlement-type mapping** (Tier A, graded from OpenF1):

| Method / endpoint | Grounds |
|---|---|
| `get_session_result` | types 1–7, 11 (wins, podium, points, position, head-to-head, classified, DNF, winning margin) |
| `get_starting_grid` (+ result) | types 8–9 (beats grid, positions gained) |
| `get_laps` | type 10 (fastest lap) |
| `get_pit` | type 12 (pit stops) |
| `get_position` | odds inputs |
| `get_drivers` | driver name → number resolution |
| `get_weather` | growth type 14 (rain) |
| `get_stints` | Epic 7 tyre-strategy features |

FastF1-sourced types (13 safety-car, 15 crash) are a separate Tier-B path — see
`docs/architecture/f1-data-source-coverage.md`.

**Validation** (`openf1.models`) — lenient Pydantic models (`extra="ignore"`) for
each endpoint (`Session`, `Driver`, `Lap`, `SessionResult`, `StartingGrid`,
`Pit`, `Position`, `Stint`, `Weather`, `Meeting`). `parse_many` validates a batch
and **collects per-row failures without aborting the run** — a bad record is
logged and skipped, not fatal.

```python
from openf1 import OpenF1Client, SessionResult, parse_many

rows = OpenF1Client().get_session_result(session_key=9158)
result = parse_many(SessionResult, rows)   # -> ParseResult(valid=[...], errors=[...])
for row in result.valid:
    ...  # typed, validated
```

## Dataverse client (`src/dataverse`)

The single governed persistence layer — an authenticated Dataverse Web API
client (CRUD, upsert-by-alternate-key, `$batch`) built on the `api` REST client
(so it inherits retry/backoff/logging) with per-request bearer tokens from a
service principal. It's entity-agnostic (you pass the entity set name), so it's
imported by OpenF1 persistence, FastF1 summaries and AI logging.

```python
from dataverse import DataverseClient, DataverseConfig

with DataverseClient(DataverseConfig.from_env()) as dv:
    cid = dv.create("contacts", {"lastname": "Smith", "firstname": "Jo"})
    dv.update("contacts", cid, {"jobtitle": "Engineer"})
    people = dv.retrieve_multiple("contacts", filter="lastname eq 'Smith'")
    dv.delete("contacts", cid)
```

### Setup (required for real use)

Provision these in your tenant, then fill `.env` (copy from `.env.example`):

1. **Entra ID app registration** → client ID, tenant ID, a client secret.
2. **Dataverse environment** with a database → environment URL.
3. **Application user** in that environment, mapped to the app registration, with
   a least-privilege security role.
4. `.env`: `DATAVERSE_URL`, `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`.

Auth uses the client-credentials flow (`azure-identity`) with a clean path to
Managed Identity later — see [ADR-0003](docs/decisions/ADR-0003-dataverse-auth.md).
The integration test runs only with `RUN_DATAVERSE_INTEGRATION=1` and valid
credentials; unit tests use a mocked transport and need no environment.

## Azure OpenAI, tools and the CRM assistant (`src/ai`)

The governed LLM layer. One `AIClient` (chat + embeddings on Azure OpenAI, Entra
auth reusing the Dataverse service principal, `shared` retry/logging) underpins:
a **prompt library** (`ai.prompts`), **structured outputs** (schema-validated
JSON with bounded repair), a **function-calling tool layer** (`ai.tools` — a
tool registry + `run_tools` loop; the single tool layer agents reuse, per
[ADR-0006](docs/decisions/ADR-0006-function-calling-boundary.md)), **guarded CRM
action tools** (writes staged behind a human-approval gate), **prompt/response
logging** to Dataverse (`ai.prompt_log`), and a conversational **CRM assistant**
(`ai.assistant`).

```python
from ai import AIClient, AzureOpenAIConfig, structured_output
from ai.assistant import CrmAssistant, DataverseCrmRetriever, EntityView

client = AIClient(AzureOpenAIConfig.from_env())     # Entra by default; API-key optional
answer = client.chat([{"role": "user", "content": "Say hello"}])

# grounded, logged CRM Q&A over Dataverse (optionally RAG-backed — see below)
assistant = CrmAssistant(client, DataverseCrmRetriever(dv, [EntityView("accounts", "Accounts", ("name", "address1_city"))]))
reply = assistant.ask("Which accounts are based in Cork?")   # answers only from the data, or says it doesn't know
```

GPT-5-family models are the default (the gpt-4o generation is deprecated); they
reject an explicit `temperature`, so `chat()` omits it unless set. See
[docs/architecture/crm-assistant.md](docs/architecture/crm-assistant.md).

## Retrieval-augmented generation (`src/rag`)

A grounded, **permission-aware**, cited Q&A pipeline over Azure AI Search:
ingestion + chunking → embeddings (idempotent) → a vector + keyword index →
**hybrid retrieval** (RRF) → **role-based access trimming** → **cited generation**
(hallucinated citations dropped). The `RagAssistant` composes it into one call;
an evaluation harness measures hit rate / groundedness / relevance.

```python
from rag import RagAssistant, Retriever, KnowledgeIndex, SearchConfig

assistant = RagAssistant(Retriever(KnowledgeIndex(SearchConfig.from_env()), client), client)
result = assistant.ask("When can a driver use DRS?", roles=["employee"])
print(result.answer, [c.source for c in result.citations])   # a guest sees only public sources
```

Access control is enforced *before* ranking — a restricted caller provably
cannot retrieve (or cite) a document their role doesn't grant. See
[docs/security/permission-aware-retrieval.md](docs/security/permission-aware-retrieval.md)
and [docs/architecture/rag-assistant.md](docs/architecture/rag-assistant.md).

## Multi-agent orchestration (`src/agents`)

The four role agents — **planner → researcher → reviewer → reporter** — and a
`MultiAgentWorkflow` that drives them to a report from a goal. Built as a custom,
lightweight orchestration over the `ai` tool layer
([ADR-0007](docs/decisions/ADR-0007-agent-framework.md)), *not* a heavyweight
framework: the researcher reuses tools and the RAG assistant, writes stay behind
the human-approval gate, and every step emits telemetry.

```python
from agents import MultiAgentWorkflow, Researcher, knowledge_search_tool
from ai import build_crm_tools

tools = build_crm_tools(dv, dv)                       # read + guarded-write tools
tools.registry.register(knowledge_search_tool(rag, roles=["employee"]))   # researcher is RAG-backed
workflow = MultiAgentWorkflow(client, researcher=Researcher(registry=tools.registry), broker=tools.broker)

result = workflow.run("Explain the DRS rules and draft a follow-up task for the team")
print(result.report)                # planner→researcher→reviewer→reporter, fully traced
print(result.pending_writes)        # any write is staged, blocked pending approval
```

See [docs/architecture/agents.md](docs/architecture/agents.md) and
[docs/architecture/agent-workflow.md](docs/architecture/agent-workflow.md).

## Paddock Club predictions game (`src/paddock`)

A virtual-credit F1 predictions game (Epic 13) grounded in the OpenF1 data above.
Free-text intake maps a punter's prediction to one of 12 Tier-A settlement types
via structured output, resolves driver names, validates parameters, and prices it
with real-world fractional odds; the deterministic settlement engine grades locked
slips against ingested results and settles wallets idempotently. The LLM proposes;
**code grades deterministically** and voids rather than guesses
([ADR-0008](docs/decisions/ADR-0008-odds-settlement.md)).

```python
from paddock.intake import WagerIntakeService

intake = WagerIntakeService(client, pricer)
result = intake.intake("Sainz to win in Singapore", session_key=9165, drivers=drivers)
# -> a priced draft slip (driver_wins #55) or a guided rejection listing supported kinds
```

See [docs/architecture/settlement-registry.md](docs/architecture/settlement-registry.md).

