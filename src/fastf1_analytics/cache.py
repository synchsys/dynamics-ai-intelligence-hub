"""FastF1 configuration and session loading (#39).

Configures a persistent, git-ignored FastF1 cache so telemetry loads are fast and
reproducible (a session loads from cache on the second run — measurably faster,
and offline). `load_session` is the thin entry point the telemetry helpers (#40)
and notebooks build on.

Install the analytics extra to use this: ``pip install -e ".[analytics]"``.
"""

from pathlib import Path
from typing import Any

import fastf1

from shared.logging import get_logger

_logger = get_logger("fastf1_analytics.cache")

# Default cache location — git-ignored (see .gitignore).
DEFAULT_CACHE_DIR = Path("datasets/fastf1-cache")


def configure_cache(path: str | Path | None = None) -> Path:
    """Enable FastF1's on-disk cache at ``path`` (default :data:`DEFAULT_CACHE_DIR`).

    Creates the directory if needed and returns it. Idempotent — safe to call
    before every load.
    """
    cache_dir = Path(path) if path is not None else DEFAULT_CACHE_DIR
    cache_dir.mkdir(parents=True, exist_ok=True)
    fastf1.Cache.enable_cache(str(cache_dir))
    _logger.info("fastf1 cache enabled at %s", cache_dir)
    return cache_dir


def load_session(
    year: int,
    event: str | int,
    session: str = "R",
    *,
    cache: str | Path | None = None,
    telemetry: bool = False,
    weather: bool = False,
    messages: bool = False,
) -> Any:
    """Load and return a FastF1 session (cache configured first).

    ``event`` is a round number or event name (e.g. ``"Singapore"``); ``session``
    is ``"R"``/``"Q"``/``"FP1"`` etc. Heavy extras (telemetry/weather/race-control
    messages) are off by default — lap data is what most analysis needs.
    """
    configure_cache(cache)
    loaded = fastf1.get_session(year, event, session)
    loaded.load(telemetry=telemetry, weather=weather, messages=messages)
    _logger.info("loaded %s %s %s", year, event, session)
    return loaded
