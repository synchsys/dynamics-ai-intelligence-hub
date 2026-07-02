"""Typed error model for the reusable REST client.

All REST failures derive from :class:`ApiError` (itself a
:class:`~shared.exceptions.ExternalServiceError`), so callers can catch the
whole family or a specific failure mode. Transient subclasses
(:class:`ApiConnectionError`, :class:`ApiTimeoutError`, and
:class:`ApiStatusError` for 429/5xx) are what the retry layer treats as
retryable.
"""

from shared.exceptions import ExternalServiceError


class ApiError(ExternalServiceError):
    """Base error for the REST client."""


class ApiConnectionError(ApiError):
    """A transport/network failure (transient)."""


class ApiTimeoutError(ApiError):
    """The request exceeded its timeout (transient)."""


class ApiStatusError(ApiError):
    """The server returned a non-2xx status.

    Carries the HTTP ``status_code`` and response ``body`` so callers can
    branch on them.
    """

    def __init__(self, status_code: int, body: str, message: str | None = None) -> None:
        self.status_code = status_code
        self.body = body
        super().__init__(message or f"HTTP {status_code}: {body[:200]}")
