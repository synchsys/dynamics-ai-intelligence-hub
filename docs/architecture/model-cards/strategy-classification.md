# Model card — strategy classification

## Overview
- **Task:** supervised classification — predict a stint's tyre **compound**
  (strategy label) from race-context features.
- **Model:** `RandomForestClassifier` (scikit-learn), `random_state = 0`;
  majority-class baseline via `DummyClassifier`.
- **Code:** `src/ml/classification.py` (#52). **Seed:** `DEFAULT_SEED = 0`.

## Data & features
- **Data:** FastF1 laps for a session (dev: 2023 Singapore GP).
- **Features (#51):** per-stint `StartLap`, `StintLength`, `AvgPace`, `BestPace`,
  `PaceRange`. **Target:** `Compound` (HARD / MEDIUM / SOFT).
- **Split:** `GroupShuffleSplit` grouped by driver — no driver in both train and
  test.

## Metrics (held-out, 2023 Singapore GP)
| | Accuracy | Macro-F1 |
|-|----------|----------|
| Baseline (majority class) | 0.42 | 0.20 |
| Model | **0.83** | **0.61** |

Confusion (labels HARD, MEDIUM, SOFT): `[[5,0,0],[0,5,0],[0,2,0]]` — HARD and
MEDIUM classified perfectly; the two SOFT test stints were misread as MEDIUM.

## Intended use & limitations
- **Intended:** portfolio demonstration of a leakage-free supervised
  classification workflow.
- **Not for:** real strategy inference — small sample, class imbalance (few SOFT
  stints), single session. Macro-F1 is dragged down by the rare class.
- No hyperparameter search or class weighting; defaults for a reproducible
  baseline model.

## Reproduce
`python scripts/ml/train_strategy_classifier.py` at seed 0.
