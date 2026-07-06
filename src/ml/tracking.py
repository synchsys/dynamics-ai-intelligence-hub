"""Experiment tracking and reproducibility (#56).

A dependency-free tracker: each run is appended as one JSON line (params +
metrics + seed) to a runs file, so runs are logged, comparable, and reproducible
without MLflow or a server. Chosen over MLflow to stay light and match the
repo's hand-rolled, fully-tested style; a local MLflow could slot in later behind
the same ``log_run`` call.

Reproducibility rests on a single documented seed (:data:`DEFAULT_SEED`) threaded
into every model's ``random_state`` — re-running with it reproduces the metrics.
Model cards live in ``docs/architecture/model-cards/``.
"""

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from shared.logging import get_logger

_logger = get_logger("ml.tracking")

# The one seed threaded into every model's random_state (see docs).
DEFAULT_SEED = 0


@dataclass(frozen=True)
class RunRecord:
    """One logged experiment run."""

    name: str
    params: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, float] = field(default_factory=dict)
    seed: int = DEFAULT_SEED

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RunRecord":
        return cls(
            name=data["name"],
            params=data.get("params", {}),
            metrics=data.get("metrics", {}),
            seed=data.get("seed", DEFAULT_SEED),
        )


class ExperimentTracker:
    """Append-only JSONL experiment log."""

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)

    def log_run(
        self,
        name: str,
        *,
        params: dict[str, Any] | None = None,
        metrics: dict[str, float] | None = None,
        seed: int = DEFAULT_SEED,
    ) -> RunRecord:
        """Append a run and return its record."""
        record = RunRecord(name=name, params=params or {}, metrics=metrics or {}, seed=seed)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(record.to_json() + "\n")
        _logger.info("logged run %r: metrics=%s seed=%d", name, record.metrics, seed)
        return record

    def runs(self) -> list[RunRecord]:
        """All logged runs, in order."""
        if not self._path.exists():
            return []
        lines = self._path.read_text(encoding="utf-8").splitlines()
        return [RunRecord.from_dict(json.loads(line)) for line in lines if line.strip()]

    def best(self, metric: str, *, minimize: bool = True) -> RunRecord | None:
        """The run with the best value of ``metric`` (min by default), or None."""
        candidates = [r for r in self.runs() if metric in r.metrics]
        if not candidates:
            return None
        return (min if minimize else max)(candidates, key=lambda r: r.metrics[metric])
