"""Conversational CRM assistant grounded in Dataverse data (#63).

A multi-turn loop: each question retrieves fresh CRM context (via a
:class:`CrmRetriever`), renders the ``crm_qa`` prompt from the library (#59) with
that context, calls the model, and returns an answer grounded in the data.
Prompt and response are logged for governance (#230's ai-layer logger). The
model is instructed to answer only from the supplied context — the read-only,
grounded precursor to guarded action tools (#64) and cited RAG answers (#65).
"""

import uuid
from collections.abc import Callable
from dataclasses import dataclass, field

from ai.assistant.retriever import CrmRetriever
from ai.client import AIClient
from ai.prompt_log import NullLogger, PromptLogger
from ai.prompts import get as get_prompt
from shared.logging import get_logger

_logger = get_logger("ai.assistant")


@dataclass(frozen=True)
class AssistantAnswer:
    """The assistant's reply plus the context it was grounded in."""

    text: str
    context: str


@dataclass
class CrmAssistant:
    """Answers CRM questions from Dataverse data, keeping conversation history."""

    client: AIClient
    retriever: CrmRetriever
    logger: PromptLogger = field(default_factory=NullLogger)
    code_factory: Callable[[], str] = field(default_factory=lambda: (lambda: uuid.uuid4().hex))
    _history: list[dict[str, str]] = field(default_factory=list, init=False)

    def ask(self, question: str) -> AssistantAnswer:
        request_code = self.code_factory()
        context = self.retriever.context(question)
        system, user = get_prompt("crm_qa").render(context=context, question=question)
        messages = [system, *self._history, user]

        self.logger.log_request(
            request_code, purpose="crm-assistant", model=self.client.model, prompt=question
        )
        answer = self.client.chat(messages)
        self.logger.log_response(request_code, raw_output=answer, decision="answer", ok=True)
        _logger.info("assistant answered a question (%d chars of context)", len(context))

        self._history.extend([user, {"role": "assistant", "content": answer}])
        return AssistantAnswer(text=answer, context=context)

    def reset(self) -> None:
        """Clear the conversation history."""
        self._history.clear()
