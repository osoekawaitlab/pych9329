"""Communication adapters for CH9329 device.

This module provides communication adapters for interacting with the CH9329 device.
The abstract base class allows for dependency injection and easy testing with mock
implementations.
"""

import sys
import time
from abc import ABC, abstractmethod

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

import serial


class CommunicationAdapter(ABC):
    """Abstract base class for communication adapters.

    This class defines the interface for communicating with the CH9329 device.
    Concrete implementations handle the actual communication protocol (e.g., serial).
    """

    @abstractmethod
    def send(self, data: bytes) -> bytes:
        """Send data to the device and receive response.

        Args:
            data: Bytes to send to the device.

        Returns:
            Response bytes from the device.

        Raises:
            ConnectionError: If communication fails.
        """

    @abstractmethod
    def close(self) -> None:
        """Close the communication channel.

        This should clean up any resources (e.g., close serial port).
        """

    @abstractmethod
    def __enter__(self) -> Self:
        """Enter context manager.

        Returns:
            Self for use in with statement.
        """

    @abstractmethod
    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        """Exit context manager and close connection.

        Args:
            exc_type: Exception type if an exception was raised.
            exc_val: Exception value if an exception was raised.
            exc_tb: Exception traceback if an exception was raised.
        """


class SerialAdapter(CommunicationAdapter):
    r"""Serial communication adapter for CH9329 device.

    This adapter uses pyserial to communicate with the CH9329 device over a
    serial connection (USB, UART, etc.).

    Args:
        port: Serial port path (e.g., "/dev/ttyUSB0" on Linux, "COM5" on Windows).
        baudrate: Communication speed in bits per second (default: 9600).
        timeout: Read timeout in seconds (default: 0.1).

    Raises:
        ConnectionError: If the serial port cannot be opened.

    Examples:
        >>> adapter = SerialAdapter("/dev/ttyUSB0", 9600)
        >>> response = adapter.send(b"\x57\xAB\x00\x02\x08")
        >>> adapter.close()

        Or using context manager:
        >>> with SerialAdapter("/dev/ttyUSB0", 9600) as adapter:
        ...     response = adapter.send(b"\x57\xAB\x00\x02\x08")
    """

    # Response packet length from CH9329
    _RESPONSE_LENGTH = 7

    # Delay between write and read (in seconds)
    _WRITE_READ_DELAY = 0.02

    def __init__(
        self,
        port: str,
        baudrate: int = 9600,
        timeout: float = 0.1,
        write_read_delay: float = 0.02,
    ) -> None:
        """Initialize serial adapter and open connection.

        Args:
            port: Serial port path.
            baudrate: Communication speed in bits per second.
            timeout: Read timeout in seconds.
            write_read_delay: Delay between write and read in seconds.

        Raises:
            ConnectionError: If the serial port cannot be opened.
        """
        self._write_read_delay = write_read_delay
        try:
            self._serial = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
            )
            # Open the port if it's not already open
            if not self._serial.is_open:
                self._serial.open()
        except (OSError, serial.SerialException) as e:
            msg = f"Failed to open serial port {port}: {e}"
            raise ConnectionError(msg) from e

    def send(self, data: bytes) -> bytes:
        """Send data to the device and receive response.

        Args:
            data: Bytes to send to the device.

        Returns:
            Response bytes from the device (7 bytes).

        Raises:
            ConnectionError: If the serial port is not open or communication fails.
        """
        if not self._serial.is_open:
            msg = "Serial port is not open"
            raise ConnectionError(msg)

        try:
            # Write data to serial port
            self._serial.write(data)

            # Wait for device to process
            time.sleep(self._write_read_delay)

            # Read response
            return self._serial.read(self._RESPONSE_LENGTH)
        except serial.SerialException as e:
            msg = f"Serial communication failed: {e}"
            raise ConnectionError(msg) from e

    def close(self) -> None:
        """Close the serial port."""
        if hasattr(self, "_serial") and self._serial.is_open:
            self._serial.close()

    def __enter__(self) -> Self:
        """Enter context manager.

        Returns:
            Self for use in with statement.
        """
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        """Exit context manager and close serial port.

        Args:
            exc_type: Exception type if an exception was raised.
            exc_val: Exception value if an exception was raised.
            exc_tb: Exception traceback if an exception was raised.
        """
        self.close()
