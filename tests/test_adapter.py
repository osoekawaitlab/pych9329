"""Tests for CH9329 communication adapters."""

from unittest.mock import MagicMock, Mock, patch

import pytest

from pych9329.adapter import CommunicationAdapter, SerialAdapter


class TestCommunicationAdapter:
    """Tests for CommunicationAdapter abstract base class."""

    def test_cannot_instantiate_abstract_class(self) -> None:
        """Test that CommunicationAdapter cannot be instantiated directly."""
        with pytest.raises(TypeError):
            CommunicationAdapter()  # type: ignore[abstract]


class TestSerialAdapter:
    """Tests for SerialAdapter implementation."""

    @patch("pych9329.adapter.serial.Serial")
    def test_init_opens_serial_port(self, mock_serial_class: Mock) -> None:
        """Test that initializing SerialAdapter opens the serial port."""
        mock_serial = MagicMock()
        # By default, pyserial opens the port during __init__
        # So is_open should be True after construction
        mock_serial.is_open = True
        mock_serial_class.return_value = mock_serial

        adapter = SerialAdapter("/dev/ttyUSB0", 9600)

        mock_serial_class.assert_called_once_with(
            port="/dev/ttyUSB0",
            baudrate=9600,
            timeout=0.1,
        )
        # Since port is already open, open() should not be called
        mock_serial.open.assert_not_called()
        assert adapter is not None

    @patch("pych9329.adapter.serial.Serial")
    def test_init_handles_closed_port(self, mock_serial_class: Mock) -> None:
        """Test that adapter handles already closed port during init."""
        mock_serial = MagicMock()
        mock_serial.is_open = False
        mock_serial_class.return_value = mock_serial

        adapter = SerialAdapter("/dev/ttyUSB0", 9600)

        # Should call open() since port is closed
        mock_serial.open.assert_called_once()
        assert adapter is not None

    @patch("pych9329.adapter.serial.Serial")
    def test_init_skips_open_if_already_open(self, mock_serial_class: Mock) -> None:
        """Test that adapter doesn't open already open port."""
        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial_class.return_value = mock_serial

        adapter = SerialAdapter("/dev/ttyUSB0", 9600)

        # Should not call open() since port is already open
        mock_serial.open.assert_not_called()
        assert adapter is not None

    @patch("pych9329.adapter.serial.Serial")
    def test_send_writes_and_reads_data(self, mock_serial_class: Mock) -> None:
        """Test that send() writes data and reads response."""
        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial.read.return_value = b"\x00\x01\x02\x03\x04\x05\x06"
        mock_serial_class.return_value = mock_serial

        adapter = SerialAdapter("/dev/ttyUSB0", 9600)
        test_data = b"\x57\xab\x00\x02\x08"

        response = adapter.send(test_data)

        mock_serial.write.assert_called_once_with(test_data)
        mock_serial.read.assert_called_once_with(7)
        assert response == b"\x00\x01\x02\x03\x04\x05\x06"

    @patch("pych9329.adapter.serial.Serial")
    @patch("pych9329.adapter.time.sleep")
    def test_send_includes_delay(
        self, mock_sleep: Mock, mock_serial_class: Mock
    ) -> None:
        """Test that send() includes a delay between write and read."""
        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial.read.return_value = b"\x00\x01\x02\x03\x04\x05\x06"
        mock_serial_class.return_value = mock_serial

        adapter = SerialAdapter("/dev/ttyUSB0", 9600)
        adapter.send(b"\x57\xab\x00\x02\x08")

        # Should sleep for 0.02 seconds (20ms) between write and read
        mock_sleep.assert_called_once_with(0.02)

    @patch("pych9329.adapter.serial.Serial")
    def test_close_closes_serial_port(self, mock_serial_class: Mock) -> None:
        """Test that close() closes the serial port."""
        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial_class.return_value = mock_serial

        adapter = SerialAdapter("/dev/ttyUSB0", 9600)
        adapter.close()

        mock_serial.close.assert_called_once()

    @patch("pych9329.adapter.serial.Serial")
    def test_context_manager_closes_on_exit(self, mock_serial_class: Mock) -> None:
        """Test that using adapter as context manager closes port on exit."""
        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial_class.return_value = mock_serial

        with SerialAdapter("/dev/ttyUSB0", 9600) as adapter:
            assert adapter is not None

        mock_serial.close.assert_called_once()

    @patch("pych9329.adapter.serial.Serial")
    def test_init_raises_error_for_invalid_port(self, mock_serial_class: Mock) -> None:
        """Test that initializing with invalid port raises an error."""
        mock_serial_class.side_effect = OSError("Port not found")

        with pytest.raises(ConnectionError, match="Failed to open serial port"):
            SerialAdapter("/dev/invalid", 9600)

    @patch("pych9329.adapter.serial.Serial")
    def test_send_raises_error_if_port_closed(self, mock_serial_class: Mock) -> None:
        """Test that send() raises an error if port is closed."""
        mock_serial = MagicMock()
        mock_serial.is_open = False
        mock_serial_class.return_value = mock_serial

        adapter = SerialAdapter("/dev/ttyUSB0", 9600)

        with pytest.raises(ConnectionError, match="Serial port is not open"):
            adapter.send(b"\x57\xab\x00\x02\x08")
