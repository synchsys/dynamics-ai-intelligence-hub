"""Standard telemetry plots (#40).

Thin matplotlib helpers over a laps table — lap-pace-by-lap and fastest-lap
bars. Each takes a DataFrame and an optional ``Axes`` (created if omitted) and
returns the ``Axes``, so plots are composable and testable headlessly without
rendering a window.
"""

from collections.abc import Sequence

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes

from fastf1_analytics.analysis import clean_laps, fastest_by_driver


def plot_lap_pace(
    laps: pd.DataFrame, *, drivers: Sequence[str] | None = None, ax: Axes | None = None
) -> Axes:
    """Line plot of lap time (seconds) vs lap number, one line per driver."""
    cleaned = clean_laps(laps)
    if drivers is not None:
        cleaned = cleaned[cleaned["Driver"].isin(drivers)]
    if ax is None:
        _fig, ax = plt.subplots()
    for driver, group in cleaned.groupby("Driver"):
        ordered = group.sort_values("LapNumber")
        ax.plot(ordered["LapNumber"], ordered["LapTimeSeconds"], marker="o", label=str(driver))
    ax.set_xlabel("Lap")
    ax.set_ylabel("Lap time (s)")
    ax.set_title("Lap pace")
    ax.legend()
    return ax


def plot_fastest_laps(laps: pd.DataFrame, *, ax: Axes | None = None) -> Axes:
    """Horizontal bar of each driver's fastest lap (fastest at the top)."""
    fastest = fastest_by_driver(laps)
    if ax is None:
        _fig, ax = plt.subplots()
    # Fastest at the top: plot in reverse so the smallest time sits highest.
    ordered = fastest.iloc[::-1]
    ax.barh(ordered["Driver"].astype(str), ordered["LapTimeSeconds"])
    ax.set_xlabel("Fastest lap (s)")
    ax.set_title("Fastest lap by driver")
    return ax
