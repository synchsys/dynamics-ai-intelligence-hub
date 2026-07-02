"""Tests for the common exception hierarchy."""

import pytest

from shared.exceptions import (
    ConfigError,
    ExternalServiceError,
    SharedError,
    ValidationError,
)


@pytest.mark.parametrize("exc_type", [ConfigError, ValidationError, ExternalServiceError])
def test_subclasses_of_shared_error(exc_type: type[SharedError]) -> None:
    assert issubclass(exc_type, SharedError)


def test_raises_and_carries_message() -> None:
    with pytest.raises(SharedError, match="boom"):
        raise ConfigError("boom")
