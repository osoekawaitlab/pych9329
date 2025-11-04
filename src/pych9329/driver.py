"""Main driver class for CH9329 USB HID device.

This module provides the high-level API for interacting with the CH9329 device.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from pych9329.evdev_mapping import (
    evdev_to_usb_hid_keyboard,
    evdev_to_usb_hid_modifier,
    evdev_to_usb_hid_mouse,
)
from pych9329.models import (
    MAX_ROLLOVER_KEYS,
    KeyboardInput,
    KeyCode,
    MediaKey,
    MouseButton,
    MouseInput,
    get_key_mapping,
)
from pych9329.protocol import CH9329Protocol
from pych9329.recorder import (
    KeyDownOperation,
    KeyUpOperation,
    MediaKeyDownOperation,
    MediaKeyUpOperation,
    MouseButtonDownOperation,
    MouseButtonUpOperation,
    MouseMoveAbsoluteOperation,
    MouseMoveRelativeOperation,
    MouseScrollOperation,
)

if TYPE_CHECKING:
    from pych9329.adapter import CommunicationAdapter
    from pych9329.recorder import OperationRecorder


class CH9329Driver:
    """High-level driver for CH9329 USB HID device.

    This class provides a user-friendly API for keyboard and mouse simulation
    through the CH9329 chip. It integrates the protocol layer and communication
    adapter to provide methods like write_string(), mouse_move(), mouse_click(),
    and media key control.

    Args:
        adapter: Communication adapter for sending/receiving data.
        screen_width: Screen width in pixels (default: 1920).
        screen_height: Screen height in pixels (default: 1080).

    Examples:
        >>> from pych9329.adapter import SerialAdapter
        >>> from pych9329.driver import CH9329Driver
        >>> adapter = SerialAdapter("/dev/ttyUSB0", 9600)
        >>> driver = CH9329Driver(adapter, screen_width=1920, screen_height=1080)
        >>> driver.write_string("Hello, World!")
        >>> driver.mouse_move_absolute(960, 540)
        >>> driver.close()

        Or using context manager:
        >>> with SerialAdapter("/dev/ttyUSB0", 9600) as adapter:
        ...     with CH9329Driver(adapter) as driver:
        ...         driver.write_string("Hello!")
    """

    def __init__(
        self,
        adapter: CommunicationAdapter,
        screen_width: int = 1920,
        screen_height: int = 1080,
        recorder: OperationRecorder | None = None,
    ) -> None:
        """Initialize the CH9329 driver.

        Args:
            adapter: Communication adapter for sending/receiving data.
            screen_width: Screen width in pixels.
            screen_height: Screen height in pixels.
            recorder: Optional operation recorder for recording actions.
        """
        self._adapter = adapter
        self._screen_width = screen_width
        self._screen_height = screen_height
        self._recorder = recorder

    def key_down(
        self,
        key: KeyCode,
        *,
        shift: bool = False,
        ctrl: bool = False,
        alt: bool = False,
        windows: bool = False,
    ) -> None:
        """Press a keyboard key down without releasing it.

        Use key_up() to release the key. This allows holding keys down
        for specific durations or pressing multiple keys simultaneously.

        Args:
            key: The key to press down (evdev KeyCode).
            shift: Whether to hold shift modifier.
            ctrl: Whether to hold ctrl modifier.
            alt: Whether to hold alt modifier.
            windows: Whether to hold windows modifier.

        Examples:
            >>> driver.key_down(KeyCode.KEY_A)  # Hold 'a' down
            >>> driver.key_up()  # Release it
            >>> # Hold Ctrl+Shift+A
            >>> driver.key_down(KeyCode.KEY_A, ctrl=True, shift=True)
            >>> driver.key_up()
        """
        # Convert evdev key code to USB HID scan code
        usb_hid_keycode = evdev_to_usb_hid_keyboard(key.value)

        # Build modifier byte (USB HID format)
        modifier = 0x00
        if ctrl:
            modifier |= 0x01
        if shift:
            modifier |= 0x02
        if alt:
            modifier |= 0x04
        if windows:
            modifier |= 0x08

        # Send key press packet
        press_packet = CH9329Protocol.build_keyboard_press_packet(
            modifier, usb_hid_keycode
        )
        self._adapter.send(press_packet)

        # Record operation if recorder is attached
        if self._recorder is not None:
            self._recorder.record(
                KeyDownOperation(key, shift=shift, ctrl=ctrl, alt=alt, windows=windows)
            )

    def key_up(self) -> None:
        """Release all currently pressed keyboard keys.

        Examples:
            >>> driver.key_down(KeyCode.A)
            >>> # ... do other things ...
            >>> driver.key_up()  # Release the key
        """
        # Send key release packet
        release_packet = CH9329Protocol.build_keyboard_release_packet()
        self._adapter.send(release_packet)

        # Record operation if recorder is attached
        if self._recorder is not None:
            self._recorder.record(KeyUpOperation())

    def send_keyboard_state(self, state: KeyboardInput) -> None:
        """Send a complete keyboard state with multiple keys and modifiers.

        This is a low-level API that directly exposes CH9329's capability
        to send up to 6 simultaneous key presses with 8 modifier keys.

        Args:
            state: The keyboard state containing modifiers and keys.

        Examples:
            >>> # Press Ctrl+Shift+A
            >>> state = KeyboardInput(
            ...     modifiers={ModifierKey.KEY_LEFTCTRL, ModifierKey.KEY_LEFTSHIFT},
            ...     keys=[KeyCode.KEY_A]
            ... )
            >>> driver.send_keyboard_state(state)
            >>>
            >>> # Press A+B+C simultaneously with Shift
            >>> state = KeyboardInput(
            ...     modifiers={ModifierKey.KEY_LEFTSHIFT},
            ...     keys=[KeyCode.KEY_A, KeyCode.KEY_B, KeyCode.KEY_C]
            ... )
            >>> driver.send_keyboard_state(state)
            >>>
            >>> # Maximum 6 keys at once
            >>> state = KeyboardInput(
            ...     keys=[KeyCode.KEY_A, KeyCode.KEY_B, KeyCode.KEY_C,
            ...           KeyCode.KEY_D, KeyCode.KEY_E, KeyCode.KEY_F]
            ... )
            >>> driver.send_keyboard_state(state)
            >>>
            >>> # Release all keys
            >>> driver.send_keyboard_state(KeyboardInput())
        """
        # Build modifier byte from evdev modifier keys
        modifier_byte = 0x00
        for modifier_key in state.modifiers:
            modifier_byte |= evdev_to_usb_hid_modifier(modifier_key.value)

        # Convert evdev key codes to USB HID scan codes
        usb_hid_keys = [evdev_to_usb_hid_keyboard(key.value) for key in state.keys]

        # Pad to 6 keys with zeros
        while len(usb_hid_keys) < MAX_ROLLOVER_KEYS:
            usb_hid_keys.append(0x00)

        # Build packet: [modifier, reserved, key1, key2, key3, key4, key5, key6]
        # This directly corresponds to USB HID keyboard report format
        data = [modifier_byte, 0x00, *usb_hid_keys]
        packet = [0x57, 0xAB, 0x00, 0x02, len(data), *data]
        checksum = sum(packet) & 0xFF
        packet.append(checksum)

        self._adapter.send(bytes(packet))

    def press_key(
        self,
        key: KeyCode,
        *,
        shift: bool = False,
        ctrl: bool = False,
        alt: bool = False,
        windows: bool = False,
    ) -> None:
        """Press and release a keyboard key.

        This is a convenience method that calls key_down() followed by key_up().
        For more control over timing, use key_down() and key_up() separately.

        Args:
            key: The key to press.
            shift: Whether to hold shift modifier.
            ctrl: Whether to hold ctrl modifier.
            alt: Whether to hold alt modifier.
            windows: Whether to hold windows modifier.

        Examples:
            >>> driver.press_key(KeyCode.A)  # Press 'a'
            >>> driver.press_key(KeyCode.A, shift=True)  # Press 'A'
            >>> driver.press_key(KeyCode.C, ctrl=True)  # Press Ctrl+C
        """
        self.key_down(key, shift=shift, ctrl=ctrl, alt=alt, windows=windows)
        self.key_up()

    def write_string(self, text: str) -> None:
        """Write a string by simulating keyboard input.

        This method automatically handles uppercase letters by adding the
        shift modifier.

        Args:
            text: The string to write.

        Raises:
            ValueError: If the string contains unsupported characters.

        Examples:
            >>> driver.write_string("Hello, World!")
            >>> driver.write_string("user@example.com")
        """
        if not text:
            return

        for char in text:
            # Get evdev modifier and keycode for this character
            evdev_modifier, evdev_keycode = get_key_mapping(char)

            # Convert evdev codes to USB HID codes
            usb_hid_keycode = evdev_to_usb_hid_keyboard(evdev_keycode)
            # Convert modifier if needed (evdev modifier code to USB HID modifier byte)
            usb_hid_modifier = (
                evdev_to_usb_hid_modifier(evdev_modifier)
                if evdev_modifier != 0x00
                else 0x00
            )

            # Send key press
            press_packet = CH9329Protocol.build_keyboard_press_packet(
                usb_hid_modifier, usb_hid_keycode
            )
            self._adapter.send(press_packet)

            # Send key release
            release_packet = CH9329Protocol.build_keyboard_release_packet()
            self._adapter.send(release_packet)

    def mouse_move_absolute(self, x: int, y: int) -> None:
        """Move mouse cursor to absolute screen position.

        The coordinates are in pixels and will be converted to the device's
        coordinate system (0-4095 for both axes).

        Args:
            x: X coordinate in pixels (0 to screen_width).
            y: Y coordinate in pixels (0 to screen_height).

        Examples:
            >>> driver.mouse_move_absolute(960, 540)  # Move to center
            >>> driver.mouse_move_absolute(0, 0)  # Move to top-left corner
        """
        # Convert pixel coordinates to device coordinates (0-4095)
        device_x = int(4096 * x / self._screen_width)
        device_y = int(4096 * y / self._screen_height)

        packet = CH9329Protocol.build_mouse_abs_packet(0x00, device_x, device_y)
        self._adapter.send(packet)

        # Record operation if recorder is attached
        if self._recorder is not None:
            self._recorder.record(MouseMoveAbsoluteOperation(x, y))

    def mouse_move_relative(self, x: int, y: int) -> None:
        """Move mouse cursor relative to current position.

        Args:
            x: Relative X movement in pixels (-127 to 127).
            y: Relative Y movement in pixels (-127 to 127).

        Examples:
            >>> driver.mouse_move_relative(10, 0)  # Move 10 pixels right
            >>> driver.mouse_move_relative(-20, 10)  # Move left and down
        """
        packet = CH9329Protocol.build_mouse_rel_packet(0x00, x, y, 0)
        self._adapter.send(packet)

        # Record operation if recorder is attached
        if self._recorder is not None:
            self._recorder.record(MouseMoveRelativeOperation(x, y))

    def mouse_button_down(self, button: MouseButton) -> None:
        """Press a mouse button down without releasing it.

        Use mouse_button_up() to release the button. This allows holding
        buttons down for drag operations.

        Args:
            button: The mouse button to press down (evdev MouseButton).

        Examples:
            >>> driver.mouse_button_down(MouseButton.BTN_LEFT)
            >>> driver.mouse_move_relative(100, 100)  # Drag
            >>> driver.mouse_button_up()
        """
        # Convert evdev button code to USB HID button bit
        usb_hid_button = evdev_to_usb_hid_mouse(button.value)

        # Send button press packet
        press_packet = CH9329Protocol.build_mouse_rel_packet(usb_hid_button, 0, 0, 0)
        self._adapter.send(press_packet)

        # Record operation if recorder is attached
        if self._recorder is not None:
            self._recorder.record(MouseButtonDownOperation(button))

    def mouse_button_up(self) -> None:
        """Release all currently pressed mouse buttons.

        Examples:
            >>> driver.mouse_button_down(MouseButton.LEFT)
            >>> # ... do drag operation ...
            >>> driver.mouse_button_up()
        """
        # Send button release packet
        release_packet = CH9329Protocol.build_mouse_rel_packet(0x00, 0, 0, 0)
        self._adapter.send(release_packet)

        # Record operation if recorder is attached
        if self._recorder is not None:
            self._recorder.record(MouseButtonUpOperation())

    def mouse_click(self, button: MouseButton) -> None:
        """Click a mouse button.

        This is a convenience method that calls mouse_button_down() followed
        by mouse_button_up(). For drag operations, use the separated methods.

        Args:
            button: The mouse button to click.

        Examples:
            >>> driver.mouse_click(MouseButton.LEFT)
            >>> driver.mouse_click(MouseButton.RIGHT)
        """
        self.mouse_button_down(button)
        self.mouse_button_up()

    def mouse_scroll(self, amount: int) -> None:
        """Scroll the mouse wheel.

        Args:
            amount: Scroll amount (-127 to 127). Positive scrolls up,
                    negative scrolls down.

        Examples:
            >>> driver.mouse_scroll(5)  # Scroll up
            >>> driver.mouse_scroll(-5)  # Scroll down
        """
        packet = CH9329Protocol.build_mouse_rel_packet(0x00, 0, 0, amount)
        self._adapter.send(packet)

        # Record operation if recorder is attached
        if self._recorder is not None:
            self._recorder.record(MouseScrollOperation(amount))

    def send_mouse_state(self, state: MouseInput) -> None:
        """Send a complete mouse state with buttons, movement, and scroll.

        This is a low-level API that directly exposes CH9329's capability
        to send multiple simultaneous mouse button presses along with
        relative movement and scroll in a single packet.

        Args:
            state: The mouse state containing buttons, movement, and scroll.

        Examples:
            >>> # Move right and down
            >>> state = MouseInput(x=10, y=10)
            >>> driver.send_mouse_state(state)
            >>>
            >>> # Left button pressed while moving
            >>> state = MouseInput(
            ...     buttons={MouseButton.BTN_LEFT},
            ...     x=5,
            ...     y=-5
            ... )
            >>> driver.send_mouse_state(state)
            >>>
            >>> # Multiple buttons with scroll
            >>> state = MouseInput(
            ...     buttons={MouseButton.BTN_LEFT, MouseButton.BTN_RIGHT},
            ...     scroll=3
            ... )
            >>> driver.send_mouse_state(state)
            >>>
            >>> # Drag operation
            >>> # Press and hold
            >>> driver.send_mouse_state(MouseInput(buttons={MouseButton.BTN_LEFT}))
            >>> # Move while holding
            >>> driver.send_mouse_state(MouseInput(
            ...     buttons={MouseButton.BTN_LEFT},
            ...     x=10, y=10
            ... ))
            >>> # Release
            >>> driver.send_mouse_state(MouseInput())
        """
        # Build button byte from evdev button codes
        button_byte = 0x00
        for button in state.buttons:
            button_byte |= evdev_to_usb_hid_mouse(button.value)

        # Build packet using protocol
        packet = CH9329Protocol.build_mouse_rel_packet(
            button_byte, state.x, state.y, state.scroll
        )
        self._adapter.send(packet)

    def media_key_down(self, key: MediaKey) -> None:
        """Press a media control key down without releasing it.

        Use media_key_up() to release the key.

        Args:
            key: The media key to press down.

        Examples:
            >>> driver.media_key_down(MediaKey.VOLUME_UP)
            >>> driver.media_key_up()
        """
        # Send media key press packet
        data0, data1, data2, data3 = key.value
        press_packet = CH9329Protocol.build_media_press_packet(
            data0, data1, data2, data3
        )
        self._adapter.send(press_packet)

        # Record operation if recorder is attached
        if self._recorder is not None:
            self._recorder.record(MediaKeyDownOperation(key))

    def media_key_up(self) -> None:
        """Release the currently pressed media key.

        Examples:
            >>> driver.media_key_down(MediaKey.MUTE)
            >>> # ... wait ...
            >>> driver.media_key_up()
        """
        # Send media key release packet
        release_packet = CH9329Protocol.build_media_release_packet()
        self._adapter.send(release_packet)

        # Record operation if recorder is attached
        if self._recorder is not None:
            self._recorder.record(MediaKeyUpOperation())

    def press_media_key(self, key: MediaKey) -> None:
        """Press a media control key.

        This is a convenience method that calls media_key_down() followed
        by media_key_up().

        Args:
            key: The media key to press.

        Examples:
            >>> driver.press_media_key(MediaKey.MUTE)
            >>> driver.press_media_key(MediaKey.VOLUME_UP)
            >>> driver.press_media_key(MediaKey.PLAY_PAUSE)
        """
        self.media_key_down(key)
        self.media_key_up()

    def close(self) -> None:
        """Close the connection to the device."""
        self._adapter.close()

    def __enter__(self) -> Self:
        """Enter context manager.

        Returns:
            Self for use in with statement.
        """
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        """Exit context manager and close connection.

        Args:
            exc_type: Exception type if an exception was raised.
            exc_val: Exception value if an exception was raised.
            exc_tb: Exception traceback if an exception was raised.
        """
        self.close()
