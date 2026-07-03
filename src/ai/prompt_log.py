"""Prompt/response logging — the Epic 8 governance capability.

Every LLM call in a feature logs its prompt and the model's response to the AI
Request / AI Response Dataverse tables, paired by ``request_code``. Governance is
wired in at the ``ai`` layer and reused by the intake pipeline (#230) and the CRM
assistant (#63). The :class:`PromptLogger` Protocol keeps callers testable;
:class:`DataversePromptLogger` is the live adapter and :class:`NullLogger` a
no-op for tests or offline runs.

``settlement_type``/``ok``/``error`` on ``log_response`` are optional — intake
uses them to record its parsed decision; the assistant simply logs an answer.
"""

from collections.abc import Mapping
from typing import Any, Protocol


class PromptLogger(Protocol):
    def log_request(self, request_code: str, *, purpose: str, model: str, prompt: str) -> None: ...
    def log_response(
        self,
        request_code: str,
        *,
        raw_output: str,
        decision: str,
        settlement_type: str | None = None,
        ok: bool = True,
        error: str | None = None,
    ) -> None: ...


class NullLogger:
    """Records nothing and never raises (tests / offline)."""

    def log_request(self, request_code: str, *, purpose: str, model: str, prompt: str) -> None:
        return None

    def log_response(
        self,
        request_code: str,
        *,
        raw_output: str,
        decision: str,
        settlement_type: str | None = None,
        ok: bool = True,
        error: str | None = None,
    ) -> None:
        return None


class SupportsUpsert(Protocol):
    def upsert(self, entity_set: str, alternate_key: str, data: Mapping[str, Any]) -> None: ...


class DataversePromptLogger:
    """Writes AI Request / AI Response rows to the ``racy_ai*`` tables."""

    def __init__(self, dataverse: SupportsUpsert) -> None:
        self._dv = dataverse

    def log_request(self, request_code: str, *, purpose: str, model: str, prompt: str) -> None:
        self._dv.upsert(
            "racy_airequests",
            f"racy_requestcode='{request_code}'",
            {
                "racy_requestcode": request_code,
                "racy_purpose": purpose,
                "racy_model": model,
                "racy_prompt": prompt,
            },
        )

    def log_response(
        self,
        request_code: str,
        *,
        raw_output: str,
        decision: str,
        settlement_type: str | None = None,
        ok: bool = True,
        error: str | None = None,
    ) -> None:
        self._dv.upsert(
            "racy_airesponses",
            f"racy_requestcode='{request_code}'",
            {
                "racy_requestcode": request_code,
                "racy_rawoutput": raw_output,
                "racy_decision": decision,
                "racy_settlementtypecode": settlement_type,
                "racy_ok": ok,
                "racy_error": error,
            },
        )
