"""Python driver for CH9329 USB HID device.

This package provides a low-level state-based API for controlling CH9329
USB HID devices. The CH9329 chip allows simulation of keyboard, mouse, and
media key inputs through serial communication.

Basic usage:
    >>> from pych9329 import CH9329Driver, SerialAdapter, KeyboardInput, KeyCode
    >>> adapter = SerialAdapter("/dev/ttyUSB0", 9600)
    >>> driver = CH9329Driver(adapter)
    >>> state = KeyboardInput(keys=[KeyCode.KEY_A])
    >>> driver.send_keyboard_input(state)
    >>> driver.close()

Context manager usage:
    >>> with SerialAdapter("/dev/ttyUSB0", 9600) as adapter:
    ...     with CH9329Driver(adapter) as driver:
    ...         state = KeyboardInput(keys=[KeyCode.KEY_H, KeyCode.KEY_I])
    ...         driver.send_keyboard_input(state)
"""

from pych9329.adapter import CommunicationAdapter, SerialAdapter
from pych9329.driver import CH9329Driver
from pych9329.exceptions import Pych9329Error, UnsupportedEvdevCodeError
from pych9329.models import (
    KeyboardInput,
    KeyCode,
    MediaKey,
    MediaKeyInput,
    ModifierKey,
    MouseButton,
    MouseInput,
)

__version__ = "0.2.0"

__all__ = [
    "CH9329Driver",
    "CommunicationAdapter",
    "KeyCode",
    "KeyboardInput",
    "MediaKey",
    "MediaKeyInput",
    "ModifierKey",
    "MouseButton",
    "MouseInput",
    "Pych9329Error",
    "SerialAdapter",
    "UnsupportedEvdevCodeError",
    "__version__",
]
