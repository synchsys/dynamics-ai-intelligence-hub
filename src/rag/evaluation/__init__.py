"""RAG evaluation — measure retrieval and answer quality (#74)."""

from rag.evaluation.dataset import (
    DEFAULT_CORPUS,
    DEFAULT_EVAL_SET,
    EvalCase,
    default_cases,
    merged_corpus,
)
from rag.evaluation.evaluator import (
    CaseResult,
    EvaluationReport,
    QueryOutcome,
    RunQuery,
    evaluate,
    is_relevant,
    make_rag_run,
)

__all__ = [
    "EvalCase",
    "DEFAULT_EVAL_SET",
    "DEFAULT_CORPUS",
    "default_cases",
    "merged_corpus",
    "QueryOutcome",
    "RunQuery",
    "CaseResult",
    "EvaluationReport",
    "evaluate",
    "is_relevant",
    "make_rag_run",
]
