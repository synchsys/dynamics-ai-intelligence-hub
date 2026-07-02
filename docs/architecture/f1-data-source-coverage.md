# Dynamics AI Intelligence Hub — F1 Data Source Coverage

> **Version:** 0.1
> **Location in repo:** `docs/architecture/f1-data-source-coverage.md`
> **Purpose:** A single reference for what OpenF1 and FastF1 expose, what the
> solution ingests today, and the rules for choosing between them. Captures
> the API coverage sweep so the decisions live in the repo, not in chat.
> **Client-agnostic:** F1 public data only.

------------------------------------------------------------------------

## 1. Source-selection rules (read first)

1. **OpenF1 is the settlement source of truth.** Its REST endpoints ingest
   cleanly via the Epic 2 REST client and ground every Tier-A settlement
   type. A settlement type takes a heavier source (FastF1) only when OpenF1
   genuinely cannot ground it (see §4).
2. **FastF1 is the analytics / ML / enrichment source.** Telemetry, tyre
   detail, sector times, coded status streams, circuit maps and deep
   history (via the Ergast-compatible backend) come from FastF1.
3. **Do not dual-ingest the same fact for the same purpose.** Telemetry and
   position come from FastF1 (Epic 5), not OpenF1 `car_data`/`location`;
   results/DNF come from OpenF1 `session_result` for settlement.
4. **Both are post-session sources.** FastF1 timing/telemetry is available
   ~30–120 minutes after a session (2018 onward); OpenF1 historical opens
   ~30 minutes after. Neither free tier gives live in-race data — which is
   why settlement is deadline-and-settle, never live.

------------------------------------------------------------------------

## 2. OpenF1 endpoint inventory (18 endpoints)

| Endpoint | Data | Used for | Status |
|---|---|---|---|
| `session_result` | position, `dnf/dns/dsq`, duration, gap_to_leader, laps | Settlement backbone (types 1–7, 11) | In use |
| `starting_grid` | grid positions | Grid-based types (8–9) | In use |
| `laps` | lap times, sectors, speeds, pit flags | Fastest-lap (10); analytics | In use |
| `pit` | pit stops + `pit_duration` | `pit_stops` (12) | In use |
| `position` | position changes over time | Odds inputs; analytics | In use |
| `drivers` | entry list / driver info | Name→number resolution | In use |
| `sessions` / `meetings` | session + weekend metadata | Race Event mapping | In use |
| `race_control` | flags, SC/VSC, penalties (text) | Type 13 fallback (parse) | In use |
| `weather` | air/track temp, rainfall, wind | Type 14 | In use |
| `stints` | tyre compound + tyre age | Strategy ML (Epic 7); Team-Principal (Tier B) | **Promote** |
| `overtakes` | driver-over-driver events | Analytics; possible market | Candidate |
| `intervals` | gap-to-leader / to car ahead | Gap analytics | Optional |
| `car_data` | speed, RPM, throttle, brake, DRS, gear | (Prefer FastF1) | Skip |
| `location` | X/Y/Z track position | (Prefer FastF1) | Skip |
| `team_radio` | radio recording mp3 URLs | Optional RAG/transcription stretch | Optional |
| `championship_drivers` (beta) | driver standings + points | Race-context ML features; RAG | **Add** |
| `championship_teams` (beta) | constructor standings | Season context; RAG | **Add** |

------------------------------------------------------------------------

## 3. FastF1 object inventory

| Object | Data | Used for | Status |
|---|---|---|---|
| `session.results` | position, **Status ('Crash'/'Gearbox')**, ClassifiedPosition (R/D/E/W/F/N), **Q1/Q2/Q3, GridPosition**, points | Crash type (15); qualifying markets; features | **Expand** |
| `session.laps` | sectors, PitIn/Out, **Compound, TyreLife, Stint, FreshTyre**, speed traps, **IsAccurate / Deleted / FastF1Generated** | Telemetry analytics; strategy ML; data-quality (Epic 6) | **Expand** |
| `session.track_status` | coded green/yellow/**SC/VSC/red** stream | Preferred grounding for type 13 | **Add** |
| `session.session_status` | Started / Finished / Aborted | Session-state checks | Optional |
| `session.car_data` / `pos_data` | telemetry channels + X/Y/Z | Epic 5 telemetry notebooks | In use |
| `session.race_control_messages` | parsed flags + messages | Crash context; penalties | In use |
| `session.weather_data` | temps, rainfall, wind | (Overlaps OpenF1 weather) | Analytics only |
| `get_circuit_info()` → `CircuitInfo` | corners, marshal lights/sectors, rotation | Track-map viz; RAG track context | Optional |
| `get_event_schedule()` / Event | calendar, session dates, `F1ApiSupport` | Fixture creation | In use |
| **Ergast / jolpica-f1 backend** | results, standings, quali, pit stops, lap times **back to 1950** | ML training depth; RAG historical facts | **Add** |
| `fastf1.plotting` | official team colours | Consistent notebook/app viz | Nicety |

------------------------------------------------------------------------

## 4. Where FastF1 grounds a settlement type better than OpenF1

Two settlement types are cleaner (or only possible) on FastF1. Both are
therefore **Tier-B, FastF1-dependent, and void-on-ambiguous** — a heavier,
slower settlement path than the OpenF1 REST flow (see ADR-0008).

| Type | Why OpenF1 is insufficient | FastF1 grounding |
|---|---|---|
| `driver_crash` (15) | `session_result` gives the DNF flag but not the *cause* | results `Status` == 'Crash' |
| `safety_car_deployed` (13, preferred) | `race_control` is free text needing fuzzy parsing | `track_status` coded SC/VSC values (deterministic) |

OpenF1 remains the Tier-A default: `driver_dnf` (7) is the deterministic
"crash" proxy, and `race_control` parsing remains the OpenF1-only fallback
for safety-car if FastF1 is not ingested.

------------------------------------------------------------------------

## 5. Opportunities this unlocks (by epic)

| Opportunity | Source | Epic |
|---|---|---|
| Qualifying markets (pole, reach Q3, quali head-to-head) reuse the race grading pattern on a different session | OpenF1 `session_result`/`starting_grid`; FastF1 Q1/Q2/Q3 | 12 (Paddock Club) |
| Strategy-classification features (compound, stint length, tyre age) | `stints` / FastF1 laps | 7 |
| Race-context ML features (championship position, points gap) | championship endpoints / Ergast | 7 |
| Deep historical form for the odds model and RAG facts (pre-2023) | FastF1 Ergast/jolpica backend | 7, 9 |
| Real messy-data hooks for data-quality work (deleted/inaccurate/interpolated laps) | FastF1 laps flags | 6 |
| Track-map visualisation and track-context enrichment | `CircuitInfo` | 5, 9, 12 |
| Radio transcription → searchable RAG (novel, optional) | OpenF1 `team_radio` mp3s | 9 (stretch) |

------------------------------------------------------------------------

## 6. Dependency risk — Ergast → jolpica-f1

FastF1's historical depth runs through **jolpica-f1**, the community
successor to the original Ergast API (which was wound down). FastF1
abstracts this behind its `backend='ergast'` interface, so the solution is
insulated at the code level. Log the risk anyway if ML/RAG build on deep
history: the jolpica service and its rate limits are the real dependency,
and historical coverage/latency should be verified before relying on it for
training data.

------------------------------------------------------------------------

## 7. Learning resources

- **OpenF1 — API documentation (endpoint list):** authoritative endpoint
  and field reference for ingestion.
- **FastF1 — Data Reference / Session API:** use for `results`, `laps`,
  `track_status`, telemetry and weather objects.
- **FastF1 — Circuit Information:** use for `CircuitInfo` track markers.
- **FastF1 — Ergast interface / jolpica-f1:** use for historical results,
  standings and lap/pit data before 2023.
