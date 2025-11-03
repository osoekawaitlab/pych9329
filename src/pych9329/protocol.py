"""CH9329 protocol packet building.

This module contains the protocol layer for building packets that the CH9329
device understands. All packet building logic is isolated here for easier testing
and maintenance.
"""


class CH9329Protocol:
    """Protocol handler for CH9329 USB HID device.

    This class provides static methods for building various types of packets
    that can be sent to the CH9329 device. All methods return bytes objects
    that can be directly sent over serial communication.

    Packet structure:
        - Header: 2 bytes (0x57, 0xAB)
        - Address: 1 byte (0x00)
        - Command: 1 byte (varies by packet type)
        - Length: 1 byte (length of data section)
        - Data: variable length (depends on command)
        - Checksum: 1 byte (sum of all previous bytes & 0xFF)
    """

    # Protocol constants
    _HEADER = (0x57, 0xAB)
    _ADDRESS = 0x00

    # Command codes
    _CMD_KEYBOARD = 0x02
    _CMD_MEDIA = 0x03
    _CMD_MOUSE_ABS = 0x04
    _CMD_MOUSE_REL = 0x05

    @staticmethod
    def _calculate_checksum(data: list[int]) -> int:
        """Calculate checksum for a packet.

        Args:
            data: List of bytes to calculate checksum for.

        Returns:
            Checksum value (sum of all bytes & 0xFF).
        """
        return sum(data) & 0xFF

    @staticmethod
    def _build_packet(command: int, data: list[int]) -> bytes:
        """Build a complete packet with header, command, data, and checksum.

        Args:
            command: Command byte for the packet.
            data: Data bytes for the packet.

        Returns:
            Complete packet as bytes object.
        """
        packet = [
            *CH9329Protocol._HEADER,
            CH9329Protocol._ADDRESS,
            command,
            len(data),
            *data,
        ]
        checksum = CH9329Protocol._calculate_checksum(packet)
        packet.append(checksum)
        return bytes(packet)

    @staticmethod
    def build_keyboard_press_packet(modifier: int, keycode: int) -> bytes:
        r"""Build a keyboard key press packet.

        Args:
            modifier: Modifier key byte (0x00 for none, 0x01 for ctrl,
                      0x02 for shift, 0x04 for alt, 0x08 for windows).
            keycode: USB HID keycode for the key to press.

        Returns:
            Keyboard press packet as bytes.

        Examples:
            >>> CH9329Protocol.build_keyboard_press_packet(0x02, 0x04)
            b'W\xab\x00\x02\x08\x02\x00\x04\x00\x00\x00\x00\x00\x10'
        """
        data = [modifier, 0x00, keycode, 0x00, 0x00, 0x00, 0x00, 0x00]
        return CH9329Protocol._build_packet(CH9329Protocol._CMD_KEYBOARD, data)

    @staticmethod
    def build_keyboard_release_packet() -> bytes:
        r"""Build a keyboard key release packet.

        This packet releases all pressed keys.

        Returns:
            Keyboard release packet as bytes.

        Examples:
            >>> CH9329Protocol.build_keyboard_release_packet()
            b'W\xab\x00\x02\x08\x00\x00\x00\x00\x00\x00\x00\x00\x0c'
        """
        data = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        return CH9329Protocol._build_packet(CH9329Protocol._CMD_KEYBOARD, data)

    @staticmethod
    def build_mouse_abs_packet(button: int, x: int, y: int) -> bytes:
        r"""Build a mouse absolute position packet.

        Args:
            button: Button state byte (0x00 for none, 0x01 for left,
                    0x02 for right, 0x04 for middle).
            x: Absolute X coordinate (0-4095).
            y: Absolute Y coordinate (0-4095).

        Returns:
            Mouse absolute position packet as bytes.

        Examples:
            >>> CH9329Protocol.build_mouse_abs_packet(0x00, 0, 0)
            b'W\xab\x00\x04\x07\x02\x00\x00\x00\x00\x00\x00\x10'
        """
        # Clamp coordinates to valid range
        x = max(0, min(4095, x))
        y = max(0, min(4095, y))

        x_low = x & 0xFF
        x_high = (x >> 8) & 0xFF
        y_low = y & 0xFF
        y_high = (y >> 8) & 0xFF

        data = [0x02, button, x_low, x_high, y_low, y_high, 0x00]
        return CH9329Protocol._build_packet(CH9329Protocol._CMD_MOUSE_ABS, data)

    @staticmethod
    def build_mouse_rel_packet(button: int, x: int, y: int, scroll: int) -> bytes:
        r"""Build a mouse relative movement packet.

        Args:
            button: Button state byte (0x00 for none, 0x01 for left,
                    0x02 for right, 0x04 for middle).
            x: Relative X movement (-127 to 127).
            y: Relative Y movement (-127 to 127).
            scroll: Scroll wheel movement (-127 to 127).

        Returns:
            Mouse relative movement packet as bytes.

        Examples:
            >>> CH9329Protocol.build_mouse_rel_packet(0x00, 10, 20, 0)
            b'W\xab\x00\x05\x05\x01\x00\n\x14\x00+'
        """
        # Clamp values to valid range
        x = max(-128, min(127, x))
        y = max(-128, min(127, y))
        scroll = max(-127, min(127, scroll))

        # Convert negative values to two's complement
        x_byte = x if x >= 0 else 0x100 + x
        y_byte = y if y >= 0 else 0x100 + y
        scroll_byte = scroll if scroll >= 0 else 0x100 + scroll

        data = [0x01, button, x_byte, y_byte, scroll_byte]
        return CH9329Protocol._build_packet(CH9329Protocol._CMD_MOUSE_REL, data)

    @staticmethod
    def build_media_press_packet(
        data0: int, data1: int, data2: int, data3: int
    ) -> bytes:
        r"""Build a media key press packet.

        Args:
            data0: First data byte (usually 0x02).
            data1: Second data byte (media key code).
            data2: Third data byte (usually 0x00).
            data3: Fourth data byte (usually 0x00).

        Returns:
            Media key press packet as bytes.

        Examples:
            >>> CH9329Protocol.build_media_press_packet(0x02, 0x04, 0x00, 0x00)
            b'W\xab\x00\x03\x04\x02\x04\x00\x00\x11'
        """
        data = [data0, data1, data2, data3]
        return CH9329Protocol._build_packet(CH9329Protocol._CMD_MEDIA, data)

    @staticmethod
    def build_media_release_packet() -> bytes:
        r"""Build a media key release packet.

        This packet releases all pressed media keys.

        Returns:
            Media key release packet as bytes.

        Examples:
            >>> CH9329Protocol.build_media_release_packet()
            b'W\xab\x00\x03\x04\x02\x00\x00\x00\x0b'
        """
        data = [0x02, 0x00, 0x00, 0x00]
        return CH9329Protocol._build_packet(CH9329Protocol._CMD_MEDIA, data)
