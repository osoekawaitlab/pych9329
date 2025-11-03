"""Tests for CH9329 data models."""

import pytest

from pych9329.models import KeyCode, MediaKey, ModifierKey, MouseButton


class TestMouseButton:
    """Tests for MouseButton enum."""

    def test_left_button_value(self) -> None:
        """Test that left button has correct value."""
        assert MouseButton.LEFT.value == 0x01

    def test_right_button_value(self) -> None:
        """Test that right button has correct value."""
        assert MouseButton.RIGHT.value == 0x02

    def test_middle_button_value(self) -> None:
        """Test that middle button has correct value."""
        assert MouseButton.MIDDLE.value == 0x04


class TestModifierKey:
    """Tests for ModifierKey enum."""

    def test_shift_value(self) -> None:
        """Test that shift key has correct value."""
        assert ModifierKey.SHIFT.value == 0x02

    def test_ctrl_value(self) -> None:
        """Test that ctrl key has correct value."""
        assert ModifierKey.CTRL.value == 0x01

    def test_alt_value(self) -> None:
        """Test that alt key has correct value."""
        assert ModifierKey.ALT.value == 0x04

    def test_windows_value(self) -> None:
        """Test that windows key has correct value."""
        assert ModifierKey.WINDOWS.value == 0x08


class TestKeyCode:
    """Tests for KeyCode enum and key mapping."""

    def test_special_key_enter(self) -> None:
        """Test that ENTER key has correct value."""
        assert KeyCode.ENTER.value == 0x28

    def test_special_key_space(self) -> None:
        """Test that SPACE key has correct value."""
        assert KeyCode.SPACE.value == 0x2C

    def test_special_key_backspace(self) -> None:
        """Test that BACKSPACE key has correct value."""
        assert KeyCode.BACKSPACE.value == 0x2A

    def test_special_key_tab(self) -> None:
        """Test that TAB key has correct value."""
        assert KeyCode.TAB.value == 0x2B

    def test_special_key_esc(self) -> None:
        """Test that ESC key has correct value."""
        assert KeyCode.ESC.value == 0x29

    def test_digit_zero(self) -> None:
        """Test that digit 0 maps to correct keycode."""
        assert KeyCode.DIGIT_0.value == 0x27

    def test_digit_one(self) -> None:
        """Test that digit 1 maps to correct keycode."""
        assert KeyCode.DIGIT_1.value == 0x1E

    def test_digit_nine(self) -> None:
        """Test that digit 9 maps to correct keycode."""
        assert KeyCode.DIGIT_9.value == 0x26

    def test_letter_a(self) -> None:
        """Test that letter A maps to correct keycode."""
        assert KeyCode.A.value == 0x04

    def test_letter_z(self) -> None:
        """Test that letter Z maps to correct keycode."""
        assert KeyCode.Z.value == 0x1D


class TestCharacterMapping:
    """Tests for character-to-keycode mapping functionality."""

    def test_lowercase_a_mapping(self) -> None:
        """Test that lowercase 'a' maps to A key without shift."""
        from pych9329.models import get_key_mapping

        modifier, keycode = get_key_mapping("a")
        assert modifier == 0x00
        assert keycode == 0x04

    def test_uppercase_a_mapping(self) -> None:
        """Test that uppercase 'A' maps to A key with shift."""
        from pych9329.models import get_key_mapping

        modifier, keycode = get_key_mapping("A")
        assert modifier == 0x02
        assert keycode == 0x04

    def test_digit_zero_mapping(self) -> None:
        """Test that '0' maps to DIGIT_0 key without shift."""
        from pych9329.models import get_key_mapping

        modifier, keycode = get_key_mapping("0")
        assert modifier == 0x00
        assert keycode == 0x27

    def test_digit_one_mapping(self) -> None:
        """Test that '1' maps to DIGIT_1 key without shift."""
        from pych9329.models import get_key_mapping

        modifier, keycode = get_key_mapping("1")
        assert modifier == 0x00
        assert keycode == 0x1E

    def test_exclamation_mapping(self) -> None:
        """Test that '!' maps to DIGIT_1 key with shift."""
        from pych9329.models import get_key_mapping

        modifier, keycode = get_key_mapping("!")
        assert modifier == 0x02
        assert keycode == 0x1E

    def test_at_sign_mapping(self) -> None:
        """Test that '@' maps to correct key."""
        from pych9329.models import get_key_mapping

        modifier, keycode = get_key_mapping("@")
        assert modifier == 0x00
        assert keycode == 0x2F

    def test_comma_mapping(self) -> None:
        """Test that ',' maps to correct key."""
        from pych9329.models import get_key_mapping

        modifier, keycode = get_key_mapping(",")
        assert modifier == 0x00
        assert keycode == 0x36

    def test_less_than_mapping(self) -> None:
        """Test that '<' maps to correct key with shift."""
        from pych9329.models import get_key_mapping

        modifier, keycode = get_key_mapping("<")
        assert modifier == 0x02
        assert keycode == 0x36

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
