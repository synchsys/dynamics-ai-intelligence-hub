"""Authenticated Dataverse Web API client package.

The single governed persistence layer for the platform — CRUD, upsert and
``$batch`` over the generic CRM entities, built on the ``api`` REST client and
``shared`` utilities. Imported by OpenF1 persistence, FastF1 summaries and AI
request/response logging.
"""

from dataverse.client import DataverseClient
from dataverse.config import DataverseConfig
from dataverse.exceptions import (
    DataverseAuthError,
    DataverseBatchError,
    DataverseError,
    DataverseNotFoundError,
)

__all__ = [
    "DataverseClient",
    "DataverseConfig",
    "DataverseError",
    "DataverseAuthError",
    "DataverseNotFoundError",
    "DataverseBatchError",
]
