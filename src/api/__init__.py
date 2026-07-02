"""Reusable REST client package.

A resilient, typed HTTP client built on the ``shared`` utilities. Foundation
for OpenF1 ingestion (Epic 4) and any future REST integration.
"""

from api.client import RestClient
from api.exceptions import (
    ApiConnectionError,
    ApiError,
    ApiStatusError,
    ApiTimeoutError,
)

__all__ = [
    "RestClient",
    "ApiError",
    "ApiConnectionError",
    "ApiTimeoutError",
    "ApiStatusError",
]
