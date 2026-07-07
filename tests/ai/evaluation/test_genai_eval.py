"""Tests for the GenAI evaluation harness (#66)."""

from types import SimpleNamespace
from typing import Any

from ai import AIClient, AzureOpenAIConfig
from ai.evaluation import (
    DEFAULT_EVAL_SET,
    GenAICase,
    LlmJudge,
    RuleScorer,
    evaluate,
    is_grounded,
    is_relevant,
)
from ai.evaluation.evaluator import groundedness

CONFIG = AzureOpenAIConfig(
    endpoint="https://x.openai.azure.com",
    chat_deployment="gpt-5-mini",
    embedding_deployment="text-embedding-3-small",
    api_key="k",
)

# --- metric functions -------------------------------------------------------


def test_groundedness_overlap() -> None:
    assert groundedness("alpha beta gamma", "alpha beta gamma delta") == 1.0
    assert groundedness("quarterly dividends", "the race at monza") == 0.0
    assert groundedness("", "anything") == 0.0  # empty output -> not grounded


def test_is_grounded_threshold() -> None:
    assert is_grounded("medium hard compounds", "medium and hard tyre compounds")
    assert not is_grounded("shareholder dividends earnings", "a dry race at monza")


def test_is_relevant_keywords() -> None:
    assert is_relevant("Verstappen won at Monza", ("verstappen", "monza"))
    assert not is_relevant("Verstappen won", ("monza",))
    assert is_relevant("anything", ())  # no keywords -> vacuously relevant


# --- dataset / harness ------------------------------------------------------


def test_eval_set_has_at_least_ten_cases() -> None:
    assert len(DEFAULT_EVAL_SET) >= 10  # AC: >= 10 evaluation cases


def test_rule_scorer_catches_exactly_the_flawed_cases() -> None:
    report = evaluate(RuleScorer())
    assert report.n == len(DEFAULT_EVAL_SET)
    flagged = {r.case.id for r in report.weaknesses}
    intentionally_flawed = {c.id for c in DEFAULT_EVAL_SET if not c.should_pass}
    assert flagged == intentionally_flawed  # harness catches the bad ones, passes the good


def test_report_rates_and_summary() -> None:
    report = evaluate()  # default RuleScorer
    assert 0.0 <= report.groundedness <= 1.0
    assert 0.0 <= report.relevance <= 1.0
    good = sum(1 for c in DEFAULT_EVAL_SET if c.should_pass)
    assert report.pass_rate == round(good / report.n, 3)
    assert "groundedness=" in report.summary() and "pass_rate=" in report.summary()


def test_empty_report_rates_are_zero() -> None:
    report = evaluate(cases=[])
    assert report.n == 0 and report.groundedness == 0.0 and report.pass_rate == 0.0


# --- LLM-as-judge (scripted SDK) --------------------------------------------


class _Completions:
    def __init__(self, content: str) -> None:
        self._content = content

    def create(self, **kwargs: Any) -> Any:
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=self._content))]
        )


class FakeSDK:
    def __init__(self, content: str) -> None:
        self.chat = SimpleNamespace(completions=_Completions(content))


def _client(content: str) -> AIClient:
    return AIClient(CONFIG, sdk=FakeSDK(content), max_attempts=1, sleep=lambda _s: None)


CASE = GenAICase("t", "answer", "src", "prompt", "output", ("kw",))


def test_llm_judge_parses_verdict() -> None:
    client = _client('{"grounded": true, "relevant": false, "reason": "misses the ask"}')
    judge = LlmJudge(client)
    verdict = judge.judge(CASE)
    assert verdict.grounded is True and verdict.relevant is False
    assert verdict.reason == "misses the ask"
    assert judge.score(CASE) == (True, False)


def test_llm_judge_plugs_into_evaluate() -> None:
    client = _client('{"grounded": true, "relevant": true}')
    report = evaluate(LlmJudge(client), cases=[CASE])
    assert report.n == 1 and report.pass_rate == 1.0
