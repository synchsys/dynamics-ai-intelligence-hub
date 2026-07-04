"""Conversational CRM assistant grounded in Dataverse data + RAG (#63, #65).

A multi-turn loop. Each question is first offered to an optional **knowledge
source** (the Epic 9 RAG assistant) for a cited, permission-aware answer; if that
grounds, its cited answer is returned. Otherwise the assistant falls back to
answering from **Dataverse data** via a :class:`CrmRetriever` and the ``crm_qa``
prompt (#59). Prompt/response are logged for governance (#230's ai-layer logger).

The knowledge source is a structural :class:`KnowledgeSource` Protocol, so this
module does not import the ``rag`` package (which depends on ``ai``) — the RAG
assistant is injected and duck-types the contract.
"""

import uuid
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol

from ai.assistant.retriever import CrmRetriever
from ai.client import AIClient
from ai.prompt_log import NullLogger, PromptLogger
from ai.prompts import get as get_prompt
from shared.logging import get_logger

_logger = get_logger("ai.assistant")


class GroundedAnswer(Protocol):
    """The shape of a knowledge-source answer (satisfied by rag.CitedAnswer)."""

    answer: str
    citations: Sequence[Any]

    @property
    def is_grounded(self) -> bool: ...


class KnowledgeSource(Protocol):
    """A cited, permission-aware knowledge answerer (the RAG assistant)."""

    def ask(self, question: str, roles: Sequence[str]) -> GroundedAnswer: ...


@dataclass(frozen=True)
class AssistantAnswer:
    """The assistant's reply, the context it used, and any source citations."""

    text: str
    context: str
    citations: list[Any] = field(default_factory=list)
    grounded_in: str = "crm"  # "knowledge" when answered from RAG, else "crm"


@dataclass
class CrmAssistant:
    """Answers questions from RAG knowledge (cited) or Dataverse data, with history."""

    client: AIClient
    retriever: CrmRetriever
    logger: PromptLogger = field(default_factory=NullLogger)
    code_factory: Callable[[], str] = field(default_factory=lambda: (lambda: uuid.uuid4().hex))
    knowledge: KnowledgeSource | None = None
    roles: Sequence[str] = ()
    _history: list[dict[str, str]] = field(default_factory=list, init=False)

    def ask(self, question: str) -> AssistantAnswer:
        request_code = self.code_factory()
        self.logger.log_request(
            request_code, purpose="crm-assistant", model=self.client.model, prompt=question
        )

        knowledge_answer = self._knowledge_answer(question)
        if knowledge_answer is not None:
            self.logger.log_response(
                request_code, raw_output=knowledge_answer.text, decision="answer-rag", ok=True
            )
            self._remember(question, knowledge_answer.text)
            return knowledge_answer

        answer = self._crm_answer(question)
        self.logger.log_response(request_code, raw_output=answer.text, decision="answer", ok=True)
        self._remember(question, answer.text)
        return answer

    def _knowledge_answer(self, question: str) -> AssistantAnswer | None:
        """Try RAG grounding; return a cited answer only if it grounded."""
        if self.knowledge is None:
            return None
        cited = self.knowledge.ask(question, self.roles)
        if not cited.is_grounded:
            return None
        _logger.info(
            "assistant answered from knowledge base (%d citation(s))", len(cited.citations)
        )
        return AssistantAnswer(
            text=cited.answer,
            context="(answered from the knowledge base)",
            citations=list(cited.citations),
            grounded_in="knowledge",
        )

    def _crm_answer(self, question: str) -> AssistantAnswer:
        """Answer from Dataverse data via the CRM retriever (the fallback path)."""
        context = self.retriever.context(question)
        system, user = get_prompt("crm_qa").render(context=context, question=question)
        answer = self.client.chat([system, *self._history, user])
        _logger.info("assistant answered from CRM data (%d chars of context)", len(context))
        return AssistantAnswer(text=answer, context=context)

    def _remember(self, question: str, answer: str) -> None:
        self._history.extend(
            [{"role": "user", "content": question}, {"role": "assistant", "content": answer}]
        )

    def reset(self) -> None:
        """Clear the conversation history."""
        self._history.clear()
