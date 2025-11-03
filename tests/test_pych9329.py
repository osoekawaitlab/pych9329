"""Tests for pych9329 package."""

import re

import pych9329


def test_version() -> None:
    """Test that the version is correctly set."""
    version_pattern = r"^\d+\.\d+\.\d+$"
    assert re.match(version_pattern, pych9329.__version__) is not None
