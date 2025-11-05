"""Main driver class for CH9329 USB HID device.

This module provides the low-level API for interacting with the CH9329 device.
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
    MediaKeyInput,
    MouseInput,
)
from pych9329.protocol import CH9329Protocol

if TYPE_CHECKING:
    from pych9329.adapter import CommunicationAdapter


class CH9329Driver:
    """Low-level driver for CH9329 USB HID device.

    This class provides direct state-based API for keyboard, mouse, and media key
    simulation through the CH9329 chip.

    Args:
        adapter: Communication adapter for sending/receiving data.

    Examples:
        >>> from pych9329.adapter import SerialAdapter
        >>> from pych9329.driver import CH9329Driver
        >>> from pych9329.models import KeyboardInput, KeyCode
        >>> adapter = SerialAdapter("/dev/ttyUSB0", 9600)
        >>> driver = CH9329Driver(adapter)
        >>> state = KeyboardInput(keys=[KeyCode.KEY_A])
        >>> driver.send_keyboard_input(state)
        >>> driver.close()

        Or using context manager:
        >>> with SerialAdapter("/dev/ttyUSB0", 9600) as adapter:
        ...     with CH9329Driver(adapter) as driver:
        ...         state = KeyboardInput(keys=[KeyCode.KEY_A])
        ...         driver.send_keyboard_input(state)
    """

    def __init__(
        self,
        adapter: CommunicationAdapter,
    ) -> None:
        """Initialize the CH9329 driver.

        Args:
            adapter: Communication adapter for sending/receiving data.
        """
        self._adapter = adapter

    def send_keyboard_input(self, input_data: KeyboardInput) -> None:
        """Send a complete keyboard input with multiple keys and modifiers.

        This is a low-level API that directly exposes CH9329's capability
        to send up to 6 simultaneous key presses with 8 modifier keys.

        Args:
            input_data: The keyboard input containing modifiers and keys.

        Examples:
            >>> # Press Ctrl+Shift+A
            >>> input_data = KeyboardInput(
            ...     modifiers={ModifierKey.KEY_LEFTCTRL, ModifierKey.KEY_LEFTSHIFT},
            ...     keys=[KeyCode.KEY_A]
            ... )
            >>> driver.send_keyboard_input(input_data)
            >>>
            >>> # Press A+B+C simultaneously with Shift
            >>> input_data = KeyboardInput(
            ...     modifiers={ModifierKey.KEY_LEFTSHIFT},
            ...     keys=[KeyCode.KEY_A, KeyCode.KEY_B, KeyCode.KEY_C]
            ... )
            >>> driver.send_keyboard_input(input_data)
            >>>
            >>> # Maximum 6 keys at once
            >>> input_data = KeyboardInput(
            ...     keys=[KeyCode.KEY_A, KeyCode.KEY_B, KeyCode.KEY_C,
            ...           KeyCode.KEY_D, KeyCode.KEY_E, KeyCode.KEY_F]
            ... )
            >>> driver.send_keyboard_input(input_data)
            >>>
            >>> # Release all keys
            >>> driver.send_keyboard_input(KeyboardInput())
        """
        # Build modifier byte from evdev modifier keys
        modifier_byte = 0x00
        for modifier_key in input_data.modifiers:
            modifier_byte |= evdev_to_usb_hid_modifier(modifier_key.value)

        # Convert evdev key codes to USB HID scan codes
        usb_hid_keys = [evdev_to_usb_hid_keyboard(key.value) for key in input_data.keys]

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

    def send_mouse_input(self, input_data: MouseInput) -> None:
        """Send a complete mouse input with buttons, movement, and scroll.

        This is a low-level API that directly exposes CH9329's capability
        to send multiple simultaneous mouse button presses along with
        relative movement and scroll in a single packet.

        Args:
            input_data: The mouse input containing buttons, movement, and scroll.

        Examples:
            >>> # Move right and down
            >>> input_data = MouseInput(x=10, y=10)
            >>> driver.send_mouse_input(input_data)
            >>>
            >>> # Left button pressed while moving
            >>> input_data = MouseInput(
            ...     buttons={MouseButton.BTN_LEFT},
            ...     x=5,
            ...     y=-5
            ... )
            >>> driver.send_mouse_input(input_data)
            >>>
            >>> # Multiple buttons with scroll
            >>> input_data = MouseInput(
            ...     buttons={MouseButton.BTN_LEFT, MouseButton.BTN_RIGHT},
            ...     scroll=3
            ... )
            >>> driver.send_mouse_input(input_data)
            >>>
            >>> # Drag operation
            >>> # Press and hold
            >>> driver.send_mouse_input(MouseInput(buttons={MouseButton.BTN_LEFT}))
            >>> # Move while holding
            >>> driver.send_mouse_input(MouseInput(
            ...     buttons={MouseButton.BTN_LEFT},
            ...     x=10, y=10
            ... ))
            >>> # Release
            >>> driver.send_mouse_input(MouseInput())
        """
        # Build button byte from evdev button codes
        button_byte = 0x00
        for button in input_data.buttons:
            button_byte |= evdev_to_usb_hid_mouse(button.value)

        # Build packet using protocol
        packet = CH9329Protocol.build_mouse_rel_packet(
            button_byte, input_data.x, input_data.y, input_data.scroll
        )
        self._adapter.send(packet)

    def send_media_key_input(self, input_data: MediaKeyInput) -> None:
        """Send a media key input.

        This is a low-level API that directly sends media key state.
        Unlike keyboard input which supports 6 simultaneous keys,
        media keys only support single key at a time.

        Args:
            input_data: The media key input containing keys to press or release.

        Examples:
            >>> # Mute audio (press)
            >>> input_data = MediaKeyInput(keys=[MediaKey.KEY_MUTE])
            >>> driver.send_media_key_input(input_data)
            >>>
            >>> # Play/pause media (press)
            >>> input_data = MediaKeyInput(keys=[MediaKey.KEY_PLAYPAUSE])
            >>> driver.send_media_key_input(input_data)
            >>>
            >>> # Adjust volume (press)
            >>> input_data = MediaKeyInput(keys=[MediaKey.KEY_VOLUMEUP])
            >>> driver.send_media_key_input(input_data)
            >>>
            >>> # Release all keys
            >>> input_data = MediaKeyInput(keys=[])
            >>> driver.send_media_key_input(input_data)
        """
        if not input_data.keys:
            # Empty keys list means release all media keys
            packet = CH9329Protocol.build_media_release_packet()
            self._adapter.send(packet)
        else:
            # Press the single media key
            # Extract the 4-byte media key code from the enum value
            data0, data1, data2, data3 = input_data.keys[0].value

            # Build packet using protocol
            packet = CH9329Protocol.build_media_press_packet(data0, data1, data2, data3)
            self._adapter.send(packet)

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
