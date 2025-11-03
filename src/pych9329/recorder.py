"""Operation recording and replay functionality.

This module implements the Command pattern to record and replay sequences of
CH9329 operations. Users can record their actions and save them to files for
later replay.
"""

from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pych9329.models import KeyCode, MediaKey, MouseButton

if TYPE_CHECKING:
    from pych9329.driver import CH9329Driver

# Minimum delay in seconds to record between operations
_MIN_DELAY_THRESHOLD = 0.001  # 1ms


class Operation(ABC):
    """Abstract base class for recordable operations.

    All operations that can be recorded and replayed must inherit from this
    class and implement the execute(), to_dict(), and from_dict() methods.
    """

    @abstractmethod
    def execute(self, driver: CH9329Driver) -> None:
        """Execute this operation on the given driver.

        Args:
            driver: The CH9329Driver to execute the operation on.
        """

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Serialize this operation to a dictionary.

        Returns:
            Dictionary representation of the operation.
        """

    @staticmethod
    @abstractmethod
    def from_dict(data: dict[str, Any]) -> Operation:
        """Deserialize an operation from a dictionary.

        Args:
            data: Dictionary representation of the operation.

        Returns:
            The deserialized operation.
        """


class KeyDownOperation(Operation):
    """Operation for pressing a key down."""

    def __init__(
        self,
        key: KeyCode,
        *,
        shift: bool = False,
        ctrl: bool = False,
        alt: bool = False,
        windows: bool = False,
    ) -> None:
        """Initialize key down operation.

        Args:
            key: The key to press down.
            shift: Whether to hold shift modifier.
            ctrl: Whether to hold ctrl modifier.
            alt: Whether to hold alt modifier.
            windows: Whether to hold windows modifier.
        """
        self.key = key
        self.shift = shift
        self.ctrl = ctrl
        self.alt = alt
        self.windows = windows

    def execute(self, driver: CH9329Driver) -> None:
        """Execute the key down operation."""
        driver.key_down(
            self.key,
            shift=self.shift,
            ctrl=self.ctrl,
            alt=self.alt,
            windows=self.windows,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "type": "key_down",
            "key": self.key.name,
            "shift": self.shift,
            "ctrl": self.ctrl,
            "alt": self.alt,
            "windows": self.windows,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> KeyDownOperation:
        """Deserialize from dictionary."""
        return KeyDownOperation(
            key=KeyCode[data["key"]],
            shift=data.get("shift", False),
            ctrl=data.get("ctrl", False),
            alt=data.get("alt", False),
            windows=data.get("windows", False),
        )


class KeyUpOperation(Operation):
    """Operation for releasing all keys."""

    def execute(self, driver: CH9329Driver) -> None:
        """Execute the key up operation."""
        driver.key_up()

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {"type": "key_up"}

    @staticmethod
    def from_dict(_data: dict[str, Any]) -> KeyUpOperation:
        """Deserialize from dictionary."""
        return KeyUpOperation()


class MouseButtonDownOperation(Operation):
    """Operation for pressing a mouse button down."""

    def __init__(self, button: MouseButton) -> None:
        """Initialize mouse button down operation.

        Args:
            button: The mouse button to press down.
        """
        self.button = button

    def execute(self, driver: CH9329Driver) -> None:
        """Execute the mouse button down operation."""
        driver.mouse_button_down(self.button)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {"type": "mouse_button_down", "button": self.button.name}

    @staticmethod
    def from_dict(data: dict[str, Any]) -> MouseButtonDownOperation:
        """Deserialize from dictionary."""
        return MouseButtonDownOperation(button=MouseButton[data["button"]])


class MouseButtonUpOperation(Operation):
    """Operation for releasing all mouse buttons."""

    def execute(self, driver: CH9329Driver) -> None:
        """Execute the mouse button up operation."""
        driver.mouse_button_up()

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {"type": "mouse_button_up"}

    @staticmethod
    def from_dict(_data: dict[str, Any]) -> MouseButtonUpOperation:
        """Deserialize from dictionary."""
        return MouseButtonUpOperation()


class MediaKeyDownOperation(Operation):
    """Operation for pressing a media key down."""

    def __init__(self, key: MediaKey) -> None:
        """Initialize media key down operation.

        Args:
            key: The media key to press down.
        """
        self.key = key

    def execute(self, driver: CH9329Driver) -> None:
        """Execute the media key down operation."""
        driver.media_key_down(self.key)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {"type": "media_key_down", "key": self.key.name}

    @staticmethod
    def from_dict(data: dict[str, Any]) -> MediaKeyDownOperation:
        """Deserialize from dictionary."""
        return MediaKeyDownOperation(key=MediaKey[data["key"]])


class MediaKeyUpOperation(Operation):
    """Operation for releasing media key."""

    def execute(self, driver: CH9329Driver) -> None:
        """Execute the media key up operation."""
        driver.media_key_up()

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {"type": "media_key_up"}

    @staticmethod
    def from_dict(_data: dict[str, Any]) -> MediaKeyUpOperation:
        """Deserialize from dictionary."""
        return MediaKeyUpOperation()


class MouseMoveAbsoluteOperation(Operation):
    """Operation for moving mouse to absolute position."""

    def __init__(self, x: int, y: int) -> None:
        """Initialize mouse move absolute operation.

        Args:
            x: X coordinate in pixels.
            y: Y coordinate in pixels.
        """
        self.x = x
        self.y = y

    def execute(self, driver: CH9329Driver) -> None:
        """Execute the mouse move absolute operation."""
        driver.mouse_move_absolute(self.x, self.y)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {"type": "mouse_move_absolute", "x": self.x, "y": self.y}

    @staticmethod
    def from_dict(data: dict[str, Any]) -> MouseMoveAbsoluteOperation:
        """Deserialize from dictionary."""
        return MouseMoveAbsoluteOperation(x=data["x"], y=data["y"])


class MouseMoveRelativeOperation(Operation):
    """Operation for moving mouse relative to current position."""

    def __init__(self, x: int, y: int) -> None:
        """Initialize mouse move relative operation.

        Args:
            x: Relative X movement in pixels.
            y: Relative Y movement in pixels.
        """
        self.x = x
        self.y = y

    def execute(self, driver: CH9329Driver) -> None:
        """Execute the mouse move relative operation."""
        driver.mouse_move_relative(self.x, self.y)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {"type": "mouse_move_relative", "x": self.x, "y": self.y}

    @staticmethod
    def from_dict(data: dict[str, Any]) -> MouseMoveRelativeOperation:
        """Deserialize from dictionary."""
        return MouseMoveRelativeOperation(x=data["x"], y=data["y"])


class MouseScrollOperation(Operation):
    """Operation for scrolling mouse wheel."""

    def __init__(self, amount: int) -> None:
        """Initialize mouse scroll operation.

        Args:
            amount: Scroll amount (-127 to 127).
        """
        self.amount = amount

    def execute(self, driver: CH9329Driver) -> None:
        """Execute the mouse scroll operation."""
        driver.mouse_scroll(self.amount)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {"type": "mouse_scroll", "amount": self.amount}

    @staticmethod
    def from_dict(data: dict[str, Any]) -> MouseScrollOperation:
        """Deserialize from dictionary."""
        return MouseScrollOperation(amount=data["amount"])


class DelayOperation(Operation):
    """Operation for adding delay between operations."""

    def __init__(self, seconds: float) -> None:
        """Initialize delay operation.

        Args:
            seconds: Number of seconds to delay.
        """
        self.seconds = seconds

    def execute(self, _driver: CH9329Driver) -> None:
        """Execute the delay operation."""
        time.sleep(self.seconds)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {"type": "delay", "seconds": self.seconds}

    @staticmethod
    def from_dict(data: dict[str, Any]) -> DelayOperation:
        """Deserialize from dictionary."""
        return DelayOperation(seconds=data["seconds"])


class OperationRecorder:
    """Records sequences of operations for later replay.

    Examples:
        >>> from pych9329 import CH9329Driver, SerialAdapter
        >>> from pych9329.recorder import OperationRecorder
        >>> recorder = OperationRecorder()
        >>> adapter = SerialAdapter("/dev/ttyUSB0", 9600)
        >>> driver = CH9329Driver(adapter, recorder=recorder)
        >>> recorder.start_recording()
        >>> driver.key_down(KeyCode.A)
        >>> driver.key_up()
        >>> operations = recorder.stop_recording()
        >>> recorder.save("my_sequence.json")
    """

    def __init__(self) -> None:
        """Initialize the operation recorder."""
        self._operations: list[Operation] = []
        self._recording = False
        self._last_time: float | None = None

    def start_recording(self) -> None:
        """Start recording operations."""
        self._operations = []
        self._recording = True
        self._last_time = time.time()

    def stop_recording(self) -> list[Operation]:
        """Stop recording and return the recorded operations.

        Returns:
            List of recorded operations.
        """
        self._recording = False
        return self._operations.copy()

    def record(self, operation: Operation) -> None:
        """Record an operation.

        If recording is active, this also records the time delay since the
        last operation.

        Args:
            operation: The operation to record.
        """
        if not self._recording:
            return

        # Record delay since last operation
        current_time = time.time()
        if self._last_time is not None:
            delay = current_time - self._last_time
            if delay > _MIN_DELAY_THRESHOLD:
                self._operations.append(DelayOperation(delay))

        self._operations.append(operation)
        self._last_time = current_time

    def save(self, filepath: str | Path) -> None:
        """Save recorded operations to a JSON file.

        Args:
            filepath: Path to the file to save to.
        """
        filepath = Path(filepath)
        data = [op.to_dict() for op in self._operations]
        filepath.write_text(json.dumps(data, indent=2))

    @staticmethod
    def load(filepath: str | Path) -> list[Operation]:
        """Load operations from a JSON file.

        Args:
            filepath: Path to the file to load from.

        Returns:
            List of loaded operations.
        """
        filepath = Path(filepath)
        data = json.loads(filepath.read_text())
        return [_operation_from_dict(op_data) for op_data in data]


class OperationReplayer:
    """Replays recorded sequences of operations.

    Examples:
        >>> from pych9329 import CH9329Driver, SerialAdapter
        >>> from pych9329.recorder import OperationReplayer
        >>> replayer = OperationReplayer()
        >>> adapter = SerialAdapter("/dev/ttyUSB0", 9600)
        >>> driver = CH9329Driver(adapter)
        >>> operations = OperationRecorder.load("my_sequence.json")
        >>> replayer.replay(operations, driver)
    """

    def replay(self, operations: list[Operation], driver: CH9329Driver) -> None:
        """Replay a sequence of operations.

        Args:
            operations: List of operations to replay.
            driver: The driver to execute operations on.
        """
        for operation in operations:
            operation.execute(driver)

    def replay_from_file(self, filepath: str | Path, driver: CH9329Driver) -> None:
        """Load and replay operations from a file.

        Args:
            filepath: Path to the file containing operations.
            driver: The driver to execute operations on.
        """
        operations = OperationRecorder.load(filepath)
        self.replay(operations, driver)


# Mapping from operation type to class
_OPERATION_TYPES: dict[str, type[Operation]] = {
    "key_down": KeyDownOperation,
    "key_up": KeyUpOperation,
    "mouse_button_down": MouseButtonDownOperation,
    "mouse_button_up": MouseButtonUpOperation,
    "media_key_down": MediaKeyDownOperation,
    "media_key_up": MediaKeyUpOperation,
    "mouse_move_absolute": MouseMoveAbsoluteOperation,
    "mouse_move_relative": MouseMoveRelativeOperation,
    "mouse_scroll": MouseScrollOperation,
    "delay": DelayOperation,
}


def _operation_from_dict(data: dict[str, Any]) -> Operation:
    """Deserialize an operation from a dictionary.

    Args:
        data: Dictionary representation of the operation.

    Returns:
        The deserialized operation.

    Raises:
        ValueError: If the operation type is unknown.
    """
    op_type = data.get("type")
    if op_type not in _OPERATION_TYPES:
        msg = f"Unknown operation type: {op_type}"
        raise ValueError(msg)

    operation_class = _OPERATION_TYPES[op_type]
    return operation_class.from_dict(data)
