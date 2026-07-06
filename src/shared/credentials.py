"""Production identity + secret resolution (#28, Epic 11).

The sanctioned way to get an Entra credential and to read secrets, so production
runs with **no secrets in source or config**:

* :func:`azure_credential` returns a ``DefaultAzureCredential`` — **Managed
  Identity** when deployed to Azure, and local dev credentials (the service-
  principal env vars, or ``az login``) otherwise. Services use this instead of a
  hard-coded ``ClientSecretCredential``, so there is no client secret in code.
* :class:`SecretResolver` reads secrets from **Key Vault** when ``KEY_VAULT_URL``
  is set (production) and from the environment (``.env``) otherwise (dev).

Local development still uses ``.env``; production uses Key Vault + Managed
Identity (see ``docs/security/secrets-and-identity.md`` and ADR-0003).
"""

import os
from collections.abc import Callable, Mapping
from typing import Any

from shared.exceptions import ConfigError
from shared.logging import get_logger

_logger = get_logger("shared.credentials")


def azure_credential() -> Any:
    """The Entra credential for service-to-service auth (MI in Azure, dev creds locally)."""
    from azure.identity import DefaultAzureCredential

    return DefaultAzureCredential()


def _to_secret_name(name: str) -> str:
    """Environment-style name → Key Vault secret name (KV allows only alphanumerics + '-')."""
    return name.replace("_", "-")


class SecretResolver:
    """Resolve secrets from Key Vault (production) or the environment (dev)."""

    def __init__(
        self,
        *,
        vault_url: str | None = None,
        env: Mapping[str, str] | None = None,
        credential_factory: Callable[[], Any] = azure_credential,
    ) -> None:
        source = os.environ if env is None else env
        self._vault_url = vault_url if vault_url is not None else source.get("KEY_VAULT_URL")
        self._env = source
        self._credential_factory = credential_factory
        self._client: Any | None = None

    @property
    def uses_key_vault(self) -> bool:
        return bool(self._vault_url)

    def resolve(self, name: str) -> str:
        """Return the secret ``name``, from Key Vault if configured else the environment."""
        if self._vault_url:
            return self._from_vault(name)
        value = self._env.get(name)
        if not value:
            raise ConfigError(f"secret '{name}' not found in environment")
        return value

    def _from_vault(self, name: str) -> str:
        from azure.keyvault.secrets import SecretClient

        assert self._vault_url is not None  # only reached when a vault is configured
        if self._client is None:
            self._client = SecretClient(
                vault_url=self._vault_url, credential=self._credential_factory()
            )
            _logger.info("resolving secrets from Key Vault %s", self._vault_url)
        return str(self._client.get_secret(_to_secret_name(name)).value)
