# Settlement Capability Registry (Tier A)

> The deterministic core of the Paddock Club predictions game (story #226,
> ADR-0008). The LLM proposes a settlement spec at intake; **code grades it**,
> reproducibly, from ingested OpenF1 data. Never the model.

## How grading works

- A grading function takes a `GradingContext` (a session's ingested rows —
  `SessionResult` / `StartingGrid` / `Lap` / `Pit`, the `#18` Pydantic models)
  and returns `WIN` / `LOSE` / `VOID`.
- **Pure functions, no live API** at grade time — the settlement engine (#229)
  builds the context from Dataverse and calls `grade(code, params, ctx)`.
- **VOID = required data absent/ambiguous** (refund, never guess). A *known*
  DNF grades to LOSE where a finish was predicted — it's data, not a gap.
- **Qualifying** grades on the same functions (just a qualifying session's rows).

## Types 1–12

| code | params | reads | WIN when | VOID when |
|---|---|---|---|---|
| `driver_wins` | driver | result | position == 1 | no result row |
| `podium_contains` | driver | result | classified & pos ≤ 3 | no result row |
| `points_finish` | driver | result | classified & pos ≤ 10 | no result row |
| `driver_finish_position` | driver, operator, value | result | operator(position, value) | no result / position null |
| `head_to_head_finish` | driver_a, driver_b | result | A classified higher than B | either missing / both unclassified |
| `classified_finish` | driver | result | not dnf/dns/dsq | no result row |
| `driver_dnf` | driver | result | dnf flag set | no result row |
| `beats_grid` | driver | grid + result | finish < grid | grid or finish missing |
| `positions_gained_at_least` | driver, n | grid + result | (grid − finish) ≥ n | grid or finish missing |
| `fastest_lap_by` | driver | laps | driver owns min lap_duration | no timed laps |
| `winning_margin` | operator, seconds | result | operator(P2 gap_to_leader, seconds) | no P2 / gap missing |
| `pit_stops` | driver, operator, n | pit | operator(stop count, n) | no pit data |

FastF1-sourced types (`safety_car_deployed` 13, `driver_crash` 15) are the
Tier-B story (#231), separate and void-on-ambiguous.

## Module (`src/paddock/settlement`)

| File | Role |
|---|---|
| `types.py` | `Outcome`, `Operator`, per-type Pydantic param models |
| `context.py` | `GradingContext` + `is_classified` |
| `drivers.py` | `resolve_driver(name/number, drivers)` → number or `None` (unresolved → caller voids) |
| `grading.py` | the 12 `grade_*` functions + `GRADERS` dispatch + `grade(code, params, ctx)` |
| `registry.py` | `SETTLEMENT_TYPES` metadata + `seed(dataverse)` → `racy_settlementtypes` |

## Consumers

- **#229** settlement engine — builds the context from Dataverse, grades locked slips.
- **#230** intake — exposes the registry to the LLM; validates its structured output against the param models.
- **#227** odds v1 — prices these same types.

Seeding the reference records needs the Paddock schema (#225); the metadata and
`seed` logic are complete and unit-tested (fake upserter) now.
