"""Tests for RAG evaluation — metrics and the case runner."""

from collections.abc import Sequence

from rag.evaluation import (
    DEFAULT_CORPUS,
    DEFAULT_EVAL_SET,
    EvalCase,
    QueryOutcome,
    RunQuery,
    default_cases,
    evaluate,
    is_relevant,
    merged_corpus,
)

# --- relevance --------------------------------------------------------------


def test_relevance_requires_all_keywords() -> None:
    assert is_relevant("DRS is used in a zone within one second", ("zone", "one second"))
    assert not is_relevant("DRS is used in a zone", ("zone", "one second"))


def test_relevance_is_case_insensitive_and_empty_is_true() -> None:
    assert is_relevant("The ZONE is here", ("zone",))
    assert is_relevant("anything", ())


# --- default set ------------------------------------------------------------


def test_default_eval_set_has_at_least_ten_cases() -> None:
    assert len(DEFAULT_EVAL_SET) >= 10
    assert default_cases() == DEFAULT_EVAL_SET


def test_merged_corpus_shapes_sources_for_ingestion() -> None:
    corpus = merged_corpus(access_tag="internal")
    assert len(corpus) == len(DEFAULT_CORPUS)
    source, text, tag = corpus[0]
    assert source == "regs.md" and tag == "internal" and "# DRS" in text


# --- runner + metrics -------------------------------------------------------

CASES = (
    EvalCase("q1", "DRS", ("zone",)),
    EvalCase("q2", "Safety Car", ("forbidden",)),
    EvalCase("q3", "Points", ("ten",)),
)


def _run_factory(outcomes: dict[str, QueryOutcome]) -> RunQuery:
    def run(question: str, roles: Sequence[str]) -> QueryOutcome:
        return outcomes[question]

    return run


def test_all_pass() -> None:
    run = _run_factory(
        {
            "q1": QueryOutcome({"DRS"}, "used in a zone", True),
            "q2": QueryOutcome({"Safety Car"}, "overtaking is forbidden", True),
            "q3": QueryOutcome({"Points"}, "top ten finishers", True),
        }
    )
    report = evaluate(run, CASES)
    assert report.n == 3
    assert report.hit_rate == 1.0 and report.groundedness == 1.0 and report.relevance == 1.0
    assert report.weaknesses == []


def test_mixed_results_scored_correctly() -> None:
    run = _run_factory(
        {
            "q1": QueryOutcome({"DRS"}, "used in a zone", True),  # pass
            "q2": QueryOutcome({"Pit Stops"}, "overtaking is forbidden", True),  # retrieval miss
            "q3": QueryOutcome({"Points"}, "no numbers here", False),  # ungrounded + irrelevant
        }
    )
    report = evaluate(run, CASES)
    assert report.hit_rate == round(2 / 3, 3)  # q1, q3 hit; q2 missed section
    assert report.groundedness == round(2 / 3, 3)  # q3 ungrounded
    assert report.relevance == round(2 / 3, 3)  # q3 missing 'ten'
    assert {r.case.question for r in report.weaknesses} == {"q2", "q3"}


def test_summary_string_includes_metrics() -> None:
    run = _run_factory({"q1": QueryOutcome({"DRS"}, "zone", True)})
    report = evaluate(run, (CASES[0],))
    assert "hit_rate=1.0" in report.summary() and "n=1" in report.summary()


def test_empty_report_rates_are_zero() -> None:
    report = evaluate(_run_factory({}), ())
    assert report.n == 0 and report.hit_rate == 0.0 and report.weaknesses == []


# --- live adapter (make_rag_run) --------------------------------------------


def test_make_rag_run_adapts_retriever_and_generation() -> None:
    import json
    from types import SimpleNamespace
    from typing import Any

    from ai import AIClient, AzureOpenAIConfig
    from rag import RetrievedChunk
    from rag.evaluation import make_rag_run

    chunk = RetrievedChunk("regs.md#0", "DRS in zones", "regs.md", "DRS", "public", 0.9)

    class FakeRetriever:
        def retrieve_for(self, query: str, roles: Any, *, top_k: int = 5) -> list[RetrievedChunk]:
            return [chunk]

    class _Completions:
        def create(self, **kwargs: Any) -> Any:
            content = json.dumps({"answer": "Use DRS in a zone.", "citations": ["regs.md#0"]})
            msg = SimpleNamespace(content=content, tool_calls=None)
            return SimpleNamespace(choices=[SimpleNamespace(message=msg)])

    sdk = SimpleNamespace(chat=SimpleNamespace(completions=_Completions()))
    config = AzureOpenAIConfig(
        endpoint="https://x", chat_deployment="m", embedding_deployment="e", api_key="k"
    )
    client = AIClient(config, sdk=sdk, max_attempts=1, sleep=lambda _s: None)

    run = make_rag_run(FakeRetriever(), client)  # type: ignore[arg-type]
    outcome = run("when can I use DRS?", ["employee"])
    assert outcome.retrieved_sections == {"DRS"}
    assert outcome.is_grounded and "zone" in outcome.answer.casefold()
