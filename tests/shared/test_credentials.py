"""Tests for production identity + secret resolution (#28)."""

from typing import Any

import pytest

import shared.credentials as credentials_mod
from shared import SecretResolver, azure_credential
from shared.exceptions import ConfigError

# --- azure_credential -------------------------------------------------------


def test_azure_credential_uses_default_azure_credential(monkeypatch: pytest.MonkeyPatch) -> None:
    import azure.identity

    monkeypatch.setattr(azure.identity, "DefaultAzureCredential", lambda: "the-credential")
    assert azure_credential() == "the-credential"


# --- SecretResolver: environment (dev) --------------------------------------


def test_resolves_from_environment_when_no_vault() -> None:
    resolver = SecretResolver(env={"AZURE_CLIENT_SECRET": "dev-secret"})
    assert not resolver.uses_key_vault
    assert resolver.resolve("AZURE_CLIENT_SECRET") == "dev-secret"


def test_missing_env_secret_raises() -> None:
    with pytest.raises(ConfigError, match="AZURE_CLIENT_SECRET"):
        SecretResolver(env={}).resolve("AZURE_CLIENT_SECRET")


# --- SecretResolver: Key Vault (production) ---------------------------------


class FakeSecretClient:
    def __init__(self, vault_url: str, credential: Any) -> None:
        self.vault_url = vault_url
        self.credential = credential
        self.requested: list[str] = []

    def get_secret(self, name: str) -> Any:
        self.requested.append(name)
        return type("S", (), {"value": f"kv:{name}"})()


def test_resolves_from_key_vault_when_url_set(monkeypatch: pytest.MonkeyPatch) -> None:
    created: dict[str, Any] = {}

    def fake_client(vault_url: str, credential: Any) -> FakeSecretClient:
        client = FakeSecretClient(vault_url, credential)
        created["client"] = client
        return client

    monkeypatch.setattr("azure.keyvault.secrets.SecretClient", fake_client)
    resolver = SecretResolver(
        vault_url="https://v.vault.azure.net", credential_factory=lambda: "cred"
    )
    assert resolver.uses_key_vault
    # underscores map to Key Vault's dash naming
    assert resolver.resolve("AZURE_CLIENT_SECRET") == "kv:AZURE-CLIENT-SECRET"
    assert created["client"].vault_url == "https://v.vault.azure.net"
    assert created["client"].credential == "cred"


def test_key_vault_client_is_created_once(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = {"n": 0}

    def fake_client(vault_url: str, credential: Any) -> FakeSecretClient:
        calls["n"] += 1
        return FakeSecretClient(vault_url, credential)

    monkeypatch.setattr("azure.keyvault.secrets.SecretClient", fake_client)
    resolver = SecretResolver(vault_url="https://v.vault.azure.net", credential_factory=lambda: "c")
    resolver.resolve("A")
    resolver.resolve("B")
    assert calls["n"] == 1  # client reused across lookups


def test_vault_url_from_env() -> None:
    resolver = SecretResolver(env={"KEY_VAULT_URL": "https://v.vault.azure.net"})
    assert resolver.uses_key_vault


def test_to_secret_name_maps_underscores() -> None:
    assert credentials_mod._to_secret_name("AZURE_CLIENT_SECRET") == "AZURE-CLIENT-SECRET"
