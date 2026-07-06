"""Tests for lap-data prep helpers (pure pandas, small fixtures)."""

from types import SimpleNamespace
from typing import Any

import pandas as pd
import pytest

import fastf1_analytics.analysis as analysis_mod
from fastf1_analytics import (
    clean_laps,
    fastest_by_driver,
    session_laps,
    stint_summary,
    to_seconds,
)


def _laps() -> pd.DataFrame:
    td = pd.to_timedelta
    return pd.DataFrame(
        {
            "Driver": ["HAM", "HAM", "VER", "VER", "VER"],
            "LapNumber": [1, 2, 1, 2, 3],
            "LapTime": [
                td("0:01:35.8"),
                td("0:01:34.2"),
                td("0:01:35.1"),
                td("0:01:33.9"),
                pd.NaT,  # timeless lap — dropped by clean_laps
            ],
            "Stint": [1, 1, 1, 1, 2],
            "Compound": ["MEDIUM", "MEDIUM", "SOFT", "SOFT", "HARD"],
            "IsAccurate": [True, True, True, False, True],
        }
    )


def test_to_seconds_converts_timedelta() -> None:
    secs = to_seconds(pd.Series(pd.to_timedelta(["0:01:35.8", "0:01:34.2"])))
    assert list(secs) == [95.8, 94.2]


def test_clean_laps_adds_seconds_and_drops_timeless() -> None:
    cleaned = clean_laps(_laps())
    assert "LapTimeSeconds" in cleaned.columns
    assert len(cleaned) == 4  # the NaT lap is gone
    assert cleaned["LapTimeSeconds"].tolist() == [95.8, 94.2, 95.1, 93.9]


def test_clean_laps_accurate_only_filters() -> None:
    cleaned = clean_laps(_laps(), accurate_only=True)
    # VER lap 2 (IsAccurate False) removed; 3 accurate timed laps remain.
    assert len(cleaned) == 3
    assert (cleaned["Driver"] == "VER").sum() == 1  # only VER's accurate lap 1 remains


def test_clean_laps_accurate_only_without_column_is_noop() -> None:
    laps = _laps().drop(columns=["IsAccurate"])
    assert len(clean_laps(laps, accurate_only=True)) == 4


def test_fastest_by_driver_sorted_ascending() -> None:
    fastest = fastest_by_driver(_laps())
    assert fastest["Driver"].tolist() == ["VER", "HAM"]  # VER 93.9 < HAM 94.2
    assert fastest["LapTimeSeconds"].tolist() == [93.9, 94.2]


def test_stint_summary_aggregates_per_driver_stint() -> None:
    summary = stint_summary(_laps())
    ham = summary[(summary["Driver"] == "HAM") & (summary["Stint"] == 1)].iloc[0]
    assert ham["Compound"] == "MEDIUM" and ham["Laps"] == 2 and ham["AvgLapSeconds"] == 95.0
    ver1 = summary[(summary["Driver"] == "VER") & (summary["Stint"] == 1)].iloc[0]
    assert ver1["Laps"] == 2 and ver1["AvgLapSeconds"] == 94.5
    # VER stint 2 was only the timeless lap -> dropped, so it isn't summarised.
    assert summary[(summary["Driver"] == "VER") & (summary["Stint"] == 2)].empty


def test_session_laps_loads_and_cleans(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_session = SimpleNamespace(laps=_laps())
    captured: dict[str, Any] = {}

    def fake_load(year: int, event: Any, session: str, *, cache: Any = None) -> Any:
        captured["args"] = (year, event, session)
        return fake_session

    monkeypatch.setattr(analysis_mod, "load_session", fake_load)
    result = session_laps(2023, "Singapore", "R")
    assert captured["args"] == (2023, "Singapore", "R")
    assert "LapTimeSeconds" in result.columns and len(result) == 4
