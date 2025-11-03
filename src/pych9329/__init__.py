"""Python driver for CH9329 USB HID device.

This package provides a high-level API for controlling CH9329 USB HID devices.
The CH9329 chip allows simulation of keyboard and mouse inputs through serial
communication.

Basic usage:
    >>> from pych9329 import CH9329Driver, SerialAdapter
    >>> adapter = SerialAdapter("/dev/ttyUSB0", 9600)
    >>> driver = CH9329Driver(adapter, screen_width=1920, screen_height=1080)
    >>> driver.write_string("Hello, World!")
    >>> driver.mouse_move_absolute(960, 540)
    >>> driver.close()

Context manager usage:
    >>> with SerialAdapter("/dev/ttyUSB0", 9600) as adapter:
    ...     with CH9329Driver(adapter) as driver:
    ...         driver.write_string("Hello!")
"""

from pych9329.adapter import CommunicationAdapter, SerialAdapter
from pych9329.driver import CH9329Driver
from pych9329.models import KeyCode, MediaKey, ModifierKey, MouseButton
from pych9329.recorder import (
    DelayOperation,
    KeyDownOperation,
    KeyUpOperation,
    MediaKeyDownOperation,
    MediaKeyUpOperation,
    MouseButtonDownOperation,
    MouseButtonUpOperation,
    MouseMoveAbsoluteOperation,
    MouseMoveRelativeOperation,
    MouseScrollOperation,
    Operation,
    OperationRecorder,
    OperationReplayer,
)

__version__ = "0.2.0"

__all__ = [
    "CH9329Driver",
    "CommunicationAdapter",
    "DelayOperation",
    "KeyCode",
    "KeyDownOperation",
    "KeyUpOperation",
    "MediaKey",
    "MediaKeyDownOperation",
    "MediaKeyUpOperation",
    "ModifierKey",
    "MouseButton",
    "MouseButtonDownOperation",
    "MouseButtonUpOperation",
    "MouseMoveAbsoluteOperation",
    "MouseMoveRelativeOperation",
    "MouseScrollOperation",
    "Operation",
    "OperationRecorder",
    "OperationReplayer",
    "SerialAdapter",
    "__version__",
]
