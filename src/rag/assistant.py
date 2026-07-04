"""End-to-end RAG assistant — the headline Epic 9 deliverable (#25 / feature #123).

One entrypoint that runs the whole pipeline for a caller: **permission-aware
hybrid retrieval** (#71/#72) → **grounded generation with citations** (#73),
enforcing the caller's Dataverse role at query time and logging prompt/response
for governance (Epic 8). It composes the existing Epic 9 components — no new
retrieval tech — into a single ``ask(question, roles)`` call.
"""

import uuid
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field

from ai.client import AIClient
from ai.prompt_log import NullLogger, PromptLogger
from rag.generation import CitedAnswer, generate_answer
from rag.retrieval import DEFAULT_POLICY, DEFAULT_TOP_K, AccessPolicy, Retriever
from shared.logging import get_logger

_logger = get_logger("rag.assistant")


@dataclass
class RagAssistant:
    """Grounded, permission-aware question answering over the knowledge index."""

    retriever: Retriever
    client: AIClient
    policy: AccessPolicy = DEFAULT_POLICY
    logger: PromptLogger = field(default_factory=NullLogger)
    code_factory: Callable[[], str] = field(default_factory=lambda: (lambda: uuid.uuid4().hex))

    def ask(
        self, question: str, roles: Iterable[str], *, top_k: int = DEFAULT_TOP_K
    ) -> CitedAnswer:
        """Answer ``question`` for a caller with ``roles``, returning a cited answer.

        Retrieval is trimmed to what ``roles`` may access before generation, so
        the answer — and its citations — can only draw on permitted sources.
        """
        roles = list(roles)
        request_code = self.code_factory()
        self.logger.log_request(
            request_code, purpose="rag-assistant", model=self.client.model, prompt=question
        )

        chunks = self.retriever.retrieve_for(question, roles, top_k=top_k, policy=self.policy)
        answer = generate_answer(self.client, question, chunks)

        self.logger.log_response(
            request_code,
            raw_output=answer.answer,
            decision="answer",
            ok=answer.is_grounded,
            error=None if chunks else "no permitted sources retrieved",
        )
        _logger.info(
            "rag answer for roles=%s: %d source(s), %d citation(s)",
            roles,
            len(chunks),
            len(answer.citations),
        )
        return answer
