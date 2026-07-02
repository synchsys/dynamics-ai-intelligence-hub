"""Environment-driven application settings.

Values resolve in precedence order: process environment > ``.env`` file >
typed defaults. All variables use the ``HUB_`` prefix. Invalid or malformed
values raise :class:`~shared.exceptions.ConfigError` rather than leaking a
Pydantic error, so callers only ever catch the project's own hierarchy.
"""

from functools import lru_cache
from typing import Literal

from pydantic import ValidationError as PydanticValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from shared.exceptions import ConfigError


class Settings(BaseSettings):
    """Typed application settings loaded from the environment.

    Extend this as later epics need configuration (endpoints, credentials via
    Key Vault references, etc.).
    """

    model_config = SettingsConfigDict(
        env_prefix="HUB_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: Literal["dev", "test", "prod"] = "dev"
    log_level: str = "INFO"
    log_json: bool = True


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings.

    Call ``get_settings.cache_clear()`` to force a reload (used in tests).
    """
    try:
        return Settings()
    except PydanticValidationError as exc:
        raise ConfigError(f"Invalid configuration: {exc}") from exc
