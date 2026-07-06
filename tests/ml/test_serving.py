"""Tests for model packaging + prediction (#57)."""

from pathlib import Path

import pandas as pd

from ml import export_model, fit_lap_model, load_model, predict
from ml.serving import build_feature_row


def _laps() -> pd.DataFrame:
    rows = []
    for d in range(6):
        for tyre in range(1, 8):
            rows.append(
                {
                    "Driver": f"D{d}",
                    "LapNumber": tyre,
                    "LapTime": pd.to_timedelta(93.0 + 0.3 * tyre, unit="s"),
                    "Stint": 1,
                    "TyreLife": tyre,
                    "Compound": "MEDIUM" if tyre % 2 else "SOFT",
                }
            )
    return pd.DataFrame(rows)


def test_fit_lap_model_bundles_metadata() -> None:
    model = fit_lap_model(_laps())
    assert model.metadata.model_type == "lap-time-regression"
    assert model.metadata.version == "1.0.0"
    assert {"LapNumber", "Stint", "StintLap", "TyreLife"} <= set(model.metadata.feature_names)
    assert any(name.startswith("Comp_") for name in model.metadata.feature_names)


def test_export_load_round_trip_predicts_identically(tmp_path: Path) -> None:
    model = fit_lap_model(_laps())
    sample = {"LapNumber": 5, "Stint": 1, "StintLap": 5, "TyreLife": 5, "Compound": "MEDIUM"}
    before = predict(model, sample)

    path = export_model(model, tmp_path / "m.joblib")
    assert path.exists()
    reloaded = load_model(path)
    assert reloaded.metadata.feature_names == model.metadata.feature_names
    assert predict(reloaded, sample) == before  # deterministic across serialisation


def test_predict_returns_float() -> None:
    model = fit_lap_model(_laps())
    result = predict(
        model, {"LapNumber": 3, "Stint": 1, "StintLap": 3, "TyreLife": 3, "Compound": "SOFT"}
    )
    assert isinstance(result, float) and result > 0


def test_build_feature_row_aligns_to_training_columns() -> None:
    names = ["LapNumber", "Stint", "StintLap", "TyreLife", "Comp_MEDIUM", "Comp_SOFT"]
    row = build_feature_row(
        {"LapNumber": 5, "Stint": 1, "StintLap": 2, "TyreLife": 2, "Compound": "SOFT"}, names
    )
    assert list(row.columns) == names
    assert row.loc[0, "Comp_SOFT"] == 1.0 and row.loc[0, "Comp_MEDIUM"] == 0.0


def test_build_feature_row_unknown_compound_is_all_zero() -> None:
    names = ["LapNumber", "Stint", "StintLap", "TyreLife", "Comp_MEDIUM", "Comp_SOFT"]
    row = build_feature_row(
        {"LapNumber": 1, "Stint": 1, "StintLap": 1, "TyreLife": 1, "Compound": "WET"}, names
    )
    assert row.loc[0, "Comp_MEDIUM"] == 0.0 and row.loc[0, "Comp_SOFT"] == 0.0
