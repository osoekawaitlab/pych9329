"""E2E tests for the pych9329 with Input Capture API."""

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


def test_keyboard_input_events_many_keys(
    input_capture_session_manager: InputCaptureSessionManager,
) -> None:
    """Test that keyboard input events are captured."""
    capture_session = input_capture_session_manager.start_session(
        name="keyboard_input_events_many_keys"
    )
    state_1 = pych9329.KeyboardState(
        keys=[
            pych9329.KeyCode.KEY_A,
            pych9329.KeyCode.KEY_B,
            pych9329.KeyCode.KEY_C,
        ]
    )
    state_2 = pych9329.KeyboardState(
        keys=[
            pych9329.KeyCode.KEY_A,
            pych9329.KeyCode.KEY_B,
            pych9329.KeyCode.KEY_C,
            pych9329.KeyCode.KEY_D,
            pych9329.KeyCode.KEY_E,
            pych9329.KeyCode.KEY_F,
        ]
    )
    state_3 = pych9329.KeyboardState(
        keys=[
            pych9329.KeyCode.KEY_B,
            pych9329.KeyCode.KEY_D,
            pych9329.KeyCode.KEY_F,
        ]
    )
    with capture_session, pych9329.SerialAdapter(port="/dev/ttyUSB0") as serial_adapter:
        driver = pych9329.CH9329Driver(serial_adapter)
        for state in (state_1, state_2, state_3):
            driver.send_keyboard_state(state)
        driver.send_keyboard_state(pych9329.KeyboardState())
    expected_codes_and_values = [
        (pych9329.KeyCode.KEY_A.name, 1),
        (pych9329.KeyCode.KEY_B.name, 1),
        (pych9329.KeyCode.KEY_C.name, 1),
        (pych9329.KeyCode.KEY_D.name, 1),
        (pych9329.KeyCode.KEY_E.name, 1),
        (pych9329.KeyCode.KEY_F.name, 1),
        (pych9329.KeyCode.KEY_A.name, 0),
        (pych9329.KeyCode.KEY_C.name, 0),
        (pych9329.KeyCode.KEY_E.name, 0),
        (pych9329.KeyCode.KEY_B.name, 0),
        (pych9329.KeyCode.KEY_D.name, 0),
        (pych9329.KeyCode.KEY_F.name, 0),
    ]
    actual_codes_and_values = [
        (event.code_name, event.value) for event in capture_session.events
    ]
    assert actual_codes_and_values == expected_codes_and_values


def test_keyboard_input_events_modifiers(
    input_capture_session_manager: InputCaptureSessionManager,
) -> None:
    """Test that keyboard input events with modifiers are captured."""
    capture_session = input_capture_session_manager.start_session(
        name="keyboard_input_events_modifiers"
    )
    state_1 = pych9329.KeyboardState(
        modifiers={pych9329.ModifierKey.KEY_LEFTCTRL},
        keys=[pych9329.KeyCode.KEY_A],
    )
    state_2 = pych9329.KeyboardState(
        modifiers={
            pych9329.ModifierKey.KEY_LEFTCTRL,
            pych9329.ModifierKey.KEY_LEFTSHIFT,
        },
        keys=[pych9329.KeyCode.KEY_A],
    )
    with capture_session, pych9329.SerialAdapter(port="/dev/ttyUSB0") as serial_adapter:
        driver = pych9329.CH9329Driver(serial_adapter)
        for state in (state_1, state_2):
            driver.send_keyboard_state(state)
        driver.send_keyboard_state(pych9329.KeyboardState())
    expected_codes_and_values = [
        (pych9329.ModifierKey.KEY_LEFTCTRL.name, 1),
        (pych9329.KeyCode.KEY_A.name, 1),
        (pych9329.ModifierKey.KEY_LEFTSHIFT.name, 1),
        (pych9329.ModifierKey.KEY_LEFTCTRL.name, 0),
        (pych9329.ModifierKey.KEY_LEFTSHIFT.name, 0),
        (pych9329.KeyCode.KEY_A.name, 0),
    ]
    actual_codes_and_values = [
        (event.code_name, event.value) for event in capture_session.events
    ]
    assert actual_codes_and_values == expected_codes_and_values


def test_keyboard_input_modifier_key_each(
    input_capture_session_manager: InputCaptureSessionManager,
) -> None:
    """Test that keyboard input events with each modifier key are captured."""
    capture_session = input_capture_session_manager.start_session(
        name="keyboard_input_events_modifier_key_each"
    )
    with capture_session, pych9329.SerialAdapter(port="/dev/ttyUSB0") as serial_adapter:
        driver = pych9329.CH9329Driver(serial_adapter)
        for mod_key in pych9329.ModifierKey:
            state = pych9329.KeyboardState(
                modifiers={mod_key},
                keys=[],
            )
            driver.send_keyboard_state(state)
            driver.send_keyboard_state(pych9329.KeyboardState())
    expected_codes_and_values: list[tuple[str, int]] = []
    for mod_key in pych9329.ModifierKey:
        expected_codes_and_values.append((mod_key.name, 1))
        expected_codes_and_values.append((mod_key.name, 0))
    actual_codes_and_values = [
        (event.code_name, event.value) for event in capture_session.events
    ]
    assert actual_codes_and_values == expected_codes_and_values


def test_keyboard_input_all_keys(
    input_capture_session_manager: InputCaptureSessionManager,
) -> None:
    """Test that keyboard input events with all keys are captured."""
    capture_session = input_capture_session_manager.start_session(
        name="keyboard_input_events_all_keys"
    )
    with capture_session, pych9329.SerialAdapter(port="/dev/ttyUSB0") as serial_adapter:
        driver = pych9329.CH9329Driver(serial_adapter)
        for key in pych9329.KeyCode:
            state = pych9329.KeyboardState(
                keys=[key],
            )
            driver.send_keyboard_state(state)
            driver.send_keyboard_state(pych9329.KeyboardState())
    expected_codes_and_values: list[tuple[str, int]] = []
    for key in pych9329.KeyCode:
        expected_codes_and_values.append((key.name, 1))
        expected_codes_and_values.append((key.name, 0))
    actual_codes_and_values = [
        (event.code_name, event.value) for event in capture_session.events
    ]
    assert actual_codes_and_values == expected_codes_and_values
