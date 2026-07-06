"""Train + evaluate strategy (compound) classification on a live session (#52).

Loads a real session, runs the driver-grouped leakage-free split, trains the
random-forest classifier, and reports accuracy / macro-F1 / confusion matrix
against a majority-class baseline — asserting the model beats it.

Run: python scripts/ml/train_strategy_classifier.py
"""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))


def main() -> int:
    from fastf1_analytics import session_laps
    from ml import train_strategy_classifier

    laps = session_laps(2023, "Singapore", "R", cache="datasets/fastf1-cache")
    result = train_strategy_classifier(laps, random_state=0)

    print(f"classes={result.classes}  n_train={result.n_train}  n_test={result.n_test}")
    print(f"baseline: acc={result.baseline.accuracy}  f1_macro={result.baseline.f1_macro}")
    print(f"model:    acc={result.model.accuracy}  f1_macro={result.model.f1_macro}")
    print(f"labels={result.model.labels}")
    print(f"confusion={result.model.confusion}")
    print(json.dumps(result.run_record()))

    ok = result.beats_baseline
    print("OK" if ok else "FAILURES PRESENT — model did not beat baseline")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
