"""Typed error model for the Dataverse Web API client.

All Dataverse failures derive from :class:`DataverseError` (a
:class:`~shared.exceptions.ExternalServiceError`), so callers can catch the
whole family or a specific failure mode.
"""

from shared.exceptions import ExternalServiceError


class DataverseError(ExternalServiceError):
    """Base error for the Dataverse client."""


class DataverseAuthError(DataverseError):
    """Failed to acquire an access token for Dataverse."""


class DataverseNotFoundError(DataverseError):
    """The requested record or entity set was not found (HTTP 404)."""


class DataverseBatchError(DataverseError):
    """A ``$batch`` request reported one or more failed operations."""
