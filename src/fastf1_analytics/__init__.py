"""FastF1 telemetry analytics (Epic 5).

Cache configuration + session loading (#39); reusable load/prepare/plot helpers
(#40) build on this. Requires the ``analytics`` extra (``pip install -e ".[analytics]"``).
"""

from fastf1_analytics.analysis import (
    clean_laps,
    fastest_by_driver,
    session_laps,
    stint_summary,
    to_seconds,
)
from fastf1_analytics.cache import DEFAULT_CACHE_DIR, configure_cache, load_session
from fastf1_analytics.plots import plot_fastest_laps, plot_lap_pace

__all__ = [
    # cache / load (#39)
    "configure_cache",
    "load_session",
    "DEFAULT_CACHE_DIR",
    # prep (#40)
    "to_seconds",
    "clean_laps",
    "fastest_by_driver",
    "stint_summary",
    "session_laps",
    # plots (#40)
    "plot_lap_pace",
    "plot_fastest_laps",
]
