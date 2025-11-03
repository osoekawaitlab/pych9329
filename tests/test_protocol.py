"""Tests for CH9329 protocol packet building."""

from pych9329.protocol import CH9329Protocol


class TestKeyboardPackets:
    """Tests for keyboard packet building."""

    def test_build_keyboard_press_packet(self) -> None:
        """Test building a keyboard key press packet."""
        # Press 'A' key (keycode 0x04) with shift (modifier 0x02)
        packet = CH9329Protocol.build_keyboard_press_packet(0x02, 0x04)

        # Expected packet structure:
        # Header: 0x57, 0xAB
        # Address: 0x00
        # Command: 0x02
        # Length: 0x08
        # Data: modifier, 0x00, keycode, 0x00, 0x00, 0x00, 0x00, 0x00
        # Checksum
        expected = bytes(
            [
                0x57,
                0xAB,
                0x00,
                0x02,
                0x08,
                0x02,
                0x00,
                0x04,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x12,  # checksum: sum of all previous bytes & 0xFF
            ]
        )
        assert packet == expected

    def test_build_keyboard_press_packet_no_modifier(self) -> None:
        """Test building a keyboard key press packet without modifier."""
        # Press 'a' key (keycode 0x04) without shift (modifier 0x00)
        packet = CH9329Protocol.build_keyboard_press_packet(0x00, 0x04)

        expected = bytes(
            [
                0x57,
                0xAB,
                0x00,
                0x02,
                0x08,
                0x00,
                0x00,
                0x04,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x10,  # checksum
            ]
        )
        assert packet == expected

    def test_build_keyboard_release_packet(self) -> None:
        """Test building a keyboard key release packet."""
        packet = CH9329Protocol.build_keyboard_release_packet()

        # Release packet has all zeros in data section
        expected = bytes(
            [
                0x57,
                0xAB,
                0x00,
                0x02,
                0x08,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x0C,  # checksum
            ]
        )
        assert packet == expected


class TestMouseAbsolutePackets:
    """Tests for mouse absolute movement packet building."""

    def test_build_mouse_abs_packet_origin(self) -> None:
        """Test building a mouse absolute move packet to origin."""
        # Move to (0, 0) with no button pressed
        packet = CH9329Protocol.build_mouse_abs_packet(0x00, 0, 0)

        # Expected packet structure:
        # Header: 0x57, 0xAB
        # Address: 0x00
        # Command: 0x04
        # Length: 0x07
        # Data: 0x02, button, x_low, x_high, y_low, y_high, 0x00
        # Checksum
        expected = bytes(
            [
                0x57,
                0xAB,
                0x00,
                0x04,
                0x07,
                0x02,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x0F,  # checksum
            ]
        )
        assert packet == expected

    def test_build_mouse_abs_packet_mid_screen(self) -> None:
        """Test building a mouse absolute move packet to middle of screen."""
        # Move to middle (x=2048, y=2048) - halfway through 4096 range
        packet = CH9329Protocol.build_mouse_abs_packet(0x00, 2048, 2048)

        # 2048 = 0x0800, so x_low=0x00, x_high=0x08
        expected = bytes(
            [
                0x57,
                0xAB,
                0x00,
                0x04,
                0x07,
                0x02,
                0x00,
                0x00,
                0x08,
                0x00,
                0x08,
                0x00,
                0x1F,  # checksum
            ]
        )
        assert packet == expected

    def test_build_mouse_abs_packet_with_button(self) -> None:
        """Test building a mouse absolute move packet with button pressed."""
        # Move to (0, 0) with left button pressed (0x01)
        packet = CH9329Protocol.build_mouse_abs_packet(0x01, 0, 0)

        expected = bytes(
            [
                0x57,
                0xAB,
                0x00,
                0x04,
                0x07,
                0x02,
                0x01,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x10,  # checksum
            ]
        )
        assert packet == expected


class TestMouseRelativePackets:
    """Tests for mouse relative movement packet building."""

    def test_build_mouse_rel_packet_no_movement(self) -> None:
        """Test building a mouse relative move packet with no movement."""
        packet = CH9329Protocol.build_mouse_rel_packet(0x00, 0, 0, 0)

        # Expected packet structure:
        # Header: 0x57, 0xAB
        # Address: 0x00
        # Command: 0x05
        # Length: 0x05
        # Data: 0x01, button, x, y, scroll
        # Checksum
        expected = bytes(
            [
                0x57,
                0xAB,
                0x00,
                0x05,
                0x05,
                0x01,
                0x00,
                0x00,
                0x00,
                0x00,
                0x0D,  # checksum
            ]
        )
        assert packet == expected

    def test_build_mouse_rel_packet_positive_movement(self) -> None:
        """Test building a mouse relative move packet with positive movement."""
        # Move right 10, down 20
        packet = CH9329Protocol.build_mouse_rel_packet(0x00, 10, 20, 0)

        expected = bytes(
            [
                0x57,
                0xAB,
                0x00,
                0x05,
                0x05,
                0x01,
                0x00,
                0x0A,
                0x14,
                0x00,
                0x2B,  # checksum
            ]
        )
        assert packet == expected

    def test_build_mouse_rel_packet_negative_movement(self) -> None:
        """Test building a mouse relative move packet with negative movement."""
        # Move left 10 (-10 = 0x100 - 10 = 246), up 20 (-20 = 0x100 - 20 = 236)
        packet = CH9329Protocol.build_mouse_rel_packet(0x00, -10, -20, 0)

        expected = bytes(
            [
                0x57,
                0xAB,
                0x00,
                0x05,
                0x05,
                0x01,
                0x00,
                0xF6,
                0xEC,
                0x00,
                0xEF,  # checksum
            ]
        )
        assert packet == expected

    def test_build_mouse_rel_packet_with_scroll(self) -> None:
        """Test building a mouse relative move packet with scroll."""
        # No movement, scroll up by 5
        packet = CH9329Protocol.build_mouse_rel_packet(0x00, 0, 0, 5)

        expected = bytes(
            [
                0x57,
                0xAB,
                0x00,
                0x05,
                0x05,
                0x01,
                0x00,
                0x00,
                0x00,
                0x05,
                0x12,  # checksum
            ]
        )
        assert packet == expected

    def test_build_mouse_rel_packet_negative_scroll(self) -> None:
        """Test building a mouse relative move packet with negative scroll."""
        # No movement, scroll down by 5 (-5 = 0x100 - 5 = 251)
        packet = CH9329Protocol.build_mouse_rel_packet(0x00, 0, 0, -5)

        expected = bytes(
            [
                0x57,
                0xAB,
                0x00,
                0x05,
                0x05,
                0x01,
                0x00,
                0x00,
                0x00,
                0xFB,
                0x08,  # checksum
            ]
        )
        assert packet == expected

    def test_build_mouse_rel_packet_with_button(self) -> None:
        """Test building a mouse relative move packet with button."""
        # Left button pressed, no movement
        packet = CH9329Protocol.build_mouse_rel_packet(0x01, 0, 0, 0)

        expected = bytes(
            [
                0x57,
                0xAB,
                0x00,
                0x05,
                0x05,
                0x01,
                0x01,
                0x00,
                0x00,
                0x00,
                0x0E,  # checksum
            ]
        )
        assert packet == expected


class TestMediaPackets:
    """Tests for media key packet building."""

    def test_build_media_press_packet_mute(self) -> None:
        """Test building a media key press packet for mute."""
        packet = CH9329Protocol.build_media_press_packet(0x02, 0x04, 0x00, 0x00)

        # Expected packet structure:
        # Header: 0x57, 0xAB
        # Address: 0x00
        # Command: 0x03
        # Length: 0x04
        # Data: 0x02, 0x04, 0x00, 0x00
        # Checksum
        expected = bytes(
            [
                0x57,
                0xAB,
                0x00,
                0x03,
                0x04,
                0x02,
                0x04,
                0x00,
                0x00,
                0x0F,  # checksum
            ]
        )
        assert packet == expected

    def test_build_media_press_packet_volume_up(self) -> None:
        """Test building a media key press packet for volume up."""
        packet = CH9329Protocol.build_media_press_packet(0x02, 0x01, 0x00, 0x00)

        expected = bytes(
            [
                0x57,
                0xAB,
                0x00,
                0x03,
                0x04,
                0x02,
                0x01,
                0x00,
                0x00,
                0x0C,  # checksum
            ]
        )
        assert packet == expected

    def test_build_media_release_packet(self) -> None:
        """Test building a media key release packet."""
        packet = CH9329Protocol.build_media_release_packet()

        # Release packet has all zeros in data section
        expected = bytes(
            [
                0x57,
                0xAB,
                0x00,
                0x03,
                0x04,
                0x02,
                0x00,
                0x00,
                0x00,
                0x0B,  # checksum
            ]
        )
        assert packet == expected


class TestPacketValidation:
    """Tests for packet validation."""

    def test_keyboard_packet_length(self) -> None:
        """Test that keyboard packets have correct length."""
        packet = CH9329Protocol.build_keyboard_press_packet(0x00, 0x04)
        assert (
            len(packet) == 14
        )  # Header(2) + Addr(1) + Cmd(1) + Len(1) + Data(8) + Checksum(1)

    def test_mouse_abs_packet_length(self) -> None:
        """Test that mouse absolute packets have correct length."""
        packet = CH9329Protocol.build_mouse_abs_packet(0x00, 0, 0)
        assert (
            len(packet) == 13
        )  # Header(2) + Addr(1) + Cmd(1) + Len(1) + Data(7) + Checksum(1)

    def test_mouse_rel_packet_length(self) -> None:
        """Test that mouse relative packets have correct length."""
        packet = CH9329Protocol.build_mouse_rel_packet(0x00, 0, 0, 0)
        assert (
            len(packet) == 11
        )  # Header(2) + Addr(1) + Cmd(1) + Len(1) + Data(5) + Checksum(1)

    def test_media_packet_length(self) -> None:
        """Test that media packets have correct length."""
        packet = CH9329Protocol.build_media_press_packet(0x02, 0x04, 0x00, 0x00)
        assert (
            len(packet) == 10
        )  # Header(2) + Addr(1) + Cmd(1) + Len(1) + Data(4) + Checksum(1)
