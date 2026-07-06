"""Free-text wager intake — the LLM front door to the Paddock game (#230).

Pipeline: free text → :func:`structured_output` reads it into a
:class:`WagerIntent` (propose one supported type or decline) → prompt/response
logged → deterministic :func:`map_parameters` resolves drivers and validates
the concrete parameters → :class:`OddsPricer` prices it → a :class:`DraftSlip`.
Any decline, unresolved driver, or invalid parameters becomes a
**reject-with-guidance** that lists the supported prediction kinds. The model
grounds against the constrained registry; it never invents a settlement type,
and it never picks final parameters that skip schema validation.
"""

import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass

from ai import AIClient, AIError, structured_output
from openf1.models import Driver
from paddock.intake.logging_repo import NullLogger, PromptLogger
from paddock.intake.mapping import MappingError, map_parameters
from paddock.intake.schema import WagerIntent
from paddock.odds import Odds, OddsPricer
from paddock.settlement.registry import SETTLEMENT_TYPES
from shared.logging import get_logger

_logger = get_logger("paddock.intake")


@dataclass(frozen=True)
class DraftSlip:
    """An accepted, priced prediction ready to be locked (#228)."""

    session_key: int
    settlement_type: str
    parameters: dict[str, object]
    restated_text: str
    odds: Odds


@dataclass(frozen=True)
class IntakeResult:
    """Either an accepted draft slip or a guided rejection."""

    accepted: bool
    slip: DraftSlip | None = None
    guidance: str | None = None


def _supported_kinds() -> str:
    lines = "\n".join(f"- {meta.label}" for meta in SETTLEMENT_TYPES)
    return f"I can price these kinds of prediction:\n{lines}"


def _reject(message: str) -> IntakeResult:
    return IntakeResult(accepted=False, guidance=f"{message}\n\n{_supported_kinds()}")


def _system_prompt(drivers: list[Driver]) -> str:
    kinds = "\n".join(f"- {meta.code}: {meta.label}" for meta in SETTLEMENT_TYPES)
    names = (
        ", ".join(f"{d.full_name or d.name_acronym} (#{d.driver_number})" for d in drivers)
        or "(no driver list available)"
    )
    return (
        "You map a punter's free-text Formula 1 prediction to exactly one supported "
        "settlement type, or decline. Supported types (code: description):\n"
        f"{kinds}\n\n"
        f"Drivers in this session: {names}\n\n"
        "Set decision='propose' with the settlement_type code and the relevant fields "
        "(driver, driver_b, operator, number), plus a one-line 'restated' summary. "
        "Use decision='decline' with a 'reason' if the text does not map to a supported "
        "type. Never invent a settlement type."
    )


class WagerIntakeService:
    """Turns free text into a priced draft slip or a guided rejection."""

    def __init__(
        self,
        client: AIClient,
        pricer: OddsPricer,
        *,
        logger: PromptLogger | None = None,
        code_factory: Callable[[], str] | None = None,
    ) -> None:
        self._client = client
        self._pricer = pricer
        self._log = logger or NullLogger()
        self._code_factory = code_factory or (lambda: uuid.uuid4().hex)

    def intake(
        self, text: str, *, session_key: int, drivers: list[Driver], user_id: str | None = None
    ) -> IntakeResult:
        request_code = self._code_factory()
        messages = [
            {"role": "system", "content": _system_prompt(drivers)},
            {"role": "user", "content": text},
        ]
        self._log.log_request(
            request_code,
            purpose="wager-intake",
            model=self._client.model,
            prompt=text,
            user_id=user_id,
        )
        start = time.perf_counter()

        def elapsed_ms() -> float:
            return (time.perf_counter() - start) * 1000

        try:
            intent = structured_output(self._client, messages, WagerIntent)
        except AIError as error:
            self._log.log_response(
                request_code,
                raw_output="",
                decision="error",
                settlement_type=None,
                ok=False,
                error=str(error),
                latency_ms=elapsed_ms(),
            )
            _logger.warning("intake could not parse a structured intent: %s", error)
            return _reject("Sorry — I couldn't understand that prediction.")

        if intent.decision == "decline":
            self._log.log_response(
                request_code,
                raw_output=intent.model_dump_json(),
                decision="decline",
                settlement_type=None,
                ok=True,
                error=None,
                latency_ms=elapsed_ms(),
            )
            return _reject(intent.reason or "That prediction isn't one I can settle.")

        try:
            settlement_type, parameters = map_parameters(intent, drivers)
        except MappingError as error:
            self._log.log_response(
                request_code,
                raw_output=intent.model_dump_json(),
                decision="propose",
                settlement_type=intent.settlement_type,
                ok=False,
                error=error.guidance,
                latency_ms=elapsed_ms(),
            )
            return _reject(error.guidance)

        self._log.log_response(
            request_code,
            raw_output=intent.model_dump_json(),
            decision="propose",
            settlement_type=settlement_type,
            ok=True,
            error=None,
            latency_ms=elapsed_ms(),
        )
        odds = self._pricer.price(settlement_type, parameters)
        slip = DraftSlip(
            session_key=session_key,
            settlement_type=settlement_type,
            parameters=parameters,
            restated_text=intent.restated or text,
            odds=odds,
        )
        return IntakeResult(accepted=True, slip=slip)
