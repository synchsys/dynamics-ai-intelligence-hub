"""Reusable resilience utilities: a timeout wrapper and a retry decorator.

**Design decision (story #23):** hand-rolled, with no third-party retry
dependency (e.g. ``tenacity``). Keeping it hand-rolled makes the retry
semantics, backoff, jitter and transient/permanent classification explicit and
fully testable, and avoids a dependency for behaviour the project treats as a
learning goal.

The REST client (story #35) and OpenF1 ingestion (story 4.2 / #17) consume
these helpers instead of reimplementing retry/backoff, so retry behaviour has a
single source of truth. Retries and give-ups are logged via ``shared.logging``.
"""

import functools
import random
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError
from logging import Logger
from typing import ParamSpec, TypeVar

from shared.exceptions import SharedError
from shared.logging import get_logger

P = ParamSpec("P")
T = TypeVar("T")

_logger = get_logger("shared.resilience")

# A retry condition is either an exception type / tuple of types (treated as
# transient) or a predicate deciding whether a given exception is transient.
RetryCondition = type[Exception] | tuple[type[Exception], ...] | Callable[[BaseException], bool]


class TimeoutExceededError(SharedError):
    """Raised when a call exceeds its allotted time."""


def compute_backoff(
    attempt: int,
    *,
    base_delay: float = 0.5,
    backoff_factor: float = 2.0,
    max_delay: float = 30.0,
    jitter: bool = True,
) -> float:
    """Return the delay (seconds) to wait before a 1-based retry ``attempt``.

    Exponential backoff (``base_delay * backoff_factor ** (attempt - 1)``)
    capped at ``max_delay``. With ``jitter`` enabled, "full jitter" is applied:
    the delay is drawn uniformly from ``[0, capped]`` to avoid thundering-herd
    retry storms.
    """
    raw = base_delay * (backoff_factor ** (attempt - 1))
    capped = min(raw, max_delay)
    if jitter:
        return random.uniform(0.0, capped)
    return capped


def _as_predicate(retry_on: RetryCondition) -> Callable[[BaseException], bool]:
    if isinstance(retry_on, type | tuple):
        exc_types = retry_on
        return lambda exc: isinstance(exc, exc_types)
    return retry_on


def retry(
    *,
    max_attempts: int = 3,
    base_delay: float = 0.5,
    backoff_factor: float = 2.0,
    max_delay: float = 30.0,
    jitter: bool = True,
    retry_on: RetryCondition = Exception,
    sleep: Callable[[float], None] = time.sleep,
    logger: Logger | None = None,
    delay_override: Callable[[BaseException, float], float] | None = None,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Retry a callable with exponential backoff and jitter.

    Only exceptions classified transient by ``retry_on`` are retried; permanent
    exceptions propagate immediately. After ``max_attempts`` the last exception
    is re-raised. ``sleep`` is injectable so tests need not wait in real time.

    ``delay_override(exc, computed_delay)`` optionally replaces the computed
    backoff for a given exception — e.g. to honour a server ``Retry-After``.
    """
    if max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")
    is_transient = _as_predicate(retry_on)
    log = logger or _logger

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    if not is_transient(exc):
                        log.warning(
                            "%s failed with non-transient error; not retrying: %s",
                            func.__name__,
                            exc,
                        )
                        raise
                    if attempt == max_attempts:
                        log.warning(
                            "%s giving up after %d attempt(s): %s",
                            func.__name__,
                            max_attempts,
                            exc,
                        )
                        raise
                    delay = compute_backoff(
                        attempt,
                        base_delay=base_delay,
                        backoff_factor=backoff_factor,
                        max_delay=max_delay,
                        jitter=jitter,
                    )
                    if delay_override is not None:
                        delay = delay_override(exc, delay)
                    log.warning(
                        "%s failed (attempt %d/%d), retrying in %.3fs: %s",
                        func.__name__,
                        attempt,
                        max_attempts,
                        delay,
                        exc,
                    )
                    sleep(delay)
            raise AssertionError("unreachable")  # pragma: no cover

        return wrapper

    return decorator


def run_with_timeout[**P, T](
    func: Callable[P, T], timeout: float, *args: P.args, **kwargs: P.kwargs
) -> T:
    """Run ``func`` and raise :class:`TimeoutExceededError` if it exceeds ``timeout``.

    Executes the call on a worker thread and abandons it (without blocking) on
    timeout. Note: the underlying thread is not forcibly killed, so this is a
    caller-side deadline, not cancellation. For I/O clients prefer the
    transport's own timeout; use this as a general safety net.
    """
    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(func, *args, **kwargs)
    try:
        return future.result(timeout=timeout)
    except FuturesTimeoutError as exc:
        raise TimeoutExceededError(
            f"call to {getattr(func, '__name__', repr(func))} exceeded {timeout}s"
        ) from exc
    finally:
        executor.shutdown(wait=False, cancel_futures=True)


def with_timeout(timeout: float) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator form of :func:`run_with_timeout`."""

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            return run_with_timeout(func, timeout, *args, **kwargs)

        return wrapper

    return decorator
