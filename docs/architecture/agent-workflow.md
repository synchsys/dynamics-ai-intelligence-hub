# Multi-agent workflow

The headline agentic deliverable (#26, feature #124): one orchestrated run that
takes a goal and drives the four core agents (#76) to a report, reusing the #61
tool layer and the Epic 9 RAG assistant, with a human-approval gate on writes and
end-to-end telemetry. The custom orchestration chosen in ADR-0007.

## Flow

```
run(goal)
  ─► Planner.plan(goal)                     → Plan(steps)        [trace: plan]
  ─► for each step:
        Researcher.research(step, context)  → findings          [trace: research[i]]
           · uses tools via run_tools: Dataverse reads, guarded writes,
             and search_knowledge (RAG assistant, permission-aware)
  ─► Reviewer.review(findings, goal)        → Review(approved…)  [trace: review]
  ─► Reporter.report(goal+findings+review)  → report            [trace: report]
  ─► WorkflowResult(plan, findings, review, report, trace, pending_writes)
```

Each step accumulates context for the next; findings from earlier steps are
passed to later research.

## Guardrails

- **Single tool layer (ADR-0006):** all tool use routes through the
  `ToolRegistry` / `run_tools`; agents do not re-implement tool calling.
- **Human approval on writes (#64):** the researcher's write tools stage a
  `PendingWrite` in the shared `ApprovalBroker` instead of executing. The run
  surfaces them as `WorkflowResult.pending_writes`; nothing is written until a
  human calls `broker.approve(...)`. Verified: a staged follow-up is **not**
  executed during the run and only writes on approval.
- **RAG-backed research (#72):** `knowledge_search_tool(rag, roles)` wraps the
  RAG assistant as a tool, capturing the caller's roles so knowledge retrieval
  stays permission-aware.
- **Telemetry:** every agent step emits a `TraceEvent(step, agent, summary)`,
  collected on `WorkflowResult.trace` and streamed to an optional `on_event`
  callback — the full run is observable.

## Contract

`MultiAgentWorkflow(client, planner?, researcher?, reviewer?, reporter?, broker?,
on_event?).run(goal) -> WorkflowResult`. Deterministic control flow and bounded
per-agent tool loops (`max_iterations`); an empty plan still produces a review
and report.

## Testing

End-to-end unit tests with an injected scripted SDK: a sample goal yields a
report with a full trace; a write action is staged pending approval (and executes
only on approve); the telemetry callback receives every step; an empty plan still
reports; and `knowledge_search_tool` wraps the RAG assistant with roles captured.
Live-verified (`scripts/agents/verify_workflow.py`) against Azure OpenAI + Azure
AI Search + Dataverse: all four agents run, a follow-up write stays **pending
approval**, telemetry prints each step, and a report is produced.
