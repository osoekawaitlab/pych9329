"""Fixtures and utilities for end-to-end tests."""

import os

import pytest
from pydantic import AnyHttpUrl

from e2e_utils import AnyHttpUrlAdapter, InputCaptureSessionManager


@pytest.fixture
def input_capture_api_url() -> AnyHttpUrl:
    """URL for input capture API."""
    return AnyHttpUrlAdapter.validate_python(os.environ["INPUT_CAPTURE_API_URL"])


@pytest.fixture
def input_capture_session_manager(
    input_capture_api_url: AnyHttpUrl,
) -> InputCaptureSessionManager:
    """Fixture for managing input capture sessions."""
    return InputCaptureSessionManager(input_capture_api_url=input_capture_api_url)
