"""Smoke test proving the toolchain and package import work end to end.

Created in story #31 to verify a fresh clone lints, type-checks and tests
cleanly. Real ``shared`` tests arrive with story #22.
"""

from shared import __version__, hello


def test_version_is_a_nonempty_string() -> None:
    assert isinstance(__version__, str)
    assert __version__


def test_hello_mentions_shared() -> None:
    assert "shared" in hello().lower()
