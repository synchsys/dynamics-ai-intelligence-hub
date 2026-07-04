# ADR-0007: Agent orchestration framework

## Status

Accepted

> Reserved as ADR-0007 by ADR-0009; this is the agent-orchestration decision for
> Epic 10 (spike 10.1 / #75). Builds directly on ADR-0006 (function-calling vs
> agent-orchestration boundary).

## Context

Epic 10 needs a multi-agent workflow (planner → researcher → reviewer →
reporter). Before building four agents we must choose how they are orchestrated,
because the wrong choice means rebuilding them. Candidates:

- **Semantic Kernel** — Microsoft-aligned; planners, plugins, memory.
- **AutoGen** — conversational multi-agent framework.
- **Custom loop** — a thin orchestration layer over our existing components.

Criteria: reuse of the #61 tool layer (ADR-0006), governance hooks (the #64
approval gate, #230 prompt/response logging), telemetry, hermetic testability
(injected SDK, 100% coverage, mypy --strict), learning value, and dependency
weight.

## Evaluation

| Criterion | Semantic Kernel | AutoGen | Custom loop |
|-----------|-----------------|---------|-------------|
| Reuse #61 tool layer | Re-abstracts tools (plugins) | Re-abstracts tools | **Reuses `run_tools`/`ToolRegistry` directly** |
| Governance (approval, logging) | Wrap/adapt its pipeline | Wrap/adapt its pipeline | **Native — same `ApprovalBroker`/`PromptLogger`** |
| Hermetic tests (injected SDK) | Framework internals to mock | Framework internals to mock | **Already the house pattern** |
| Dependency weight | Heavy | Heavy | **None new** |
| Learning value | Framework API | Framework API | **The orchestration itself** |
| Risk | Abstraction lock-in | Fast-moving API | Must build coordination (small) |

A tiny proof (a single `Agent` calling one tool) was built to validate the custom
path: an agent = instructions + a `ToolRegistry`, and `run(task)` delegates to
`run_tools` (#61). It works with the injected fake SDK and needs no new
dependency — see `src/agents/` and `tests/agents/test_agent.py`.

## Decision

**Build a custom, lightweight orchestration layer in `src/agents/`, reusing the
Epic 8 tool layer (#61).** An `Agent` pairs a role/instructions with a
`ToolRegistry` and runs via `run_tools`; the multi-agent workflow (#76 → #124)
composes agents with deterministic, testable control flow (the same pattern as
the `Workflow`/pipeline style used elsewhere in the project).

Semantic Kernel and AutoGen are **not** adopted: both re-abstract tool calling
(conflicting with ADR-0006's single tool layer), add heavy dependencies, and make
the governance spine and hermetic tests harder — for no benefit at this scale.

## Consequences

- **Positive:** one tool layer end to end (assistant + agents); governance
  (approval gate, prompt/response logging) and telemetry reuse existing
  components; agents are unit-testable with the injected SDK at 100% coverage; no
  new dependencies; the orchestration logic is the portfolio artefact.
- **Negative / constraints:** we implement coordination ourselves (agent
  hand-off, aggregation, termination bounds) rather than getting it from a
  framework — kept small and deterministic. If future needs outgrow the custom
  layer, the `Agent`/tool boundary is thin enough to swap the orchestrator without
  touching the tools.

## Implications for 10.2–10.Z

- **#76 (four core agents):** each is an `Agent` (instructions + scoped tools) —
  planner, researcher (may use the RAG assistant / read tools), reviewer,
  reporter.
- **Telemetry (#78) / safety (#79) / approval (#80):** wrap `run_tools` and the
  `ApprovalBroker`; no framework adapters needed.
- **#124 / #86 (workflow assembly):** deterministic orchestration of the agents
  into planner → researcher → reviewer → reporter, logged and bounded.
