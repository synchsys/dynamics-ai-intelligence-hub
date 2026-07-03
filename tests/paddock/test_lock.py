"""Tests for confirm-and-lock (domain + service)."""

from collections.abc import Mapping, Sequence
from datetime import datetime, timedelta
from typing import Any

import pytest

from paddock.wager import (
    AlreadyLocked,
    DeadlinePassed,
    InsufficientFunds,
    RaceEvent,
    WagerLockService,
    WagerSlip,
    Wallet,
    lock_wager,
)

NOW = datetime(2024, 5, 1, 12, 0, 0)
DEADLINE = NOW + timedelta(hours=1)


def slip(status: str = "Draft", stake: float = 10.0) -> WagerSlip:
    return WagerSlip(slip_code="S1", session_key=9165, player_code="P1", stake=stake, status=status)


def wallet(balance: float = 100.0) -> Wallet:
    return Wallet(player_code="P1", balance=balance)


def race(deadline: datetime = DEADLINE) -> RaceEvent:
    return RaceEvent(session_key=9165, status="Open", lock_deadline=deadline)


# --- domain ----------------------------------------------------------------


def test_lock_success_debits_and_locks() -> None:
    outcome = lock_wager(slip(stake=25.0), wallet(100.0), race(), NOW)
    assert outcome.slip_updates == {"racy_status": "Locked"}
    assert outcome.wallet_updates == {"racy_balance": 75.0}
    assert outcome.new_balance == 75.0


def test_lock_rejects_non_draft() -> None:
    with pytest.raises(AlreadyLocked):
        lock_wager(slip(status="Locked"), wallet(), race(), NOW)


def test_lock_rejects_after_deadline() -> None:
    with pytest.raises(DeadlinePassed):
        lock_wager(slip(), wallet(), race(deadline=NOW - timedelta(minutes=1)), NOW)


def test_lock_rejects_insufficient_funds() -> None:
    with pytest.raises(InsufficientFunds):
        lock_wager(slip(stake=200.0), wallet(100.0), race(), NOW)


def test_lock_exactly_funded_is_allowed() -> None:
    outcome = lock_wager(slip(stake=100.0), wallet(100.0), race(), NOW)
    assert outcome.new_balance == 0.0


# --- service (atomic commit) -----------------------------------------------


class FakeDataverse:
    def __init__(self) -> None:
        self.batches: list[list[tuple[str, str, Mapping[str, Any]]]] = []

    def batch_upsert(self, operations: Sequence[tuple[str, str, Mapping[str, Any]]]) -> None:
        self.batches.append(list(operations))


def test_service_commits_both_updates_in_one_batch() -> None:
    dv = FakeDataverse()
    outcome = WagerLockService(dv).confirm_and_lock(slip(stake=30.0), wallet(50.0), race(), NOW)
    assert outcome.new_balance == 20.0
    assert len(dv.batches) == 1  # single atomic changeset
    ops = dv.batches[0]
    entity_sets = {op[0] for op in ops}
    assert entity_sets == {"racy_wagerslips", "racy_wallets"}
    slip_op = next(op for op in ops if op[0] == "racy_wagerslips")
    assert slip_op[1] == "racy_slipcode='S1'"
    assert slip_op[2] == {"racy_status": "Locked"}


def test_service_does_not_commit_on_rejection() -> None:
    dv = FakeDataverse()
    with pytest.raises(InsufficientFunds):
        WagerLockService(dv).confirm_and_lock(slip(stake=999.0), wallet(10.0), race(), NOW)
    assert dv.batches == []  # nothing persisted — no partial debit
