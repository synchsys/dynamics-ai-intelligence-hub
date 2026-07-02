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
pytest                    # tests with coverage (fails under 80%)
```

Run all of them before pushing.

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
