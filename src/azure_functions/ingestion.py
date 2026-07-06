"""Timer-triggered OpenF1 → Dataverse ingestion (#20).

Wires the existing ingestion pipeline (``OpenF1Persister.ingest_session``) into
the Functions timer trigger. Configuration and secrets come from app settings
(the environment) — never source. Re-runs are idempotent because persistence is
upsert-by-alternate-key.

Orchestration (``run_ingestion``) is pure and unit-tested with a fake persister;
``build_persister`` constructs the real clients from env, and ``ingest_from_env``
is what the timer binding calls.
"""

import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

from dataverse import DataverseClient, DataverseConfig
from openf1 import OpenF1Client, OpenF1Persister
from shared.exceptions import ConfigError
from shared.logging import get_logger

_logger = get_logger("azure_functions.ingestion")


class SupportsIngest(Protocol):
    def ingest_session(self, session_key: int) -> Any: ...


@dataclass(frozen=True)
class IngestionConfig:
    """Which session the scheduled run ingests (from app settings)."""

    session_key: int

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "IngestionConfig":
        source = os.environ if env is None else env
        raw = source.get("INGEST_SESSION_KEY")
        if not raw:
            raise ConfigError("Missing app setting INGEST_SESSION_KEY")
        return cls(session_key=int(raw))


def build_persister() -> OpenF1Persister:
    """Construct the OpenF1 → Dataverse persister from environment settings."""
    dataverse = DataverseClient(DataverseConfig.from_env())
    return OpenF1Persister(OpenF1Client(), dataverse)


def run_ingestion(persister: SupportsIngest, session_key: int, now: datetime) -> dict[str, Any]:
    """Run the pipeline for one session and return a summary (idempotent)."""
    summary = persister.ingest_session(session_key)
    result = {
        "task": "openf1-ingestion",
        "at": now.isoformat(),
        "session_key": session_key,
        "upserted": summary.total_upserted,
        "settleable": summary.settleable,
    }
    _logger.info("scheduled ingestion complete: %s", result)
    return result


def ingest_from_env(
    now: datetime,
    *,
    env: Mapping[str, str] | None = None,
    persister_factory: Callable[[], SupportsIngest] = build_persister,
) -> dict[str, Any]:
    """Read config from app settings, build the pipeline, and run it (timer entrypoint)."""
    config = IngestionConfig.from_env(env)
    return run_ingestion(persister_factory(), config.session_key, now)
