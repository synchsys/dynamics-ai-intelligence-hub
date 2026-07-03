"""Typed error model for the Azure OpenAI client."""

from shared.exceptions import ExternalServiceError


class AIError(ExternalServiceError):
    """Base error for LLM calls."""


class AIAuthError(AIError):
    """Authentication/authorization failure against Azure OpenAI."""


class AIRateLimitError(AIError):
    """The model endpoint rate-limited the request (429)."""
