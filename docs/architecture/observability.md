# Ingestion observability

The scheduled ingestion (#20) is observable from the start (#21): every run is
timed, counted, logged, and emits metrics, and a failure surfaces as a failed
invocation that an alert fires on.

## What each run emits (`src/azure_functions/observability.py`)

`observed_ingestion` wraps the run and produces:

- **Structured logs** — `ingestion start` / `ingestion complete` / `ingestion
  failed`, each with `run_id`, `session_key`, `duration_ms`, and outcome. Our
  JSON logger (`shared.logging`) flows these to Application Insights traces.
- **Custom metrics** (via a `MetricSink`; `LoggingMetricSink` in production):
  - `ingestion.records` — rows upserted this run
  - `ingestion.duration_ms` — run duration (tagged `outcome=success|failed`)
  - `ingestion.failures` — `1` on a failed run
- **A run id** per run, on every log line and metric, so a run is traceable end
  to end.

## Failure handling

On any exception the failure metric is emitted and the error is logged **with
context** (run id, session, duration), then **re-raised** — so the Function
invocation fails. That makes failures visible in App Insights (failed
invocations + the `ingestion.failures` metric) and gives the alert something to
fire on, rather than swallowing the error.

## Alert rule (Azure Monitor — deploy-time step)

A metric alert on failed runs, e.g.:

```bash
az monitor metrics alert create \
  --name ingestion-failures \
  --resource-group rg-racy-ai-dev \
  --scopes <function-app-app-insights-resource-id> \
  --condition "count customMetrics/ingestion.failures > 0" \
  --window-size 1h --evaluation-frequency 15m \
  --description "OpenF1 ingestion run failed"
```

(Or a log-search alert on failed `scheduled_ingestion` invocations.) Creating the
alert requires the deployed Function App + its Application Insights resource, so
it's a deploy-time step; the code emits the signal it fires on.

## Verification

Unit tests cover the success path (record + `records`/`duration_ms` metrics), the
failure path (`failures` metric emitted, error re-raised), and the metric sink.
Once deployed, a forced failure (e.g. a bad `INGEST_SESSION_KEY`) produces a
failed invocation + the failure metric, triggering the alert.
