"""Persist ingested OpenF1 data into Dataverse, idempotently.

Reads via :class:`~openf1.client.OpenF1Client`, validates via
``openf1.models.parse_many`` (bad rows are logged and skipped, never fatal),
maps to Dataverse columns via :mod:`openf1.mapping`, and **upserts by alternate
key in bounded ``$batch`` changesets** so re-ingestion produces no duplicates and
voluminous endpoints (laps/position) ingest in a few round-trips rather than one
per row (which timed out a full-session run — see ``BATCH_SIZE``).

A Race Event is **settleable** only once the Tier-A minimum
(`drivers` + `session_result`) has landed for its session — :func:`is_settleable`.
Marking the Race Event record itself is deferred to the Paddock schema (#225) /
settlement engine (#229).
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol

from openf1.client import OpenF1Client
from openf1.mapping import MAPPINGS, SETTLEMENT_REQUIRED, EntityMap
from openf1.models import parse_many
from shared.logging import get_logger

_logger = get_logger("openf1.persistence")

# Rows per $batch changeset. Dataverse caps a changeset at 1000 operations; 100
# keeps each batch comfortably under that with a bounded request size, while
# collapsing the per-row round-trips (and per-row token fetches) that made a
# full-session ingest of the voluminous laps/position endpoints time out.
BATCH_SIZE = 100


class SupportsBatchUpsert(Protocol):
    """The slice of the Dataverse client this module needs (see `DataverseClient`)."""

    def batch_upsert(self, operations: Sequence[tuple[str, str, Mapping[str, Any]]]) -> None: ...


def _chunked(
    items: Sequence[tuple[str, str, Mapping[str, Any]]], size: int
) -> list[Sequence[tuple[str, str, Mapping[str, Any]]]]:
    """Split ``items`` into consecutive chunks of at most ``size``."""
    return [items[i : i + size] for i in range(0, len(items), size)]


def _fmt_key_value(value: Any) -> str:
    """Render an alternate-key value: numbers bare, everything else quoted."""
    if isinstance(value, bool):  # bool is an int subclass — guard first
        return f"'{value}'"
    if isinstance(value, int | float):
        return str(value)
    return f"'{value}'"


def build_alternate_key(entity_map: EntityMap, row: Mapping[str, Any]) -> str:
    """Build a Dataverse alternate-key expression (e.g. ``racy_sessionkey=9158``)."""
    parts = []
    for field_name in entity_map.alt_key_fields:
        column = entity_map.field_map[field_name]
        parts.append(f"{column}={_fmt_key_value(row[field_name])}")
    return ",".join(parts)


def map_row(entity_map: EntityMap, row: Mapping[str, Any]) -> dict[str, Any]:
    """Map a validated OpenF1 row (dict) to a Dataverse payload, dropping ``None``."""
    return {
        column: row[of_field]
        for of_field, column in entity_map.field_map.items()
        if row.get(of_field) is not None
    }


@dataclass
class EndpointResult:
    endpoint: str
    upserted: int = 0
    invalid: int = 0


@dataclass
class IngestSummary:
    session_key: int
    endpoints: dict[str, EndpointResult] = field(default_factory=dict)

    @property
    def total_upserted(self) -> int:
        return sum(r.upserted for r in self.endpoints.values())

    @property
    def settleable(self) -> bool:
        """True once the Tier-A minimum landed (drivers + session_result rows)."""
        return all(
            self.endpoints.get(name) is not None and self.endpoints[name].upserted > 0
            for name in SETTLEMENT_REQUIRED
        )


class OpenF1Persister:
    """Ingest a session's OpenF1 data into Dataverse via idempotent upserts."""

    def __init__(
        self, openf1: OpenF1Client, dataverse: SupportsBatchUpsert, *, batch_size: int = BATCH_SIZE
    ) -> None:
        self._openf1 = openf1
        self._dv = dataverse
        self._batch_size = batch_size
        self._log = _logger

    def persist_endpoint(self, entity_map: EntityMap, session_key: int) -> EndpointResult:
        rows = getattr(self._openf1, entity_map.client_method)(session_key=session_key)
        parsed = parse_many(entity_map.model, rows)
        result = EndpointResult(endpoint=entity_map.endpoint, invalid=len(parsed.errors))
        operations = [
            (
                entity_map.entity_set,
                build_alternate_key(entity_map, model.model_dump()),
                map_row(entity_map, model.model_dump()),
            )
            for model in parsed.valid
        ]
        # Upsert in bounded $batch changesets — one round-trip per ~batch_size rows
        # instead of one per row, so large endpoints ingest within the timeout.
        for chunk in _chunked(operations, self._batch_size):
            self._dv.batch_upsert(chunk)
            result.upserted += len(chunk)
        self._log.info(
            "openf1 persist %s: upserted=%d invalid=%d (%d batch(es))",
            entity_map.endpoint,
            result.upserted,
            result.invalid,
            len(_chunked(operations, self._batch_size)),
        )
        return result

    def ingest_session(self, session_key: int) -> IngestSummary:
        """Persist every mapped endpoint for a session; returns a per-endpoint summary."""
        summary = IngestSummary(session_key=session_key)
        for name, entity_map in MAPPINGS.items():
            summary.endpoints[name] = self.persist_endpoint(entity_map, session_key)
        self._log.info(
            "openf1 ingest session %d: %d rows, settleable=%s",
            session_key,
            summary.total_upserted,
            summary.settleable,
        )
        return summary


def is_settleable(summary: IngestSummary) -> bool:
    """Tier-A settlement-completeness check for an ingested session."""
    return summary.settleable
