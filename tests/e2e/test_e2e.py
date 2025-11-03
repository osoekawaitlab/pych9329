"""E2E tests for the pych9329 with Input Capture API."""

from itertools import product

import pych9329
from e2e_utils import InputCaptureSessionManager


def test_no_input_events(
    input_capture_session_manager: InputCaptureSessionManager,
) -> None:
    """Test that no input events are captured initially."""
    capture_session = input_capture_session_manager.start_session(
        name="no_input_events"
    )
    with capture_session, pych9329.SerialAdapter(port="/dev/ttyUSB0") as serial_adapter:
        _ = pych9329.CH9329Driver(serial_adapter)
    assert len(capture_session.events) == 0


def test_keyboard_input_events(
    input_capture_session_manager: InputCaptureSessionManager,
) -> None:
    """Test that keyboard input events are captured."""
    capture_session = input_capture_session_manager.start_session(
        name="keyboard_input_events"
    )
    ctrl_key = (False, True)
    shift_key = (False, True)
    alt_key = (False, True)
    windows_key = (False, True)
    with capture_session, pych9329.SerialAdapter(port="/dev/ttyUSB0") as serial_adapter:
        driver = pych9329.CH9329Driver(serial_adapter)
        for key_code, ctrl, shift, alt, win in product(
            (pych9329.KeyCode.W,), ctrl_key, shift_key, alt_key, windows_key
        ):
            driver.key_down(
                key_code,
                ctrl=ctrl,
                shift=shift,
                alt=alt,
                windows=win,
            )
            driver.key_up()
            break
    idx = 0
    observed_events = capture_session.events
    print()
    for e in observed_events:
        print(e)
    print()
    for key_code, ctrl, shift, alt, win in product(
        (pych9329.KeyCode.W,), ctrl_key, shift_key, alt_key, windows_key
    ):
        expected_events = (
            [
                (mod.value, 1)
                for mod, pressed in zip(
                    pych9329.ModifierKey, [ctrl, shift, alt, win], strict=True
                )
                if pressed
            ]
            + [(key_code.value, 1)]
            + [
                (mod.value, 0)
                for mod, pressed in zip(
                    pych9329.ModifierKey, [ctrl, shift, alt, win], strict=True
                )
                if pressed
            ]
            + [(key_code.value, 0)]
        )
        actual = [
            (e.code, e.value) for e in observed_events[idx : idx + len(expected_events)]
        ]
        assert actual == expected_events, (
            f"Mismatch at index {idx} for key_code={key_code}, ctrl={ctrl}, shift={shift}, alt={alt}, win={win}"
        )
        idx += len(expected_events)
