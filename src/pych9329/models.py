"""Data models for CH9329 USB HID device.

This module contains enums and functions for representing keyboard keys,
mouse buttons, media keys, and character-to-keycode mappings.
"""

from enum import Enum


class MouseButton(Enum):
    """Mouse button constants for CH9329 device.

    These values are used in mouse click and press operations.
    """

    LEFT = 0x01
    RIGHT = 0x02
    MIDDLE = 0x04


class ModifierKey(Enum):
    """Keyboard modifier key constants.

    These values represent modifier key states in the HID protocol.
    """

    CTRL = 0x01
    SHIFT = 0x02
    ALT = 0x04
    WINDOWS = 0x08


class KeyCode(Enum):
    """Keyboard key codes for CH9329 device.

    These are USB HID keyboard scan codes.
    """

    # Special keys
    ENTER = 0x28
    ESC = 0x29
    BACKSPACE = 0x2A
    TAB = 0x2B
    SPACE = 0x2C
    ZENHAN = 0x35

    # Digit keys
    DIGIT_0 = 0x27
    DIGIT_1 = 0x1E
    DIGIT_2 = 0x1F
    DIGIT_3 = 0x20
    DIGIT_4 = 0x21
    DIGIT_5 = 0x22
    DIGIT_6 = 0x23
    DIGIT_7 = 0x24
    DIGIT_8 = 0x25
    DIGIT_9 = 0x26

    # Letter keys (A-Z)
    A = 0x04
    B = 0x05
    C = 0x06
    D = 0x07
    E = 0x08
    F = 0x09
    G = 0x0A
    H = 0x0B
    I = 0x0C  # noqa: E741
    J = 0x0D
    K = 0x0E
    L = 0x0F
    M = 0x10
    N = 0x11
    O = 0x12  # noqa: E741
    P = 0x13
    Q = 0x14
    R = 0x15
    S = 0x16
    T = 0x17
    U = 0x18
    V = 0x19
    W = 0x1A
    X = 0x1B
    Y = 0x1C
    Z = 0x1D

    # Symbol keys
    MINUS = 0x2D
    EQUAL = 0x2E
    LEFT_BRACKET = 0x2F
    RIGHT_BRACKET = 0x30
    BACKSLASH = 0x31
    SEMICOLON = 0x33
    APOSTROPHE = 0x34
    COMMA = 0x36
    PERIOD = 0x37
    SLASH = 0x38
    YEN = 0x87
    INTL_YEN = 0x89


class MediaKey(Enum):
    """Media control key constants.

    Values are tuples of (byte1, byte2, byte3, byte4) that represent
    the media control packet data.
    """

    EJECT = (0x02, 0x80, 0x00, 0x00)
    CD_STOP = (0x02, 0x40, 0x00, 0x00)
    PREV_TRACK = (0x02, 0x20, 0x00, 0x00)
    NEXT_TRACK = (0x02, 0x10, 0x00, 0x00)
    PLAY_PAUSE = (0x02, 0x08, 0x00, 0x00)
    MUTE = (0x02, 0x04, 0x00, 0x00)
    VOLUME_DOWN = (0x02, 0x02, 0x00, 0x00)
    VOLUME_UP = (0x02, 0x01, 0x00, 0x00)


def _build_character_map() -> dict[str, tuple[int, int]]:
    """Build the character to (modifier, keycode) mapping table."""
    char_map: dict[str, tuple[int, int]] = {
        # Symbols without shift
        "-": (0x00, KeyCode.MINUS.value),
        "=": (0x00, KeyCode.EQUAL.value),
        "[": (0x00, KeyCode.LEFT_BRACKET.value),
        "]": (0x00, KeyCode.RIGHT_BRACKET.value),
        ";": (0x00, KeyCode.SEMICOLON.value),
        "'": (0x00, KeyCode.APOSTROPHE.value),
        "`": (0x00, KeyCode.ZENHAN.value),
        ",": (0x00, KeyCode.COMMA.value),
        ".": (0x00, KeyCode.PERIOD.value),
        "/": (0x00, KeyCode.SLASH.value),
        " ": (0x00, KeyCode.SPACE.value),
        # Japanese layout specific
        "@": (0x00, KeyCode.LEFT_BRACKET.value),  # Shift+2 on US, but not on JP
        "^": (0x00, KeyCode.EQUAL.value),
        "\\": (0x00, KeyCode.INTL_YEN.value),
        "_": (0x00, KeyCode.YEN.value),
    }

    # Digits 0-9
    for i in range(10):
        char_map[str(i)] = (0x00, getattr(KeyCode, f"DIGIT_{i}").value)

    # Letters a-z and A-Z
    for _, char_code in enumerate(range(ord("a"), ord("z") + 1)):
        char = chr(char_code)
        keycode = getattr(KeyCode, char.upper()).value
        char_map[char] = (0x00, keycode)
        char_map[char.upper()] = (ModifierKey.SHIFT.value, keycode)

    # Symbols with shift
    shifted_symbols = {
        "!": "1",
        "\"'": "2",
        "#": "3",
        "$": "4",
        "%": "5",
        "&": "6",
        "'": "7",
        "(": "8",
        ")": "9",
        "~": "=",
        "|": "\\",
        "{": "[",
        "}": "]",
        "+": ";",
        "*": ":",
        "<": ",",
        ">": ".",
        "?": "/",
    }
    for symbol, base_char in shifted_symbols.items():
        if base_char in char_map:
            _, keycode = char_map[base_char]
            char_map[symbol] = (ModifierKey.SHIFT.value, keycode)

    return char_map


# Character to (modifier, keycode) mapping table
_CHARACTER_MAP = _build_character_map()


def get_key_mapping(char: str) -> tuple[int, int]:
    """Get the modifier and keycode for a character.

    Args:
        char: A single character to map to keyboard input.

    Returns:
        A tuple of (modifier, keycode) where:
            - modifier: Modifier key byte (0x00 for none, 0x02 for shift)
            - keycode: USB HID keycode for the key

    Raises:
        ValueError: If the character is not supported.

    Examples:
        >>> get_key_mapping('a')
        (0, 4)
        >>> get_key_mapping('A')
        (2, 4)
        >>> get_key_mapping('!')
        (2, 30)
    """
    if char not in _CHARACTER_MAP:
        msg = f"Unsupported character: {char!r}"
        raise ValueError(msg)
    return _CHARACTER_MAP[char]
