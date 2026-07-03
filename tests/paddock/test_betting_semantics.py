"""End-to-end real-world betting semantics: stake, odds, return, and net P&L.

Confirms the money behaves like a real wager: at a fraction of "A/B", a winning
stake returns stake + stake*(A/B), a loss forfeits the stake, and a void refunds
it — with the stake debited at lock (#228) and the gross return credited at
settlement (#229).
"""

from datetime import datetime, timedelta

from paddock.odds import decimal_to_fraction
from paddock.settlement import Outcome
from paddock.wager import RaceEvent, WagerSlip, Wallet, lock_wager, payout

NOW = datetime(2024, 5, 1, 12, 0, 0)


def _net(stake: float, decimal_odds: float, outcome: Outcome) -> float:
    """Net wallet change over the real lifecycle: debit stake at lock, credit payout."""
    slip = WagerSlip("S1", 9165, "P1", stake, "Draft")
    wallet = Wallet("P1", 1000.0)
    race = RaceEvent(9165, "Open", NOW + timedelta(hours=1))
    locked = lock_wager(slip, wallet, race, NOW)  # debits the stake
    debited = locked.new_balance - wallet.balance  # negative
    credited = payout(outcome, stake, decimal_odds)
    return round(debited + credited, 2)


def test_two_to_one_against_pays_like_the_real_world() -> None:
    # 2/1 == decimal 3.0: £10 wins £20 profit (£30 back).
    assert decimal_to_fraction(3.0) == (2, 1)
    assert payout(Outcome.WIN, 10.0, 3.0) == 30.0  # total return incl. stake
    assert _net(10.0, 3.0, Outcome.WIN) == 20.0  # profit = stake * (2/1)


def test_odds_on_favourite_pays_less_than_stake_in_profit() -> None:
    # 1/2 == decimal 1.5: £10 wins £5 profit.
    assert decimal_to_fraction(1.5) == (1, 2)
    assert _net(10.0, 1.5, Outcome.WIN) == 5.0


def test_evens_doubles_the_stake() -> None:
    assert decimal_to_fraction(2.0) == (1, 1)  # evens
    assert _net(10.0, 2.0, Outcome.WIN) == 10.0  # £10 profit


def test_loss_forfeits_only_the_stake() -> None:
    assert _net(10.0, 3.0, Outcome.LOSE) == -10.0


def test_void_refunds_the_stake_net_zero() -> None:
    assert _net(10.0, 3.0, Outcome.VOID) == 0.0
