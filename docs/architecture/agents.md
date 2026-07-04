# Core agents

The four role agents (#76) that the multi-agent workflow (#124) assembles. Each
is built on the `Agent` primitive (ADR-0007) — a role + the #61 tool layer — and
is individually testable with a defined input/output contract.

## The primitive

`Agent(name, instructions, registry, max_iterations)` runs a task via `run_tools`
(#61): its `instructions` become the system message, optional `context` from a
prior step is passed as a message, and the agent may call the tools in its
registry. Agents reuse the single tool layer rather than re-abstracting it
(ADR-0006).

## Contracts

| Agent | Input → Output | Mechanism | Tools |
|-------|----------------|-----------|-------|
| **Planner** | goal → `Plan(steps: list[str])` | structured output (#60) | none |
| **Researcher** | task (+context) → findings `str` | `Agent.run` / `run_tools` | yes (Dataverse reads, RAG) |
| **Reviewer** | content (+goal) → `Review(approved, issues, summary)` | structured output | none |
| **Reporter** | material → report `str` | plain generation | none |

- **Planner** breaks a goal into a short ordered list of concrete steps
  (schema-valid, capped by `max_steps`).
- **Researcher** is the only tool-using agent: it investigates using its
  registry and reports findings grounded strictly in tool results, saying what's
  missing rather than guessing.
- **Reviewer** returns a machine-actionable verdict so the workflow can branch on
  `approved` / act on `issues`.
- **Reporter** composes the final human-facing report from the goal, findings,
  and review — using only that material.

## Composition (preview of #124)

```
Planner.plan(goal) ─► for each step: Researcher.research(step) ─► findings
findings ─► Reviewer.review(findings, goal) ─► verdict
goal + findings + verdict ─► Reporter.report(...) ─► final report
```

The workflow (#124) wires these deterministically, with telemetry (#78), safety
(#79), and human approval (#80) layered on the shared `run_tools` / `ApprovalBroker`.

## Testing

Each agent is unit-tested in isolation with an injected fake SDK (structured
verdicts, tool-loop findings, plan steps, report prose) at 100% coverage.
Live-verified end to end (`scripts/agents/verify_core_agents.py`): planner →
researcher (counts session-9165 results via a Dataverse tool → 19) → reviewer →
reporter, against Azure OpenAI + Dataverse.
