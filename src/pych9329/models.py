"""Data models for CH9329 USB HID device.

This module contains enums and functions for representing keyboard keys,
mouse buttons, media keys, and character-to-keycode mappings.

All key and button codes follow the Linux evdev naming convention.
"""

from dataclasses import dataclass, field
from enum import Enum

from evdev import ecodes

MAX_ROLLOVER_KEYS = 6


class MouseButton(Enum):
    """Mouse button constants for CH9329 device.

    These values follow evdev button code naming and values.
    """

    BTN_LEFT = ecodes.BTN_LEFT
    BTN_RIGHT = ecodes.BTN_RIGHT
    BTN_MIDDLE = ecodes.BTN_MIDDLE


class ModifierKey(Enum):
    """Keyboard modifier key constants.

    These values follow evdev key code naming and values.
    """

    KEY_LEFTCTRL = ecodes.KEY_LEFTCTRL
    KEY_RIGHTCTRL = ecodes.KEY_RIGHTCTRL
    KEY_LEFTSHIFT = ecodes.KEY_LEFTSHIFT
    KEY_RIGHTSHIFT = ecodes.KEY_RIGHTSHIFT
    KEY_LEFTALT = ecodes.KEY_LEFTALT
    KEY_RIGHTALT = ecodes.KEY_RIGHTALT
    KEY_LEFTMETA = ecodes.KEY_LEFTMETA  # Windows key
    KEY_RIGHTMETA = ecodes.KEY_RIGHTMETA


class KeyCode(Enum):
    """Keyboard key codes for CH9329 device.

    These values follow evdev key code naming and values.
    """

    # Special keys
    KEY_ENTER = ecodes.KEY_ENTER
    KEY_ESC = ecodes.KEY_ESC
    KEY_BACKSPACE = ecodes.KEY_BACKSPACE
    KEY_TAB = ecodes.KEY_TAB
    KEY_SPACE = ecodes.KEY_SPACE
    KEY_GRAVE = ecodes.KEY_GRAVE  # ZENHAN key

    # Digit keys
    KEY_0 = ecodes.KEY_0
    KEY_1 = ecodes.KEY_1
    KEY_2 = ecodes.KEY_2
    KEY_3 = ecodes.KEY_3
    KEY_4 = ecodes.KEY_4
    KEY_5 = ecodes.KEY_5
    KEY_6 = ecodes.KEY_6
    KEY_7 = ecodes.KEY_7
    KEY_8 = ecodes.KEY_8
    KEY_9 = ecodes.KEY_9

    # Letter keys (A-Z)
    KEY_A = ecodes.KEY_A
    KEY_B = ecodes.KEY_B
    KEY_C = ecodes.KEY_C
    KEY_D = ecodes.KEY_D
    KEY_E = ecodes.KEY_E
    KEY_F = ecodes.KEY_F
    KEY_G = ecodes.KEY_G
    KEY_H = ecodes.KEY_H
    KEY_I = ecodes.KEY_I
    KEY_J = ecodes.KEY_J
    KEY_K = ecodes.KEY_K
    KEY_L = ecodes.KEY_L
    KEY_M = ecodes.KEY_M
    KEY_N = ecodes.KEY_N
    KEY_O = ecodes.KEY_O
    KEY_P = ecodes.KEY_P
    KEY_Q = ecodes.KEY_Q
    KEY_R = ecodes.KEY_R
    KEY_S = ecodes.KEY_S
    KEY_T = ecodes.KEY_T
    KEY_U = ecodes.KEY_U
    KEY_V = ecodes.KEY_V
    KEY_W = ecodes.KEY_W
    KEY_X = ecodes.KEY_X
    KEY_Y = ecodes.KEY_Y
    KEY_Z = ecodes.KEY_Z

    # Symbol keys
    KEY_MINUS = ecodes.KEY_MINUS
    KEY_EQUAL = ecodes.KEY_EQUAL
    KEY_LEFTBRACE = ecodes.KEY_LEFTBRACE
    KEY_RIGHTBRACE = ecodes.KEY_RIGHTBRACE
    KEY_BACKSLASH = ecodes.KEY_BACKSLASH
    KEY_SEMICOLON = ecodes.KEY_SEMICOLON
    KEY_APOSTROPHE = ecodes.KEY_APOSTROPHE
    KEY_COMMA = ecodes.KEY_COMMA
    KEY_DOT = ecodes.KEY_DOT
    KEY_SLASH = ecodes.KEY_SLASH
    KEY_YEN = ecodes.KEY_YEN
    KEY_RO = ecodes.KEY_RO


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
    """Build the character to (evdev modifier, evdev keycode) mapping table."""
    char_map: dict[str, tuple[int, int]] = {
        # Symbols without shift
        "-": (0x00, KeyCode.KEY_MINUS.value),
        "=": (0x00, KeyCode.KEY_EQUAL.value),
        "[": (0x00, KeyCode.KEY_LEFTBRACE.value),
        "]": (0x00, KeyCode.KEY_RIGHTBRACE.value),
        ";": (0x00, KeyCode.KEY_SEMICOLON.value),
        "'": (0x00, KeyCode.KEY_APOSTROPHE.value),
        "`": (0x00, KeyCode.KEY_GRAVE.value),
        ",": (0x00, KeyCode.KEY_COMMA.value),
        ".": (0x00, KeyCode.KEY_DOT.value),
        "/": (0x00, KeyCode.KEY_SLASH.value),
        " ": (0x00, KeyCode.KEY_SPACE.value),
        "@": (0x00, KeyCode.KEY_LEFTBRACE.value),
        "^": (0x00, KeyCode.KEY_EQUAL.value),
        "\\": (0x00, KeyCode.KEY_YEN.value),
        "_": (0x02, KeyCode.KEY_YEN.value),
    }

    # Digits 0-9
    for i in range(10):
        char_map[str(i)] = (0x00, getattr(KeyCode, f"KEY_{i}").value)

    # Letters a-z and A-Z
    for _, char_code in enumerate(range(ord("a"), ord("z") + 1)):
        char = chr(char_code)
        keycode = getattr(KeyCode, f"KEY_{char.upper()}").value
        char_map[char] = (0x00, keycode)
        char_map[char.upper()] = (ModifierKey.KEY_LEFTSHIFT.value, keycode)

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
            char_map[symbol] = (ModifierKey.KEY_LEFTSHIFT.value, keycode)

    return char_map


# Character to (modifier, keycode) mapping table
_CHARACTER_MAP = _build_character_map()


def get_key_mapping(char: str) -> tuple[int, int]:
    """Get the evdev modifier and keycode for a character.

    Args:
        char: A single character to map to keyboard input.

    Returns:
        A tuple of (modifier, keycode) where:
            - modifier: evdev modifier key code (0x00 for none)
            - keycode: evdev key code for the key

    Raises:
        ValueError: If the character is not supported.

    Examples:
        >>> get_key_mapping('a')
        (0, 30)
        >>> get_key_mapping('A')  # doctest: +SKIP
        (42, 30)
        >>> get_key_mapping('!')  # doctest: +SKIP
        (42, 2)
    """
    if char not in _CHARACTER_MAP:
        msg = f"Unsupported character: {char!r}"
        raise ValueError(msg)
    return _CHARACTER_MAP[char]


@dataclass
class KeyboardState:
    """Represents the complete state of keyboard input for CH9329.

    This model directly corresponds to the USB HID keyboard packet structure,
    which supports up to 8 modifier keys and 6 simultaneous regular keys.

    Args:
        modifiers: Set of modifier keys (Ctrl, Shift, Alt, Meta).
        keys: List of regular keys (maximum 6 keys).

    Raises:
        ValueError: If more than 6 keys are provided.

    Examples:
        >>> # Single key with modifiers
        >>> state = KeyboardState(
        ...     modifiers={ModifierKey.KEY_LEFTCTRL, ModifierKey.KEY_LEFTSHIFT},
        ...     keys=[KeyCode.KEY_A]
        ... )
        >>> # Multiple keys pressed simultaneously
        >>> state = KeyboardState(
        ...     modifiers={ModifierKey.KEY_LEFTSHIFT},
        ...     keys=[KeyCode.KEY_A, KeyCode.KEY_B, KeyCode.KEY_C]
        ... )
        >>> # Maximum 6 keys
        >>> state = KeyboardState(
        ...     keys=[KeyCode.KEY_A, KeyCode.KEY_B, KeyCode.KEY_C,
        ...           KeyCode.KEY_D, KeyCode.KEY_E, KeyCode.KEY_F]
        ... )
    """

    modifiers: set[ModifierKey] = field(default_factory=set)
    keys: list[KeyCode] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate keyboard state constraints.

        Raises:
            ValueError: If more than 6 keys are provided.
        """
        if len(self.keys) > MAX_ROLLOVER_KEYS:
            msg = f"Maximum {MAX_ROLLOVER_KEYS} keys allowed, got {len(self.keys)}"
            raise ValueError(msg)
