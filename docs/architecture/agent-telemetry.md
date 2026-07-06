# Agent Telemetry & Tracing

Per-step observability for a multi-agent run (#78). Every step of
`MultiAgentWorkflow.run` emits one structured trace, correlated under a single
`run_id`, carrying its timing and token cost. This makes a run debuggable —
which step ran, how long it took, what it cost — and defines the telemetry
schema that Epic 11 (11.D) consolidates into the platform observability standard.

## Flow

```
run() ─► run_id = run_id_factory()                      # one id for the whole run
      ─► client.on_usage = accumulate                   # meter tokens across all completions
      for each step (plan → research[i] → review → report):
        start = clock(); before = tokens_seen
        <agent does its work>                            # completions funnel through AIClient.complete
        record(step, agent, summary,
               duration_ms = (clock()-start)*1000,
               tokens      = tokens_seen - before)       # per-step token delta
          ├─► trace.append(TraceEvent(...))              # in-memory, returned in WorkflowResult
          ├─► telemetry.track_event("agent.step", ...)   # → Application Insights
          └─► on_event(event)                            # optional live callback
      finally: client.on_usage = previous_hook           # no lingering side effect
```

Token metering is non-invasive: `AIClient.complete` fires an optional
`on_usage(total_tokens)` hook after every completion, and since **every** agent
call (`chat`, `structured_output`, the researcher's tool loop) funnels through
`complete`, a running total lets each step report the delta it incurred — no need
to thread usage through the planner/researcher/reviewer/reporter APIs.

## Correlation

- **`run_id`** — one id per `run()`, stamped on every `TraceEvent` and on every
  emitted `agent.step` event. Injectable (`run_id_factory`) for deterministic
  tests; `uuid4().hex` in production.
- **`sequence`** — dense `0..n` ordering of steps within a run, so traces sort
  deterministically even if the sink reorders on ingest.

## TraceEvent schema (`src/agents/workflow.py`)

| Field | Type | Meaning |
|---|---|---|
| `run_id` | str | Correlates all steps of one run |
| `sequence` | int | 0-based step order within the run |
| `step` | str | `plan` / `research[i]` / `review` / `report` |
| `agent` | str | `planner` / `researcher` / `reviewer` / `reporter` |
| `summary` | str | Short, previewed description of the step's output |
| `duration_ms` | float | Wall-clock time for the step (rounded to 0.1 ms) |
| `tokens` | int \| None | Total tokens the step consumed (`None` if the SDK reported no usage) |

## Application Insights emission (`src/agents/telemetry.py`)

The workflow emits through a `TelemetrySink` Protocol so it stays testable. The
default `LoggingTelemetrySink` writes each step as a structured log line that
Application Insights ingests as a **`customEvent`** — the same "log →
App Insights" approach as ingestion observability (#21,
`azure_functions.observability`). The `track_event(name, properties,
measurements)` signature mirrors the Azure Monitor `TelemetryClient.track_event`
API, so a live `opencensus`/`azure-monitor`-backed sink drops in behind the same
Protocol with no workflow changes.

Each step becomes one `agent.step` event:

| customEvent | Field | Source |
|---|---|---|
| **name** | `agent.step` | `STEP_EVENT` |
| **properties** | `run_id`, `sequence`, `step`, `agent` | correlation + identity (string dimensions) |
| **measurements** | `duration_ms`, `tokens` | numeric metrics for aggregation |

Splitting dimensions (properties) from metrics (measurements) matches the
App Insights custom-telemetry model: properties are filterable/groupable, and
measurements roll up into `customMeasurements` for percentiles and sums. In
Log Analytics a run is then reconstructed with, e.g.:

```kusto
customEvents
| where name == "agent.step"
| extend run_id = tostring(customDimensions.run_id)
| where run_id == "<id>"
| project sequence = toint(customDimensions.sequence), step = tostring(customDimensions.step),
          duration_ms = todouble(customMeasurements.duration_ms), tokens = todouble(customMeasurements.tokens)
| order by sequence asc
```

## Alignment with 11.D

`run_id` correlation, the properties/measurements split, and the "log →
customEvent/customMetric" emission path are shared with the ingestion
observability record, so Epic 11's consolidation standardises one schema across
ingestion and agent runs rather than reconciling two.
