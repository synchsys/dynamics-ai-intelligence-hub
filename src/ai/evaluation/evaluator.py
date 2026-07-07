"""Score GenAI outputs and aggregate a report (#66).

The default :class:`RuleScorer` is deterministic and dependency-free:

- **relevance** — the output contains every expected keyword (lexical cue check);
- **groundedness** — the share of the output's content words that appear in the
  source is at or above a threshold. This is a **lexical proxy** for faithfulness
  (it catches hallucinated content that introduces source-absent vocabulary; it
  does not judge semantic entailment — that's what :class:`~ai.evaluation.judge.LlmJudge`
  adds). The choice is documented in ``docs/architecture/genai-evaluation.md``.

Scoring is behind a :class:`Scorer` Protocol, so the rule scorer and the
LLM-as-judge are interchangeable and the report is agnostic to which ran.
"""

import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from ai.evaluation.dataset import DEFAULT_EVAL_SET, GenAICase

# Small stop list; content tokens are alphanumeric, length >= 4, not a stop word.
# (Most short words are already excluded by the length >= 4 rule; these are the
# length-4+ function words worth dropping so overlap reflects content, not filler.)
_STOP = frozenset(
    [
        "from",
        "into",
        "over",
        "that",
        "this",
        "these",
        "those",
        "were",
        "been",
        "being",
        "with",
        "which",
        "what",
        "when",
        "where",
        "will",
        "would",
        "your",
        "have",
        "here",
    ]
)
_GROUNDED_THRESHOLD = 0.5


def _content_tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", text.casefold()) if len(t) >= 4 and t not in _STOP}


def groundedness(output: str, source: str) -> float:
    """Share of the output's content words that appear in the source (0..1)."""
    out = _content_tokens(output)
    if not out:
        return 0.0
    return round(len(out & _content_tokens(source)) / len(out), 3)


def is_grounded(output: str, source: str, *, threshold: float = _GROUNDED_THRESHOLD) -> bool:
    return groundedness(output, source) >= threshold


def is_relevant(output: str, keywords: Sequence[str]) -> bool:
    """Rule-based relevance: the output mentions every expected keyword."""
    lowered = output.casefold()
    return all(kw.casefold() in lowered for kw in keywords) if keywords else True


@dataclass(frozen=True)
class CaseScore:
    case: GenAICase
    grounded: bool
    relevant: bool

    @property
    def passed(self) -> bool:
        return self.grounded and self.relevant


class Scorer(Protocol):
    def score(self, case: GenAICase) -> tuple[bool, bool]:
        """Return (grounded, relevant) for a case's output."""
        ...


class RuleScorer:
    """Deterministic lexical scorer (groundedness overlap + keyword relevance)."""

    def __init__(self, *, threshold: float = _GROUNDED_THRESHOLD) -> None:
        self._threshold = threshold

    def score(self, case: GenAICase) -> tuple[bool, bool]:
        grounded = is_grounded(case.output, case.source, threshold=self._threshold)
        return grounded, is_relevant(case.output, case.keywords)


@dataclass(frozen=True)
class EvalReport:
    results: list[CaseScore]

    @property
    def n(self) -> int:
        return len(self.results)

    def _rate(self, attr: str) -> float:
        if not self.results:
            return 0.0
        return round(sum(1 for r in self.results if getattr(r, attr)) / self.n, 3)

    @property
    def groundedness(self) -> float:
        return self._rate("grounded")

    @property
    def relevance(self) -> float:
        return self._rate("relevant")

    @property
    def pass_rate(self) -> float:
        return self._rate("passed")

    @property
    def weaknesses(self) -> list[CaseScore]:
        return [r for r in self.results if not r.passed]

    def summary(self) -> str:
        return (
            f"n={self.n}  groundedness={self.groundedness}  relevance={self.relevance}  "
            f"pass_rate={self.pass_rate}  weaknesses={len(self.weaknesses)}"
        )


def evaluate(
    scorer: Scorer | None = None, cases: Sequence[GenAICase] = DEFAULT_EVAL_SET
) -> EvalReport:
    """Score every case with ``scorer`` (rule-based by default) into a report."""
    active = scorer or RuleScorer()
    results = []
    for case in cases:
        grounded, relevant = active.score(case)
        results.append(CaseScore(case=case, grounded=grounded, relevant=relevant))
    return EvalReport(results=results)
