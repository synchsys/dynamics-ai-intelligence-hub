"""Train the v2 odds model and report calibration + heuristic comparison (#232).

Builds a leakage-free training set from several 2023 races (each driver's form =
their finishing positions in the *other* races; label = win/podium in the held
race), trains the calibrated model, prints a calibration curve, and compares
model vs heuristic prices for a strong and a weak driver.

Run: python scripts/paddock/train_odds_model.py
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))

ROUNDS = [1, 2, 3, 4, 5, 6]  # 2023 rounds


def main() -> int:
    import numpy as np
    from sklearn.calibration import calibration_curve

    from fastf1_analytics import load_session
    from paddock import HeuristicPricer
    from paddock.odds_model import ModelPricer, train_odds_model

    # race -> {driver_number: finishing_position (None = DNF/unclassified)}
    races: dict[int, dict[int, int | None]] = {}
    for rnd in ROUNDS:
        results = load_session(2023, rnd, "R", cache="datasets/fastf1-cache").results
        races[rnd] = {
            int(row.DriverNumber): (int(row.Position) if not np.isnan(row.Position) else None)
            for row in results.itertuples()
        }
    print(f"loaded {len(races)} races")

    # Leave-one-out samples: form from the other races, outcome in the held race.
    samples: list[tuple[list[int | None], bool, bool]] = []
    for held, table in races.items():
        for driver, pos in table.items():
            form = [races[r].get(driver) for r in races if r != held]
            samples.append((form, pos == 1, pos is not None and pos <= 3))
    model = train_odds_model(samples, cv=3)
    print(f"trained on {len(samples)} driver-race samples")

    # Calibration curve for the win model.
    from paddock.odds_model import _row, form_features

    feats = [_row(form_features(f)) for f, _w, _p in samples]
    probs = model.win_model.predict_proba(feats)[:, 1]
    actual, predicted = calibration_curve(
        [w for _f, w, _p in samples], probs, n_bins=5, strategy="quantile"
    )
    print("calibration (predicted -> actual win rate):")
    for p, a in zip(predicted, actual, strict=False):
        print(f"  {p:.2f} -> {a:.2f}")

    # Model vs heuristic for a season-long-strong (#1 VER) and weaker driver.
    season_form = {d: [races[r].get(d) for r in races] for d in {1, 77}}
    heuristic = HeuristicPricer(season_form)
    pricer = ModelPricer(model, season_form, fallback=heuristic)
    for dn in (1, 77):
        m = pricer.price("driver_wins", {"driver_number": dn})
        h = heuristic.price("driver_wins", {"driver_number": dn})
        print(
            f"driver {dn} win: model {m.line} (p={m.probability:.2f}) | heuristic {h.line} (p={h.probability:.2f})"
        )

    ok = 0.0 <= float(probs.min()) and float(probs.max()) <= 1.0
    print("OK" if ok else "FAILURES PRESENT")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
