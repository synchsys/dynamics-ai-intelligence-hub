# ML feature sets

Three documented, leakage-checked feature sets (`src/ml/features.py`, #51), each
tied to a portfolio model. Feature transformers are pandas functions, unit-tested
with small fixtures.

## 1. Lap/stint features → lap-time regression (#49)

`lap_features(laps) -> (X, y)`. One row per lap; `y = LapTimeSeconds`.

| Feature | Rationale |
|---------|-----------|
| `LapNumber` | Race progress (fuel burn, track evolution) |
| `Stint` | Which stint the lap belongs to |
| `StintLap` | Lap position within the stint (tyre warm-up/wear) |
| `TyreLife` | Tyre age in laps (degradation); falls back to `StintLap` |
| `Comp_*` | One-hot tyre compound |

**Leakage check:** every feature is known at the *start* of the lap; nothing is
derived from the lap's own time or from later laps, and the target is returned
separately (never a column of `X`).

## 2. Race-context features → strategy classification (#52)

`race_context_features(laps) -> (X, y)`. One row per driver+stint; `y = Compound`.

| Feature | Rationale |
|---------|-----------|
| `StartLap` | When the stint began (early/late strategy) |
| `StintLength` | Laps in the stint (stint aggression) |
| `AvgPace` / `BestPace` | Pace level of the stint (seconds) |
| `PaceRange` | Degradation proxy (slowest − fastest lap) |

**Leakage check:** each row summarises one completed stint; the target is the
stint's compound and is excluded from the features — the features describe *when*
and *how* the stint ran, not which tyre it used.

## 3. Audit features → anomaly detection (#55)

`audit_features(events, *, as_of) -> X`. One row per entity; **unsupervised**.
Consumes the Epic 6 audit export (#48: `EntityId`, `Actor`, `ChangedOn`).

| Feature | Rationale |
|---------|-----------|
| `ChangeCount` | Total changes (volume) |
| `DistinctActors` | How many actors touched the entity |
| `RecencyDays` | Days since the last change |
| `ActiveSpanDays` | First→last change span |
| `ChangesLast7d` | Recent burst detection |

**Leakage check:** only events at or before the explicit `as_of` cutoff are used,
so features never see the future; `as_of` is a parameter (not "now") for
reproducibility. Unsupervised, so there is no target to leak.

## Status

The lap and race-context sets are built on live FastF1 data today. The audit set
is implemented and tested on a fixture matching the #48 export schema; it wires
to real audit data once that export exists (which depends on the app + auditing
being enabled).
