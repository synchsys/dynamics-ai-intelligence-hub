"""Common exception hierarchy for the Dynamics AI Intelligence Hub.

Every application-specific exception derives from :class:`SharedError`, giving
callers a single base to catch and one place to add cross-cutting behaviour.
Downstream epics subclass these (e.g. a Dataverse or OpenF1 client extends
:class:`ExternalServiceError`).
"""


class SharedError(Exception):
    """Base class for all application-specific errors."""


class ConfigError(SharedError):
    """Raised when configuration is missing, malformed or invalid."""


class ValidationError(SharedError):
    """Raised when data fails an internal validation check."""


class ExternalServiceError(SharedError):
    """Base for failures talking to an external service (REST API, Dataverse)."""
