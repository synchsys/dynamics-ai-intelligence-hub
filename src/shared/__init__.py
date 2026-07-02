"""Shared utilities for the Dynamics AI Intelligence Hub.

Configuration loading, structured logging and the common exception hierarchy —
imported across every later epic. Resilience utilities (timeout + retry) live
in ``shared.resilience`` (story #23).
"""

from shared.config import Settings, get_settings
from shared.exceptions import (
    ConfigError,
    ExternalServiceError,
    SharedError,
    ValidationError,
)
from shared.logging import (
    JsonFormatter,
    bind_correlation_id,
    configure_logging,
    get_correlation_id,
    get_logger,
)
from shared.resilience import (
    TimeoutExceededError,
    compute_backoff,
    retry,
    run_with_timeout,
    with_timeout,
)

__version__ = "0.1.0"

__all__ = [
    "Settings",
    "get_settings",
    "JsonFormatter",
    "bind_correlation_id",
    "configure_logging",
    "get_correlation_id",
    "get_logger",
    "SharedError",
    "ConfigError",
    "ValidationError",
    "ExternalServiceError",
    "TimeoutExceededError",
    "retry",
    "run_with_timeout",
    "with_timeout",
    "compute_backoff",
    "__version__",
]
