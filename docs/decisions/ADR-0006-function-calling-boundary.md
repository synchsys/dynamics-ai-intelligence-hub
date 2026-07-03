# ADR-0006: Function-calling vs agent-orchestration boundary

## Status

Accepted

## Context

Two epics need the model to invoke tools:

- **Epic 8 (Generative AI)** — the CRM assistant and the Paddock free-text
  intake (#230) need a single model to call registered tools (read a Dataverse
  record, propose a settlement spec) and act on the results.
- **Epic 10 (Agents)** — a multi-agent workflow (planner → researcher →
  reviewer → reporter) coordinates several model calls, each of which also needs
  to invoke tools.

Without an explicit boundary, tool plumbing (schema description, argument
validation, dispatch, the call/result loop) would be implemented twice — once in
the assistant and again in the agent framework — diverging in validation rules
and error handling. That is exactly the duplication this ADR exists to prevent.

## Decision

There is **one tool layer**, owned by Epic 8, living in `src/ai/tools/`:

- `Tool` — a name + description + **Pydantic parameter model** + handler. The
  parameter model is the single source of truth for both the schema advertised
  to the model and the argument validation applied before the handler runs.
- `ToolRegistry` — registration + `openai_schema()` + `dispatch()` (validates
  arguments, then runs the handler; unknown tool → typed error).
- `run_tools()` — the bounded, single-model function-calling loop: advertise
  tools, dispatch each requested call, feed results (and tool errors) back, and
  iterate until the model returns a final answer or the iteration budget is hit.

**Epic 8 owns single-model function calling. Epic 10 owns multi-agent
orchestration and *reuses* this layer** — each agent calls `run_tools` (or the
registry directly); it does **not** re-implement tool routing, validation, or
dispatch. The orchestration framework decision itself (how agents are
coordinated) is a separate concern, tracked under Epic 10 (spike 10.1 /
ADR-0007).

## Consequences

- **Positive:** one validated dispatch path; argument validation and error
  handling are defined once and shared; agents stay thin (planning + delegation)
  and inherit the tool layer's safety. Tools are unit-testable in isolation with
  a fake gateway, and the whole loop is testable with an injected fake SDK.
- **Negative / constraints:** the tool layer must stay agent-agnostic — no
  orchestration concepts (roles, hand-offs, shared scratchpads) leak into
  `src/ai/tools/`. Cross-layer tools (e.g. Dataverse reads) enter via a
  structural `Protocol` so `src/ai` never imports `src/dataverse` directly.
- **Boundary with structured outputs (#60):** `structured_output` is for "return
  schema-valid JSON"; the tool layer is for "call code and act on the result".
  Function calling may use structured outputs internally but they remain
  distinct capabilities.
