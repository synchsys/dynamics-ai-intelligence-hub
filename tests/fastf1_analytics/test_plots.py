"""Tests for the telemetry plot helpers (headless Agg backend)."""

import matplotlib.pyplot as plt
import pandas as pd

from fastf1_analytics import plot_fastest_laps, plot_lap_pace


def _laps() -> pd.DataFrame:
    td = pd.to_timedelta
    return pd.DataFrame(
        {
            "Driver": ["HAM", "HAM", "VER", "VER"],
            "LapNumber": [1, 2, 1, 2],
            "LapTime": [td("0:01:35.8"), td("0:01:34.2"), td("0:01:35.1"), td("0:01:33.9")],
            "Stint": [1, 1, 1, 1],
            "Compound": ["MEDIUM", "MEDIUM", "SOFT", "SOFT"],
        }
    )


def test_plot_lap_pace_one_line_per_driver() -> None:
    ax = plot_lap_pace(_laps())
    assert len(ax.get_lines()) == 2  # HAM + VER
    assert ax.get_xlabel() == "Lap" and ax.get_ylabel() == "Lap time (s)"
    legend = ax.get_legend()
    assert legend is not None
    assert {t.get_text() for t in legend.get_texts()} == {"HAM", "VER"}
    plt.close("all")


def test_plot_lap_pace_driver_filter() -> None:
    ax = plot_lap_pace(_laps(), drivers=["VER"])
    assert len(ax.get_lines()) == 1
    plt.close("all")


def test_plot_lap_pace_uses_supplied_axes() -> None:
    _fig, ax = plt.subplots()
    returned = plot_lap_pace(_laps(), ax=ax)
    assert returned is ax
    plt.close("all")


def test_plot_fastest_laps_one_bar_per_driver() -> None:
    ax = plot_fastest_laps(_laps())
    assert len(ax.patches) == 2  # one bar per driver
    assert ax.get_xlabel() == "Fastest lap (s)"
    plt.close("all")


def test_plot_fastest_laps_uses_supplied_axes() -> None:
    _fig, ax = plt.subplots()
    assert plot_fastest_laps(_laps(), ax=ax) is ax
    plt.close("all")
