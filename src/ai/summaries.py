"""AI-generated summaries of CRM records (#62).

Fetches a record's fields via the Dataverse layer, renders a prompt-library
template (``crm_summary``), calls the governed :class:`~ai.client.AIClient`, and
logs the prompt/response for governance (#69). Long context is bounded by
character-truncation (flagged on the result) so a large record can't blow the
model's context window. The Dataverse read is a :class:`RecordSource` Protocol,
so the summariser is unit-tested without a live environment.
"""

import time
import uuid
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Protocol

from ai.client import AIClient, usage_tokens
from ai.exceptions import AIError
from ai.prompt_log import NullLogger, PromptLogger
from ai.prompts import get as get_prompt
from shared.logging import get_logger

_logger = get_logger("ai.summaries")

# Fields worth summarising per entity (skips GUIDs/system columns).
ACCOUNT_FIELDS = ("name", "accountnumber", "address1_city", "telephone1")
CASE_FIELDS = (
    "racy_casecode",
    "racy_title",
    "racy_prioritycode",
    "racy_statuscode",
    "racy_accountnumber",
)


class SummaryError(AIError):
    """No record matched, so there is nothing to summarise."""


class RecordSource(Protocol):
    """The slice of the Dataverse client this module needs."""

    def retrieve_multiple(
        self,
        entity_set: str,
        *,
        filter: str | None = ...,
        select: Sequence[str] | None = ...,
        top: int | None = ...,
    ) -> list[dict[str, Any]]: ...


@dataclass(frozen=True)
class SummaryResult:
    """A generated summary and whether its source context was truncated."""

    text: str
    truncated: bool
    tokens: int | None = None


def _format_record(row: Mapping[str, Any]) -> str:
    """Render a record's non-null business fields as ``key: value`` lines."""
    return "\n".join(f"{k}: {v}" for k, v in row.items() if v is not None and not k.startswith("@"))


@dataclass
class CrmSummariser:
    """Summarises a CRM record via the prompt library, with logging + truncation."""

    client: AIClient
    source: RecordSource
    logger: PromptLogger = NullLogger()
    code_factory: Callable[[], str] = staticmethod(lambda: uuid.uuid4().hex)
    max_context_chars: int = 6000
    max_words: int = 120

    def summarise(
        self,
        entity_set: str,
        record_filter: str,
        *,
        record_type: str,
        fields: Sequence[str] | None = None,
        user_id: str | None = None,
    ) -> SummaryResult:
        """Fetch the matching record and return a concise, logged summary."""
        rows = self.source.retrieve_multiple(entity_set, filter=record_filter, select=fields, top=1)
        if not rows:
            raise SummaryError(f"no {record_type} matched: {record_filter}")

        record_text = _format_record(rows[0])
        truncated = len(record_text) > self.max_context_chars
        if truncated:
            record_text = record_text[: self.max_context_chars]
            _logger.info("summary context truncated to %d chars", self.max_context_chars)

        request_code = self.code_factory()
        self.logger.log_request(
            request_code,
            purpose="crm-summary",
            model=self.client.model,
            prompt=record_text,
            user_id=user_id,
        )
        start = time.perf_counter()
        try:
            messages = get_prompt("crm_summary").render(
                record_type=record_type, max_words=self.max_words, record=record_text
            )
            response = self.client.complete(messages)
            text = str(response.choices[0].message.content or "")
        except AIError as error:
            self.logger.log_response(
                request_code,
                raw_output="",
                decision="error",
                ok=False,
                error=str(error),
                latency_ms=(time.perf_counter() - start) * 1000,
            )
            raise
        tokens = usage_tokens(response)
        self.logger.log_response(
            request_code,
            raw_output=text,
            decision="summary",
            ok=True,
            tokens=tokens,
            latency_ms=(time.perf_counter() - start) * 1000,
        )
        _logger.info(
            "summarised %s (%d chars in, %d out)", record_type, len(record_text), len(text)
        )
        return SummaryResult(text=text, truncated=truncated, tokens=tokens)

    def summarise_account(
        self, account_number: str, *, user_id: str | None = None
    ) -> SummaryResult:
        return self.summarise(
            "accounts",
            f"accountnumber eq '{account_number}'",
            record_type="account",
            fields=ACCOUNT_FIELDS,
            user_id=user_id,
        )

    def summarise_case(self, case_code: str, *, user_id: str | None = None) -> SummaryResult:
        return self.summarise(
            "racy_cases",
            f"racy_casecode eq '{case_code}'",
            record_type="case",
            fields=CASE_FIELDS,
            user_id=user_id,
        )
