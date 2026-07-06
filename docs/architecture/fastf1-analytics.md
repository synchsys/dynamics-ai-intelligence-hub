# FastF1 analytics helpers

Reusable load / prepare / plot helpers (`src/fastf1_analytics`, #39–#40) so
telemetry notebooks stay thin and the logic is tested. The prep functions are
pure pandas (unit-tested with small fixtures, no FastF1/network); only the load
helpers touch FastF1.

## API

**Cache & load (#39)**
- `configure_cache(path=None) -> Path` — enable FastF1's on-disk cache (default
  `datasets/fastf1-cache/`, git-ignored). Idempotent.
- `load_session(year, event, session="R", *, cache=None, telemetry=False, weather=False, messages=False)`
  — return a loaded FastF1 session (heavy extras off by default).

**Prepare (#40)** — operate on a laps DataFrame
- `to_seconds(series) -> Series[float]` — Timedelta lap times → seconds.
- `clean_laps(laps, *, accurate_only=False) -> DataFrame` — add `LapTimeSeconds`,
  drop timeless laps, optionally keep only FastF1-accurate laps.
- `fastest_by_driver(laps) -> DataFrame` — fastest lap per driver, ascending.
- `stint_summary(laps) -> DataFrame` — per driver+stint: compound, lap count,
  average pace.
- `session_laps(year, event, session="R", *, cache=None) -> DataFrame` — load +
  clean in one call.

**Plot (#40)** — take a laps DataFrame + optional `Axes`, return the `Axes`
- `plot_lap_pace(laps, *, drivers=None, ax=None)` — lap time vs lap number per driver.
- `plot_fastest_laps(laps, *, ax=None)` — horizontal bar of each driver's fastest lap.

## Usage

`notebooks/lap-telemetry.ipynb` is the thin reference — it imports the helpers
and calls `session_laps` → `plot_lap_pace` / `plot_fastest_laps` / `stint_summary`
in a few lines. Feature engineering (#51) and the ML models (#49, #53) build on
`clean_laps` / `stint_summary`.

## Testing

Prep helpers are unit-tested with tiny fixtures; plots are tested headlessly
(Agg backend) by asserting line/bar counts and labels; `load_session` /
`session_laps` are tested with FastF1 monkeypatched. Live-verified via
`scripts/analytics/verify_fastf1.py`.
