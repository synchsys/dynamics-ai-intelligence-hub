"""Reusable REST client built on the shared resilience and logging utilities.

A thin wrapper over ``httpx`` that adds timeout handling, retry-with-backoff
(via :func:`shared.resilience.retry` — not a local copy), structured logging
and a typed error model. OpenF1 ingestion (Epic 4) and any future REST
integration build on this instead of hand-rolling HTTP boilerplate.

**Transport decision (story #35):** ``httpx`` — modern, typed, first-class
timeouts, and sync + async support for the later Azure Functions work.
"""

import time
from collections.abc import Callable, Mapping
from types import TracebackType
from typing import Any

import httpx

from api.exceptions import (
    ApiConnectionError,
    ApiStatusError,
    ApiTimeoutError,
)
from shared.logging import get_logger
from shared.resilience import retry

# Cap on how long a server-provided Retry-After can make us wait.
_MAX_RETRY_AFTER = 120.0


def _is_transient(exc: BaseException) -> bool:
    """Classify which REST failures are worth retrying."""
    if isinstance(exc, ApiConnectionError | ApiTimeoutError):
        return True
    if isinstance(exc, ApiStatusError):
        return exc.status_code == 429 or 500 <= exc.status_code < 600
    return False


def _parse_retry_after(value: str | None) -> float | None:
    """Parse a ``Retry-After`` header value (numeric seconds form only).

    The HTTP-date form falls back to ``None`` so the caller uses normal backoff.
    """
    if value is None:
        return None
    value = value.strip()
    if value.isdigit():
        return float(value)
    return None


def _retry_after_delay(exc: BaseException, computed: float) -> float:
    """Honour a server ``Retry-After`` (capped) over the computed backoff."""
    if isinstance(exc, ApiStatusError) and exc.retry_after is not None:
        return min(exc.retry_after, _MAX_RETRY_AFTER)
    return computed


class RestClient:
    """A configurable, resilient REST client.

    Exposes ``get``/``post``/``request`` returning the raw ``httpx.Response``.
    Transient failures (connection errors, timeouts, 429/5xx) are retried with
    exponential backoff and jitter; permanent failures (4xx) raise immediately.
    """

    def __init__(
        self,
        base_url: str,
        *,
        headers: Mapping[str, str] | None = None,
        timeout: float = 10.0,
        max_attempts: int = 3,
        base_delay: float = 0.5,
        transport: httpx.BaseTransport | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._log = get_logger("api.client")
        self._client = httpx.Client(
            base_url=base_url.rstrip("/"),
            headers=dict(headers or {}),
            timeout=timeout,
            transport=transport,
        )
        # Retry wraps the single-shot request using the SHARED decorator,
        # honouring a server Retry-After header on 429 via delay_override.
        self._do_request = retry(
            max_attempts=max_attempts,
            base_delay=base_delay,
            retry_on=_is_transient,
            sleep=sleep,
            logger=self._log,
            delay_override=_retry_after_delay,
        )(self._request_once)

    def _request_once(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        try:
            response = self._client.request(method, url, **kwargs)
        except httpx.TimeoutException as exc:
            raise ApiTimeoutError(f"{method} {url} timed out") from exc
        except httpx.TransportError as exc:
            raise ApiConnectionError(f"{method} {url} failed: {exc}") from exc
        if response.is_error:
            raise ApiStatusError(
                response.status_code,
                response.text,
                retry_after=_parse_retry_after(response.headers.get("Retry-After")),
            )
        return response

    def request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        self._log.info("%s %s", method, path)
        return self._do_request(method, path, **kwargs)

    def get(self, path: str, **kwargs: Any) -> httpx.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> httpx.Response:
        return self.request("POST", path, **kwargs)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "RestClient":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()
