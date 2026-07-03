"""Azure OpenAI integration — the governed LLM entrypoint (Epic 8).

A single client wrapping chat + embeddings, built on the ``openai`` SDK with
``shared`` config/retry/logging. Foundation for function calling, structured
outputs, the CRM assistant, RAG and agents.
"""

from ai.client import AIClient, build_sdk
from ai.config import AzureOpenAIConfig
from ai.crm_tools import ApprovalBroker, ApprovalError, CrmActionTools, build_crm_tools
from ai.exceptions import AIAuthError, AIError, AIRateLimitError
from ai.prompt_log import DataversePromptLogger, NullLogger, PromptLogger
from ai.structured import structured_output

__all__ = [
    "AIClient",
    "build_sdk",
    "AzureOpenAIConfig",
    "AIError",
    "AIAuthError",
    "AIRateLimitError",
    "structured_output",
    "PromptLogger",
    "NullLogger",
    "DataversePromptLogger",
    "build_crm_tools",
    "CrmActionTools",
    "ApprovalBroker",
    "ApprovalError",
]
