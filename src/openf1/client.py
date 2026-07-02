"""OpenF1 ingestion client.

A thin, typed wrapper over the Epic 2 :class:`~api.client.RestClient` (so it
inherits timeouts, retry/backoff and structured logging) exposing the OpenF1
endpoints the solution depends on — including the **settlement source-of-truth**
endpoints (`session_result`, `starting_grid`, `pit`, `position`) that ground the
Paddock Club registry (ADR-0008).

Methods return raw ``list[dict]``; Pydantic validation lands in story 4.3, and
pagination / explicit 429 handling in 4.2. OpenF1 is a public, no-auth API.
A qualifying ``session_key`` flows through the same methods as a race one, so
qualifying markets settle on the same path (see the endpoint→settlement mapping
in the README).
"""

import time
from collections.abc import Callable, Mapping
from typing import Any

from api.client import RestClient
from shared.logging import get_logger

DEFAULT_BASE_URL = "https://api.openf1.org/v1"

# Query-filter values OpenF1 accepts (equality on a field).
FilterValue = str | int | float | bool


class OpenF1Client:
    """Typed client for the OpenF1 REST API, built on the reusable REST client."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        *,
        timeout: float = 15.0,
        rest: RestClient | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._log = get_logger("openf1.client")
        self._rest = rest or RestClient(base_url, timeout=timeout, sleep=sleep)

    def _get(self, endpoint: str, filters: Mapping[str, FilterValue]) -> list[dict[str, Any]]:
        params = {key: value for key, value in filters.items() if value is not None}
        self._log.info("openf1 GET /%s %s", endpoint, params or "")
        response = self._rest.get(f"/{endpoint}", params=params or None)
        payload = response.json()
        if not isinstance(payload, list):
            return [payload]
        return payload

    # -- weekend / entry metadata ------------------------------------------

    def get_meetings(self, **filters: FilterValue) -> list[dict[str, Any]]:
        return self._get("meetings", filters)

    def get_sessions(self, **filters: FilterValue) -> list[dict[str, Any]]:
        return self._get("sessions", filters)

    def get_drivers(self, **filters: FilterValue) -> list[dict[str, Any]]:
        return self._get("drivers", filters)

    # -- settlement source-of-truth ----------------------------------------

    def get_session_result(self, **filters: FilterValue) -> list[dict[str, Any]]:
        return self._get("session_result", filters)

    def get_starting_grid(self, **filters: FilterValue) -> list[dict[str, Any]]:
        return self._get("starting_grid", filters)

    def get_laps(self, **filters: FilterValue) -> list[dict[str, Any]]:
        return self._get("laps", filters)

    def get_pit(self, **filters: FilterValue) -> list[dict[str, Any]]:
        return self._get("pit", filters)

    def get_position(self, **filters: FilterValue) -> list[dict[str, Any]]:
        return self._get("position", filters)

    # -- analytics / ML -----------------------------------------------------

    def get_stints(self, **filters: FilterValue) -> list[dict[str, Any]]:
        return self._get("stints", filters)

    def get_weather(self, **filters: FilterValue) -> list[dict[str, Any]]:
        return self._get("weather", filters)

    # -- lifecycle ----------------------------------------------------------

    def close(self) -> None:
        self._rest.close()

    def __enter__(self) -> "OpenF1Client":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
