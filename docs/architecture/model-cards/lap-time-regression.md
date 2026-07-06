# Model card — lap-time regression

## Overview
- **Task:** supervised regression — predict a lap's time (seconds) from lap/stint
  context.
- **Model:** `HistGradientBoostingRegressor` (scikit-learn), default
  hyperparameters, `random_state = 0`.
- **Code:** `src/ml/regression.py` (#49). **Seed:** `DEFAULT_SEED = 0`.

## Data & features
- **Data:** FastF1 laps for a session (dev: 2023 Singapore GP), cleaned via
  `clean_laps`.
- **Features (#51):** `LapNumber`, `Stint`, `StintLap`, `TyreLife`, one-hot
  compound. **Target:** `LapTimeSeconds`.
- **Split:** `GroupShuffleSplit` grouped by driver — no driver appears in both
  train and test.

## Metrics (held-out, 2023 Singapore GP)
| | MAE (s) | RMSE (s) | R² |
|-|--------|---------|----|
| Baseline (train mean) | 3.99 | 7.98 | — |
| Model | **1.52** | **3.43** | **0.81** |

779 train / 283 test laps; the model roughly halves the baseline MAE.

## Intended use & limitations
- **Intended:** portfolio demonstration of a leakage-free supervised workflow;
  relative lap-pace estimation within a session.
- **Not for:** cross-session prediction (single-session training), or timing
  decisions — it excludes traffic, weather, and safety-car context.
- Lap data includes in/out and traffic-affected laps (no accuracy filter),
  inflating RMSE; no hyperparameter search.

## Reproduce
`python scripts/ml/train_lap_regression.py` (or `log_experiments.py`) at seed 0.
