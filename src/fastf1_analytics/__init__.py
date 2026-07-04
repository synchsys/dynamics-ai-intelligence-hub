"""FastF1 telemetry analytics (Epic 5).

Cache configuration + session loading (#39); reusable load/prepare/plot helpers
(#40) build on this. Requires the ``analytics`` extra (``pip install -e ".[analytics]"``).
"""

from fastf1_analytics.cache import DEFAULT_CACHE_DIR, configure_cache, load_session

__all__ = ["configure_cache", "load_session", "DEFAULT_CACHE_DIR"]
