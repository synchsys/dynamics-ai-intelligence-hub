"""Versioned, reusable prompt templates (#59)."""

from ai.prompts.library import (
    ACCOUNT_BRIEFING,
    CRM_QA,
    LIBRARY,
    SUMMARISE_ACTIVITY,
    PromptError,
    PromptTemplate,
    get,
    render,
)

__all__ = [
    "PromptTemplate",
    "PromptError",
    "LIBRARY",
    "CRM_QA",
    "SUMMARISE_ACTIVITY",
    "ACCOUNT_BRIEFING",
    "get",
    "render",
]
