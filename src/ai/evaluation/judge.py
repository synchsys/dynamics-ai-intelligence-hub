"""LLM-as-judge scorer for GenAI evaluation (#66).

A semantic alternative to the lexical :class:`~ai.evaluation.evaluator.RuleScorer`:
prompts the model to judge *groundedness* (does the output only use facts from the
source?) and *relevance* (does it address the prompt?) as a structured verdict.
Implements the same :class:`~ai.evaluation.evaluator.Scorer` contract, so it drops
into :func:`~ai.evaluation.evaluator.evaluate` unchanged. Live-only (needs Azure
OpenAI); the rule scorer is the deterministic CI path.
"""

from pydantic import BaseModel, Field

from ai.client import AIClient
from ai.evaluation.dataset import GenAICase
from ai.structured import structured_output

_RUBRIC = (
    "You are a strict evaluator of generative-AI output. Given a SOURCE (the only "
    "facts the output may use), the PROMPT it answered, and the OUTPUT, judge two "
    "things independently:\n"
    "- grounded: true only if every claim in OUTPUT is supported by SOURCE (no "
    "invented or contradicted facts).\n"
    "- relevant: true only if OUTPUT actually addresses PROMPT.\n"
    "Return the structured verdict with a one-line reason."
)


class Judgement(BaseModel):
    """The judge's structured verdict for one output."""

    grounded: bool = Field(description="OUTPUT uses only facts supported by SOURCE")
    relevant: bool = Field(description="OUTPUT addresses the PROMPT")
    reason: str = Field(default="", description="one-line rationale")


class LlmJudge:
    """Scores a case with an LLM rubric; satisfies the Scorer protocol."""

    def __init__(self, client: AIClient) -> None:
        self._client = client

    def judge(self, case: GenAICase) -> Judgement:
        messages = [
            {"role": "system", "content": _RUBRIC},
            {
                "role": "user",
                "content": (
                    f"SOURCE:\n{case.source}\n\nPROMPT:\n{case.prompt}\n\nOUTPUT:\n{case.output}"
                ),
            },
        ]
        return structured_output(self._client, messages, Judgement)

    def score(self, case: GenAICase) -> tuple[bool, bool]:
        verdict = self.judge(case)
        return verdict.grounded, verdict.relevant
