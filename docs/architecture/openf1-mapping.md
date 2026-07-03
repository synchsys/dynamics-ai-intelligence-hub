# OpenF1 → Dataverse mapping

> How ingested OpenF1 data lands in Dataverse (story #19). The authoritative,
> code-level source is `src/openf1/mapping.py`; this document is the
> human-readable view. Logical names use the **`racy`** publisher prefix
> (`racy_…`) per ADR-0009 / the Dataverse tech doc §3.

## Principles

- **OpenF1 is the settlement source of truth** (ADR-0008). Rows are validated
  by `openf1.models` (lenient Pydantic), then upserted.
- **Idempotent upsert by alternate key** — re-ingestion never duplicates. Keys
  are composite OpenF1 identifiers (`session_key` + `driver_number` [+ more]).
- **Void, don't guess** — invalid rows are logged and skipped, not fatal.
- A session is **settleable** once the Tier-A minimum landed: `drivers` +
  `session_result`.

## Entity map

| OpenF1 endpoint | Dataverse entity set | Alternate key | Grounds |
|---|---|---|---|
| `sessions` | `racy_sessions` | `session_key` | Race Event mapping |
| `drivers` | `racy_drivers` | `session_key`, `driver_number` | name→number resolution |
| `session_result` | `racy_sessionresults` | `session_key`, `driver_number` | settlement types 1–7, 11 |
| `starting_grid` | `racy_startinggrids` | `session_key`, `driver_number` | types 8–9 |
| `laps` | `racy_laps` | `session_key`, `driver_number`, `lap_number` | type 10 |
| `pit` | `racy_pitstops` | `session_key`, `driver_number`, `lap_number` | type 12 |
| `position` | `racy_positions` | `session_key`, `driver_number`, `date` | odds inputs |
| `stints` | `racy_stints` | `session_key`, `driver_number`, `stint_number` | Epic 7 strategy features |
| `weather` | `racy_weather` | `session_key`, `date` | growth type 14 |

## Status

Entity-set and column logical names are **provisional** until the Dataverse
schema (Epic 3, story #6) is created in the environment; `mapping.py` is the one
place to reconcile them. Writes go through `DataverseClient.upsert` (per-row);
`$batch` upsert is a possible later optimisation. The end-to-end integration
test runs only against a provisioned environment with the `racy_` tables.
