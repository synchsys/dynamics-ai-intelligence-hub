"""Live end-to-end verification of the Paddock settlement spine (#226-#229).

Two parts against the real ``racy_`` Dataverse tables and the ingested OpenF1
session 9165 (2023 Singapore GP):

* **Part A (read-only)** — build a :class:`GradingContext` from live data and
  grade a curated set of the 12 Tier-A settlement types, asserting each against
  the known race result. Includes the void-on-missing cases (no grid/lap/pit
  data ingested → those graders must VOID, never guess).
* **Part B (mutating, self-cleaning)** — seed WIN / LOSE / VOID slips + wallets,
  run the real :class:`SettlementEngine` over live Dataverse, assert payouts and
  wallet balances, re-run to prove idempotency, then delete everything it made.

Run: ``python scripts/paddock/verify_settlement.py`` (requires .env).
"""

import json
import os
import pathlib
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))

SESSION_KEY = 9165  # 2023 Singapore GP — results ingested; no grid/lap/pit rows

# Primary-key logical names (schema name lowercased + "id").
PRIMARY_ID = {
    "racy_wagerslips": "racy_wagerslipid",
    "racy_wallets": "racy_walletid",
    "racy_settlements": "racy_settlementid",
}


def _load_env() -> None:
    for line in (pathlib.Path(__file__).resolve().parents[2] / ".env").read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


def _check(label: str, got: object, want: object) -> bool:
    ok = got == want
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}: got {got!r}, want {want!r}")
    return ok


def part_a(repo: object) -> bool:
    from paddock.settlement import Outcome
    from paddock.settlement import grade as grade_spec

    ctx = repo.grading_context(SESSION_KEY)  # type: ignore[attr-defined]
    print(
        f"Part A — grading over live data: {len(ctx.results)} results, "
        f"{len(ctx.grid)} grid, {len(ctx.laps)} laps, {len(ctx.pit)} pit rows"
    )
    W, L, V = Outcome.WIN, Outcome.LOSE, Outcome.VOID
    cases = [
        # result-based (data present)
        ("driver_wins #55 (Sainz, P1)", "driver_wins", {"driver_number": 55}, W),
        ("driver_wins #4 (Norris, P2)", "driver_wins", {"driver_number": 4}, L),
        ("podium_contains #44 (P3)", "podium_contains", {"driver_number": 44}, W),
        ("podium_contains #16 (P4)", "podium_contains", {"driver_number": 16}, L),
        ("points_finish #20 (P10)", "points_finish", {"driver_number": 20}, W),
        ("points_finish #23 (P11)", "points_finish", {"driver_number": 23}, L),
        (
            "driver_finish_position #4 <=2",
            "driver_finish_position",
            {"driver_number": 4, "operator": "<=", "value": 2},
            W,
        ),
        (
            "head_to_head #55 vs #4",
            "head_to_head_finish",
            {"driver_a": 55, "driver_b": 4},
            W,
        ),
        (
            "head_to_head #55 vs #31 (DNF)",
            "head_to_head_finish",
            {"driver_a": 55, "driver_b": 31},
            W,
        ),
        ("classified_finish #63 (P16 DNF)", "classified_finish", {"driver_number": 63}, L),
        ("driver_dnf #77 (Bottas DNF)", "driver_dnf", {"driver_number": 77}, W),
        ("driver_dnf #55 (finished)", "driver_dnf", {"driver_number": 55}, L),
        (
            "winning_margin < 1.0s (gap 0.812)",
            "winning_margin",
            {"operator": "<", "seconds": 1.0},
            W,
        ),
        (
            "winning_margin < 0.5s",
            "winning_margin",
            {"operator": "<", "seconds": 0.5},
            L,
        ),
        # void-on-missing (no grid/lap/pit data) + unknown driver
        ("beats_grid #55 (no grid)", "beats_grid", {"driver_number": 55}, V),
        (
            "positions_gained>=3 (no grid)",
            "positions_gained_at_least",
            {"driver_number": 55, "n": 3},
            V,
        ),
        ("fastest_lap_by #55 (no laps)", "fastest_lap_by", {"driver_number": 55}, V),
        (
            "pit_stops <=2 (no pits)",
            "pit_stops",
            {"driver_number": 55, "operator": "<=", "n": 2},
            V,
        ),
        ("driver_wins #99 (unknown)", "driver_wins", {"driver_number": 99}, V),
    ]
    ok = True
    for label, code, params, want in cases:
        ok &= _check(label, grade_spec(code, params, ctx), want)
    return ok


def _delete_all(dv: object, entity_set: str) -> int:
    rows = dv.retrieve_multiple(entity_set)  # type: ignore[attr-defined]
    for r in rows:
        dv.delete(entity_set, r[PRIMARY_ID[entity_set]])  # type: ignore[attr-defined]
    return len(rows)


def part_b(dv: object, repo: object) -> bool:
    from paddock.wager.settlement import SettlementEngine

    print("\nPart B — end-to-end settlement (mutating, self-cleaning)")
    # Clean slate: remove any stale test rows so settle_session sees only ours.
    for es in ("racy_settlements", "racy_wagerslips", "racy_wallets"):
        n = _delete_all(dv, es)
        if n:
            print(f"  cleared {n} pre-existing {es} row(s)")

    # Seed three players, each starting at 100 (post-lock balance), one slip each.
    seeds = [
        ("WVER1", "SVER1", "driver_wins", {"driver_number": 55}, 50.0, 1.30, "WIN", 65.0, 165.0),
        ("WVER2", "SVER2", "driver_dnf", {"driver_number": 55}, 40.0, 3.00, "LOSE", 0.0, 100.0),
        ("WVER3", "SVER3", "beats_grid", {"driver_number": 55}, 20.0, 2.00, "VOID", 20.0, 120.0),
    ]
    for player, slip, code, params, stake, odds, _kind, _payout, _bal in seeds:
        dv.create(  # type: ignore[attr-defined]
            "racy_wallets", {"racy_playercode": player, "racy_balance": 100.0}
        )
        dv.create(  # type: ignore[attr-defined]
            "racy_wagerslips",
            {
                "racy_slipcode": slip,
                "racy_sessionkey": SESSION_KEY,
                "racy_playercode": player,
                "racy_settlementtypecode": code,
                "racy_parameters": json.dumps(params),
                "racy_stake": stake,
                "racy_frozenodds": odds,
                "racy_status": "Locked",
            },
        )

    engine = SettlementEngine(repo)  # type: ignore[arg-type]
    run1 = engine.settle_session(SESSION_KEY, datetime.now(timezone.utc))
    print(f"  run 1: settled={run1.settled} voided={run1.voided} "
          f"reconciled={run1.reconciled} unchanged={run1.unchanged}")

    ok = True
    ok &= _check("run1 settled (WIN+LOSE)", run1.settled, 2)
    ok &= _check("run1 voided", run1.voided, 1)
    for player, slip, _c, _p, _s, _o, kind, payout, bal in seeds:
        ok &= _check(f"{slip} payout ({kind})", repo.existing_payout(slip), payout)  # type: ignore[attr-defined]
        ok &= _check(f"{player} balance", repo.wallet_balance(player), bal)  # type: ignore[attr-defined]

    # Idempotency: re-running settles nothing new and leaves balances untouched.
    run2 = engine.settle_session(SESSION_KEY, datetime.now(timezone.utc))
    print(f"  run 2: settled={run2.settled} voided={run2.voided} "
          f"reconciled={run2.reconciled} unchanged={run2.unchanged}")
    ok &= _check("run2 unchanged (idempotent)", run2.unchanged, 3)
    ok &= _check("run2 no new settlements", run2.settled + run2.voided + run2.reconciled, 0)
    for player, _slip, _c, _p, _s, _o, _k, _pay, bal in seeds:
        ok &= _check(f"{player} balance stable", repo.wallet_balance(player), bal)  # type: ignore[attr-defined]

    # Cleanup — remove everything this run created.
    for es in ("racy_settlements", "racy_wagerslips", "racy_wallets"):
        n = _delete_all(dv, es)
        print(f"  cleaned up {n} {es} row(s)")
    return ok


def main() -> int:
    _load_env()
    from dataverse.client import DataverseClient
    from dataverse.config import DataverseConfig
    from paddock.wager.settlement_repo import DataverseSettlementRepository

    dv = DataverseClient(DataverseConfig.from_env())
    repo = DataverseSettlementRepository(dv)

    ok_a = part_a(repo)
    ok_b = part_b(dv, repo)
    print(f"\n{'ALL PASS' if ok_a and ok_b else 'FAILURES PRESENT'} "
          f"(Part A: {'ok' if ok_a else 'FAIL'}, Part B: {'ok' if ok_b else 'FAIL'})")
    return 0 if ok_a and ok_b else 1


if __name__ == "__main__":
    raise SystemExit(main())
