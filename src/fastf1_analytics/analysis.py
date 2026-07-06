"""Lap-data preparation helpers (#40).

Pure pandas transforms over a FastF1 laps table — clean/convert lap times, and
summarise fastest laps and stints — so notebooks stay thin and the logic is
unit-testable with small fixtures (no FastF1 or network needed). ``session_laps``
is the one convenience that touches FastF1, via the #39 loader.
"""

from pathlib import Path
from typing import Any

import pandas as pd

from fastf1_analytics.cache import load_session


def to_seconds(lap_time: "pd.Series[Any]") -> "pd.Series[float]":
    """Convert a Timedelta lap-time series to float seconds."""
    return pd.to_timedelta(lap_time).dt.total_seconds()


def clean_laps(laps: pd.DataFrame, *, accurate_only: bool = False) -> pd.DataFrame:
    """Return laps with a numeric ``LapTimeSeconds`` column, dropping timeless laps.

    With ``accurate_only`` (and an ``IsAccurate`` column present), keeps only laps
    FastF1 marked accurate — the right default for pace analysis.
    """
    out = laps.copy()
    out["LapTimeSeconds"] = to_seconds(out["LapTime"])
    out = out[out["LapTimeSeconds"].notna()]
    if accurate_only and "IsAccurate" in out.columns:
        out = out[out["IsAccurate"]]
    return out.reset_index(drop=True)


def fastest_by_driver(laps: pd.DataFrame) -> pd.DataFrame:
    """Fastest lap per driver, ascending — columns ``Driver``, ``LapTimeSeconds``."""
    cleaned = clean_laps(laps)
    fastest = (
        cleaned.groupby("Driver", as_index=False)["LapTimeSeconds"]
        .min()
        .sort_values("LapTimeSeconds", ignore_index=True)
    )
    return fastest


def stint_summary(laps: pd.DataFrame) -> pd.DataFrame:
    """Per driver+stint: compound, lap count, and average pace (seconds)."""
    cleaned = clean_laps(laps)
    grouped = cleaned.groupby(["Driver", "Stint"], as_index=False).agg(
        Compound=("Compound", "first"),
        Laps=("LapTimeSeconds", "size"),
        AvgLapSeconds=("LapTimeSeconds", "mean"),
    )
    grouped["AvgLapSeconds"] = grouped["AvgLapSeconds"].round(3)
    return grouped


def session_laps(
    year: int, event: str | int, session: str = "R", *, cache: str | Path | None = None
) -> pd.DataFrame:
    """Load a session (via #39) and return its cleaned laps DataFrame."""
    loaded = load_session(year, event, session, cache=cache)
    return clean_laps(loaded.laps)
