"""Model packaging + prediction for serving (#57).

Serialises a trained lap-time model with version metadata (including the exact
training feature columns) and reconstructs an aligned feature row at inference
time, so a single-record request predicts through the same pipeline the model was
trained on. Persistence uses ``joblib``; the HTTP binding lives in
``azure_functions.inference``.
"""

from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

from ml.features import lap_features

MODEL_TYPE = "lap-time-regression"
MODEL_VERSION = "1.0.0"

# Raw request fields (before one-hot encoding of Compound).
LAP_REQUEST_FIELDS = ("LapNumber", "Stint", "StintLap", "TyreLife", "Compound")


@dataclass(frozen=True)
class ModelMetadata:
    model_type: str
    version: str
    feature_names: list[str]


@dataclass(frozen=True)
class ServedModel:
    estimator: Any
    metadata: ModelMetadata


def fit_lap_model(laps: pd.DataFrame, *, random_state: int = 0) -> ServedModel:
    """Fit the lap-time regressor on all rows and bundle it with its metadata."""
    features, target = lap_features(laps)
    estimator = HistGradientBoostingRegressor(random_state=random_state).fit(features, target)
    metadata = ModelMetadata(MODEL_TYPE, MODEL_VERSION, list(features.columns))
    return ServedModel(estimator=estimator, metadata=metadata)


def export_model(model: ServedModel, path: str | Path) -> Path:
    """Serialise a :class:`ServedModel` to ``path`` (joblib); returns the path."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"estimator": model.estimator, "metadata": asdict(model.metadata)}, target)
    return target


def load_model(path: str | Path) -> ServedModel:
    """Load a serialised :class:`ServedModel`."""
    payload = joblib.load(Path(path))
    return ServedModel(
        estimator=payload["estimator"], metadata=ModelMetadata(**payload["metadata"])
    )


def build_feature_row(features: Mapping[str, Any], feature_names: list[str]) -> pd.DataFrame:
    """Turn a single raw request into a one-row frame aligned to the training columns."""
    row = pd.DataFrame([{field: features.get(field) for field in LAP_REQUEST_FIELDS}])
    encoded = pd.get_dummies(row, columns=["Compound"], prefix="Comp")
    return encoded.reindex(columns=feature_names, fill_value=0).astype(float)


def predict(model: ServedModel, features: Mapping[str, Any]) -> float:
    """Predict lap time (seconds) for one raw feature record."""
    row = build_feature_row(features, model.metadata.feature_names)
    return float(model.estimator.predict(row)[0])
