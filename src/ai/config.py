"""Azure OpenAI connection configuration.

Loaded from the environment (``.env`` locally). No secrets in source. Auth is
**Entra token by default** (reusing the Dataverse service principal — grant it
the *Cognitive Services OpenAI User* role on the resource), with an optional
``AZURE_OPENAI_API_KEY`` override for quick local spikes.
"""

import os
from collections.abc import Mapping
from dataclasses import dataclass

from shared.exceptions import ConfigError

# Token scope for Entra-authenticated Azure OpenAI / Cognitive Services calls.
COGNITIVE_SCOPE = "https://cognitiveservices.azure.com/.default"
_REQUIRED = (
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_CHAT_DEPLOYMENT",
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT",
)


@dataclass(frozen=True)
class AzureOpenAIConfig:
    """Immutable Azure OpenAI settings."""

    endpoint: str
    chat_deployment: str
    embedding_deployment: str
    api_version: str = "2024-10-21"
    api_key: str | None = None
    # Entra service principal (reused from Dataverse) when no api_key is set.
    tenant_id: str | None = None
    client_id: str | None = None
    client_secret: str | None = None

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "AzureOpenAIConfig":
        source = os.environ if env is None else env
        missing = [k for k in _REQUIRED if not source.get(k)]
        if missing:
            raise ConfigError(f"Missing Azure OpenAI environment variables: {', '.join(missing)}")
        return cls(
            endpoint=source["AZURE_OPENAI_ENDPOINT"].rstrip("/"),
            chat_deployment=source["AZURE_OPENAI_CHAT_DEPLOYMENT"],
            embedding_deployment=source["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"],
            api_version=source.get("AZURE_OPENAI_API_VERSION", "2024-10-21"),
            api_key=source.get("AZURE_OPENAI_API_KEY") or None,
            tenant_id=source.get("AZURE_TENANT_ID"),
            client_id=source.get("AZURE_CLIENT_ID"),
            client_secret=source.get("AZURE_CLIENT_SECRET"),
        )

    @property
    def uses_key(self) -> bool:
        return self.api_key is not None
