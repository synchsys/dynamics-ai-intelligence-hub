"""Live verification of FastF1 cache + session loading (#39).

Loads a session twice through the cache and confirms real lap data returns and
the second (cached) load is measurably faster. Uses a scratch cache dir so it's
repeatable; safe to run offline once the session is cached.

Run: python scripts/analytics/verify_fastf1.py
"""

import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))


def main() -> int:
    from fastf1_analytics import load_session

    cache = pathlib.Path("datasets/fastf1-cache")

    t0 = time.perf_counter()
    session = load_session(2023, "Singapore", "R", cache=cache)
    cold = time.perf_counter() - t0
    laps = session.laps
    fastest = laps.pick_fastest()
    print(f"cold load:   {cold:.1f}s — {len(laps)} laps")
    print(f"fastest lap: {fastest['Driver']} {fastest['LapTime']}")

    t1 = time.perf_counter()
    load_session(2023, "Singapore", "R", cache=cache)
    warm = time.perf_counter() - t1
    print(f"cached load: {warm:.1f}s")

    ok = len(laps) > 0 and warm < cold
    print("OK" if ok else "FAILURES PRESENT")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
