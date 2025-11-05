"""E2E tests for mouse input with Input Capture API."""

import pych9329
from e2e_utils import InputCaptureSessionManager


def test_mouse_no_input_events(
    input_capture_session_manager: InputCaptureSessionManager,
) -> None:
    """Test that no mouse input events are captured initially."""
    capture_session = input_capture_session_manager.start_session(
        name="mouse_no_input_events"
    )
    with capture_session, pych9329.SerialAdapter(port="/dev/ttyUSB0") as serial_adapter:
        _ = pych9329.CH9329Driver(serial_adapter)
    assert len(capture_session.events) == 0


def test_mouse_button_events(
    input_capture_session_manager: InputCaptureSessionManager,
) -> None:
    """Test that mouse button events are captured."""
    capture_session = input_capture_session_manager.start_session(
        name="mouse_button_events"
    )
    with capture_session, pych9329.SerialAdapter(port="/dev/ttyUSB0") as serial_adapter:
        driver = pych9329.CH9329Driver(serial_adapter)
        # Press left button
        driver.send_mouse_input(
            pych9329.MouseInput(buttons={pych9329.MouseButton.BTN_LEFT})
        )
        # Release all buttons
        driver.send_mouse_input(pych9329.MouseInput())
        # Press right button
        driver.send_mouse_input(
            pych9329.MouseInput(buttons={pych9329.MouseButton.BTN_RIGHT})
        )
        # Release all buttons
        driver.send_mouse_input(pych9329.MouseInput())

    expected_codes_and_values = [
        (f"('{pych9329.MouseButton.BTN_LEFT.name}', 'BTN_MOUSE')", 1),
        (f"('{pych9329.MouseButton.BTN_LEFT.name}', 'BTN_MOUSE')", 0),
        (pych9329.MouseButton.BTN_RIGHT.name, 1),
        (pych9329.MouseButton.BTN_RIGHT.name, 0),
    ]
    actual_codes_and_values = [
        (event.code_name, event.value) for event in capture_session.events
    ]
    assert actual_codes_and_values == expected_codes_and_values


def test_mouse_multiple_buttons(
    input_capture_session_manager: InputCaptureSessionManager,
) -> None:
    """Test that multiple mouse buttons can be pressed simultaneously."""
    capture_session = input_capture_session_manager.start_session(
        name="mouse_multiple_buttons"
    )
    with capture_session, pych9329.SerialAdapter(port="/dev/ttyUSB0") as serial_adapter:
        driver = pych9329.CH9329Driver(serial_adapter)
        # Press left and right buttons simultaneously
        driver.send_mouse_input(
            pych9329.MouseInput(
                buttons={
                    pych9329.MouseButton.BTN_LEFT,
                    pych9329.MouseButton.BTN_RIGHT,
                }
            )
        )
        # Release all buttons
        driver.send_mouse_input(pych9329.MouseInput())

    expected_codes_and_values = [
        (f"('{pych9329.MouseButton.BTN_LEFT.name}', 'BTN_MOUSE')", 1),
        (pych9329.MouseButton.BTN_RIGHT.name, 1),
        (f"('{pych9329.MouseButton.BTN_LEFT.name}', 'BTN_MOUSE')", 0),
        (pych9329.MouseButton.BTN_RIGHT.name, 0),
    ]
    actual_codes_and_values = [
        (event.code_name, event.value) for event in capture_session.events
    ]
    assert actual_codes_and_values == expected_codes_and_values


def test_mouse_movement_events(
    input_capture_session_manager: InputCaptureSessionManager,
) -> None:
    """Test that mouse movement events are captured."""
    capture_session = input_capture_session_manager.start_session(
        name="mouse_movement_events"
    )
    with capture_session, pych9329.SerialAdapter(port="/dev/ttyUSB0") as serial_adapter:
        driver = pych9329.CH9329Driver(serial_adapter)
        # Move right and down
        driver.send_mouse_input(pych9329.MouseInput(x=10, y=10))
        # Move left and up
        driver.send_mouse_input(pych9329.MouseInput(x=-10, y=-10))

    expected_codes_and_values = [
        ("REL_X", 10),
        ("REL_Y", 10),
        ("REL_X", -10),
        ("REL_Y", -10),
    ]
    actual_codes_and_values = [
        (event.code_name, event.value) for event in capture_session.events
    ]
    assert actual_codes_and_values == expected_codes_and_values


def test_mouse_scroll_events(
    input_capture_session_manager: InputCaptureSessionManager,
) -> None:
    """Test that mouse scroll events are captured."""
    capture_session = input_capture_session_manager.start_session(
        name="mouse_scroll_events"
    )
    with capture_session, pych9329.SerialAdapter(port="/dev/ttyUSB0") as serial_adapter:
        driver = pych9329.CH9329Driver(serial_adapter)
        # Scroll up
        driver.send_mouse_input(pych9329.MouseInput(scroll=3))
        # Scroll down
        driver.send_mouse_input(pych9329.MouseInput(scroll=-3))

    expected_codes_and_values = [
        ("REL_WHEEL", 3),
        ("REL_WHEEL_HI_RES", 360),
        ("REL_WHEEL", -3),
        ("REL_WHEEL_HI_RES", -360),
    ]
    actual_codes_and_values = [
        (event.code_name, event.value) for event in capture_session.events
    ]
    assert actual_codes_and_values == expected_codes_and_values


def test_mouse_button_with_movement(
    input_capture_session_manager: InputCaptureSessionManager,
) -> None:
    """Test that mouse button and movement can be sent together."""
    capture_session = input_capture_session_manager.start_session(
        name="mouse_button_with_movement"
    )
    with capture_session, pych9329.SerialAdapter(port="/dev/ttyUSB0") as serial_adapter:
        driver = pych9329.CH9329Driver(serial_adapter)
        # Drag operation: press left button and move
        driver.send_mouse_input(
            pych9329.MouseInput(buttons={pych9329.MouseButton.BTN_LEFT}, x=5, y=5)
        )
        # Release button
        driver.send_mouse_input(pych9329.MouseInput())

    expected_codes_and_values = [
        (f"('{pych9329.MouseButton.BTN_LEFT.name}', 'BTN_MOUSE')", 1),
        ("REL_X", 5),
        ("REL_Y", 5),
        (f"('{pych9329.MouseButton.BTN_LEFT.name}', 'BTN_MOUSE')", 0),
    ]
    actual_codes_and_values = [
        (event.code_name, event.value) for event in capture_session.events
    ]

    assert actual_codes_and_values == expected_codes_and_values


def test_mouse_all_buttons(
    input_capture_session_manager: InputCaptureSessionManager,
) -> None:
    """Test that all mouse buttons are captured correctly."""
    capture_session = input_capture_session_manager.start_session(
        name="mouse_all_buttons"
    )
    with capture_session, pych9329.SerialAdapter(port="/dev/ttyUSB0") as serial_adapter:
        driver = pych9329.CH9329Driver(serial_adapter)
        for button in pych9329.MouseButton:
            driver.send_mouse_input(pych9329.MouseInput(buttons={button}))
            driver.send_mouse_input(pych9329.MouseInput())

    expected_codes_and_values: list[tuple[str, int]] = [
        (f"('{pych9329.MouseButton.BTN_LEFT.name}', 'BTN_MOUSE')", 1),
        (f"('{pych9329.MouseButton.BTN_LEFT.name}', 'BTN_MOUSE')", 0),
        (pych9329.MouseButton.BTN_RIGHT.name, 1),
        (pych9329.MouseButton.BTN_RIGHT.name, 0),
        (pych9329.MouseButton.BTN_MIDDLE.name, 1),
        (pych9329.MouseButton.BTN_MIDDLE.name, 0),
    ]

    actual_codes_and_values = [
        (event.code_name, event.value) for event in capture_session.events
    ]
    assert actual_codes_and_values == expected_codes_and_values
