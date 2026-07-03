"""Governed Azure OpenAI entrypoint — chat + embeddings.

One wrapper every LLM feature calls through: config from ``shared`` (no inline
secrets), **retry via ``shared.resilience``** on transient API errors, structured
logging, and a typed error model. Built on the official ``openai`` SDK's
``AzureOpenAI`` client; the SDK instance is injectable so tests run without
network or credentials.

Foundation for function calling (#61), structured outputs, the CRM assistant,
RAG generation (Epic 9), agents (Epic 10) and the Paddock free-text intake (#230).
"""

import time
from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from typing import Any

import openai

from ai.config import COGNITIVE_SCOPE, AzureOpenAIConfig
from ai.exceptions import AIAuthError, AIError, AIRateLimitError
from shared.logging import get_logger
from shared.resilience import retry

_logger = get_logger("ai.client")

# openai error types worth retrying (transient).
_TRANSIENT = (
    openai.APIConnectionError,
    openai.APITimeoutError,
    openai.RateLimitError,
    openai.InternalServerError,
)


def _is_transient(exc: BaseException) -> bool:
    return isinstance(exc, _TRANSIENT)


def build_sdk(config: AzureOpenAIConfig) -> Any:
    """Construct the Azure OpenAI SDK client (Entra token by default, or API key)."""
    from openai import AzureOpenAI

    if config.uses_key:
        return AzureOpenAI(
            azure_endpoint=config.endpoint, api_version=config.api_version, api_key=config.api_key
        )
    from azure.identity import ClientSecretCredential, get_bearer_token_provider

    credential = ClientSecretCredential(
        tenant_id=config.tenant_id or "",
        client_id=config.client_id or "",
        client_secret=config.client_secret or "",
    )
    return AzureOpenAI(
        azure_endpoint=config.endpoint,
        api_version=config.api_version,
        azure_ad_token_provider=get_bearer_token_provider(credential, COGNITIVE_SCOPE),
    )


class AIClient:
    """Chat + embeddings over Azure OpenAI, with shared retry and logging."""

    def __init__(
        self,
        config: AzureOpenAIConfig,
        *,
        sdk: Any | None = None,
        max_attempts: int = 3,
        base_delay: float = 0.5,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._config = config
        self._log = _logger
        self._sdk = sdk if sdk is not None else build_sdk(config)
        self._retry = retry(
            max_attempts=max_attempts,
            base_delay=base_delay,
            retry_on=_is_transient,
            sleep=sleep,
            logger=self._log,
        )

    @contextmanager
    def _translate(self) -> Iterator[None]:
        try:
            yield
        except openai.AuthenticationError as exc:
            raise AIAuthError(str(exc)) from exc
        except openai.RateLimitError as exc:
            raise AIRateLimitError(str(exc)) from exc
        except openai.OpenAIError as exc:
            raise AIError(str(exc)) from exc

    def chat(
        self,
        messages: Sequence[Mapping[str, Any]],
        *,
        temperature: float | None = None,
        **opts: Any,
    ) -> str:
        """Return the assistant's reply to a chat message list.

        ``temperature`` is omitted unless set — GPT-5-era reasoning models only
        accept the service default and 400 on any explicit value.
        """
        self._log.info("ai chat: %d message(s) -> %s", len(messages), self._config.chat_deployment)
        if temperature is not None:
            opts["temperature"] = temperature

        def _call() -> Any:
            return self._sdk.chat.completions.create(
                model=self._config.chat_deployment,
                messages=list(messages),
                **opts,
            )

        with self._translate():
            response = self._retry(_call)()
        return str(response.choices[0].message.content or "")

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        """Return an embedding vector per input string."""
        items = list(texts)
        self._log.info("ai embed: %d input(s) -> %s", len(items), self._config.embedding_deployment)

        def _call() -> Any:
            return self._sdk.embeddings.create(model=self._config.embedding_deployment, input=items)

        with self._translate():
            response = self._retry(_call)()
        return [list(item.embedding) for item in response.data]
