"""Tests for FastF1 cache config + session loading (fastf1 monkeypatched)."""

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import fastf1
import pytest

import fastf1_analytics.cache as cache_mod
from fastf1_analytics import configure_cache, load_session


def test_configure_cache_creates_dir_and_enables(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    enabled: list[str] = []
    monkeypatch.setattr(fastf1.Cache, "enable_cache", staticmethod(enabled.append))
    target = tmp_path / "ff1"

    result = configure_cache(target)
    assert result == target
    assert target.is_dir()
    assert enabled == [str(target)]


def test_configure_cache_defaults_to_module_dir(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(fastf1.Cache, "enable_cache", staticmethod(lambda _p: None))
    monkeypatch.setattr(cache_mod, "DEFAULT_CACHE_DIR", tmp_path / "default-cache")
    result = configure_cache()
    assert result == tmp_path / "default-cache" and result.is_dir()


def test_load_session_configures_cache_and_loads(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(fastf1.Cache, "enable_cache", staticmethod(lambda _p: None))
    captured: dict[str, Any] = {}

    def fake_get_session(year: int, event: Any, session: str) -> Any:
        captured["get"] = (year, event, session)

        def load(**kwargs: Any) -> None:
            captured["load"] = kwargs

        return SimpleNamespace(load=load)

    monkeypatch.setattr(fastf1, "get_session", fake_get_session)

    session = load_session(2023, "Singapore", "R", cache=tmp_path, telemetry=True)
    assert captured["get"] == (2023, "Singapore", "R")
    assert captured["load"] == {"telemetry": True, "weather": False, "messages": False}
    assert session is not None


def test_load_session_defaults_are_lightweight(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(fastf1.Cache, "enable_cache", staticmethod(lambda _p: None))
    captured: dict[str, Any] = {}
    monkeypatch.setattr(
        fastf1,
        "get_session",
        lambda *a: SimpleNamespace(load=lambda **kw: captured.update(kw)),
    )
    load_session(2024, 1, cache=tmp_path)
    # Heavy extras off by default — only lap data.
    assert captured == {"telemetry": False, "weather": False, "messages": False}
