"""HTTP model-inference logic for the Functions app (#57).

Validates a lap-feature request, predicts through the serialised lap-time model
(#57 packaging), and returns a typed prediction — the ML bridge callable from the
app and agents. The model is **loaded once and reused** (cached by path). Logic
is bindings-free and unit-tested; ``function_app.py`` is the thin HTTP binding.
The model artefact path comes from the ``MODEL_PATH`` app setting.
"""

import os
from typing import Any

from pydantic import BaseModel, ValidationError

from ml.serving import ServedModel, load_model, predict
from shared.exceptions import ConfigError
from shared.logging import get_logger

_logger = get_logger("azure_functions.inference")

# Load-once cache: path -> ServedModel.
_MODEL_CACHE: dict[str, ServedModel] = {}


class LapPredictionRequest(BaseModel):
    """Input contract for a lap-time prediction."""

    LapNumber: int
    Stint: int
    StintLap: int
    TyreLife: int
    Compound: str


def load_served_model(path: str | None = None) -> ServedModel:
    """Load the model from ``path`` (or ``MODEL_PATH``), caching per path."""
    resolved = path or os.environ.get("MODEL_PATH")
    if not resolved:
        raise ConfigError("Missing app setting MODEL_PATH")
    if resolved not in _MODEL_CACHE:
        _MODEL_CACHE[resolved] = load_model(resolved)
        _logger.info("loaded model artefact %s", resolved)
    return _MODEL_CACHE[resolved]


def predict_lap_time(body: dict[str, Any], *, model: ServedModel) -> dict[str, Any]:
    """Validate ``body`` and return a typed prediction (raises ValidationError)."""
    request = LapPredictionRequest.model_validate(body)
    seconds = predict(model, request.model_dump())
    return {
        "prediction_seconds": round(seconds, 3),
        "model": model.metadata.model_type,
        "version": model.metadata.version,
    }


def handle_predict(
    body: dict[str, Any] | None, *, model: ServedModel
) -> tuple[int, dict[str, Any]]:
    """Return ``(status, payload)`` — 200 with a prediction, or 400 on invalid input."""
    try:
        return 200, predict_lap_time(body or {}, model=model)
    except ValidationError as error:
        return 400, {"error": "invalid input", "detail": error.errors(include_url=False)}
