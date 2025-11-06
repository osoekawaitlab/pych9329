"""Test heterogeneous input events: keyboard, mouse and media keys."""

import ch9329py
from e2e_utils import InputCaptureSessionManager

KEY_REPEAT_VALUE = 2


def test_keyboard_and_media_key_events(
    input_capture_session_manager: InputCaptureSessionManager,
) -> None:
    """Test that keyboard and media key events are captured correctly."""
    capture_session = input_capture_session_manager.start_session(
        name="keyboard_and_media_key_events"
    )
    with capture_session, ch9329py.SerialAdapter(port="/dev/ttyUSB0") as serial_adapter:
        driver = ch9329py.CH9329Driver(serial_adapter)
        driver.send_keyboard_input(
            ch9329py.KeyboardInput(
                modifiers={ch9329py.ModifierKey.KEY_LEFTCTRL},
                keys=[ch9329py.KeyCode.KEY_A],
            )
        )

        # Send media key input: Volume Up
        driver.send_media_key_input(
            ch9329py.MediaKeyInput(keys=[ch9329py.MediaKey.KEY_VOLUMEUP])
        )
        driver.send_keyboard_input(
            ch9329py.KeyboardInput(
                modifiers={ch9329py.ModifierKey.KEY_LEFTSHIFT},
                keys=[ch9329py.KeyCode.KEY_Z],
            )
        )  # Keep keys pressed
        driver.send_media_key_input(
            ch9329py.MediaKeyInput(keys=[ch9329py.MediaKey.KEY_VOLUMEDOWN])
        )
        driver.send_media_key_input(ch9329py.MediaKeyInput(keys=[]))  # Release all
        driver.send_keyboard_input(ch9329py.KeyboardInput())  # Release all keys

    expected_codes_and_values = [
        ("KEY_LEFTCTRL", 1),
        ("KEY_A", 1),
        ("KEY_VOLUMEUP", 1),
        ("KEY_LEFTCTRL", 0),
        ("KEY_LEFTSHIFT", 1),
        ("KEY_A", 0),
        ("KEY_Z", 1),
        ("KEY_VOLUMEUP", 0),
        ("KEY_VOLUMEDOWN", 1),
        ("KEY_VOLUMEDOWN", 0),
        ("KEY_LEFTSHIFT", 0),
        ("KEY_Z", 0),
    ]
    actual_codes_and_values = [
        (event.code_name, event.value)
        for event in capture_session.events
        if event.value != KEY_REPEAT_VALUE
    ]
    assert actual_codes_and_values == expected_codes_and_values


def test_shift_left_drag_mouse(
    input_capture_session_manager: InputCaptureSessionManager,
) -> None:
    """Test that holding Shift while dragging with the mouse is captured."""
    capture_session = input_capture_session_manager.start_session(
        name="shift_left_drag_mouse"
    )
    with capture_session, ch9329py.SerialAdapter(port="/dev/ttyUSB0") as serial_adapter:
        driver = ch9329py.CH9329Driver(serial_adapter)
        driver.send_keyboard_input(
            ch9329py.KeyboardInput(
                modifiers={ch9329py.ModifierKey.KEY_LEFTSHIFT},
                keys=[],
            )
        )
        driver.send_mouse_input(
            ch9329py.MouseInput(
                buttons={ch9329py.MouseButton.BTN_LEFT},
                x=20,
                y=15,
            )
        )
        driver.send_mouse_input(
            ch9329py.MouseInput(
                buttons={ch9329py.MouseButton.BTN_LEFT},
                x=20,
                y=15,
            )
        )
        # Release left mouse button
        driver.send_mouse_input(
            ch9329py.MouseInput(
                buttons=set(),
                x=0,
                y=0,
            )
        )
        driver.send_keyboard_input(ch9329py.KeyboardInput())

    expected_codes_and_values = [
        ("KEY_LEFTSHIFT", 1),
        (f"('{ch9329py.MouseButton.BTN_LEFT.name}', 'BTN_MOUSE')", 1),
        ("REL_X", 20),
        ("REL_Y", 15),
        ("REL_X", 20),
        ("REL_Y", 15),
        (f"('{ch9329py.MouseButton.BTN_LEFT.name}', 'BTN_MOUSE')", 0),
        ("KEY_LEFTSHIFT", 0),
    ]
    actual_codes_and_values = [
        (event.code_name, event.value)
        for event in capture_session.events
        if event.value != KEY_REPEAT_VALUE
    ]
    assert actual_codes_and_values == expected_codes_and_values
