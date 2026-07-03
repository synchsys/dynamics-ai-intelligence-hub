"""Prompt/response logging for intake (#230, Epic 8 governance).

Every intake call logs its prompt and the model's response to the AI Request /
AI Response Dataverse tables, paired by ``request_code``. Governance is wired in
here, in the feature, not bolted on later. The :class:`PromptLogger` Protocol
keeps the service testable; :class:`DataversePromptLogger` is the live adapter
and :class:`NullLogger` is a no-op for tests or offline runs.
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
        settlement_type: str | None,
        ok: bool,
        error: str | None,
    ) -> None: ...


class NullLogger:
    """A logger that records nothing (tests / offline)."""

    def log_request(self, request_code: str, *, purpose: str, model: str, prompt: str) -> None:
        return None

    def log_response(
        self,
        request_code: str,
        *,
        raw_output: str,
        decision: str,
        settlement_type: str | None,
        ok: bool,
        error: str | None,
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
        settlement_type: str | None,
        ok: bool,
        error: str | None,
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
