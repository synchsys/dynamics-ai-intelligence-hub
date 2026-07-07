"""GenAI output evaluation harness (#66).

Scores generated **summaries** and **assistant answers** for *groundedness* (does
the output stick to its source?) and *relevance* (does it address the ask?),
against a reproducible labelled set (:mod:`dataset`). Two interchangeable scorers
(ADR-free, choice recorded in ``docs/architecture/genai-evaluation.md``):

- :class:`~ai.evaluation.evaluator.RuleScorer` — deterministic, dependency-free
  (lexical groundedness + keyword relevance); runs in CI.
- :class:`~ai.evaluation.judge.LlmJudge` — LLM-as-judge over the same contract,
  for a semantic score at portfolio-demo time.
"""

from ai.evaluation.dataset import DEFAULT_EVAL_SET, GenAICase
from ai.evaluation.evaluator import (
    CaseScore,
    EvalReport,
    RuleScorer,
    Scorer,
    evaluate,
    is_grounded,
    is_relevant,
)
from ai.evaluation.judge import Judgement, LlmJudge

__all__ = [
    "GenAICase",
    "DEFAULT_EVAL_SET",
    "evaluate",
    "RuleScorer",
    "Scorer",
    "CaseScore",
    "EvalReport",
    "is_grounded",
    "is_relevant",
    "LlmJudge",
    "Judgement",
]
