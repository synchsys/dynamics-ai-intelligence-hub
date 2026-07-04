"""Conversational CRM assistant grounded in Dataverse data (Epic 8, #63)."""

from ai.assistant.retriever import (
    CrmRetriever,
    DataverseCrmRetriever,
    EntityView,
    ReadGateway,
)
from ai.assistant.service import (
    AssistantAnswer,
    CrmAssistant,
    GroundedAnswer,
    KnowledgeSource,
)

__all__ = [
    "CrmAssistant",
    "AssistantAnswer",
    "CrmRetriever",
    "DataverseCrmRetriever",
    "EntityView",
    "ReadGateway",
    "KnowledgeSource",
    "GroundedAnswer",
]
