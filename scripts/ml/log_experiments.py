"""Log portfolio-model runs and demonstrate reproducibility (#56).

Runs lap-time regression twice (same seed) and stint clustering once on a live
FastF1 session, logging each to a JSONL experiment log. Asserts the two
regression runs reproduce identical metrics (fixed-seed reproducibility) and
prints the best run by MAE.

Run: python scripts/ml/log_experiments.py
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))


def main() -> int:
    from fastf1_analytics import session_laps
    from ml import (
        DEFAULT_SEED,
        ExperimentTracker,
        cluster_stints,
        race_context_features,
        train_lap_regressor,
    )

    laps = session_laps(2023, "Singapore", "R", cache="datasets/fastf1-cache")
    tracker = ExperimentTracker("datasets/experiments/runs.jsonl")

    # Two identical regression runs at the fixed seed.
    for _ in range(2):
        result = train_lap_regressor(laps, random_state=DEFAULT_SEED)
        tracker.log_run(
            "lap-time-regression",
            params={"model": "HistGradientBoostingRegressor", "n_train": result.n_train},
            metrics=vars(result.model),
            seed=DEFAULT_SEED,
        )

    # One clustering run.
    features, _ = race_context_features(laps)
    features = features[features["StintLength"] >= 5].reset_index(drop=True)
    clustering = cluster_stints(features, random_state=DEFAULT_SEED)
    tracker.log_run(
        "stint-clustering",
        params={"algorithm": "KMeans", "k": clustering.k},
        metrics={"silhouette": clustering.silhouette},
        seed=DEFAULT_SEED,
    )

    runs = tracker.runs()
    reg_runs = [r for r in runs if r.name == "lap-time-regression"]
    reproducible = reg_runs[0].metrics == reg_runs[1].metrics
    best = tracker.best("mae")

    print(f"logged {len(runs)} runs to datasets/experiments/runs.jsonl")
    for r in runs:
        print(f"  {r.name}: {r.metrics} (seed={r.seed})")
    print(f"regression reproducible at seed {DEFAULT_SEED}: {reproducible}")
    print(f"best by MAE: {best.name if best else None}")

    ok = len(runs) >= 2 and reproducible and best is not None
    print("OK" if ok else "FAILURES PRESENT")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
