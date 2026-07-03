"""Dataverse-backed :class:`~paddock.wager.settlement.SettlementRepository`.

Reads the ingested F1 rows + locked slips + wallets from the ``racy_`` tables and
commits each settlement (Settlement record + wallet balance + slip status) in one
atomic ``$batch`` changeset. This is the live wiring; the settlement-engine logic
and idempotency are unit-tested against a fake repository.
"""

import json
from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any, Protocol

from openf1.models import Lap, Pit, SessionResult, StartingGrid
from paddock.settlement import GradingContext
from paddock.wager.settlement import SlipRecord

BatchOp = tuple[str, str, Mapping[str, Any]]


class DataverseGateway(Protocol):
    def retrieve_multiple(
        self, entity_set: str, *, filter: str | None = ..., select: Sequence[str] | None = ...
    ) -> list[dict[str, Any]]: ...
    def batch_upsert(self, operations: Sequence[BatchOp]) -> None: ...


class DataverseSettlementRepository:
    """Implements the settlement repository over the ``racy_`` Dataverse tables."""

    def __init__(self, dataverse: DataverseGateway) -> None:
        self._dv = dataverse

    def grading_context(self, session_key: int) -> GradingContext:
        f = f"racy_sessionkey eq {session_key}"
        results = [
            SessionResult(
                session_key=session_key,
                driver_number=r["racy_drivernumber"],
                position=r.get("racy_position"),
                dnf=bool(r.get("racy_dnf")),
                dns=bool(r.get("racy_dns")),
                dsq=bool(r.get("racy_dsq")),
                gap_to_leader=r.get("racy_gaptoleader"),
            )
            for r in self._dv.retrieve_multiple("racy_sessionresults", filter=f)
        ]
        grid = [
            StartingGrid(
                session_key=session_key,
                driver_number=r["racy_drivernumber"],
                position=r.get("racy_gridposition"),
            )
            for r in self._dv.retrieve_multiple("racy_startinggrids", filter=f)
        ]
        laps = [
            Lap(
                session_key=session_key,
                driver_number=r["racy_drivernumber"],
                lap_number=r.get("racy_lapnumber"),
                lap_duration=r.get("racy_lapduration"),
            )
            for r in self._dv.retrieve_multiple("racy_laps", filter=f)
        ]
        pit = [
            Pit(
                session_key=session_key,
                driver_number=r["racy_drivernumber"],
                lap_number=r.get("racy_lapnumber"),
                pit_duration=r.get("racy_pitduration"),
            )
            for r in self._dv.retrieve_multiple("racy_pitstops", filter=f)
        ]
        return GradingContext(results=results, grid=grid, laps=laps, pit=pit)

    def locked_slips(self, session_key: int) -> Sequence[SlipRecord]:
        rows = self._dv.retrieve_multiple(
            "racy_wagerslips",
            filter=f"racy_sessionkey eq {session_key} and racy_status ne 'Draft'",
        )
        return [
            SlipRecord(
                slip_code=r["racy_slipcode"],
                player_code=r["racy_playercode"],
                settlement_type=r["racy_settlementtypecode"],
                parameters=json.loads(r.get("racy_parameters") or "{}"),
                stake=float(r.get("racy_stake") or 0.0),
                odds=float(r.get("racy_frozenodds") or 0.0),
            )
            for r in rows
        ]

    def existing_payout(self, slip_code: str) -> float | None:
        rows = self._dv.retrieve_multiple(
            "racy_settlements", filter=f"racy_slipcode eq '{slip_code}'", select=["racy_payout"]
        )
        return float(rows[0]["racy_payout"]) if rows else None

    def wallet_balance(self, player_code: str) -> float:
        rows = self._dv.retrieve_multiple(
            "racy_wallets", filter=f"racy_playercode eq '{player_code}'", select=["racy_balance"]
        )
        return float(rows[0]["racy_balance"]) if rows else 0.0

    def commit_settlement(
        self,
        *,
        slip_code: str,
        player_code: str,
        new_balance: float,
        result: str,
        payout: float,
        slip_status: str,
        graded_on: datetime,
    ) -> None:
        self._dv.batch_upsert(
            [
                (
                    "racy_settlements",
                    f"racy_slipcode='{slip_code}'",
                    {
                        "racy_slipcode": slip_code,
                        "racy_result": result,
                        "racy_payout": payout,
                        "racy_gradedon": graded_on.isoformat(),
                        "racy_datasnapshot": graded_on.isoformat(),
                    },
                ),
                ("racy_wallets", f"racy_playercode='{player_code}'", {"racy_balance": new_balance}),
                ("racy_wagerslips", f"racy_slipcode='{slip_code}'", {"racy_status": slip_status}),
            ]
        )
