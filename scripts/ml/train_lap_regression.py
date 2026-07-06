"""Train + evaluate lap-time regression on a live FastF1 session (#49).

Loads a real session, runs the driver-grouped, leakage-free train/test split,
trains the gradient-boosting regressor, and reports held-out MAE/RMSE/R² against
the naive baseline — asserting the model beats it.

Run: python scripts/ml/train_lap_regression.py
"""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))


def main() -> int:
    from fastf1_analytics import session_laps
    from ml import train_lap_regressor

    laps = session_laps(2023, "Singapore", "R", cache="datasets/fastf1-cache")
    result = train_lap_regressor(laps, random_state=0)

    print(f"n_train={result.n_train}  n_test={result.n_test}  features={len(result.features)}")
    print(f"baseline: MAE={result.baseline.mae}s  RMSE={result.baseline.rmse}s")
    print(f"model:    MAE={result.model.mae}s  RMSE={result.model.rmse}s  R2={result.model.r2}")
    print(json.dumps(result.run_record()))

    ok = result.beats_baseline
    print("OK" if ok else "FAILURES PRESENT — model did not beat baseline")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
