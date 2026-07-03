"""Settlement engine — grade locked wagers and update wallets, idempotently (story #229).

Once a race session is ingested, each locked slip is graded via the deterministic
registry (#226), a Settlement is written, and the wallet is credited by the
**payout**. The engine is:

* **Idempotent** — a slip is graded via a wallet *delta* against any prior
  settlement, so re-running the same race produces identical balances (delta 0).
* **Reconciling** — if ingested data is later corrected and a slip re-grades to a
  different outcome, the wallet is adjusted by the difference (never double-paid).
* **Void-on-missing** — a VOID grade refunds the stake.

Wallet accounting: the stake was debited at lock (#228); settlement credits the
**payout** — ``stake * odds`` on a win, ``stake`` (refund) on a void, ``0`` on a
loss. Net effect: win → gain, loss → stake lost, void → zero.

The domain (:func:`payout`, :func:`settle_slip`) is pure; :class:`SettlementEngine`
orchestrates over a :class:`SettlementRepository`. The Azure Functions timer
trigger that runs it on a schedule is the thin wrapper deferred to #20/#10.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

from paddock.settlement import GradingContext, Outcome
from paddock.settlement import grade as grade_spec

_RESULT = {Outcome.WIN: "Won", Outcome.LOSE: "Lost", Outcome.VOID: "Void"}


def payout(outcome: Outcome, stake: float, odds: float) -> float:
    """Gross amount credited to the wallet for an outcome (stake was debited at lock)."""
    if outcome is Outcome.WIN:
        return round(stake * odds, 2)
    if outcome is Outcome.VOID:
        return round(stake, 2)  # refund
    return 0.0  # loss


@dataclass(frozen=True)
class SlipRecord:
    """A locked wager slip to settle."""

    slip_code: str
    player_code: str
    settlement_type: str
    parameters: Mapping[str, Any]
    stake: float
    odds: float


@dataclass(frozen=True)
class SlipSettlement:
    """The computed settlement for one slip (result + wallet delta)."""

    slip_code: str
    result: str
    payout: float
    wallet_delta: float
    slip_status: str


def settle_slip(
    stake: float, odds: float, outcome: Outcome, existing_payout: float | None
) -> SlipSettlement:
    """Compute a slip's settlement and the wallet delta vs any prior payout.

    ``wallet_delta`` is ``new_payout - existing_payout`` so re-running with the
    same outcome yields 0 (idempotent) and a corrected outcome reconciles.
    """
    new_payout = payout(outcome, stake, odds)
    delta = round(new_payout - (existing_payout or 0.0), 2)
    result = _RESULT[outcome]
    return SlipSettlement(
        slip_code="",  # filled by the engine
        result=result,
        payout=new_payout,
        wallet_delta=delta,
        slip_status=result,
    )


@dataclass
class SettlementRun:
    """Run metrics."""

    settled: int = 0
    voided: int = 0
    reconciled: int = 0
    unchanged: int = 0

    @property
    def total_processed(self) -> int:
        return self.settled + self.voided + self.reconciled + self.unchanged


class SettlementRepository(Protocol):
    """The data access the engine needs; the Dataverse adapter implements it."""

    def grading_context(self, session_key: int) -> GradingContext: ...
    def locked_slips(self, session_key: int) -> Sequence[SlipRecord]: ...
    def existing_payout(self, slip_code: str) -> float | None: ...
    def wallet_balance(self, player_code: str) -> float: ...
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
    ) -> None: ...


class SettlementEngine:
    """Grade and settle all locked slips for an ingested session, idempotently."""

    def __init__(self, repo: SettlementRepository) -> None:
        self._repo = repo

    def settle_session(self, session_key: int, now: datetime) -> SettlementRun:
        ctx = self._repo.grading_context(session_key)
        run = SettlementRun()
        balances: dict[str, float] = {}
        for slip in self._repo.locked_slips(session_key):
            outcome = grade_spec(slip.settlement_type, dict(slip.parameters), ctx)
            existing = self._repo.existing_payout(slip.slip_code)
            ss = settle_slip(slip.stake, slip.odds, outcome, existing)

            if existing is not None and ss.wallet_delta == 0.0:
                run.unchanged += 1  # already settled to the same result — nothing to do
                continue

            if slip.player_code not in balances:
                balances[slip.player_code] = self._repo.wallet_balance(slip.player_code)
            balances[slip.player_code] = round(balances[slip.player_code] + ss.wallet_delta, 2)

            self._repo.commit_settlement(
                slip_code=slip.slip_code,
                player_code=slip.player_code,
                new_balance=balances[slip.player_code],
                result=ss.result,
                payout=ss.payout,
                slip_status=ss.slip_status,
                graded_on=now,
            )

            if existing is not None:
                run.reconciled += 1
            elif outcome is Outcome.VOID:
                run.voided += 1
            else:
                run.settled += 1
        return run
