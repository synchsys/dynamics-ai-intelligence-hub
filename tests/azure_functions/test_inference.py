"""Tests for the HTTP inference logic (#57)."""

import pandas as pd
import pytest

import azure_functions.inference as inference_mod
from azure_functions.inference import (
    handle_predict,
    load_served_model,
    predict_lap_time,
)
from ml import fit_lap_model
from ml.serving import ServedModel
from shared.exceptions import ConfigError


def _model() -> ServedModel:
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
                    "Compound": "MEDIUM",
                }
            )
    return fit_lap_model(pd.DataFrame(rows))


VALID = {"LapNumber": 5, "Stint": 1, "StintLap": 5, "TyreLife": 5, "Compound": "MEDIUM"}


def test_predict_lap_time_valid() -> None:
    result = predict_lap_time(VALID, model=_model())
    assert result["model"] == "lap-time-regression" and result["version"] == "1.0.0"
    assert isinstance(result["prediction_seconds"], float) and result["prediction_seconds"] > 0


def test_predict_lap_time_invalid_raises() -> None:
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        predict_lap_time({"LapNumber": "not-an-int"}, model=_model())


def test_handle_predict_200_and_400() -> None:
    model = _model()
    status_ok, payload_ok = handle_predict(VALID, model=model)
    assert status_ok == 200 and payload_ok["prediction_seconds"] > 0

    status_bad, payload_bad = handle_predict({"LapNumber": 1}, model=model)  # missing fields
    assert status_bad == 400 and payload_bad["error"] == "invalid input"


def test_handle_predict_none_body_is_400() -> None:
    status, payload = handle_predict(None, model=_model())
    assert status == 400 and "error" in payload


def test_load_served_model_caches_by_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path: object
) -> None:
    inference_mod._MODEL_CACHE.clear()
    calls = {"n": 0}

    def fake_load(path: str) -> str:
        calls["n"] += 1
        return f"model-for-{path}"

    monkeypatch.setattr(inference_mod, "load_model", fake_load)
    a = load_served_model("/some/model.joblib")
    b = load_served_model("/some/model.joblib")
    assert a is b and calls["n"] == 1  # loaded once, reused


def test_load_served_model_missing_path_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MODEL_PATH", raising=False)
    with pytest.raises(ConfigError, match="MODEL_PATH"):
        load_served_model()
