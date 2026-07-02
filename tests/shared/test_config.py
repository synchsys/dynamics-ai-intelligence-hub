"""Tests for environment-driven settings and precedence."""

import pytest

from shared.config import get_settings
from shared.exceptions import ConfigError

_ENV_VARS = ("HUB_ENVIRONMENT", "HUB_LOG_LEVEL", "HUB_LOG_JSON")


def _reset(monkeypatch: pytest.MonkeyPatch, **env: str) -> None:
    for key in _ENV_VARS:
        monkeypatch.delenv(key, raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    get_settings.cache_clear()


def test_typed_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    _reset(monkeypatch)
    settings = get_settings()
    assert settings.environment == "dev"
    assert settings.log_level == "INFO"
    assert settings.log_json is True


def test_env_overrides_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    _reset(monkeypatch, HUB_ENVIRONMENT="prod", HUB_LOG_LEVEL="DEBUG", HUB_LOG_JSON="false")
    settings = get_settings()
    assert settings.environment == "prod"
    assert settings.log_level == "DEBUG"
    assert settings.log_json is False


def test_settings_are_cached(monkeypatch: pytest.MonkeyPatch) -> None:
    _reset(monkeypatch)
    assert get_settings() is get_settings()


def test_invalid_value_raises_config_error(monkeypatch: pytest.MonkeyPatch) -> None:
    _reset(monkeypatch, HUB_ENVIRONMENT="nonsense")
    with pytest.raises(ConfigError):
        get_settings()
