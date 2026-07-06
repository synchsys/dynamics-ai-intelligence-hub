# Strategy classification

The supervised **classification** deliverable (#52, Epic 7): predict a stint's
tyre compound from race-context features — completing the supervised (regression
#49) + classification (this) + unsupervised (clustering #53) trio.

## Approach (`src/ml/classification.py`)

1. **Features/target** — `race_context_features(laps)` → per-stint X (`StartLap`,
   `StintLength`, `AvgPace`, `BestPace`, `PaceRange`) and `y = Compound`.
2. **Leakage-free split** — `GroupShuffleSplit` grouped by driver.
3. **Baseline** — `DummyClassifier(most_frequent)`.
4. **Model** — `RandomForestClassifier` (`random_state = 0`).
5. **Metrics** — accuracy, macro-F1, and a confusion matrix; `beats_baseline`
   compares macro-F1 (which penalises ignoring rare classes, unlike accuracy).
6. **Run logging** — `run_record()` for the experiment tracker (#56).

## Results (live — 2023 Singapore GP)

| | Accuracy | Macro-F1 |
|-|----------|----------|
| Baseline (majority) | 0.42 | 0.20 |
| Random forest | **0.83** | **0.61** |

31 train / 12 test stints across HARD/MEDIUM/SOFT. The model classifies HARD and
MEDIUM stints perfectly and clearly beats the baseline; the two held-out SOFT
stints are misread as MEDIUM (rare class, small sample).

## Limitations

- Small, imbalanced sample from a single session — macro-F1 is dragged by the
  rare SOFT class; pooling races and class weighting would help.
- No hyperparameter search. See the model card for full details.
