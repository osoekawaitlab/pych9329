"""Tests for CH9329 main driver class."""

from unittest.mock import Mock

import pytest

from pych9329.driver import CH9329Driver
from pych9329.models import KeyCode, MediaKey, MouseButton


class TestCH9329DriverInit:
    """Tests for CH9329Driver initialization."""

    def test_init_with_adapter(self) -> None:
        """Test initializing driver with a communication adapter."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter, screen_width=1920, screen_height=1080)

        assert driver is not None

    def test_init_with_default_screen_size(self) -> None:
        """Test that driver uses default screen size."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter)

        assert driver is not None


class TestCH9329DriverKeyboard:
    """Tests for keyboard input methods."""

    def test_press_key_sends_press_and_release(self) -> None:
        """Test that press_key sends both press and release packets."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter)

        driver.press_key(KeyCode.A)

        # Should send press packet and then release packet
        assert mock_adapter.send.call_count == 2

    def test_press_key_with_shift(self) -> None:
        """Test pressing a key with shift modifier."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter)

        driver.press_key(KeyCode.A, shift=True)

        # Should send press with shift and then release
        assert mock_adapter.send.call_count == 2
        # First call should have shift modifier (0x02)
        first_call_data = mock_adapter.send.call_args_list[0][0][0]
        # Check that modifier byte is 0x02 (shift)
        assert first_call_data[5] == 0x02

    def test_press_key_with_ctrl(self) -> None:
        """Test pressing a key with ctrl modifier."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter)

        driver.press_key(KeyCode.C, ctrl=True)

        assert mock_adapter.send.call_count == 2
        # First call should have ctrl modifier (0x01)
        first_call_data = mock_adapter.send.call_args_list[0][0][0]
        assert first_call_data[5] == 0x01

    def test_press_key_with_multiple_modifiers(self) -> None:
        """Test pressing a key with multiple modifiers."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter)

        driver.press_key(KeyCode.C, ctrl=True, shift=True)

        assert mock_adapter.send.call_count == 2
        # First call should have ctrl + shift (0x01 | 0x02 = 0x03)
        first_call_data = mock_adapter.send.call_args_list[0][0][0]
        assert first_call_data[5] == 0x03

    def test_write_string_single_char(self) -> None:
        """Test writing a single character string."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter)

        driver.write_string("a")

        # Should send press and release for one character
        assert mock_adapter.send.call_count == 2

    def test_write_string_multiple_chars(self) -> None:
        """Test writing a multi-character string."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter)

        driver.write_string("abc")

        # Should send press and release for each character (3 * 2 = 6)
        assert mock_adapter.send.call_count == 6

    def test_write_string_with_uppercase(self) -> None:
        """Test writing string with uppercase letters."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter)

        driver.write_string("A")

        # Should send press and release
        assert mock_adapter.send.call_count == 2
        # First call should have shift modifier for uppercase
        first_call_data = mock_adapter.send.call_args_list[0][0][0]
        assert first_call_data[5] == 0x02  # shift modifier

    def test_write_string_empty(self) -> None:
        """Test writing empty string does nothing."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter)

        driver.write_string("")

        # Should not send any packets
        mock_adapter.send.assert_not_called()

    def test_write_string_with_unsupported_char_raises_error(self) -> None:
        """Test that writing unsupported characters raises ValueError."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter)

        with pytest.raises(ValueError, match="Unsupported character"):
            driver.write_string("あ")


class TestCH9329DriverMouse:
    """Tests for mouse input methods."""

    def test_mouse_move_absolute(self) -> None:
        """Test moving mouse to absolute position."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter, screen_width=1920, screen_height=1080)

        driver.mouse_move_absolute(960, 540)

        # Should send one mouse absolute packet
        mock_adapter.send.assert_called_once()

    def test_mouse_move_relative(self) -> None:
        """Test moving mouse relative to current position."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter)

        driver.mouse_move_relative(10, 20)

        # Should send one mouse relative packet
        mock_adapter.send.assert_called_once()

    def test_mouse_click_left(self) -> None:
        """Test left mouse button click."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter)

        driver.mouse_click(MouseButton.LEFT)

        # Should send press and release packets
        assert mock_adapter.send.call_count == 2

    def test_mouse_click_right(self) -> None:
        """Test right mouse button click."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter)

        driver.mouse_click(MouseButton.RIGHT)

        assert mock_adapter.send.call_count == 2

    def test_mouse_scroll_up(self) -> None:
        """Test scrolling mouse wheel up."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter)

        driver.mouse_scroll(5)

        # Should send one scroll packet
        mock_adapter.send.assert_called_once()

    def test_mouse_scroll_down(self) -> None:
        """Test scrolling mouse wheel down."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter)

        driver.mouse_scroll(-5)

        # Should send one scroll packet
        mock_adapter.send.assert_called_once()


class TestCH9329DriverMedia:
    """Tests for media key methods."""

    def test_media_key_press(self) -> None:
        """Test pressing a media key."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter)

        driver.press_media_key(MediaKey.MUTE)

        # Should send press and release packets
        assert mock_adapter.send.call_count == 2

    def test_media_key_volume_up(self) -> None:
        """Test volume up media key."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter)

        driver.press_media_key(MediaKey.VOLUME_UP)

        assert mock_adapter.send.call_count == 2

    def test_media_key_play_pause(self) -> None:
        """Test play/pause media key."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter)

        driver.press_media_key(MediaKey.PLAY_PAUSE)

        assert mock_adapter.send.call_count == 2


class TestCH9329DriverContextManager:
    """Tests for context manager support."""

    def test_context_manager_closes_adapter(self) -> None:
        """Test that using driver as context manager closes adapter."""
        mock_adapter = Mock()

        with CH9329Driver(mock_adapter) as driver:
            assert driver is not None

        mock_adapter.close.assert_called_once()

    def test_close_method_closes_adapter(self) -> None:
        """Test that close method closes the adapter."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter)

        driver.close()

        mock_adapter.close.assert_called_once()


class TestCH9329DriverScreenCoordinates:
    """Tests for screen coordinate conversion."""

    def test_pixel_to_device_coordinates_origin(self) -> None:
        """Test converting origin pixel coordinates."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter, screen_width=1920, screen_height=1080)

        driver.mouse_move_absolute(0, 0)

        # Should send packet with device coordinates (0, 0)
        call_data = mock_adapter.send.call_args[0][0]
        # Check x and y coordinates in packet (bytes 7-10)
        x_low, x_high = call_data[7], call_data[8]
        y_low, y_high = call_data[9], call_data[10]
        assert (x_high << 8) | x_low == 0
        assert (y_high << 8) | y_low == 0

    def test_pixel_to_device_coordinates_center(self) -> None:
        """Test converting center pixel coordinates."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter, screen_width=1920, screen_height=1080)

        # Move to center of screen
        driver.mouse_move_absolute(960, 540)

        call_data = mock_adapter.send.call_args[0][0]
        x_low, x_high = call_data[7], call_data[8]
        y_low, y_high = call_data[9], call_data[10]
        x_device = (x_high << 8) | x_low
        y_device = (y_high << 8) | y_low

        # Center should be around 2048 (half of 4096)
        assert 2000 < x_device < 2100
        assert 2000 < y_device < 2100


class TestCH9329DriverSeparatedKeyboard:
    """Tests for separated keyboard press/release methods."""

    def test_key_down_sends_only_press(self) -> None:
        """Test that key_down sends only press packet."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter)

        driver.key_down(KeyCode.A)

        # Should send only press packet
        mock_adapter.send.assert_called_once()

    def test_key_up_sends_only_release(self) -> None:
        """Test that key_up sends only release packet."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter)

        driver.key_up()

        # Should send only release packet
        mock_adapter.send.assert_called_once()

    def test_key_down_with_modifiers(self) -> None:
        """Test key_down with modifier keys."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter)

        driver.key_down(KeyCode.C, shift=True, ctrl=True)

        mock_adapter.send.assert_called_once()
        # Check that modifier byte has shift + ctrl (0x02 | 0x01 = 0x03)
        call_data = mock_adapter.send.call_args[0][0]
        assert call_data[5] == 0x03

    def test_key_down_then_key_up_sequence(self) -> None:
        """Test that key_down followed by key_up works correctly."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter)

        driver.key_down(KeyCode.B)
        driver.key_up()

        # Should have sent 2 packets total
        assert mock_adapter.send.call_count == 2


class TestCH9329DriverSeparatedMouse:
    """Tests for separated mouse button press/release methods."""

    def test_mouse_button_down_sends_only_press(self) -> None:
        """Test that mouse_button_down sends only press packet."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter)

        driver.mouse_button_down(MouseButton.LEFT)

        # Should send only press packet
        mock_adapter.send.assert_called_once()

    def test_mouse_button_up_sends_only_release(self) -> None:
        """Test that mouse_button_up sends only release packet."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter)

        driver.mouse_button_up()

        # Should send only release packet
        mock_adapter.send.assert_called_once()

    def test_mouse_button_down_then_up_sequence(self) -> None:
        """Test that mouse_button_down followed by mouse_button_up works."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter)

        driver.mouse_button_down(MouseButton.RIGHT)
        driver.mouse_button_up()

        # Should have sent 2 packets total
        assert mock_adapter.send.call_count == 2


class TestCH9329DriverSeparatedMedia:
    """Tests for separated media key press/release methods."""

    def test_media_key_down_sends_only_press(self) -> None:
        """Test that media_key_down sends only press packet."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter)

        driver.media_key_down(MediaKey.MUTE)

        # Should send only press packet
        mock_adapter.send.assert_called_once()

    def test_media_key_up_sends_only_release(self) -> None:
        """Test that media_key_up sends only release packet."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter)

        driver.media_key_up()

        # Should send only release packet
        mock_adapter.send.assert_called_once()

    def test_media_key_down_then_up_sequence(self) -> None:
        """Test that media_key_down followed by media_key_up works."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter)

        driver.media_key_down(MediaKey.VOLUME_UP)
        driver.media_key_up()

        # Should have sent 2 packets total
        assert mock_adapter.send.call_count == 2


class TestCH9329DriverWithRecorder:
    """Tests for driver integration with operation recorder."""

    def test_driver_with_recorder_records_operations(self) -> None:
        """Test that driver with recorder records operations."""
        from pych9329.recorder import OperationRecorder

        mock_adapter = Mock()
        recorder = OperationRecorder()
        driver = CH9329Driver(mock_adapter, recorder=recorder)

        recorder.start_recording()
        driver.key_down(KeyCode.A)
        driver.key_up()
        operations = recorder.stop_recording()

        # Should have recorded at least 2 operations (key_down and key_up)
        assert len(operations) >= 2

    def test_driver_without_recorder_works_normally(self) -> None:
        """Test that driver without recorder works normally."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter)

        # Should work without errors
        driver.key_down(KeyCode.A)
        driver.key_up()

        assert mock_adapter.send.call_count == 2


class TestCH9329DriverBackwardCompatibility:
    """Tests to ensure backward compatibility with combined methods."""

    def test_press_key_still_works(self) -> None:
        """Test that press_key convenience method still works."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter)

        driver.press_key(KeyCode.A)

        # Should send 2 packets (press and release)
        assert mock_adapter.send.call_count == 2

    def test_mouse_click_still_works(self) -> None:
        """Test that mouse_click convenience method still works."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter)

        driver.mouse_click(MouseButton.LEFT)

        # Should send 2 packets (press and release)
        assert mock_adapter.send.call_count == 2

    def test_press_media_key_still_works(self) -> None:
        """Test that press_media_key convenience method still works."""
        mock_adapter = Mock()
        driver = CH9329Driver(mock_adapter)

        driver.press_media_key(MediaKey.MUTE)

        # Should send 2 packets (press and release)
        assert mock_adapter.send.call_count == 2
