# dynamics-ai-intelligence-hub

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
toolchain lives under the `dev` optional-dependency group.

## Running checks locally

The same four gates the CI pipeline enforces (story #9):

```bash
ruff check .              # lint (pycodestyle, pyflakes, isort, pyupgrade, bugbear, simplify)
black --check .           # formatting
mypy src tests            # static types (strict)
pytest                    # tests (fast; editor-friendly, no coverage)
pytest --cov=src --cov-report=term-missing --cov-fail-under=80   # tests + coverage gate
```

Run all of them before pushing. Coverage is intentionally kept out of pytest's
`addopts` so VS Code's Test Explorer and debugger work; the CI pipeline
(story #9) runs the `--cov` command to enforce the 80% gate.

## Project layout

```
src/            # source packages (src-layout, importable after editable install)
  shared/       # config, logging, exceptions, resilience (built in Epic 2)
  api/          # reusable REST client
  dataverse/    # Dataverse Web API client
  openf1/       # OpenF1 ingestion
  fastf1_analytics/
  ai/           # Azure OpenAI integration, assistant
  rag/          # retrieval-augmented generation
  agents/       # multi-agent orchestration
  azure_functions/
tests/          # mirrors src/
docs/           # architecture, decisions (ADRs), diagrams, learning, security, retrospectives
notebooks/      # analysis notebooks
datasets/       # openf1, audit-history, sample-crm
infrastructure/ # bicep, terraform, environments
portfolio/      # portfolio artefacts
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

