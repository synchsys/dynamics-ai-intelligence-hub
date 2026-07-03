"""Tests for the Dataverse-backed settlement repository (fake gateway)."""

from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

from paddock.wager import DataverseSettlementRepository

BatchOp = tuple[str, str, Mapping[str, Any]]


class FakeGateway:
    def __init__(self, tables: dict[str, list[dict[str, Any]]]) -> None:
        self._tables = tables
        self.batches: list[Sequence[BatchOp]] = []

    def retrieve_multiple(
        self, entity_set: str, *, filter: str | None = None, select: Sequence[str] | None = None
    ) -> list[dict[str, Any]]:
        return self._tables.get(entity_set, [])

    def batch_upsert(self, operations: Sequence[BatchOp]) -> None:
        self.batches.append(list(operations))


def test_grading_context_maps_rows_to_models() -> None:
    gw = FakeGateway(
        {
            "racy_sessionresults": [
                {"racy_drivernumber": 1, "racy_position": 1, "racy_dnf": False},
                {"racy_drivernumber": 2, "racy_position": None, "racy_dnf": True},
            ],
            "racy_startinggrids": [{"racy_drivernumber": 1, "racy_gridposition": 3}],
            "racy_laps": [{"racy_drivernumber": 1, "racy_lapnumber": 5, "racy_lapduration": 81.2}],
            "racy_pitstops": [{"racy_drivernumber": 1, "racy_lapnumber": 20}],
        }
    )
    ctx = DataverseSettlementRepository(gw).grading_context(9165)
    assert len(ctx.results) == 2
    assert ctx.result_for(1) is not None and ctx.result_for(1).position == 1  # type: ignore[union-attr]
    assert ctx.grid_for(1) is not None
    assert ctx.laps[0].lap_duration == 81.2


def test_locked_slips_parses_params_json() -> None:
    gw = FakeGateway(
        {
            "racy_wagerslips": [
                {
                    "racy_slipcode": "S1",
                    "racy_playercode": "P1",
                    "racy_settlementtypecode": "driver_finish_position",
                    "racy_parameters": '{"driver_number": 1, "operator": "<=", "value": 5}',
                    "racy_stake": 10.0,
                    "racy_frozenodds": 2.5,
                }
            ]
        }
    )
    slips = DataverseSettlementRepository(gw).locked_slips(9165)
    assert len(slips) == 1
    assert slips[0].parameters["operator"] == "<="
    assert slips[0].odds == 2.5


def test_existing_payout_and_wallet_balance() -> None:
    gw = FakeGateway(
        {
            "racy_settlements": [{"racy_payout": 40.0}],
            "racy_wallets": [{"racy_balance": 90.0}],
        }
    )
    repo = DataverseSettlementRepository(gw)
    assert repo.existing_payout("S1") == 40.0
    assert repo.wallet_balance("P1") == 90.0


def test_missing_settlement_and_wallet_defaults() -> None:
    repo = DataverseSettlementRepository(FakeGateway({}))
    assert repo.existing_payout("S1") is None
    assert repo.wallet_balance("P1") == 0.0


def test_commit_settlement_is_one_atomic_batch() -> None:
    gw = FakeGateway({})
    DataverseSettlementRepository(gw).commit_settlement(
        slip_code="S1",
        player_code="P1",
        new_balance=90.0,
        result="Won",
        payout=40.0,
        slip_status="Won",
        graded_on=datetime(2024, 5, 1, 18, 0, 0),
    )
    assert len(gw.batches) == 1
    entity_sets = {op[0] for op in gw.batches[0]}
    assert entity_sets == {"racy_settlements", "racy_wallets", "racy_wagerslips"}
