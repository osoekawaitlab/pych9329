"""Data models for CH9329 USB HID device.

This module contains enums and functions for representing keyboard keys,
mouse buttons, media keys, and character-to-keycode mappings.

All key and button codes follow the Linux evdev naming convention.
"""

from enum import Enum

from evdev import ecodes
from pydantic import BaseModel, Field

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

    These values follow evdev key code naming convention.
    Values are tuples of (byte1, byte2, byte3, byte4) that represent
    the media control packet data.
    """

    KEY_EJECTCD = (0x02, 0x80, 0x00, 0x00)
    KEY_STOPCD = (0x02, 0x40, 0x00, 0x00)
    KEY_PREVIOUSSONG = (0x02, 0x20, 0x00, 0x00)
    KEY_NEXTSONG = (0x02, 0x10, 0x00, 0x00)
    KEY_PLAYPAUSE = (0x02, 0x08, 0x00, 0x00)
    KEY_MUTE = (0x02, 0x04, 0x00, 0x00)
    KEY_VOLUMEDOWN = (0x02, 0x02, 0x00, 0x00)
    KEY_VOLUMEUP = (0x02, 0x01, 0x00, 0x00)


class BaseCh9329Model(BaseModel):
    """Base model for CH9329 input models.

    Configured to use enum values directly during serialization.
    """


class KeyboardInput(BaseCh9329Model):
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
        >>> state = KeyboardInput(
        ...     modifiers={ModifierKey.KEY_LEFTCTRL, ModifierKey.KEY_LEFTSHIFT},
        ...     keys=[KeyCode.KEY_A]
        ... )
        >>> # Multiple keys pressed simultaneously
        >>> state = KeyboardInput(
        ...     modifiers={ModifierKey.KEY_LEFTSHIFT},
        ...     keys=[KeyCode.KEY_A, KeyCode.KEY_B, KeyCode.KEY_C]
        ... )
        >>> # Maximum 6 keys
        >>> state = KeyboardInput(
        ...     keys=[KeyCode.KEY_A, KeyCode.KEY_B, KeyCode.KEY_C,
        ...           KeyCode.KEY_D, KeyCode.KEY_E, KeyCode.KEY_F]
        ... )
    """

    modifiers: set[ModifierKey] = Field(default_factory=set)
    keys: list[KeyCode] = Field(default_factory=list, max_length=MAX_ROLLOVER_KEYS)


class MouseInput(BaseCh9329Model):
    """Represents the complete state of mouse input for CH9329.

    This model corresponds to the USB HID mouse relative movement packet,
    which supports multiple simultaneous button presses, relative movement,
    and scroll wheel input.

    Args:
        buttons: Set of mouse buttons currently pressed.
        x: Relative X movement (-128 to 127).
        y: Relative Y movement (-128 to 127).
        scroll: Scroll wheel movement (-127 to 127).

    Raises:
        ValueError: If movement or scroll values are out of range.

    Examples:
        >>> # Move right and down
        >>> state = MouseInput(x=10, y=10)
        >>> # Left button pressed while moving
        >>> state = MouseInput(
        ...     buttons={MouseButton.BTN_LEFT},
        ...     x=5,
        ...     y=-5
        ... )
        >>> # Multiple buttons with scroll
        >>> state = MouseInput(
        ...     buttons={MouseButton.BTN_LEFT, MouseButton.BTN_RIGHT},
        ...     scroll=3
        ... )
        >>> # Release all buttons (no movement)
        >>> state = MouseInput()
    """

    buttons: set[MouseButton] = Field(default_factory=set)
    x: int = Field(default=0, ge=-128, le=127)
    y: int = Field(default=0, ge=-128, le=127)
    scroll: int = Field(default=0, ge=-127, le=127)


class MediaKeyInput(BaseCh9329Model):
    """Represents media key input for CH9329.

    This model corresponds to the USB HID media control packet. Unlike keyboard
    input which supports 6 simultaneous keys, media keys only support single
    key press at a time.

    Args:
        keys: List of media keys (maximum 1 key). Empty list releases all keys.

    Raises:
        ValueError: If more than 1 key is provided.

    Examples:
        >>> # Mute audio (press)
        >>> input_data = MediaKeyInput(keys=[MediaKey.KEY_MUTE])
        >>> # Play/pause media (press)
        >>> input_data = MediaKeyInput(keys=[MediaKey.KEY_PLAYPAUSE])
        >>> # Adjust volume (press)
        >>> input_data = MediaKeyInput(keys=[MediaKey.KEY_VOLUMEUP])
        >>> # Release all keys
        >>> input_data = MediaKeyInput(keys=[])
        >>> # or simply
        >>> input_data = MediaKeyInput()
    """

    keys: list[MediaKey] = Field(default_factory=list, max_length=1)
