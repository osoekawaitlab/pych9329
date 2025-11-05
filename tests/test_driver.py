"""Tests for CH9329 main driver class."""

from unittest.mock import Mock

from pych9329.adapter import CommunicationAdapter
from pych9329.driver import CH9329Driver
from pych9329.evdev_mapping import (
    evdev_to_usb_hid_keyboard,
    evdev_to_usb_hid_modifier,
    evdev_to_usb_hid_mouse,
)
from pych9329.models import (
    KeyboardInput,
    KeyCode,
    MediaKey,
    MediaKeyInput,
    ModifierKey,
    MouseButton,
    MouseInput,
)

# Protocol constants
PACKET_HEADER = b"\x57\xab"
CMD_KEYBOARD = b"\x00\x02"
CMD_MOUSE_REL = b"\x00\x05"
CMD_MEDIA = b"\x00\x03"

# Packet structure offsets
OFFSET_HEADER = 0
OFFSET_CMD = 2
OFFSET_DATA_LEN = 4
OFFSET_DATA = 5

# Keyboard packet structure
KEYBOARD_DATA_LEN = 0x08
KEYBOARD_MODIFIER_OFFSET = 5
KEYBOARD_RESERVED_OFFSET = 6
KEYBOARD_KEY1_OFFSET = 7

# Mouse packet structure
MOUSE_DATA_LEN = 0x05
MOUSE_ADDR = 0x01
MOUSE_BUTTON_OFFSET = 6
MOUSE_X_OFFSET = 7
MOUSE_Y_OFFSET = 8
MOUSE_SCROLL_OFFSET = 9

# Media packet structure
MEDIA_DATA_LEN = 0x04
MEDIA_DATA0_OFFSET = 5
MEDIA_DATA1_OFFSET = 6
MEDIA_DATA2_OFFSET = 7
MEDIA_DATA3_OFFSET = 8
MEDIA_REPORT_ID = 0x02  # Media control report ID (first byte of data)

# USB HID modifier bits
USB_HID_MODIFIER_CTRL = 0x01
USB_HID_MODIFIER_SHIFT = 0x02
USB_HID_MODIFIER_ALT = 0x04
USB_HID_MODIFIER_META = 0x08

# USB HID mouse button bits
USB_HID_BTN_LEFT = 0x01
USB_HID_BTN_RIGHT = 0x02
USB_HID_BTN_MIDDLE = 0x04


# Two's complement helper
def to_twos_complement(value: int, bits: int = 8) -> int:
    """Convert a negative number to two's complement representation."""
    if value < 0:
        return (1 << bits) + value
    return value


class TestCH9329DriverInit:
    """Tests for CH9329Driver initialization."""

    def test_init_with_adapter(self) -> None:
        """Test initializing driver with a communication adapter."""
        mock_adapter = Mock(spec=CommunicationAdapter)
        driver = CH9329Driver(mock_adapter)

        assert driver is not None


class TestCH9329DriverContextManager:
    """Tests for CH9329Driver context manager functionality."""

    def test_context_manager_closes_adapter(self) -> None:
        """Test that context manager closes adapter on exit."""
        mock_adapter = Mock(spec=CommunicationAdapter)
        with CH9329Driver(mock_adapter) as driver:
            assert driver is not None

        mock_adapter.close.assert_called_once()

    def test_close_method_closes_adapter(self) -> None:
        """Test that close() method closes the adapter."""
        mock_adapter = Mock(spec=CommunicationAdapter)
        driver = CH9329Driver(mock_adapter)
        driver.close()

        mock_adapter.close.assert_called_once()


class TestCH9329DriverSendKeyboardInput:
    """Tests for send_keyboard_input() low-level API."""

    def test_empty_state_releases_all_keys(self) -> None:
        """Test that empty state sends all zeros (release packet)."""
        mock_adapter = Mock(spec=CommunicationAdapter)
        driver = CH9329Driver(mock_adapter)

        driver.send_keyboard_input(KeyboardInput())

        assert mock_adapter.send.call_count == 1
        packet = mock_adapter.send.call_args[0][0]

        # Verify packet structure
        expected_packet_len = 14  # header(2) + cmd(2) + len(1) + data(8) + checksum(1)
        assert len(packet) == expected_packet_len
        assert packet[OFFSET_HEADER : OFFSET_HEADER + 2] == PACKET_HEADER
        assert packet[OFFSET_CMD : OFFSET_CMD + 2] == CMD_KEYBOARD
        assert packet[OFFSET_DATA_LEN] == KEYBOARD_DATA_LEN

        # All data bytes should be 0x00 (no modifiers, no keys)
        data_start = OFFSET_DATA
        data_end = data_start + KEYBOARD_DATA_LEN
        assert packet[data_start:data_end] == b"\x00" * KEYBOARD_DATA_LEN

    def test_single_key_without_modifiers(self) -> None:
        """Test sending single key without modifiers."""
        mock_adapter = Mock(spec=CommunicationAdapter)
        driver = CH9329Driver(mock_adapter)

        driver.send_keyboard_input(KeyboardInput(keys=[KeyCode.KEY_A]))

        packet = mock_adapter.send.call_args[0][0]

        # Verify no modifiers
        assert packet[KEYBOARD_MODIFIER_OFFSET] == 0x00
        # Verify reserved byte
        assert packet[KEYBOARD_RESERVED_OFFSET] == 0x00
        # Verify KEY_A in first key slot
        expected_key_a = evdev_to_usb_hid_keyboard(KeyCode.KEY_A.value)
        assert packet[KEYBOARD_KEY1_OFFSET] == expected_key_a

    def test_single_key_with_modifiers(self) -> None:
        """Test sending key with multiple modifiers."""
        mock_adapter = Mock(spec=CommunicationAdapter)
        driver = CH9329Driver(mock_adapter)

        state = KeyboardInput(
            modifiers={ModifierKey.KEY_LEFTCTRL, ModifierKey.KEY_LEFTSHIFT},
            keys=[KeyCode.KEY_A],
        )
        driver.send_keyboard_input(state)

        packet = mock_adapter.send.call_args[0][0]

        # Verify modifiers
        expected_modifiers = USB_HID_MODIFIER_CTRL | USB_HID_MODIFIER_SHIFT
        assert packet[KEYBOARD_MODIFIER_OFFSET] == expected_modifiers

        # Verify key
        expected_key_a = evdev_to_usb_hid_keyboard(KeyCode.KEY_A.value)
        assert packet[KEYBOARD_KEY1_OFFSET] == expected_key_a

    def test_multiple_keys_simultaneously(self) -> None:
        """Test sending multiple keys at once."""
        mock_adapter = Mock(spec=CommunicationAdapter)
        driver = CH9329Driver(mock_adapter)

        keys = [KeyCode.KEY_A, KeyCode.KEY_B, KeyCode.KEY_C]
        driver.send_keyboard_input(KeyboardInput(keys=keys))

        packet = mock_adapter.send.call_args[0][0]

        # Verify keys
        for i, key in enumerate(keys):
            expected_key_code = evdev_to_usb_hid_keyboard(key.value)
            assert packet[KEYBOARD_KEY1_OFFSET + i] == expected_key_code

        # Verify remaining key slots are empty
        for i in range(len(keys), 6):
            assert packet[KEYBOARD_KEY1_OFFSET + i] == 0x00

    def test_maximum_six_keys(self) -> None:
        """Test sending maximum 6 keys at once."""
        mock_adapter = Mock(spec=CommunicationAdapter)
        driver = CH9329Driver(mock_adapter)

        keys = [
            KeyCode.KEY_A,
            KeyCode.KEY_B,
            KeyCode.KEY_C,
            KeyCode.KEY_D,
            KeyCode.KEY_E,
            KeyCode.KEY_F,
        ]
        driver.send_keyboard_input(KeyboardInput(keys=keys))

        packet = mock_adapter.send.call_args[0][0]

        # Verify all 6 key slots are filled
        for i, key in enumerate(keys):
            expected_key_code = evdev_to_usb_hid_keyboard(key.value)
            assert packet[KEYBOARD_KEY1_OFFSET + i] == expected_key_code

    def test_all_modifiers(self) -> None:
        """Test sending all 8 modifiers at once."""
        mock_adapter = Mock(spec=CommunicationAdapter)
        driver = CH9329Driver(mock_adapter)

        all_modifiers = {
            ModifierKey.KEY_LEFTCTRL,
            ModifierKey.KEY_RIGHTCTRL,
            ModifierKey.KEY_LEFTSHIFT,
            ModifierKey.KEY_RIGHTSHIFT,
            ModifierKey.KEY_LEFTALT,
            ModifierKey.KEY_RIGHTALT,
            ModifierKey.KEY_LEFTMETA,
            ModifierKey.KEY_RIGHTMETA,
        }
        driver.send_keyboard_input(KeyboardInput(modifiers=all_modifiers))

        packet = mock_adapter.send.call_args[0][0]

        # Calculate expected modifier byte
        expected_modifier_byte = 0x00
        for modifier in all_modifiers:
            expected_modifier_byte |= evdev_to_usb_hid_modifier(modifier.value)

        assert packet[KEYBOARD_MODIFIER_OFFSET] == expected_modifier_byte


class TestCH9329DriverSendMouseInput:
    """Tests for send_mouse_input() low-level API."""

    def test_empty_state_no_movement(self) -> None:
        """Test that empty state sends no buttons or movement."""
        mock_adapter = Mock(spec=CommunicationAdapter)
        driver = CH9329Driver(mock_adapter)

        driver.send_mouse_input(MouseInput())

        assert mock_adapter.send.call_count == 1
        packet = mock_adapter.send.call_args[0][0]

        # Verify packet structure
        # Packet format: header + cmd + len + addr + data + checksum
        expected_packet_len = 11
        assert len(packet) == expected_packet_len
        assert packet[OFFSET_HEADER : OFFSET_HEADER + 2] == PACKET_HEADER
        assert packet[OFFSET_CMD : OFFSET_CMD + 2] == CMD_MOUSE_REL
        assert packet[OFFSET_DATA_LEN] == MOUSE_DATA_LEN
        assert packet[OFFSET_DATA] == MOUSE_ADDR

        # Verify no buttons, movement, or scroll
        assert packet[MOUSE_BUTTON_OFFSET] == 0x00
        assert packet[MOUSE_X_OFFSET] == 0x00
        assert packet[MOUSE_Y_OFFSET] == 0x00
        assert packet[MOUSE_SCROLL_OFFSET] == 0x00

    def test_movement_only(self) -> None:
        """Test sending only movement."""
        mock_adapter = Mock(spec=CommunicationAdapter)
        driver = CH9329Driver(mock_adapter)

        x_movement = 10
        y_movement = -20
        driver.send_mouse_input(MouseInput(x=x_movement, y=y_movement))

        packet = mock_adapter.send.call_args[0][0]

        # Verify no buttons
        assert packet[MOUSE_BUTTON_OFFSET] == 0x00
        # Verify movement
        assert packet[MOUSE_X_OFFSET] == x_movement
        assert packet[MOUSE_Y_OFFSET] == to_twos_complement(y_movement)

    def test_single_button_no_movement(self) -> None:
        """Test sending single button without movement."""
        mock_adapter = Mock(spec=CommunicationAdapter)
        driver = CH9329Driver(mock_adapter)

        driver.send_mouse_input(MouseInput(buttons={MouseButton.BTN_LEFT}))

        packet = mock_adapter.send.call_args[0][0]

        # Verify left button pressed
        expected_button_byte = evdev_to_usb_hid_mouse(MouseButton.BTN_LEFT.value)
        assert packet[MOUSE_BUTTON_OFFSET] == expected_button_byte
        # Verify no movement
        assert packet[MOUSE_X_OFFSET] == 0x00
        assert packet[MOUSE_Y_OFFSET] == 0x00

    def test_multiple_buttons(self) -> None:
        """Test sending multiple buttons."""
        mock_adapter = Mock(spec=CommunicationAdapter)
        driver = CH9329Driver(mock_adapter)

        buttons = {MouseButton.BTN_LEFT, MouseButton.BTN_RIGHT}
        driver.send_mouse_input(MouseInput(buttons=buttons))

        packet = mock_adapter.send.call_args[0][0]

        # Calculate expected button byte
        expected_button_byte = 0x00
        for button in buttons:
            expected_button_byte |= evdev_to_usb_hid_mouse(button.value)

        assert packet[MOUSE_BUTTON_OFFSET] == expected_button_byte

    def test_button_with_movement(self) -> None:
        """Test sending button with movement."""
        mock_adapter = Mock(spec=CommunicationAdapter)
        driver = CH9329Driver(mock_adapter)

        x_movement = 5
        y_movement = -5
        state = MouseInput(buttons={MouseButton.BTN_LEFT}, x=x_movement, y=y_movement)
        driver.send_mouse_input(state)

        packet = mock_adapter.send.call_args[0][0]

        # Verify button
        expected_button_byte = evdev_to_usb_hid_mouse(MouseButton.BTN_LEFT.value)
        assert packet[MOUSE_BUTTON_OFFSET] == expected_button_byte
        # Verify movement
        assert packet[MOUSE_X_OFFSET] == x_movement
        assert packet[MOUSE_Y_OFFSET] == to_twos_complement(y_movement)

    def test_scroll_only(self) -> None:
        """Test sending only scroll."""
        mock_adapter = Mock(spec=CommunicationAdapter)
        driver = CH9329Driver(mock_adapter)

        scroll_amount = 3
        driver.send_mouse_input(MouseInput(scroll=scroll_amount))

        packet = mock_adapter.send.call_args[0][0]

        # Verify no buttons or movement
        assert packet[MOUSE_BUTTON_OFFSET] == 0x00
        assert packet[MOUSE_X_OFFSET] == 0x00
        assert packet[MOUSE_Y_OFFSET] == 0x00
        # Verify scroll
        assert packet[MOUSE_SCROLL_OFFSET] == scroll_amount

    def test_all_parameters(self) -> None:
        """Test sending all parameters at once."""
        mock_adapter = Mock(spec=CommunicationAdapter)
        driver = CH9329Driver(mock_adapter)

        buttons = {MouseButton.BTN_LEFT, MouseButton.BTN_MIDDLE}
        x_movement = 10
        y_movement = -10
        scroll_amount = 5

        state = MouseInput(
            buttons=buttons,
            x=x_movement,
            y=y_movement,
            scroll=scroll_amount,
        )
        driver.send_mouse_input(state)

        packet = mock_adapter.send.call_args[0][0]

        # Calculate expected button byte
        expected_button_byte = 0x00
        for button in buttons:
            expected_button_byte |= evdev_to_usb_hid_mouse(button.value)

        assert packet[MOUSE_BUTTON_OFFSET] == expected_button_byte
        assert packet[MOUSE_X_OFFSET] == x_movement
        assert packet[MOUSE_Y_OFFSET] == to_twos_complement(y_movement)
        assert packet[MOUSE_SCROLL_OFFSET] == scroll_amount


class TestCH9329DriverSendMediaKeyInput:
    """Tests for send_media_key_input() low-level API."""

    def test_empty_state_releases_all_keys(self) -> None:
        """Test sending empty state releases all media keys."""
        mock_adapter = Mock(spec=CommunicationAdapter)
        driver = CH9329Driver(mock_adapter)

        driver.send_media_key_input(MediaKeyInput(keys=[]))

        assert mock_adapter.send.call_count == 1
        packet = mock_adapter.send.call_args[0][0]

        # Verify packet structure for release
        expected_packet_len = 10  # header(2) + cmd(2) + len(1) + data(4) + checksum(1)
        assert len(packet) == expected_packet_len
        assert packet[OFFSET_HEADER : OFFSET_HEADER + 2] == PACKET_HEADER
        assert packet[OFFSET_CMD : OFFSET_CMD + 2] == CMD_MEDIA
        assert packet[OFFSET_DATA_LEN] == MEDIA_DATA_LEN

        # Verify release packet data (0x02, 0x00, 0x00, 0x00)
        assert packet[MEDIA_DATA0_OFFSET] == MEDIA_REPORT_ID
        assert packet[MEDIA_DATA1_OFFSET] == 0x00
        assert packet[MEDIA_DATA2_OFFSET] == 0x00
        assert packet[MEDIA_DATA3_OFFSET] == 0x00

    def test_mute_key(self) -> None:
        """Test sending mute media key."""
        mock_adapter = Mock(spec=CommunicationAdapter)
        driver = CH9329Driver(mock_adapter)

        driver.send_media_key_input(MediaKeyInput(keys=[MediaKey.KEY_MUTE]))

        assert mock_adapter.send.call_count == 1
        packet = mock_adapter.send.call_args[0][0]

        # Verify packet structure
        expected_packet_len = 10
        assert len(packet) == expected_packet_len
        assert packet[OFFSET_HEADER : OFFSET_HEADER + 2] == PACKET_HEADER
        assert packet[OFFSET_CMD : OFFSET_CMD + 2] == CMD_MEDIA
        assert packet[OFFSET_DATA_LEN] == MEDIA_DATA_LEN

        # Verify media key data
        expected_data = MediaKey.KEY_MUTE.value
        assert packet[MEDIA_DATA0_OFFSET] == expected_data[0]
        assert packet[MEDIA_DATA1_OFFSET] == expected_data[1]
        assert packet[MEDIA_DATA2_OFFSET] == expected_data[2]
        assert packet[MEDIA_DATA3_OFFSET] == expected_data[3]

    def test_volume_up_key(self) -> None:
        """Test sending volume up media key."""
        mock_adapter = Mock(spec=CommunicationAdapter)
        driver = CH9329Driver(mock_adapter)

        driver.send_media_key_input(MediaKeyInput(keys=[MediaKey.KEY_VOLUMEUP]))

        packet = mock_adapter.send.call_args[0][0]

        expected_data = MediaKey.KEY_VOLUMEUP.value
        assert packet[MEDIA_DATA0_OFFSET] == expected_data[0]
        assert packet[MEDIA_DATA1_OFFSET] == expected_data[1]

    def test_volume_down_key(self) -> None:
        """Test sending volume down media key."""
        mock_adapter = Mock(spec=CommunicationAdapter)
        driver = CH9329Driver(mock_adapter)

        driver.send_media_key_input(MediaKeyInput(keys=[MediaKey.KEY_VOLUMEDOWN]))

        packet = mock_adapter.send.call_args[0][0]

        expected_data = MediaKey.KEY_VOLUMEDOWN.value
        assert packet[MEDIA_DATA0_OFFSET] == expected_data[0]
        assert packet[MEDIA_DATA1_OFFSET] == expected_data[1]

    def test_play_pause_key(self) -> None:
        """Test sending play/pause media key."""
        mock_adapter = Mock(spec=CommunicationAdapter)
        driver = CH9329Driver(mock_adapter)

        driver.send_media_key_input(MediaKeyInput(keys=[MediaKey.KEY_PLAYPAUSE]))

        packet = mock_adapter.send.call_args[0][0]

        expected_data = MediaKey.KEY_PLAYPAUSE.value
        assert packet[MEDIA_DATA0_OFFSET] == expected_data[0]
        assert packet[MEDIA_DATA1_OFFSET] == expected_data[1]

    def test_next_track_key(self) -> None:
        """Test sending next track media key."""
        mock_adapter = Mock(spec=CommunicationAdapter)
        driver = CH9329Driver(mock_adapter)

        driver.send_media_key_input(MediaKeyInput(keys=[MediaKey.KEY_NEXTSONG]))

        packet = mock_adapter.send.call_args[0][0]

        expected_data = MediaKey.KEY_NEXTSONG.value
        assert packet[MEDIA_DATA0_OFFSET] == expected_data[0]
        assert packet[MEDIA_DATA1_OFFSET] == expected_data[1]

    def test_prev_track_key(self) -> None:
        """Test sending previous track media key."""
        mock_adapter = Mock(spec=CommunicationAdapter)
        driver = CH9329Driver(mock_adapter)

        driver.send_media_key_input(MediaKeyInput(keys=[MediaKey.KEY_PREVIOUSSONG]))

        packet = mock_adapter.send.call_args[0][0]

        expected_data = MediaKey.KEY_PREVIOUSSONG.value
        assert packet[MEDIA_DATA0_OFFSET] == expected_data[0]
        assert packet[MEDIA_DATA1_OFFSET] == expected_data[1]
