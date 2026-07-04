"""Run the RAG evaluation and compute metrics (#74).

Measures **retrieval hit rate** (did retrieval surface the expected section?),
**groundedness** (did the answer cite a source?), and **relevance** (does the
answer contain the expected cues?). The pipeline under test is injected as a
``RunQuery`` callable, so the evaluator is pure and unit-testable; ``make_rag_run``
adapts a live :class:`~rag.retrieval.Retriever` + generation into that callable.
"""

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from ai.client import AIClient
from rag.evaluation.dataset import DEFAULT_EVAL_SET, EvalCase
from rag.generation import generate_answer
from rag.retrieval import Retriever


@dataclass(frozen=True)
class QueryOutcome:
    """What a pipeline produced for one question."""

    retrieved_sections: set[str]
    answer: str
    is_grounded: bool


RunQuery = Callable[[str, Sequence[str]], QueryOutcome]


def is_relevant(answer: str, keywords: Sequence[str]) -> bool:
    """Rule-based relevance: the answer mentions every expected keyword."""
    lowered = answer.casefold()
    return all(kw.casefold() in lowered for kw in keywords) if keywords else True


@dataclass(frozen=True)
class CaseResult:
    case: EvalCase
    outcome: QueryOutcome
    hit: bool
    grounded: bool
    relevant: bool

    @property
    def passed(self) -> bool:
        return self.hit and self.grounded and self.relevant


@dataclass(frozen=True)
class EvaluationReport:
    results: list[CaseResult]

    @property
    def n(self) -> int:
        return len(self.results)

    def _rate(self, attr: str) -> float:
        if not self.results:
            return 0.0
        passed = sum(1 for r in self.results if getattr(r, attr))
        return round(passed / self.n, 3)

    @property
    def hit_rate(self) -> float:
        return self._rate("hit")

    @property
    def groundedness(self) -> float:
        return self._rate("grounded")

    @property
    def relevance(self) -> float:
        return self._rate("relevant")

    @property
    def weaknesses(self) -> list[CaseResult]:
        return [r for r in self.results if not r.passed]

    def summary(self) -> str:
        return (
            f"n={self.n}  hit_rate={self.hit_rate}  groundedness={self.groundedness}  "
            f"relevance={self.relevance}  weaknesses={len(self.weaknesses)}"
        )


def evaluate(run: RunQuery, cases: Sequence[EvalCase] = DEFAULT_EVAL_SET) -> EvaluationReport:
    """Run every case through ``run`` and score retrieval + answer quality."""
    results: list[CaseResult] = []
    for case in cases:
        outcome = run(case.question, case.roles)
        results.append(
            CaseResult(
                case=case,
                outcome=outcome,
                hit=case.expected_section in outcome.retrieved_sections,
                grounded=outcome.is_grounded,
                relevant=is_relevant(outcome.answer, case.keywords),
            )
        )
    return EvaluationReport(results=results)


def make_rag_run(retriever: Retriever, client: AIClient, *, top_k: int = 5) -> RunQuery:
    """Adapt a live retriever + generation into a ``RunQuery`` for evaluation."""

    def run(question: str, roles: Sequence[str]) -> QueryOutcome:
        chunks = retriever.retrieve_for(question, roles, top_k=top_k)
        answer = generate_answer(client, question, chunks)
        return QueryOutcome(
            retrieved_sections={c.section for c in chunks if c.section},
            answer=answer.answer,
            is_grounded=answer.is_grounded,
        )

    return run
