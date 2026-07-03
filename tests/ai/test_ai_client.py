"""Tests for the Azure OpenAI client (injected fake SDK, no network/creds)."""

from types import SimpleNamespace
from typing import Any

import httpx
import openai
import pytest

from ai import AIAuthError, AIClient, AIError, AIRateLimitError, AzureOpenAIConfig
from ai.client import _is_transient, build_sdk
from shared.exceptions import ConfigError

CONFIG = AzureOpenAIConfig(
    endpoint="https://x.openai.azure.com",
    chat_deployment="gpt-4o",
    embedding_deployment="text-embedding-3-small",
    api_key="k",
)


def _chat_response(text: str) -> SimpleNamespace:
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=text))])


def _embed_response(vectors: list[list[float]]) -> SimpleNamespace:
    return SimpleNamespace(data=[SimpleNamespace(embedding=v) for v in vectors])


class _Endpoint:
    def __init__(self, responder: Any) -> None:
        self._responder = responder
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        return self._responder(kwargs)


class FakeSDK:
    def __init__(self, chat: Any = None, embed: Any = None) -> None:
        self.chat = SimpleNamespace(
            completions=_Endpoint(chat or (lambda kw: _chat_response("ok")))
        )
        self.embeddings = _Endpoint(embed or (lambda kw: _embed_response([[0.0]])))


def make_client(sdk: FakeSDK, *, max_attempts: int = 2) -> AIClient:
    return AIClient(CONFIG, sdk=sdk, max_attempts=max_attempts, sleep=lambda _s: None)


def _timeout() -> openai.APITimeoutError:
    return openai.APITimeoutError(httpx.Request("POST", "https://x"))


def _status(exc_cls: type[openai.APIStatusError], code: int) -> openai.APIStatusError:
    resp = httpx.Response(code, request=httpx.Request("POST", "https://x"))
    return exc_cls("boom", response=resp, body=None)


# --- happy paths -----------------------------------------------------------


def test_chat_returns_content() -> None:
    sdk = FakeSDK(chat=lambda kw: _chat_response("hello world"))
    assert make_client(sdk).chat([{"role": "user", "content": "hi"}]) == "hello world"


def test_chat_sends_model_and_messages() -> None:
    sdk = FakeSDK()
    make_client(sdk).chat([{"role": "user", "content": "hi"}], temperature=0.7)
    call = sdk.chat.completions.calls[0]
    assert call["model"] == "gpt-4o"
    assert call["messages"] == [{"role": "user", "content": "hi"}]
    assert call["temperature"] == 0.7


def test_embed_returns_vectors() -> None:
    sdk = FakeSDK(embed=lambda kw: _embed_response([[0.1, 0.2], [0.3, 0.4]]))
    assert make_client(sdk).embed(["a", "b"]) == [[0.1, 0.2], [0.3, 0.4]]


def test_none_content_becomes_empty_string() -> None:
    sdk = FakeSDK(chat=lambda kw: _chat_response(None))  # type: ignore[arg-type]
    assert make_client(sdk).chat([{"role": "user", "content": "hi"}]) == ""


# --- retry + error mapping -------------------------------------------------


def test_chat_retries_transient_then_succeeds() -> None:
    calls = {"n": 0}

    def responder(kw: dict[str, Any]) -> Any:
        calls["n"] += 1
        if calls["n"] == 1:
            raise _timeout()
        return _chat_response("recovered")

    assert (
        make_client(FakeSDK(chat=responder), max_attempts=2).chat(
            [{"role": "user", "content": "x"}]
        )
        == "recovered"
    )
    assert calls["n"] == 2


def test_persistent_transient_maps_to_ai_error() -> None:
    def responder(kw: dict[str, Any]) -> Any:
        raise _timeout()

    with pytest.raises(AIError):
        make_client(FakeSDK(chat=responder), max_attempts=2).chat(
            [{"role": "user", "content": "x"}]
        )


def test_auth_error_maps_and_is_not_retried() -> None:
    calls = {"n": 0}

    def responder(kw: dict[str, Any]) -> Any:
        calls["n"] += 1
        raise _status(openai.AuthenticationError, 401)

    with pytest.raises(AIAuthError):
        make_client(FakeSDK(chat=responder), max_attempts=3).chat(
            [{"role": "user", "content": "x"}]
        )
    assert calls["n"] == 1  # auth errors are permanent


def test_rate_limit_maps_after_retries() -> None:
    def responder(kw: dict[str, Any]) -> Any:
        raise _status(openai.RateLimitError, 429)

    with pytest.raises(AIRateLimitError):
        make_client(FakeSDK(embed=responder), max_attempts=2).embed(["a"])


def test_is_transient_predicate() -> None:
    assert _is_transient(_timeout()) is True
    assert _is_transient(_status(openai.AuthenticationError, 401)) is False


# --- config ----------------------------------------------------------------


def test_config_from_env_and_key_auth() -> None:
    cfg = AzureOpenAIConfig.from_env(
        {
            "AZURE_OPENAI_ENDPOINT": "https://x.openai.azure.com/",
            "AZURE_OPENAI_CHAT_DEPLOYMENT": "gpt-4o",
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": "emb",
            "AZURE_OPENAI_API_KEY": "secret",
        }
    )
    assert cfg.endpoint == "https://x.openai.azure.com"  # trailing slash stripped
    assert cfg.uses_key is True


def test_config_defaults_to_entra_when_no_key() -> None:
    cfg = AzureOpenAIConfig.from_env(
        {
            "AZURE_OPENAI_ENDPOINT": "https://x",
            "AZURE_OPENAI_CHAT_DEPLOYMENT": "gpt-4o",
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": "emb",
            "AZURE_TENANT_ID": "t",
            "AZURE_CLIENT_ID": "c",
            "AZURE_CLIENT_SECRET": "s",
        }
    )
    assert cfg.uses_key is False
    assert cfg.tenant_id == "t"


def test_config_missing_required_raises() -> None:
    with pytest.raises(ConfigError, match="AZURE_OPENAI_CHAT_DEPLOYMENT"):
        AzureOpenAIConfig.from_env({"AZURE_OPENAI_ENDPOINT": "https://x"})


# --- SDK construction (build_sdk) ------------------------------------------


def test_build_sdk_key_auth(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}
    monkeypatch.setattr(openai, "AzureOpenAI", lambda **kw: captured.update(kw) or captured)
    build_sdk(CONFIG)
    assert captured["api_key"] == "k"
    assert captured["azure_endpoint"] == CONFIG.endpoint
    assert "azure_ad_token_provider" not in captured


def test_build_sdk_entra_auth(monkeypatch: pytest.MonkeyPatch) -> None:
    import azure.identity

    captured: dict[str, Any] = {}
    monkeypatch.setattr(openai, "AzureOpenAI", lambda **kw: captured.update(kw) or captured)
    monkeypatch.setattr(
        azure.identity, "ClientSecretCredential", lambda **kw: SimpleNamespace(**kw)
    )
    monkeypatch.setattr(azure.identity, "get_bearer_token_provider", lambda cred, scope: "token-fn")
    entra_config = AzureOpenAIConfig(
        endpoint="https://x.openai.azure.com",
        chat_deployment="gpt-4o",
        embedding_deployment="emb",
        tenant_id="t",
        client_id="c",
        client_secret="s",
    )
    build_sdk(entra_config)
    assert captured["azure_ad_token_provider"] == "token-fn"
    assert "api_key" not in captured
