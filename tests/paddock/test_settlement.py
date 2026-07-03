"""Tests for the settlement engine (domain + idempotent orchestration)."""

from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

from openf1.models import SessionResult
from paddock.settlement import GradingContext, Outcome
from paddock.wager import SettlementEngine, SlipRecord, payout, settle_slip

NOW = datetime(2024, 5, 1, 18, 0, 0)


# --- pure domain -----------------------------------------------------------


def test_payout_win_lose_void() -> None:
    assert payout(Outcome.WIN, 10.0, 3.5) == 35.0
    assert payout(Outcome.LOSE, 10.0, 3.5) == 0.0
    assert payout(Outcome.VOID, 10.0, 3.5) == 10.0  # refund


def test_settle_slip_delta_vs_existing() -> None:
    first = settle_slip(10.0, 3.0, Outcome.WIN, None)
    assert first.payout == 30.0 and first.wallet_delta == 30.0 and first.result == "Won"
    # re-grade same outcome -> zero delta (idempotent)
    again = settle_slip(10.0, 3.0, Outcome.WIN, 30.0)
    assert again.wallet_delta == 0.0
    # reconcile from Lost (0) to Won (30) -> +30
    fixed = settle_slip(10.0, 3.0, Outcome.WIN, 0.0)
    assert fixed.wallet_delta == 30.0


# --- engine over a fake repository -----------------------------------------


class FakeRepo:
    def __init__(self, ctx: GradingContext, slips: list[SlipRecord], balances: dict[str, float]):
        self._ctx = ctx
        self._slips = slips
        self.payouts: dict[str, float] = {}
        self.balances = balances
        self.commits: list[dict[str, Any]] = []

    def grading_context(self, session_key: int) -> GradingContext:
        return self._ctx

    def locked_slips(self, session_key: int) -> Sequence[SlipRecord]:
        return self._slips

    def existing_payout(self, slip_code: str) -> float | None:
        return self.payouts.get(slip_code)

    def wallet_balance(self, player_code: str) -> float:
        return self.balances[player_code]

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
        self.commits.append(
            {
                "slip": slip_code,
                "player": player_code,
                "balance": new_balance,
                "result": result,
                "payout": payout,
            }
        )
        self.balances[player_code] = new_balance
        self.payouts[slip_code] = payout  # persist for idempotent re-runs


def _slip(
    code: str, stype: str, params: Mapping[str, Any], stake: float, odds: float
) -> SlipRecord:
    return SlipRecord(
        slip_code=code,
        player_code="P1",
        settlement_type=stype,
        parameters=params,
        stake=stake,
        odds=odds,
    )


def _ctx_winner_1() -> GradingContext:
    return GradingContext(results=[SessionResult(session_key=1, driver_number=1, position=1)])


def test_first_run_settles_win_and_credits_wallet() -> None:
    repo = FakeRepo(
        _ctx_winner_1(), [_slip("S1", "driver_wins", {"driver_number": 1}, 10.0, 4.0)], {"P1": 50.0}
    )
    run = SettlementEngine(repo).settle_session(1, NOW)
    assert run.settled == 1 and run.reconciled == 0
    assert repo.balances["P1"] == 90.0  # 50 + 10*4 payout


def test_rerun_is_idempotent() -> None:
    repo = FakeRepo(
        _ctx_winner_1(), [_slip("S1", "driver_wins", {"driver_number": 1}, 10.0, 4.0)], {"P1": 50.0}
    )
    SettlementEngine(repo).settle_session(1, NOW)
    balance_after_first = repo.balances["P1"]
    run2 = SettlementEngine(repo).settle_session(1, NOW)
    assert run2.unchanged == 1 and run2.settled == 0
    assert repo.balances["P1"] == balance_after_first  # no double-pay


def test_void_refunds_stake() -> None:
    # driver 99 has no result row -> VOID
    repo = FakeRepo(
        _ctx_winner_1(),
        [_slip("S1", "driver_wins", {"driver_number": 99}, 10.0, 4.0)],
        {"P1": 50.0},
    )
    run = SettlementEngine(repo).settle_session(1, NOW)
    assert run.voided == 1
    assert repo.balances["P1"] == 60.0  # refund the 10 stake


def test_reconciles_after_data_correction() -> None:
    # First graded as a loss (driver 2 not the winner); pre-seed that settlement.
    repo = FakeRepo(
        _ctx_winner_1(), [_slip("S1", "driver_wins", {"driver_number": 1}, 10.0, 4.0)], {"P1": 50.0}
    )
    repo.payouts["S1"] = 0.0  # a prior "Lost" settlement
    run = SettlementEngine(repo).settle_session(1, NOW)
    assert run.reconciled == 1
    assert repo.balances["P1"] == 90.0  # +40 correction


def test_multiple_slips_same_player_use_running_balance() -> None:
    slips = [
        _slip("S1", "driver_wins", {"driver_number": 1}, 10.0, 2.0),  # payout 20
        _slip("S2", "podium_contains", {"driver_number": 1}, 5.0, 1.5),  # payout 7.5
    ]
    repo = FakeRepo(_ctx_winner_1(), slips, {"P1": 100.0})
    run = SettlementEngine(repo).settle_session(1, NOW)
    assert run.settled == 2
    assert run.total_processed == 2
    assert repo.balances["P1"] == 127.5  # 100 + 20 + 7.5 on the running balance
