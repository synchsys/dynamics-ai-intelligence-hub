"""Train + serialise the lap-time model for serving (#57).

Fits the lap-time regressor on a live FastF1 session and writes a versioned model
artefact into the Functions package (git-ignored), so it ships with the deploy
and the inference Function finds it as the bundled default (or via MODEL_PATH).

Run: python scripts/ml/export_lap_model.py
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))

# Bundled next to azure_functions.inference so `func publish` from src/ ships it
# and inference.load_served_model() finds it with no MODEL_PATH needed.
ARTEFACT = str(
    pathlib.Path(__file__).resolve().parents[2]
    / "src/azure_functions/artifacts/lap-time-regression.joblib"
)


def main() -> int:
    from fastf1_analytics import session_laps
    from ml import export_model, fit_lap_model, load_model, predict

    laps = session_laps(2023, "Singapore", "R", cache="datasets/fastf1-cache")
    model = fit_lap_model(laps)
    path = export_model(model, ARTEFACT)
    print(f"exported {model.metadata.model_type} v{model.metadata.version} -> {path}")
    print(f"features: {model.metadata.feature_names}")

    # Round-trip smoke check.
    reloaded = load_model(path)
    sample = {"LapNumber": 15, "Stint": 2, "StintLap": 5, "TyreLife": 5, "Compound": "MEDIUM"}
    seconds = predict(reloaded, sample)
    print(f"sample prediction for {sample}: {seconds:.3f}s")
    ok = seconds > 0
    print("OK" if ok else "FAILURES PRESENT")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
