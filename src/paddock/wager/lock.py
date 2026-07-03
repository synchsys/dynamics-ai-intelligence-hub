"""Confirm-and-lock: the atomic Draft → Locked wager transition (story #228).

Locking freezes the slip's spec + odds (already set at draft time), debits the
stake from the wallet, and blocks further edits — but only before the Race
Event's lock deadline and only if the wallet is funded. Per ADR-0009 this is a
**tightly-scoped transaction** (the project is Python-first, so a service over
the Dataverse client rather than a C# plug-in); atomicity — "no partial debit"
— comes from committing the slip + wallet updates in a single ``$batch``
changeset.

The domain function :func:`lock_wager` is pure (takes ``now`` explicitly) and
fully unit-tested; :class:`WagerLockService` applies it against Dataverse.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

from shared.exceptions import SharedError

BatchOp = tuple[str, str, Mapping[str, Any]]

DRAFT = "Draft"
LOCKED = "Locked"


class LockError(SharedError):
    """A wager could not be locked."""


class AlreadyLocked(LockError):
    """The slip is not in Draft (already locked/settled/void)."""


class DeadlinePassed(LockError):
    """The race event's lock deadline has passed."""


class InsufficientFunds(LockError):
    """The wallet balance does not cover the stake."""


@dataclass(frozen=True)
class WagerSlip:
    slip_code: str
    session_key: int
    player_code: str
    stake: float
    status: str


@dataclass(frozen=True)
class Wallet:
    player_code: str
    balance: float


@dataclass(frozen=True)
class RaceEvent:
    session_key: int
    status: str
    lock_deadline: datetime


@dataclass(frozen=True)
class LockOutcome:
    """The record updates a successful lock must persist (atomically)."""

    slip_updates: Mapping[str, Any]
    wallet_updates: Mapping[str, Any]
    new_balance: float


def lock_wager(
    slip: WagerSlip, wallet: Wallet, race_event: RaceEvent, now: datetime
) -> LockOutcome:
    """Validate and compute the lock; raise a :class:`LockError` if it can't proceed."""
    if slip.status != DRAFT:
        raise AlreadyLocked(f"slip {slip.slip_code} is {slip.status}, not {DRAFT}")
    if now > race_event.lock_deadline:
        raise DeadlinePassed(f"lock deadline {race_event.lock_deadline.isoformat()} has passed")
    if wallet.balance < slip.stake:
        raise InsufficientFunds(f"balance {wallet.balance} < stake {slip.stake}")
    new_balance = round(wallet.balance - slip.stake, 2)
    return LockOutcome(
        slip_updates={"racy_status": LOCKED},
        wallet_updates={"racy_balance": new_balance},
        new_balance=new_balance,
    )


class SupportsBatchUpsert(Protocol):
    def batch_upsert(self, operations: Sequence[BatchOp]) -> None: ...


class WagerLockService:
    """Applies :func:`lock_wager` to Dataverse, committing atomically."""

    def __init__(self, dataverse: SupportsBatchUpsert) -> None:
        self._dv = dataverse

    def confirm_and_lock(
        self, slip: WagerSlip, wallet: Wallet, race_event: RaceEvent, now: datetime
    ) -> LockOutcome:
        outcome = lock_wager(slip, wallet, race_event, now)
        self._dv.batch_upsert(
            [
                ("racy_wagerslips", f"racy_slipcode='{slip.slip_code}'", outcome.slip_updates),
                ("racy_wallets", f"racy_playercode='{wallet.player_code}'", outcome.wallet_updates),
            ]
        )
        return outcome
