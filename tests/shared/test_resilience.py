"""Tests for the timeout wrapper and retry decorator."""

import time

import pytest

from shared.resilience import (
    TimeoutExceededError,
    compute_backoff,
    retry,
    run_with_timeout,
    with_timeout,
)


def _noop_sleep(_seconds: float) -> None:
    return None


# --- compute_backoff -------------------------------------------------------


def test_backoff_is_exponential_without_jitter() -> None:
    assert compute_backoff(1, base_delay=1.0, backoff_factor=2.0, jitter=False) == 1.0
    assert compute_backoff(2, base_delay=1.0, backoff_factor=2.0, jitter=False) == 2.0
    assert compute_backoff(3, base_delay=1.0, backoff_factor=2.0, jitter=False) == 4.0


def test_backoff_is_capped() -> None:
    assert (
        compute_backoff(10, base_delay=1.0, backoff_factor=2.0, max_delay=5.0, jitter=False) == 5.0
    )


def test_backoff_jitter_stays_within_cap() -> None:
    for _ in range(50):
        delay = compute_backoff(3, base_delay=1.0, backoff_factor=2.0, max_delay=4.0, jitter=True)
        assert 0.0 <= delay <= 4.0


# --- retry -----------------------------------------------------------------


def test_retries_transient_then_succeeds() -> None:
    calls = {"n": 0}

    @retry(max_attempts=3, retry_on=ValueError, sleep=_noop_sleep)
    def flaky() -> str:
        calls["n"] += 1
        if calls["n"] < 3:
            raise ValueError("transient")
        return "ok"

    assert flaky() == "ok"
    assert calls["n"] == 3


def test_gives_up_after_max_attempts() -> None:
    calls = {"n": 0}

    @retry(max_attempts=3, retry_on=ValueError, sleep=_noop_sleep)
    def always_fails() -> None:
        calls["n"] += 1
        raise ValueError("still transient")

    with pytest.raises(ValueError, match="still transient"):
        always_fails()
    assert calls["n"] == 3


def test_permanent_error_not_retried() -> None:
    calls = {"n": 0}

    @retry(max_attempts=5, retry_on=ValueError, sleep=_noop_sleep)
    def raises_permanent() -> None:
        calls["n"] += 1
        raise KeyError("permanent")

    with pytest.raises(KeyError):
        raises_permanent()
    assert calls["n"] == 1


def test_predicate_condition() -> None:
    calls = {"n": 0}

    @retry(
        max_attempts=3,
        retry_on=lambda exc: isinstance(exc, RuntimeError) and "retry" in str(exc),
        sleep=_noop_sleep,
    )
    def conditional() -> str:
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("please retry")
        return "done"

    assert conditional() == "done"
    assert calls["n"] == 2


def test_success_on_first_attempt_does_not_sleep() -> None:
    sleeps: list[float] = []

    @retry(max_attempts=3, sleep=sleeps.append)
    def ok() -> int:
        return 42

    assert ok() == 42
    assert sleeps == []


def test_invalid_max_attempts() -> None:
    with pytest.raises(ValueError, match="max_attempts"):
        retry(max_attempts=0)


def test_retry_logs_on_retry_and_giveup(capsys: pytest.CaptureFixture[str]) -> None:
    from shared.logging import configure_logging

    configure_logging(json_output=False)

    @retry(max_attempts=2, retry_on=ValueError, sleep=_noop_sleep)
    def fails() -> None:
        raise ValueError("boom")

    with pytest.raises(ValueError):
        fails()
    err = capsys.readouterr().err
    assert "retrying" in err
    assert "giving up" in err


# --- timeout ---------------------------------------------------------------


def test_run_with_timeout_returns_value() -> None:
    assert run_with_timeout(lambda: 7, 1.0) == 7


def test_run_with_timeout_passes_args() -> None:
    assert run_with_timeout(lambda a, b: a + b, 1.0, 2, b=3) == 5


def test_run_with_timeout_raises_on_slow_call() -> None:
    def slow() -> None:
        time.sleep(0.5)

    with pytest.raises(TimeoutExceededError):
        run_with_timeout(slow, 0.05)


def test_with_timeout_decorator() -> None:
    @with_timeout(1.0)
    def quick() -> str:
        return "fast"

    assert quick() == "fast"


def test_delay_override_replaces_computed_backoff() -> None:
    sleeps: list[float] = []
    calls = {"n": 0}

    @retry(
        max_attempts=3,
        retry_on=ValueError,
        sleep=sleeps.append,
        delay_override=lambda _exc, _computed: 99.0,
    )
    def flaky() -> str:
        calls["n"] += 1
        if calls["n"] < 3:
            raise ValueError("transient")
        return "ok"

    assert flaky() == "ok"
    assert sleeps == [99.0, 99.0]
