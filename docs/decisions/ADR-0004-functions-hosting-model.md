# ADR-0004: Azure Functions hosting model

## Status

Accepted

## Context

The serverless foundation (#10) needs a hosting plan. The app must scale to zero
when idle (a dev/portfolio project — no standing cost), run Python v2 functions,
and host a timer-triggered ingestion job plus HTTP endpoints for AI/health, with
room to grow into the GenAI and agent workloads (Epics 8/10). Candidate plans:

- **Consumption** — the classic serverless plan: cheapest, scale-to-zero,
  mature, but slower cold starts and limited networking/concurrency controls.
- **Flex Consumption** — the current Microsoft-recommended plan for new function
  apps: still scale-to-zero and pay-per-use, with faster/decoupled cold starts,
  per-instance concurrency, configurable instance memory, and VNet integration.
- **Premium / Dedicated** — always-warm, no scale-to-zero — rejected: standing
  cost, unnecessary for this workload.

## Decision

Use **Flex Consumption** as the primary hosting model, in the same region as the
other resources (uksouth). It keeps scale-to-zero economics while giving better
cold-start behaviour and the concurrency/networking headroom the later AI
workloads will want — and it's the plan Microsoft now steers new Python apps to.

**Fallback:** plain **Consumption** if Flex Consumption is unavailable in the
target region or the sponsorship subscription — the app code is identical (Python
v2), so switching plans is a deployment-config change only.

## Consequences

- **Positive:** no idle cost; one app that all of ingestion (#20), the assistant,
  and the agent workflow extend; a modern baseline with better cold starts than
  Consumption.
- **Negative / constraints:** Flex Consumption has some feature/region variance
  vs Consumption; if hit, fall back to Consumption (no code change). Cold starts
  still exist (mitigated, not eliminated) — fine for a timer job and dev HTTP.
- **Cost monitoring** (#82) tracks actual spend once deployed.

## Notes

The app uses the **Python v2 programming model** (`function_app.py` with
decorators). Trigger *logic* lives in `handlers.py` so it is unit-tested without
the Functions host; `function_app.py` is the binding layer, verified by
`func start` locally and a deployed HTTP smoke test (see README).
