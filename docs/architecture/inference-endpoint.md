# Inference endpoint

The lap-time model served over HTTP on the Functions platform (#57) — ML made
callable from the app and agents behind a stable endpoint.

## Packaging

`ml.serving.fit_lap_model(laps)` fits the lap-time regressor and bundles it with
**version metadata**, crucially the exact training feature columns.
`export_model` serialises it with joblib; `scripts/ml/export_lap_model.py`
produces the artefact at `src/azure_functions/artifacts/lap-time-regression.joblib`
(git-ignored). Because the deploy root is `src/`, the artefact ships **inside the
package**, and `load_served_model()` finds it as the **bundled default** via
`__file__` — so `/predict` works with no app setting and independent of the
host's working directory.

Resolution order (`load_served_model`): explicit path → **`MODEL_PATH`** app
setting (override, e.g. to load from a mounted share) → bundled artefact. The
model is loaded **once per path** (cached and reused across invocations). If none
resolves, the endpoint returns 500 with a clear `MODEL_PATH` error.

## Endpoint contract

`POST /api/predict` (function-key auth).

**Request** — one lap-feature record:

```json
{ "LapNumber": 15, "Stint": 2, "StintLap": 5, "TyreLife": 5, "Compound": "MEDIUM" }
```

**200 response**:

```json
{ "prediction_seconds": 100.789, "model": "lap-time-regression", "version": "1.0.0" }
```

**400 response** (invalid/missing fields) — a clear error with per-field detail:

```json
{ "error": "invalid input", "detail": [ ... ] }
```

At inference the raw record is one-hot encoded and **reindexed to the model's
stored `feature_names`** (missing compounds → 0), so requests predict through the
exact pipeline the model was trained on. An unknown compound yields all-zero
compound columns rather than an error.

## Design

Validation (`LapPredictionRequest`, Pydantic) and prediction live in
`azure_functions/inference.py` (bindings-free, unit-tested); `function_app.py` is
the thin HTTP binding. Verified live: the exported artefact predicts ~100.8s for a
mid-race medium-tyre lap, returning 200; malformed input returns 400.

## Reproduce

```bash
pip install -e ".[analytics,functions]"
python scripts/ml/export_lap_model.py                 # -> artifacts/models/lap-time-regression.joblib
MODEL_PATH=artifacts/models/lap-time-regression.joblib func start   # in src/azure_functions
curl -X POST localhost:7071/api/predict -d '{"LapNumber":15,"Stint":2,"StintLap":5,"TyreLife":5,"Compound":"MEDIUM"}'
```
