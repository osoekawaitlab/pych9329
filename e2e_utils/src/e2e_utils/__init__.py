"""End-to-end test utilities for pych9329."""

from collections.abc import Generator
from types import TracebackType
from typing import TYPE_CHECKING
from urllib.parse import urljoin
from urllib.request import Request, urlopen

import pytest
from hid_recorder import EventItem
from pydantic import AnyHttpUrl, BaseModel, TypeAdapter
from ulid import ULID

if TYPE_CHECKING:
    from hid_interceptor import InputEvent


AnyHttpUrlAdapter = TypeAdapter(AnyHttpUrl)


class EventItemSequence(BaseModel):
    """Represents a sequence of input events."""

    events: list[EventItem]


class SessionCreateResponse(BaseModel):
    """Represents the response from creating a session."""

    id: ULID
    name: str


class SessionCreateRequest(BaseModel):
    """Represents the request to create a session."""

    name: str


def join_url_base_and_path(base: AnyHttpUrl, path: str) -> str:
    """Join a base URL and a path."""
    return str(AnyHttpUrlAdapter.validate_python(urljoin(str(base), path)))


@pytest.fixture
def input_capture_api_session_id(
    input_capture_api_url: AnyHttpUrl,
) -> Generator[ULID, None, None]:
    """Get the session ID for the input capture API."""
    with urlopen(  # noqa: S310
        join_url_base_and_path(input_capture_api_url, "/sessions")
    ) as response:
        session_id = response.read().decode("utf-8")
    try:
        yield ULID.from_str(session_id)
    finally:
        request = Request(  # noqa: S310
            join_url_base_and_path(
                input_capture_api_url,
                f"/sessions/{session_id}",
            ),
            method="PATCH",
            data=b'{"status":"ended"}',
        )
        with urlopen(request):  # noqa: S310
            pass


class InputCaptureSession:
    """Represents an input capture session."""

    def __init__(self, input_capture_api_url: AnyHttpUrl, name: str) -> None:
        """Initialize the input capture session."""
        self.input_capture_api_url = input_capture_api_url
        self.session_id: ULID | None = None
        self.events: list[InputEvent] = []
        self.name = name

    def __enter__(self) -> "InputCaptureSession":
        """Start session and store session ID."""
        request = Request(  # noqa: S310
            join_url_base_and_path(self.input_capture_api_url, "/sessions"),
            method="POST",
            headers={"Content-Type": "application/json"},
            data=SessionCreateRequest(name=self.name).model_dump_json().encode("utf-8"),
        )
        with urlopen(request) as response:  # noqa: S310
            self.session_id = SessionCreateResponse.model_validate_json(
                response.read().decode("utf-8")
            ).id
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Close session and fetch captured events."""
        if self.session_id is None:
            return
        end_request = Request(  # noqa: S310
            join_url_base_and_path(
                self.input_capture_api_url,
                f"/sessions/{self.session_id}",
            ),
            headers={"Content-Type": "application/json"},
            method="PATCH",
            data=b'{"status":"ended"}',
        )
        with urlopen(end_request):  # noqa: S310
            pass
        request = Request(  # noqa: S310
            join_url_base_and_path(
                self.input_capture_api_url,
                f"/sessions/{self.session_id}/events",
            )
        )
        with urlopen(request) as response:  # noqa: S310
            event_sequence = EventItemSequence.model_validate_json(
                response.read().decode("utf-8")
            )
        self.events = [item.event for item in event_sequence.events]


class InputCaptureSessionManager:
    """Manages input capture sessions for end-to-end tests."""

    def __init__(self, input_capture_api_url: AnyHttpUrl) -> None:
        """Initialize the session manager with the API URL."""
        self.input_capture_api_url = input_capture_api_url

    def start_session(self, name: str) -> InputCaptureSession:
        """Start a new input capture session."""
        return InputCaptureSession(self.input_capture_api_url, name=name)


__all__ = ["AnyHttpUrlAdapter", "InputCaptureSession", "InputCaptureSessionManager"]
