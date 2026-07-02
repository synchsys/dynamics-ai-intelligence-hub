"""Dataverse connection configuration.

Loaded from the environment (``.env`` locally, CI/Key Vault in deployment).
Secrets never live in source. The client-credentials token ``scope`` and the
Web API ``api_base`` are derived from the environment URL.
"""

import os
from collections.abc import Mapping
from dataclasses import dataclass

from shared.exceptions import ConfigError

_REQUIRED = ("DATAVERSE_URL", "AZURE_TENANT_ID", "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET")
API_VERSION = "v9.2"


@dataclass(frozen=True)
class DataverseConfig:
    """Immutable Dataverse connection settings."""

    dataverse_url: str
    tenant_id: str
    client_id: str
    client_secret: str

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "DataverseConfig":
        """Build config from environment variables, raising ``ConfigError`` if any are missing."""
        source = os.environ if env is None else env
        missing = [key for key in _REQUIRED if not source.get(key)]
        if missing:
            raise ConfigError(f"Missing Dataverse environment variables: {', '.join(missing)}")
        return cls(
            dataverse_url=source["DATAVERSE_URL"].rstrip("/"),
            tenant_id=source["AZURE_TENANT_ID"],
            client_id=source["AZURE_CLIENT_ID"],
            client_secret=source["AZURE_CLIENT_SECRET"],
        )

    @property
    def scope(self) -> str:
        """OAuth scope for the client-credentials flow."""
        return f"{self.dataverse_url}/.default"

    @property
    def api_base(self) -> str:
        """Base URL of the Dataverse Web API."""
        return f"{self.dataverse_url}/api/data/{API_VERSION}"
