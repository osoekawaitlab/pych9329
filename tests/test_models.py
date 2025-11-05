"""Tests for CH9329 data models."""

import pytest
from evdev import ecodes
from pydantic import ValidationError

from pych9329.models import (
    KeyboardInput,
    KeyCode,
    MediaKey,
    MediaKeyInput,
    ModifierKey,
    MouseButton,
    MouseInput,
)


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


class TestMediaKey:
    """Tests for MediaKey enum."""

    def test_mute_value(self) -> None:
        """Test that KEY_MUTE key has correct packet data."""
        assert MediaKey.KEY_MUTE.value == (0x02, 0x04, 0x00, 0x00)

    def test_volume_up_value(self) -> None:
        """Test that KEY_VOLUMEUP key has correct packet data."""
        assert MediaKey.KEY_VOLUMEUP.value == (0x02, 0x01, 0x00, 0x00)

    def test_volume_down_value(self) -> None:
        """Test that KEY_VOLUMEDOWN key has correct packet data."""
        assert MediaKey.KEY_VOLUMEDOWN.value == (0x02, 0x02, 0x00, 0x00)

    def test_play_pause_value(self) -> None:
        """Test that KEY_PLAYPAUSE key has correct packet data."""
        assert MediaKey.KEY_PLAYPAUSE.value == (0x02, 0x08, 0x00, 0x00)

    def test_next_track_value(self) -> None:
        """Test that KEY_NEXTSONG key has correct packet data."""
        assert MediaKey.KEY_NEXTSONG.value == (0x02, 0x10, 0x00, 0x00)

    def test_prev_track_value(self) -> None:
        """Test that KEY_PREVIOUSSONG key has correct packet data."""
        assert MediaKey.KEY_PREVIOUSSONG.value == (0x02, 0x20, 0x00, 0x00)


class TestKeyboardInput:
    """Tests for KeyboardInput data model."""

    def test_empty_state(self) -> None:
        """Test creating an empty keyboard state."""
        state = KeyboardInput()
        assert state.modifiers == set()
        assert state.keys == []

    def test_single_key(self) -> None:
        """Test creating state with single key."""
        state = KeyboardInput(keys=[KeyCode.KEY_A])
        assert state.modifiers == set()
        assert state.keys == [KeyCode.KEY_A]

    def test_single_key_with_modifiers(self) -> None:
        """Test creating state with key and modifiers."""
        state = KeyboardInput(
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
        keys = [KeyCode.KEY_A, KeyCode.KEY_B, KeyCode.KEY_C]
        state = KeyboardInput(keys=keys)
        assert len(state.keys) == len(keys)
        assert state.keys == keys

    def test_maximum_six_keys(self) -> None:
        """Test creating state with exactly 6 keys."""
        keys = [
            KeyCode.KEY_A,
            KeyCode.KEY_B,
            KeyCode.KEY_C,
            KeyCode.KEY_D,
            KeyCode.KEY_E,
            KeyCode.KEY_F,
        ]
        state = KeyboardInput(keys=keys)
        assert len(state.keys) == len(keys)
        assert state.keys == keys

    def test_more_than_six_keys_raises_error(self) -> None:
        """Test that more than 6 keys raises ValidationError."""
        with pytest.raises(
            ValidationError,
            match=r".*List should have at most 6 items after validation, not 7.*",
        ):
            KeyboardInput(
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
        modifiers = {
            ModifierKey.KEY_LEFTCTRL,
            ModifierKey.KEY_RIGHTCTRL,
            ModifierKey.KEY_LEFTSHIFT,
            ModifierKey.KEY_RIGHTSHIFT,
            ModifierKey.KEY_LEFTALT,
            ModifierKey.KEY_RIGHTALT,
            ModifierKey.KEY_LEFTMETA,
            ModifierKey.KEY_RIGHTMETA,
        }
        state = KeyboardInput(modifiers=modifiers)
        assert len(state.modifiers) == len(modifiers)


class TestMouseInput:
    """Tests for MouseInput data model."""

    def test_empty_state(self) -> None:
        """Test creating an empty mouse state."""
        state = MouseInput()
        assert state.buttons == set()
        assert state.x == 0
        assert state.y == 0
        assert state.scroll == 0

    def test_movement_only(self) -> None:
        """Test creating state with only movement."""
        dx = 10
        dy = -20
        state = MouseInput(x=dx, y=dy)
        assert state.buttons == set()
        assert state.x == dx
        assert state.y == dy
        assert state.scroll == 0

    def test_scroll_only(self) -> None:
        """Test creating state with only scroll."""
        dscroll = 5
        state = MouseInput(scroll=dscroll)
        assert state.buttons == set()
        assert state.x == 0
        assert state.y == 0
        assert state.scroll == dscroll

    def test_single_button(self) -> None:
        """Test creating state with single button."""
        state = MouseInput(buttons={MouseButton.BTN_LEFT})
        assert state.buttons == {MouseButton.BTN_LEFT}

    def test_multiple_buttons(self) -> None:
        """Test creating state with multiple buttons."""
        buttons = {MouseButton.BTN_LEFT, MouseButton.BTN_RIGHT}
        state = MouseInput(buttons=buttons)
        assert len(state.buttons) == len(buttons)
        assert state.buttons == {MouseButton.BTN_LEFT, MouseButton.BTN_RIGHT}

    def test_button_with_movement(self) -> None:
        """Test creating state with button and movement."""
        dx = 5
        dy = -5
        state = MouseInput(buttons={MouseButton.BTN_LEFT}, x=dx, y=dy)
        assert state.buttons == {MouseButton.BTN_LEFT}
        assert state.x == dx
        assert state.y == dy

    def test_all_parameters(self) -> None:
        """Test creating state with all parameters."""
        buttons = {MouseButton.BTN_LEFT, MouseButton.BTN_RIGHT}
        dx = 10
        dy = -10
        dscroll = 3
        state = MouseInput(
            buttons=buttons,
            x=dx,
            y=dy,
            scroll=dscroll,
        )
        assert len(state.buttons) == len(buttons)
        assert state.x == dx
        assert state.y == dy
        assert state.scroll == dscroll

    def test_x_min_boundary(self) -> None:
        """Test x movement at minimum boundary."""
        dx = -128
        state = MouseInput(x=dx)
        assert state.x == dx

    def test_x_max_boundary(self) -> None:
        """Test x movement at maximum boundary."""
        dx = 127
        state = MouseInput(x=dx)
        assert state.x == dx

    def test_x_below_min_raises_error(self) -> None:
        """Test that x below minimum raises ValidationError."""
        with pytest.raises(
            ValidationError, match=r".*Input should be greater than or equal to -128.*"
        ):
            MouseInput(x=-129)

    def test_x_above_max_raises_error(self) -> None:
        """Test that x above maximum raises ValidationError."""
        with pytest.raises(
            ValidationError, match=r".*Input should be less than or equal to 127.*"
        ):
            MouseInput(x=128)

    def test_y_min_boundary(self) -> None:
        """Test y movement at minimum boundary."""
        dy = -128
        state = MouseInput(y=dy)
        assert state.y == dy

    def test_y_max_boundary(self) -> None:
        """Test y movement at maximum boundary."""
        dy = 127
        state = MouseInput(y=dy)
        assert state.y == dy

    def test_y_below_min_raises_error(self) -> None:
        """Test that y below minimum raises ValidationError."""
        with pytest.raises(
            ValidationError, match=r".*Input should be greater than or equal to -128.*"
        ):
            MouseInput(y=-129)

    def test_y_above_max_raises_error(self) -> None:
        """Test that y above maximum raises ValidationError."""
        with pytest.raises(
            ValidationError, match=r".*Input should be less than or equal to 127.*"
        ):
            MouseInput(y=128)

    def test_scroll_min_boundary(self) -> None:
        """Test scroll at minimum boundary."""
        dscroll = -127
        state = MouseInput(scroll=dscroll)
        assert state.scroll == dscroll

    def test_scroll_max_boundary(self) -> None:
        """Test scroll at maximum boundary."""
        dscroll = 127
        state = MouseInput(scroll=dscroll)
        assert state.scroll == dscroll

    def test_scroll_below_min_raises_error(self) -> None:
        """Test that scroll below minimum raises ValidationError."""
        with pytest.raises(
            ValidationError, match=r".*Input should be greater than or equal to -127.*"
        ):
            MouseInput(scroll=-128)

    def test_scroll_above_max_raises_error(self) -> None:
        """Test that scroll above maximum raises ValidationError."""
        with pytest.raises(
            ValidationError, match=r".*Input should be less than or equal to 127.*"
        ):
            MouseInput(scroll=128)


class TestMediaKeyInput:
    """Tests for MediaKeyInput data model."""

    def test_empty_state(self) -> None:
        """Test creating an empty media key state (all keys released)."""
        input_data = MediaKeyInput()
        assert input_data.keys == []

    def test_single_media_key(self) -> None:
        """Test creating input with single media key."""
        input_data = MediaKeyInput(keys=[MediaKey.KEY_MUTE])
        assert input_data.keys == [MediaKey.KEY_MUTE]

    def test_play_pause_key(self) -> None:
        """Test creating input with play/pause key."""
        input_data = MediaKeyInput(keys=[MediaKey.KEY_PLAYPAUSE])
        assert input_data.keys == [MediaKey.KEY_PLAYPAUSE]

    def test_volume_up_key(self) -> None:
        """Test creating input with volume up key."""
        input_data = MediaKeyInput(keys=[MediaKey.KEY_VOLUMEUP])
        assert input_data.keys == [MediaKey.KEY_VOLUMEUP]

    def test_volume_down_key(self) -> None:
        """Test creating input with volume down key."""
        input_data = MediaKeyInput(keys=[MediaKey.KEY_VOLUMEDOWN])
        assert input_data.keys == [MediaKey.KEY_VOLUMEDOWN]

    def test_next_track_key(self) -> None:
        """Test creating input with next track key."""
        input_data = MediaKeyInput(keys=[MediaKey.KEY_NEXTSONG])
        assert input_data.keys == [MediaKey.KEY_NEXTSONG]

    def test_prev_track_key(self) -> None:
        """Test creating input with previous track key."""
        input_data = MediaKeyInput(keys=[MediaKey.KEY_PREVIOUSSONG])
        assert input_data.keys == [MediaKey.KEY_PREVIOUSSONG]

    def test_more_than_one_key_raises_error(self) -> None:
        """Test that providing more than one key raises validation error."""
        with pytest.raises(ValidationError):
            MediaKeyInput(keys=[MediaKey.KEY_MUTE, MediaKey.KEY_VOLUMEUP])
