# Model evaluation & comparison

A single, consistent harness (#54, `src/ml/evaluation.py`) evaluates the
regression (#49) and classification (#52) models the same way, so results are
comparable and reproducible.

## Method

- **`cross_val_scores`** — the shared core: `cross_validate` over a
  **`GroupKFold` grouped by driver**, so every fold is leakage-free (no driver in
  both train and test) and the estimate is more robust than a single split.
  `neg_*` sklearn scorers are flipped to positive so MAE/RMSE read naturally.
- **`compare_regression` / `compare_classification`** — run the baseline and the
  model through that core and return a **model-vs-baseline table** with the same
  metrics per task.

## Metric choices

**Regression** — **MAE** (average error in seconds, directly interpretable),
**RMSE** (penalises large errors more), **R²** (variance explained; ~0 means "no
better than the mean").

**Classification** — **Accuracy** (overall correct rate) and **macro-F1** (mean
per-class F1). Macro-F1 is reported because the classes are imbalanced (few SOFT
stints) — accuracy alone would flatter a model that ignores the rare class.

## Results (live — 2023 Singapore GP, 5-fold GroupKFold)

**Regression (lap time)**

| model | MAE (s) | RMSE (s) | R² |
|-------|--------|---------|----|
| baseline (mean) | 4.29 | 8.40 | −0.00 |
| gradient boosting | **1.72** | **3.86** | **0.78** |

**Classification (compound)**

| model | Accuracy | Macro-F1 |
|-------|----------|----------|
| baseline (majority) | 0.49 | 0.29 |
| random forest | **0.69** | **0.60** |

Both models beat their baselines under cross-validation. The CV figures are
slightly less optimistic than the single-split numbers in each model card — which
is the point: they're a fairer, more robust estimate of generalisation.

## Reproduce

`notebooks/model-comparison.ipynb`, or call `compare_regression(laps)` /
`compare_classification(laps)` directly. Deterministic at `random_state = 0`.
