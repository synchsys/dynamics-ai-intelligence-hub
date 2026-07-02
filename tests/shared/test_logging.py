"""Tests for structured logging and correlation-id propagation."""

import json
import logging
from typing import cast

import pytest

from shared.logging import (
    bind_correlation_id,
    configure_logging,
    get_correlation_id,
    get_logger,
)


def _last_record(captured: str) -> dict[str, object]:
    return cast(dict[str, object], json.loads(captured.strip().splitlines()[-1]))


def test_configure_emits_json(capsys: pytest.CaptureFixture[str]) -> None:
    configure_logging(level="INFO", json_output=True)
    get_logger("test.logger").info("hello world")
    record = _last_record(capsys.readouterr().err)
    assert record["message"] == "hello world"
    assert record["level"] == "INFO"
    assert record["logger"] == "test.logger"


def test_plain_output(capsys: pytest.CaptureFixture[str]) -> None:
    configure_logging(json_output=False)
    get_logger("t").info("plain message")
    err = capsys.readouterr().err
    assert "plain message" in err
    with pytest.raises(json.JSONDecodeError):
        json.loads(err.strip().splitlines()[-1])


def test_correlation_id_attached(capsys: pytest.CaptureFixture[str]) -> None:
    configure_logging(json_output=True)
    assert bind_correlation_id("abc123") == "abc123"
    assert get_correlation_id() == "abc123"
    get_logger("t").warning("with id")
    record = _last_record(capsys.readouterr().err)
    assert record["correlation_id"] == "abc123"


def test_bind_generates_id_when_none() -> None:
    generated = bind_correlation_id()
    assert isinstance(generated, str)
    assert generated


def test_exc_info_included(capsys: pytest.CaptureFixture[str]) -> None:
    configure_logging(json_output=True)
    logger = get_logger("t")
    try:
        raise ValueError("kaboom")
    except ValueError:
        logger.exception("failed")
    record = _last_record(capsys.readouterr().err)
    assert "kaboom" in str(record["exc_info"])


def test_get_logger_returns_logger() -> None:
    assert isinstance(get_logger("x"), logging.Logger)
