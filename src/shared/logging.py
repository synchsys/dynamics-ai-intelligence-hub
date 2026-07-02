"""Structured, JSON-friendly logging with a correlation id.

:func:`configure_logging` installs a formatter on the root logger,
:func:`get_logger` returns a namespaced logger, and :func:`bind_correlation_id`
sets a ``contextvars`` value that is attached to every emitted record so a
single request can be traced across async calls and Azure Functions invocations
without threading an id through every function signature.
"""

import json
import logging
import uuid
from contextvars import ContextVar
from typing import Any

_correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)


class JsonFormatter(logging.Formatter):
    """Render log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        correlation_id = _correlation_id.get()
        if correlation_id is not None:
            payload["correlation_id"] = correlation_id
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def bind_correlation_id(value: str | None = None) -> str:
    """Bind a correlation id to the current context, generating one if needed.

    Returns the id that was bound.
    """
    correlation_id = value or uuid.uuid4().hex
    _correlation_id.set(correlation_id)
    return correlation_id


def get_correlation_id() -> str | None:
    """Return the correlation id bound to the current context, if any."""
    return _correlation_id.get()


def configure_logging(level: str | None = None, *, json_output: bool = True) -> None:
    """Configure root logging.

    Replaces existing handlers with a single stream handler using either the
    :class:`JsonFormatter` or a plain human-readable format.
    """
    handler = logging.StreamHandler()
    if json_output:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter("%(levelname)s %(name)s %(message)s"))
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level or "INFO")


def get_logger(name: str) -> logging.Logger:
    """Return a namespaced logger."""
    return logging.getLogger(name)
