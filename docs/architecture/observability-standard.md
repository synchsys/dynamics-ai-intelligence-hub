# Observability Standard

The single standard for logs, metrics, and traces across the solution (#29 /
Epic 11 11.D). It unifies the previously siloed **ingestion** (#21) and
**agent** (#78) telemetry — plus HTTP inference and the CRM/RAG assistants —
under one store, one query path, one correlation model, and one dashboard.

## Store & query path

All runtime telemetry goes to **one Application Insights** resource,
`racy-appi-dev` (uksouth), which is **workspace-based** — its data lives in a
linked Log Analytics workspace, not the classic component store.

> **Query the workspace, not the classic API.** `az monitor app-insights query`
> (the classic `api.applicationinsights.io` path) returns **nothing** for a
> workspace-based resource. Query the linked workspace with the **workspace
> schema** (`AppRequests`, `AppTraces`, `AppDependencies`, `AppExceptions`):
>
> ```bash
> WS=$(az monitor app-insights component show --app racy-appi-dev -g rg-racy-ai-dev \
>        --query workspaceResourceId -o tsv)
> WSID=$(az monitor log-analytics workspace show --ids "$WS" --query customerId -o tsv)
> az monitor log-analytics query -w "$WSID" --analytics-query "AppRequests | take 10" -o table
> ```

The Function App forwards telemetry via `APPLICATIONINSIGHTS_CONNECTION_STRING`
(set at create). No code emits to App Insights directly — the host ships
`AppRequests` (HTTP triggers), `AppExceptions`, `AppDependencies`, and forwards
Python `logging` records as `AppTraces`.

## 1. Logs

Emitted through `shared.logging.get_logger(name)` — plain namespaced
`logging.Logger`s (propagation on, no custom handlers), so on the Functions host
they reach the host's App Insights handler and land as **`AppTraces`**:

| Field | Source | In `AppTraces` |
|---|---|---|
| level | `record.levelname` | `SeverityLevel` |
| message | rendered log message | `Message` |
| category | Functions host | `Properties.Category` = `Function.<name>.User` for in-function logs |
| correlation_id | `bind_correlation_id()` (contextvar) | in `Message` when bound |

Verified live: a timer ingestion run emits `Function.scheduled_ingestion.User`
traces — `ingestion start run_id=…`, `openf1 GET /sessions …`,
`metric ingestion.failures=1 {…}` — all queryable in `AppTraces`.

`configure_logging()` (which clears root handlers) is for **local/CLI** use only
— it must **not** run on the Functions host, or it removes the host's App
Insights handler. It is not called in the deployed path.

## 2. Metrics

Naming: **`<domain>.<metric>`**, lower-dotted. Current metrics (ingestion, #21):

| Metric | Meaning |
|---|---|
| `ingestion.records` | rows upserted in a run |
| `ingestion.duration_ms` | run wall-clock |
| `ingestion.failures` | 1 per failed run (drives the alert) |

Emitted by `LoggingMetricSink` as a structured **log line** —
`metric <name>=<value> {properties}` — so today a metric is an `AppTraces` row,
extracted in KQL (below), **not** a native `customMetrics` point. The sink is a
Protocol: a future `OpenTelemetryMetricSink` can emit native `customMetrics`
without touching callers.

## 3. Traces & correlation

Every multi-step operation carries a **`run_id`** (uuid hex) correlating its
steps, and a **duration** and **success/failure** signal:

| Source | Correlation | Timing | Failure signal | Shape |
|---|---|---|---|---|
| Ingestion (`ObservabilityRecord`) | `run_id` | `duration_ms` | `ingestion.failures` metric + re-raise | log lines |
| Agent workflow (`TraceEvent`) | `run_id` + `sequence` | `duration_ms` | step `AppExceptions` | `agent.step` log lines |
| HTTP predict/health | host `operation_Id` | `AppRequests.DurationMs` | `ResultCode` | `AppRequests` |

Agent steps emit `event agent.step {run_id, sequence, step, agent} {duration_ms,
tokens}` via `LoggingTelemetrySink` (→ `AppTraces`).

## 4. AI governance log (separate surface)

Prompt/response governance (#69) is **not** in App Insights — it is written to
the Dataverse **AI Request / AI Response** tables (`racy_airequests` /
`racy_airesponses`): prompt, model, acting `user_id`, raw output, decision,
`tokens`, `latency_ms`. See `docs/architecture/ai-logging.md`. Operational
telemetry (App Insights) answers *is it healthy/fast/failing*; the governance
log answers *what did the model do, for whom*.

## KQL library

Validated against the live workspace. `TimeGenerated` is UTC.

**Ingestion runs** (metrics parsed from trace lines):
```kusto
AppTraces
| where Message startswith "metric ingestion."
| parse Message with "metric " name "=" value:real " " *
| summarize sum(value) by name, bin(TimeGenerated, 1h)
```

**Agent steps** (per run):
```kusto
AppTraces
| where Message startswith "event agent.step"
| parse Message with * "'run_id': '" run_id "'" *
| parse Message with * "'duration_ms': " duration_ms:real *
| project TimeGenerated, run_id, duration_ms
```

**Function health / latency**:
```kusto
AppRequests
| summarize total=count(), failures=countif(Success == false),
            p95_ms=percentile(DurationMs, 95) by Name, bin(TimeGenerated, 15m)
```

**Errors**:
```kusto
AppExceptions | project TimeGenerated, ProblemId, OuterMessage, Method | order by TimeGenerated desc
```

## Dashboard & alerts

- **Dashboard:** an Azure Monitor **Workbook** (`infrastructure/bicep/modules/observability.bicep`)
  with tiles for request volume/latency, failures, ingestion runs, and agent
  steps — one view over ingestion + agents against this standard.
- **Alerts** (`scheduledQueryRules`, same module): **function failures**
  (`AppRequests` `Success == false`), **ingestion failures** (`ingestion.failures`
  trace), and **high latency** (`AppRequests` p95 over threshold). Deployed via
  the Bicep in `infrastructure/` (ADR-0002); CI-driven deploy is #88.

## Conformance checklist (new telemetry must)

1. Log via `shared.logging.get_logger` (never `print`, never a bespoke handler).
2. Give any multi-step operation a `run_id` and stamp it on every line/event.
3. Name metrics `<domain>.<metric>`; emit a `*.failures` signal on failure.
4. Record a `duration_ms`.
5. Keep secrets/PII out of logs (business content only).
