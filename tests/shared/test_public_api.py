"""Cross-module import smoke test (task #200).

Proves another module can import and use the ``shared`` public API.
"""

import shared
from shared import ConfigError, SharedError, configure_logging, get_logger, get_settings


def test_public_api_exports() -> None:
    for name in shared.__all__:
        assert hasattr(shared, name), f"missing export: {name}"


def test_api_is_usable() -> None:
    configure_logging(json_output=True)
    logger = get_logger(__name__)
    logger.info("shared package is usable")
    assert issubclass(ConfigError, SharedError)
    assert get_settings().environment in {"dev", "test", "prod"}


def test_version_present() -> None:
    assert isinstance(shared.__version__, str)
    assert shared.__version__
