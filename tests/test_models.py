"""Tests for CH9329 data models."""

import pytest
from evdev import ecodes

from pych9329.models import KeyboardState, KeyCode, MediaKey, ModifierKey, MouseButton


class TestMouseButton:
    """Tests for MouseButton enum."""

    def test_left_button_value(self) -> None:
        """Test that BTN_LEFT has correct evdev value."""
        assert MouseButton.BTN_LEFT.value == ecodes.BTN_LEFT

    def test_right_button_value(self) -> None:
        """Test that BTN_RIGHT has correct evdev value."""
        assert MouseButton.BTN_RIGHT.value == ecodes.BTN_RIGHT

    def test_middle_button_value(self) -> None:
        """Test that BTN_MIDDLE has correct evdev value."""
        assert MouseButton.BTN_MIDDLE.value == ecodes.BTN_MIDDLE


class TestModifierKey:
    """Tests for ModifierKey enum."""

    def test_left_shift_value(self) -> None:
        """Test that KEY_LEFTSHIFT has correct evdev value."""
        assert ModifierKey.KEY_LEFTSHIFT.value == ecodes.KEY_LEFTSHIFT

    def test_left_ctrl_value(self) -> None:
        """Test that KEY_LEFTCTRL has correct evdev value."""
        assert ModifierKey.KEY_LEFTCTRL.value == ecodes.KEY_LEFTCTRL

    def test_left_alt_value(self) -> None:
        """Test that KEY_LEFTALT has correct evdev value."""
        assert ModifierKey.KEY_LEFTALT.value == ecodes.KEY_LEFTALT

    def test_left_meta_value(self) -> None:
        """Test that KEY_LEFTMETA (Windows key) has correct evdev value."""
        assert ModifierKey.KEY_LEFTMETA.value == ecodes.KEY_LEFTMETA


class TestKeyCode:
    """Tests for KeyCode enum and key mapping."""

    def test_special_key_enter(self) -> None:
        """Test that KEY_ENTER has correct evdev value."""
        assert KeyCode.KEY_ENTER.value == ecodes.KEY_ENTER

    def test_special_key_space(self) -> None:
        """Test that KEY_SPACE has correct evdev value."""
        assert KeyCode.KEY_SPACE.value == ecodes.KEY_SPACE

    def test_special_key_backspace(self) -> None:
        """Test that KEY_BACKSPACE has correct evdev value."""
        assert KeyCode.KEY_BACKSPACE.value == ecodes.KEY_BACKSPACE

    def test_special_key_tab(self) -> None:
        """Test that KEY_TAB has correct evdev value."""
        assert KeyCode.KEY_TAB.value == ecodes.KEY_TAB

    def test_special_key_esc(self) -> None:
        """Test that KEY_ESC has correct evdev value."""
        assert KeyCode.KEY_ESC.value == ecodes.KEY_ESC

    def test_digit_zero(self) -> None:
        """Test that KEY_0 has correct evdev value."""
        assert KeyCode.KEY_0.value == ecodes.KEY_0

    def test_digit_one(self) -> None:
        """Test that KEY_1 has correct evdev value."""
        assert KeyCode.KEY_1.value == ecodes.KEY_1

    def test_digit_nine(self) -> None:
        """Test that KEY_9 has correct evdev value."""
        assert KeyCode.KEY_9.value == ecodes.KEY_9

    def test_letter_a(self) -> None:
        """Test that KEY_A has correct evdev value."""
        assert KeyCode.KEY_A.value == ecodes.KEY_A

    def test_letter_z(self) -> None:
        """Test that KEY_Z has correct evdev value."""
        assert KeyCode.KEY_Z.value == ecodes.KEY_Z


class TestCharacterMapping:
    """Tests for character-to-keycode mapping functionality."""

    def test_lowercase_a_mapping(self) -> None:
        """Test that lowercase 'a' maps to KEY_A without shift (evdev codes)."""
        from pych9329.models import get_key_mapping

        modifier, keycode = get_key_mapping("a")
        assert modifier == 0x00
        assert keycode == ecodes.KEY_A

    def test_uppercase_a_mapping(self) -> None:
        """Test that uppercase 'A' maps to KEY_A with shift (evdev codes)."""
        from pych9329.models import get_key_mapping

        modifier, keycode = get_key_mapping("A")
        assert modifier == ecodes.KEY_LEFTSHIFT
        assert keycode == ecodes.KEY_A

    def test_digit_zero_mapping(self) -> None:
        """Test that '0' maps to KEY_0 without shift (evdev codes)."""
        from pych9329.models import get_key_mapping

        modifier, keycode = get_key_mapping("0")
        assert modifier == 0x00
        assert keycode == ecodes.KEY_0

    def test_digit_one_mapping(self) -> None:
        """Test that '1' maps to KEY_1 without shift (evdev codes)."""
        from pych9329.models import get_key_mapping

        modifier, keycode = get_key_mapping("1")
        assert modifier == 0x00
        assert keycode == ecodes.KEY_1

    def test_exclamation_mapping(self) -> None:
        """Test that '!' maps to KEY_1 with shift (evdev codes)."""
        from pych9329.models import get_key_mapping

        modifier, keycode = get_key_mapping("!")
        assert modifier == ecodes.KEY_LEFTSHIFT
        assert keycode == ecodes.KEY_1

    def test_at_sign_mapping(self) -> None:
        """Test that '@' maps to correct key (evdev codes)."""
        from pych9329.models import get_key_mapping

        modifier, keycode = get_key_mapping("@")
        assert modifier == 0x00
        assert keycode == ecodes.KEY_LEFTBRACE

    def test_comma_mapping(self) -> None:
        """Test that ',' maps to correct key (evdev codes)."""
        from pych9329.models import get_key_mapping

        modifier, keycode = get_key_mapping(",")
        assert modifier == 0x00
        assert keycode == ecodes.KEY_COMMA

    def test_less_than_mapping(self) -> None:
        """Test that '<' maps to correct key with shift (evdev codes)."""
        from pych9329.models import get_key_mapping

        modifier, keycode = get_key_mapping("<")
        assert modifier == ecodes.KEY_LEFTSHIFT
        assert keycode == ecodes.KEY_COMMA

    def test_unmapped_character_raises_error(self) -> None:
        """Test that unmapped characters raise ValueError."""
        from pych9329.models import get_key_mapping

        with pytest.raises(ValueError, match="Unsupported character"):
            get_key_mapping("あ")


class TestMediaKey:
    """Tests for MediaKey enum."""

    def test_mute_value(self) -> None:
        """Test that MUTE key has correct packet data."""
        assert MediaKey.MUTE.value == (0x02, 0x04, 0x00, 0x00)

    def test_volume_up_value(self) -> None:
        """Test that VOLUME_UP key has correct packet data."""
        assert MediaKey.VOLUME_UP.value == (0x02, 0x01, 0x00, 0x00)

    def test_volume_down_value(self) -> None:
        """Test that VOLUME_DOWN key has correct packet data."""
        assert MediaKey.VOLUME_DOWN.value == (0x02, 0x02, 0x00, 0x00)

    def test_play_pause_value(self) -> None:
        """Test that PLAY_PAUSE key has correct packet data."""
        assert MediaKey.PLAY_PAUSE.value == (0x02, 0x08, 0x00, 0x00)

    def test_next_track_value(self) -> None:
        """Test that NEXT_TRACK key has correct packet data."""
        assert MediaKey.NEXT_TRACK.value == (0x02, 0x10, 0x00, 0x00)

    def test_prev_track_value(self) -> None:
        """Test that PREV_TRACK key has correct packet data."""
        assert MediaKey.PREV_TRACK.value == (0x02, 0x20, 0x00, 0x00)


class TestKeyboardState:
    """Tests for KeyboardState data model."""

    def test_empty_state(self) -> None:
        """Test creating an empty keyboard state."""
        state = KeyboardState()
        assert state.modifiers == set()
        assert state.keys == []

    def test_single_key(self) -> None:
        """Test creating state with single key."""
        state = KeyboardState(keys=[KeyCode.KEY_A])
        assert state.modifiers == set()
        assert state.keys == [KeyCode.KEY_A]

    def test_single_key_with_modifiers(self) -> None:
        """Test creating state with key and modifiers."""
        state = KeyboardState(
            modifiers={ModifierKey.KEY_LEFTCTRL, ModifierKey.KEY_LEFTSHIFT},
            keys=[KeyCode.KEY_A],
        )
        assert state.modifiers == {
            ModifierKey.KEY_LEFTCTRL,
            ModifierKey.KEY_LEFTSHIFT,
        }
        assert state.keys == [KeyCode.KEY_A]

    def test_multiple_keys(self) -> None:
        """Test creating state with multiple keys."""
        state = KeyboardState(keys=[KeyCode.KEY_A, KeyCode.KEY_B, KeyCode.KEY_C])
        assert len(state.keys) == 3
        assert state.keys == [KeyCode.KEY_A, KeyCode.KEY_B, KeyCode.KEY_C]

    def test_maximum_six_keys(self) -> None:
        """Test creating state with exactly 6 keys."""
        state = KeyboardState(
            keys=[
                KeyCode.KEY_A,
                KeyCode.KEY_B,
                KeyCode.KEY_C,
                KeyCode.KEY_D,
                KeyCode.KEY_E,
                KeyCode.KEY_F,
            ]
        )
        assert len(state.keys) == 6

    def test_more_than_six_keys_raises_error(self) -> None:
        """Test that more than 6 keys raises ValueError."""
        with pytest.raises(ValueError, match="Maximum 6 keys allowed, got 7"):
            KeyboardState(
                keys=[
                    KeyCode.KEY_A,
                    KeyCode.KEY_B,
                    KeyCode.KEY_C,
                    KeyCode.KEY_D,
                    KeyCode.KEY_E,
                    KeyCode.KEY_F,
                    KeyCode.KEY_G,
                ]
            )

    def test_all_modifiers(self) -> None:
        """Test creating state with all modifier keys."""
        state = KeyboardState(
            modifiers={
                ModifierKey.KEY_LEFTCTRL,
                ModifierKey.KEY_RIGHTCTRL,
                ModifierKey.KEY_LEFTSHIFT,
                ModifierKey.KEY_RIGHTSHIFT,
                ModifierKey.KEY_LEFTALT,
                ModifierKey.KEY_RIGHTALT,
                ModifierKey.KEY_LEFTMETA,
                ModifierKey.KEY_RIGHTMETA,
            }
        )
        assert len(state.modifiers) == 8
