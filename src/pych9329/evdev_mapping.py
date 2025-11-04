"""Mapping between evdev codes and USB HID codes for CH9329."""

from evdev import ecodes

from .exceptions import UnsupportedEvdevCodeError

# Mapping from evdev key codes to USB HID keyboard scan codes
_EVDEV_TO_USB_HID_KEYBOARD: dict[int, int] = {
    # Letters A-Z
    ecodes.KEY_A: 0x04,
    ecodes.KEY_B: 0x05,
    ecodes.KEY_C: 0x06,
    ecodes.KEY_D: 0x07,
    ecodes.KEY_E: 0x08,
    ecodes.KEY_F: 0x09,
    ecodes.KEY_G: 0x0A,
    ecodes.KEY_H: 0x0B,
    ecodes.KEY_I: 0x0C,
    ecodes.KEY_J: 0x0D,
    ecodes.KEY_K: 0x0E,
    ecodes.KEY_L: 0x0F,
    ecodes.KEY_M: 0x10,
    ecodes.KEY_N: 0x11,
    ecodes.KEY_O: 0x12,
    ecodes.KEY_P: 0x13,
    ecodes.KEY_Q: 0x14,
    ecodes.KEY_R: 0x15,
    ecodes.KEY_S: 0x16,
    ecodes.KEY_T: 0x17,
    ecodes.KEY_U: 0x18,
    ecodes.KEY_V: 0x19,
    ecodes.KEY_W: 0x1A,
    ecodes.KEY_X: 0x1B,
    ecodes.KEY_Y: 0x1C,
    ecodes.KEY_Z: 0x1D,
    # Digits 0-9
    ecodes.KEY_1: 0x1E,
    ecodes.KEY_2: 0x1F,
    ecodes.KEY_3: 0x20,
    ecodes.KEY_4: 0x21,
    ecodes.KEY_5: 0x22,
    ecodes.KEY_6: 0x23,
    ecodes.KEY_7: 0x24,
    ecodes.KEY_8: 0x25,
    ecodes.KEY_9: 0x26,
    ecodes.KEY_0: 0x27,
    # Special keys
    ecodes.KEY_ENTER: 0x28,
    ecodes.KEY_ESC: 0x29,
    ecodes.KEY_BACKSPACE: 0x2A,
    ecodes.KEY_TAB: 0x2B,
    ecodes.KEY_SPACE: 0x2C,
    ecodes.KEY_GRAVE: 0x35,  # ZENHAN key
    # Symbol keys
    ecodes.KEY_MINUS: 0x2D,
    ecodes.KEY_EQUAL: 0x2E,
    ecodes.KEY_LEFTBRACE: 0x2F,
    ecodes.KEY_RIGHTBRACE: 0x30,
    ecodes.KEY_BACKSLASH: 0x31,
    ecodes.KEY_SEMICOLON: 0x33,
    ecodes.KEY_APOSTROPHE: 0x34,
    ecodes.KEY_COMMA: 0x36,
    ecodes.KEY_DOT: 0x37,
    ecodes.KEY_SLASH: 0x38,
    ecodes.KEY_RO: 0x87,
    ecodes.KEY_YEN: 0x89,  # INTL_YEN
}

# Mapping from evdev mouse button codes to USB HID mouse button bits
_EVDEV_TO_USB_HID_MOUSE: dict[int, int] = {
    ecodes.BTN_LEFT: 0x01,
    ecodes.BTN_RIGHT: 0x02,
    ecodes.BTN_MIDDLE: 0x04,
}

# Mapping from evdev modifier key codes to USB HID modifier bits
_EVDEV_TO_USB_HID_MODIFIER: dict[int, int] = {
    ecodes.KEY_LEFTCTRL: 0x01,
    ecodes.KEY_RIGHTCTRL: 0x10,
    ecodes.KEY_LEFTSHIFT: 0x02,
    ecodes.KEY_RIGHTSHIFT: 0x20,
    ecodes.KEY_LEFTALT: 0x04,
    ecodes.KEY_RIGHTALT: 0x40,
    ecodes.KEY_LEFTMETA: 0x08,  # Windows key
    ecodes.KEY_RIGHTMETA: 0x80,
}


def evdev_to_usb_hid_keyboard(evdev_code: int) -> int:
    """Convert evdev key code to USB HID keyboard scan code.

    Args:
        evdev_code: The evdev key code (e.g., ecodes.KEY_A).

    Returns:
        The corresponding USB HID keyboard scan code.

    Raises:
        UnsupportedEvdevCodeError: If the evdev code is not supported.

    Examples:
        >>> from evdev import ecodes
        >>> evdev_to_usb_hid_keyboard(ecodes.KEY_A)
        4
    """
    if evdev_code not in _EVDEV_TO_USB_HID_KEYBOARD:
        raise UnsupportedEvdevCodeError(evdev_code)
    return _EVDEV_TO_USB_HID_KEYBOARD[evdev_code]


def evdev_to_usb_hid_mouse(evdev_code: int) -> int:
    """Convert evdev mouse button code to USB HID mouse button bit.

    Args:
        evdev_code: The evdev mouse button code (e.g., ecodes.BTN_LEFT).

    Returns:
        The corresponding USB HID mouse button bit.

    Raises:
        UnsupportedEvdevCodeError: If the evdev code is not supported.

    Examples:
        >>> from evdev import ecodes
        >>> evdev_to_usb_hid_mouse(ecodes.BTN_LEFT)
        1
    """
    if evdev_code not in _EVDEV_TO_USB_HID_MOUSE:
        raise UnsupportedEvdevCodeError(evdev_code)
    return _EVDEV_TO_USB_HID_MOUSE[evdev_code]


def evdev_to_usb_hid_modifier(evdev_code: int) -> int:
    """Convert evdev modifier key code to USB HID modifier bit.

    Args:
        evdev_code: The evdev modifier key code (e.g., ecodes.KEY_LEFTCTRL).

    Returns:
        The corresponding USB HID modifier bit.

    Raises:
        UnsupportedEvdevCodeError: If the evdev code is not supported.

    Examples:
        >>> from evdev import ecodes
        >>> evdev_to_usb_hid_modifier(ecodes.KEY_LEFTCTRL)
        1
    """
    if evdev_code not in _EVDEV_TO_USB_HID_MODIFIER:
        raise UnsupportedEvdevCodeError(evdev_code)
    return _EVDEV_TO_USB_HID_MODIFIER[evdev_code]


def is_supported_evdev_code(evdev_code: int) -> bool:
    """Check if an evdev code is supported by CH9329.

    Args:
        evdev_code: The evdev code to check.

    Returns:
        True if the code is supported, False otherwise.

    Examples:
        >>> from evdev import ecodes
        >>> is_supported_evdev_code(ecodes.KEY_A)
        True
        >>> is_supported_evdev_code(999)
        False
    """
    return (
        evdev_code in _EVDEV_TO_USB_HID_KEYBOARD
        or evdev_code in _EVDEV_TO_USB_HID_MOUSE
        or evdev_code in _EVDEV_TO_USB_HID_MODIFIER
    )
