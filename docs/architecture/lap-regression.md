# Lap-time regression

The core supervised-ML deliverable (#49, Epic 7): predict lap time from the
lap/stint features (#51), beating a naive baseline on a leakage-free hold-out.

## Approach (`src/ml/regression.py`)

1. **Features/target** — `lap_features(laps)` → per-lap X (`LapNumber`, `Stint`,
   `StintLap`, `TyreLife`, compound one-hot) and `y = LapTimeSeconds`.
2. **Leakage-free split** — `GroupShuffleSplit` **grouped by driver**, so no
   driver appears in both train and test. The model must generalise the effect of
   tyre age / lap / compound, not memorise a specific driver's pace. (Feature-level
   leakage is already prevented in #51: the target and any lap-time-derived
   quantities are never features.)
3. **Baseline** — predict the training-set mean lap time for every held-out lap.
4. **Model** — `HistGradientBoostingRegressor` (handles numeric + one-hot,
   no scaling needed), deterministic given `random_state`.
5. **Metrics** — MAE, RMSE, R² on the held-out test set; `beats_baseline` is
   `model.mae < baseline.mae`.
6. **Run logging** — `run_record()` returns a flat dict (model, sizes, baseline,
   metrics, beats_baseline) for experiment tracking (#56).

## Results (live — 2023 Singapore GP, `scripts/ml/train_lap_regression.py`)

| | MAE (s) | RMSE (s) | R² |
|-|--------|---------|----|
| Baseline (train mean) | 3.99 | 7.98 | — |
| **Gradient boosting** | **1.52** | **3.43** | **0.81** |

779 train / 283 test laps (grouped by driver). The model roughly **halves** the
mean absolute error and explains ~81% of held-out lap-time variance — clearly
beating the baseline.

## Limitations

- Trained on a single session; a fuller model would pool sessions and add
  track/weather context.
- Lap data includes in/out and traffic-affected laps (no accuracy filter here),
  which inflate variance — filtering to accurate laps would tighten RMSE but
  narrow the feature distribution.
- No hyperparameter search; defaults are used for a defensible, reproducible
  baseline model rather than a tuned one.
