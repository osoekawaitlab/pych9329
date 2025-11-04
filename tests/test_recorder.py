"""Unit tests for the recorder module."""

# ruff: noqa: SLF001

import json
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from pych9329.models import KeyCode, MediaKey, MouseButton
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
    _operation_from_dict,
)


class TestKeyDownOperation:
    """Tests for KeyDownOperation class."""

    def test_execute_calls_driver_key_down(self) -> None:
        """Test that execute() calls driver.key_down()."""
        driver = MagicMock()
        operation = KeyDownOperation(KeyCode.KEY_A, shift=True, ctrl=False)

        operation.execute(driver)

        driver.key_down.assert_called_once_with(
            KeyCode.KEY_A, shift=True, ctrl=False, alt=False, windows=False
        )

    def test_to_dict_serializes_correctly(self) -> None:
        """Test that to_dict() serializes the operation."""
        operation = KeyDownOperation(KeyCode.KEY_B, shift=False, ctrl=True, alt=True)

        result = operation.to_dict()

        assert result == {
            "type": "key_down",
            "key": "KEY_B",
            "shift": False,
            "ctrl": True,
            "alt": True,
            "windows": False,
        }

    def test_from_dict_deserializes_correctly(self) -> None:
        """Test that from_dict() deserializes the operation."""
        data = {
            "type": "key_down",
            "key": "KEY_C",
            "shift": True,
            "ctrl": False,
            "alt": False,
            "windows": True,
        }

        operation = KeyDownOperation.from_dict(data)

        assert operation.key == KeyCode.KEY_C
        assert operation.shift is True
        assert operation.ctrl is False
        assert operation.alt is False
        assert operation.windows is True

    def test_from_dict_with_missing_modifiers(self) -> None:
        """Test that from_dict() handles missing modifier keys."""
        data = {"type": "key_down", "key": "KEY_D"}

        operation = KeyDownOperation.from_dict(data)

        assert operation.key == KeyCode.KEY_D
        assert operation.shift is False
        assert operation.ctrl is False
        assert operation.alt is False
        assert operation.windows is False


class TestKeyUpOperation:
    """Tests for KeyUpOperation class."""

    def test_execute_calls_driver_key_up(self) -> None:
        """Test that execute() calls driver.key_up()."""
        driver = MagicMock()
        operation = KeyUpOperation()

        operation.execute(driver)

        driver.key_up.assert_called_once_with()

    def test_to_dict_serializes_correctly(self) -> None:
        """Test that to_dict() serializes the operation."""
        operation = KeyUpOperation()

        result = operation.to_dict()

        assert result == {"type": "key_up"}

    def test_from_dict_deserializes_correctly(self) -> None:
        """Test that from_dict() deserializes the operation."""
        data = {"type": "key_up"}

        operation = KeyUpOperation.from_dict(data)

        assert isinstance(operation, KeyUpOperation)


class TestMouseButtonDownOperation:
    """Tests for MouseButtonDownOperation class."""

    def test_execute_calls_driver_mouse_button_down(self) -> None:
        """Test that execute() calls driver.mouse_button_down()."""
        driver = MagicMock()
        operation = MouseButtonDownOperation(MouseButton.BTN_LEFT)

        operation.execute(driver)

        driver.mouse_button_down.assert_called_once_with(MouseButton.BTN_LEFT)

    def test_to_dict_serializes_correctly(self) -> None:
        """Test that to_dict() serializes the operation."""
        operation = MouseButtonDownOperation(MouseButton.BTN_RIGHT)

        result = operation.to_dict()

        assert result == {"type": "mouse_button_down", "button": "BTN_RIGHT"}

    def test_from_dict_deserializes_correctly(self) -> None:
        """Test that from_dict() deserializes the operation."""
        data = {"type": "mouse_button_down", "button": "BTN_MIDDLE"}

        operation = MouseButtonDownOperation.from_dict(data)

        assert operation.button == MouseButton.BTN_MIDDLE


class TestMouseButtonUpOperation:
    """Tests for MouseButtonUpOperation class."""

    def test_execute_calls_driver_mouse_button_up(self) -> None:
        """Test that execute() calls driver.mouse_button_up()."""
        driver = MagicMock()
        operation = MouseButtonUpOperation()

        operation.execute(driver)

        driver.mouse_button_up.assert_called_once_with()

    def test_to_dict_serializes_correctly(self) -> None:
        """Test that to_dict() serializes the operation."""
        operation = MouseButtonUpOperation()

        result = operation.to_dict()

        assert result == {"type": "mouse_button_up"}

    def test_from_dict_deserializes_correctly(self) -> None:
        """Test that from_dict() deserializes the operation."""
        data = {"type": "mouse_button_up"}

        operation = MouseButtonUpOperation.from_dict(data)

        assert isinstance(operation, MouseButtonUpOperation)


class TestMediaKeyDownOperation:
    """Tests for MediaKeyDownOperation class."""

    def test_execute_calls_driver_media_key_down(self) -> None:
        """Test that execute() calls driver.media_key_down()."""
        driver = MagicMock()
        operation = MediaKeyDownOperation(MediaKey.MUTE)

        operation.execute(driver)

        driver.media_key_down.assert_called_once_with(MediaKey.MUTE)

    def test_to_dict_serializes_correctly(self) -> None:
        """Test that to_dict() serializes the operation."""
        operation = MediaKeyDownOperation(MediaKey.VOLUME_UP)

        result = operation.to_dict()

        assert result == {"type": "media_key_down", "key": "VOLUME_UP"}

    def test_from_dict_deserializes_correctly(self) -> None:
        """Test that from_dict() deserializes the operation."""
        data = {"type": "media_key_down", "key": "PLAY_PAUSE"}

        operation = MediaKeyDownOperation.from_dict(data)

        assert operation.key == MediaKey.PLAY_PAUSE


class TestMediaKeyUpOperation:
    """Tests for MediaKeyUpOperation class."""

    def test_execute_calls_driver_media_key_up(self) -> None:
        """Test that execute() calls driver.media_key_up()."""
        driver = MagicMock()
        operation = MediaKeyUpOperation()

        operation.execute(driver)

        driver.media_key_up.assert_called_once_with()

    def test_to_dict_serializes_correctly(self) -> None:
        """Test that to_dict() serializes the operation."""
        operation = MediaKeyUpOperation()

        result = operation.to_dict()

        assert result == {"type": "media_key_up"}

    def test_from_dict_deserializes_correctly(self) -> None:
        """Test that from_dict() deserializes the operation."""
        data = {"type": "media_key_up"}

        operation = MediaKeyUpOperation.from_dict(data)

        assert isinstance(operation, MediaKeyUpOperation)


class TestMouseMoveAbsoluteOperation:
    """Tests for MouseMoveAbsoluteOperation class."""

    def test_execute_calls_driver_mouse_move_absolute(self) -> None:
        """Test that execute() calls driver.mouse_move_absolute()."""
        driver = MagicMock()
        operation = MouseMoveAbsoluteOperation(100, 200)

        operation.execute(driver)

        driver.mouse_move_absolute.assert_called_once_with(100, 200)

    def test_to_dict_serializes_correctly(self) -> None:
        """Test that to_dict() serializes the operation."""
        operation = MouseMoveAbsoluteOperation(300, 400)

        result = operation.to_dict()

        assert result == {"type": "mouse_move_absolute", "x": 300, "y": 400}

    def test_from_dict_deserializes_correctly(self) -> None:
        """Test that from_dict() deserializes the operation."""
        data = {"type": "mouse_move_absolute", "x": 500, "y": 600}

        operation = MouseMoveAbsoluteOperation.from_dict(data)

        assert operation.x == 500
        assert operation.y == 600


class TestMouseMoveRelativeOperation:
    """Tests for MouseMoveRelativeOperation class."""

    def test_execute_calls_driver_mouse_move_relative(self) -> None:
        """Test that execute() calls driver.mouse_move_relative()."""
        driver = MagicMock()
        operation = MouseMoveRelativeOperation(10, -20)

        operation.execute(driver)

        driver.mouse_move_relative.assert_called_once_with(10, -20)

    def test_to_dict_serializes_correctly(self) -> None:
        """Test that to_dict() serializes the operation."""
        operation = MouseMoveRelativeOperation(-30, 40)

        result = operation.to_dict()

        assert result == {"type": "mouse_move_relative", "x": -30, "y": 40}

    def test_from_dict_deserializes_correctly(self) -> None:
        """Test that from_dict() deserializes the operation."""
        data = {"type": "mouse_move_relative", "x": 50, "y": -60}

        operation = MouseMoveRelativeOperation.from_dict(data)

        assert operation.x == 50
        assert operation.y == -60


class TestMouseScrollOperation:
    """Tests for MouseScrollOperation class."""

    def test_execute_calls_driver_mouse_scroll(self) -> None:
        """Test that execute() calls driver.mouse_scroll()."""
        driver = MagicMock()
        operation = MouseScrollOperation(5)

        operation.execute(driver)

        driver.mouse_scroll.assert_called_once_with(5)

    def test_to_dict_serializes_correctly(self) -> None:
        """Test that to_dict() serializes the operation."""
        operation = MouseScrollOperation(-3)

        result = operation.to_dict()

        assert result == {"type": "mouse_scroll", "amount": -3}

    def test_from_dict_deserializes_correctly(self) -> None:
        """Test that from_dict() deserializes the operation."""
        data = {"type": "mouse_scroll", "amount": 7}

        operation = MouseScrollOperation.from_dict(data)

        assert operation.amount == 7


class TestDelayOperation:
    """Tests for DelayOperation class."""

    @patch("time.sleep")
    def test_execute_calls_time_sleep(self, mock_sleep: MagicMock) -> None:
        """Test that execute() calls time.sleep()."""
        driver = MagicMock()
        operation = DelayOperation(0.5)

        operation.execute(driver)

        mock_sleep.assert_called_once_with(0.5)

    def test_to_dict_serializes_correctly(self) -> None:
        """Test that to_dict() serializes the operation."""
        operation = DelayOperation(1.5)

        result = operation.to_dict()

        assert result == {"type": "delay", "seconds": 1.5}

    def test_from_dict_deserializes_correctly(self) -> None:
        """Test that from_dict() deserializes the operation."""
        data = {"type": "delay", "seconds": 2.5}

        operation = DelayOperation.from_dict(data)

        assert operation.seconds == 2.5


class TestOperationRecorder:
    """Tests for OperationRecorder class."""

    def test_start_recording_clears_operations(self) -> None:
        """Test that start_recording() clears existing operations."""
        recorder = OperationRecorder()
        recorder._operations = [KeyUpOperation()]

        recorder.start_recording()

        assert recorder._operations == []
        assert recorder._recording is True

    def test_stop_recording_returns_operations(self) -> None:
        """Test that stop_recording() returns recorded operations."""
        recorder = OperationRecorder()
        op1 = KeyDownOperation(KeyCode.KEY_A)
        op2 = KeyUpOperation()
        recorder._operations = [op1, op2]
        recorder._recording = True

        result = recorder.stop_recording()

        assert result == [op1, op2]
        assert recorder._recording is False

    def test_record_adds_operation_when_recording(self) -> None:
        """Test that record() adds operation when recording is active."""
        recorder = OperationRecorder()
        recorder.start_recording()
        operation = KeyDownOperation(KeyCode.KEY_B)

        recorder.record(operation)

        assert operation in recorder._operations

    def test_record_ignores_operation_when_not_recording(self) -> None:
        """Test that record() ignores operation when not recording."""
        recorder = OperationRecorder()
        operation = KeyDownOperation(KeyCode.KEY_C)

        recorder.record(operation)

        assert operation not in recorder._operations

    @patch("time.time")
    def test_record_adds_delay_between_operations(self, mock_time: MagicMock) -> None:
        """Test that record() adds delay between operations."""
        mock_time.side_effect = [0.0, 0.1, 0.2]  # start, first record, second record
        recorder = OperationRecorder()
        recorder.start_recording()
        op1 = KeyDownOperation(KeyCode.KEY_D)
        op2 = KeyUpOperation()

        recorder.record(op1)
        recorder.record(op2)

        # Should have: DelayOperation(0.1), op1, DelayOperation(0.1), op2
        assert len(recorder._operations) == 4
        assert isinstance(recorder._operations[0], DelayOperation)
        assert recorder._operations[0].seconds == pytest.approx(0.1)
        assert isinstance(recorder._operations[1], KeyDownOperation)
        assert isinstance(recorder._operations[2], DelayOperation)
        assert recorder._operations[2].seconds == pytest.approx(0.1)
        assert isinstance(recorder._operations[3], KeyUpOperation)

    @patch("time.time")
    def test_record_skips_small_delays(self, mock_time: MagicMock) -> None:
        """Test that record() skips delays smaller than 1ms."""
        mock_time.side_effect = [0.0, 0.0005, 0.001]  # 0.5ms delay (should skip)
        recorder = OperationRecorder()
        recorder.start_recording()
        op1 = KeyDownOperation(KeyCode.KEY_E)
        op2 = KeyUpOperation()

        recorder.record(op1)
        recorder.record(op2)

        # Should have: op1, op2 (no delay)
        assert len(recorder._operations) == 2
        assert isinstance(recorder._operations[0], KeyDownOperation)
        assert isinstance(recorder._operations[1], KeyUpOperation)

    def test_save_writes_json_file(self) -> None:
        """Test that save() writes operations to JSON file."""
        recorder = OperationRecorder()
        recorder._operations = [
            KeyDownOperation(KeyCode.KEY_F),
            KeyUpOperation(),
        ]

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            filepath = f.name

        try:
            recorder.save(filepath)

            data = json.loads(Path(filepath).read_text())

            assert len(data) == 2
            assert data[0]["type"] == "key_down"
            assert data[0]["key"] == "KEY_F"
            assert data[1]["type"] == "key_up"
        finally:
            Path(filepath).unlink()

    def test_load_reads_json_file(self) -> None:
        """Test that load() reads operations from JSON file."""
        data = [
            {
                "type": "key_down",
                "key": "KEY_G",
                "shift": False,
                "ctrl": False,
                "alt": False,
                "windows": False,
            },
            {"type": "key_up"},
        ]

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            json.dump(data, f)
            filepath = f.name

        try:
            operations = OperationRecorder.load(filepath)

            assert len(operations) == 2
            assert isinstance(operations[0], KeyDownOperation)
            assert operations[0].key == KeyCode.KEY_G
            assert isinstance(operations[1], KeyUpOperation)
        finally:
            Path(filepath).unlink()


class TestOperationReplayer:
    """Tests for OperationReplayer class."""

    def test_replay_executes_all_operations(self) -> None:
        """Test that replay() executes all operations in sequence."""
        driver = MagicMock()
        replayer = OperationReplayer()
        operations = [
            KeyDownOperation(KeyCode.KEY_H),
            KeyUpOperation(),
            MouseButtonDownOperation(MouseButton.BTN_LEFT),
            MouseButtonUpOperation(),
        ]

        replayer.replay(operations, driver)

        assert driver.key_down.call_count == 1
        assert driver.key_up.call_count == 1
        assert driver.mouse_button_down.call_count == 1
        assert driver.mouse_button_up.call_count == 1

    def test_replay_from_file_loads_and_replays(self) -> None:
        """Test that replay_from_file() loads and replays operations."""
        driver = MagicMock()
        replayer = OperationReplayer()
        data = [
            {
                "type": "key_down",
                "key": "KEY_I",
                "shift": False,
                "ctrl": False,
                "alt": False,
                "windows": False,
            },
            {"type": "key_up"},
        ]

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            json.dump(data, f)
            filepath = f.name

        try:
            replayer.replay_from_file(filepath, driver)

            driver.key_down.assert_called_once()
            driver.key_up.assert_called_once()
        finally:
            Path(filepath).unlink()


class TestOperationFromDict:
    """Tests for _operation_from_dict() function."""

    def test_deserializes_all_operation_types(self) -> None:
        """Test that _operation_from_dict() handles all operation types."""
        test_cases: list[tuple[dict[str, Any], type[Operation]]] = [
            ({"type": "key_down", "key": "KEY_A"}, KeyDownOperation),
            ({"type": "key_up"}, KeyUpOperation),
            (
                {"type": "mouse_button_down", "button": "BTN_LEFT"},
                MouseButtonDownOperation,
            ),
            ({"type": "mouse_button_up"}, MouseButtonUpOperation),
            ({"type": "media_key_down", "key": "MUTE"}, MediaKeyDownOperation),
            ({"type": "media_key_up"}, MediaKeyUpOperation),
            (
                {"type": "mouse_move_absolute", "x": 100, "y": 200},
                MouseMoveAbsoluteOperation,
            ),
            (
                {"type": "mouse_move_relative", "x": 10, "y": 20},
                MouseMoveRelativeOperation,
            ),
            ({"type": "mouse_scroll", "amount": 5}, MouseScrollOperation),
            ({"type": "delay", "seconds": 1.0}, DelayOperation),
        ]

        for data, expected_class in test_cases:
            operation = _operation_from_dict(data)
            assert isinstance(operation, expected_class)

    def test_raises_error_for_unknown_type(self) -> None:
        """Test that _operation_from_dict() raises error for unknown type."""
        data = {"type": "unknown_operation"}

        with pytest.raises(ValueError, match="Unknown operation type"):
            _operation_from_dict(data)
