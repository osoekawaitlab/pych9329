# pych9329

A modern, type-safe Python driver for the CH9329 USB HID device. Control keyboards, mice, and media keys programmatically with a clean, low-level state-based API.

## ✨ Features

- 🔌 **Low-level state-based API**: Direct control over device state matching USB HID protocol
- 🐧 **evdev-compatible**: All key/button codes follow Linux evdev naming convention

## 📦 Installation

### Using uv (recommended)

```bash
uv add git+https://github.com/osoekawaitlab/pych9329.git
```

### Using pip

```bash
pip install git+https://github.com/osoekawaitlab/pych9329.git
```

### From source

```bash
git clone https://github.com/osoekawaitlab/pych9329.git
cd pych9329
uv sync
```

## 🚀 Quick Start

### Basic Example

```python
from pych9329 import (
    CH9329Driver,
    SerialAdapter,
    KeyboardInput,
    KeyCode,
    ModifierKey,
)

# Connect to the CH9329 device
with SerialAdapter("/dev/ttyUSB0", 9600) as adapter:
    with CH9329Driver(adapter) as driver:
        # Press Ctrl+Shift+A
        input_data = KeyboardInput(
            modifiers={ModifierKey.KEY_LEFTCTRL, ModifierKey.KEY_LEFTSHIFT},
            keys=[KeyCode.KEY_A],
        )
        driver.send_keyboard_input(input_data)

        # Release all keys
        driver.send_keyboard_input(KeyboardInput())
```

## 📖 API Overview

pych9329 provides a **state-based API** where you send complete input states to the device. This matches the underlying USB HID protocol and gives you precise control.

### Three Core Methods

- `send_keyboard_input(input_data: KeyboardInput)` - Send keyboard state
- `send_mouse_input(input_data: MouseInput)` - Send mouse state
- `send_media_key_input(input_data: MediaKeyInput)` - Send media key state

## 🎹 Keyboard Control

### Basic Keyboard Input

```python
from pych9329 import CH9329Driver, SerialAdapter, KeyboardInput, KeyCode

with SerialAdapter("/dev/ttyUSB0", 9600) as adapter:
    driver = CH9329Driver(adapter)

    # Press a single key
    input_data = KeyboardInput(keys=[KeyCode.KEY_A])
    driver.send_keyboard_input(input_data)

    # Release all keys
    driver.send_keyboard_input(KeyboardInput())
```

### Keyboard with Modifiers

```python
from pych9329 import KeyboardInput, KeyCode, ModifierKey

# Ctrl+C
input_data = KeyboardInput(
    modifiers={ModifierKey.KEY_LEFTCTRL},
    keys=[KeyCode.KEY_C],
)
driver.send_keyboard_input(input_data)

# Ctrl+Shift+A
input_data = KeyboardInput(
    modifiers={ModifierKey.KEY_LEFTCTRL, ModifierKey.KEY_LEFTSHIFT},
    keys=[KeyCode.KEY_A],
)
driver.send_keyboard_input(input_data)

# Release all
driver.send_keyboard_input(KeyboardInput())
```

### Multiple Simultaneous Keys

The CH9329 supports up to 6 simultaneous regular keys (N-key rollover):

```python
# Press A+B+C simultaneously
input_data = KeyboardInput(
    keys=[KeyCode.KEY_A, KeyCode.KEY_B, KeyCode.KEY_C]
)
driver.send_keyboard_input(input_data)

# Maximum 6 keys at once
input_data = KeyboardInput(
    keys=[
        KeyCode.KEY_A,
        KeyCode.KEY_B,
        KeyCode.KEY_C,
        KeyCode.KEY_D,
        KeyCode.KEY_E,
        KeyCode.KEY_F,
    ]
)
driver.send_keyboard_input(input_data)

# Release all keys
driver.send_keyboard_input(KeyboardInput())
```

### Available Keys

All keys follow evdev naming convention:

- **Letters**: `KEY_A` through `KEY_Z`
- **Numbers**: `KEY_0` through `KEY_9`
- **Special keys**: `KEY_ENTER`, `KEY_SPACE`, `KEY_BACKSPACE`, `KEY_TAB`, `KEY_ESC`
- **Symbols**: `KEY_MINUS`, `KEY_EQUAL`, `KEY_LEFTBRACE`, `KEY_RIGHTBRACE`, etc.
- **Modifiers**: `KEY_LEFTCTRL`, `KEY_RIGHTCTRL`, `KEY_LEFTSHIFT`, `KEY_RIGHTSHIFT`, `KEY_LEFTALT`, `KEY_RIGHTALT`, `KEY_LEFTMETA`, `KEY_RIGHTMETA`

## 🖱️ Mouse Control

### Mouse Movement

```python
from pych9329 import MouseInput

# Relative movement (right 10px, down 10px)
input_data = MouseInput(x=10, y=10)
driver.send_mouse_input(input_data)

# Movement ranges: x and y are -128 to 127
input_data = MouseInput(x=-50, y=-50)  # Left 50px, up 50px
driver.send_mouse_input(input_data)
```

### Mouse Buttons

```python
from pych9329 import MouseInput, MouseButton

# Press left button
input_data = MouseInput(buttons={MouseButton.BTN_LEFT})
driver.send_mouse_input(input_data)

# Press multiple buttons
input_data = MouseInput(
    buttons={MouseButton.BTN_LEFT, MouseButton.BTN_RIGHT}
)
driver.send_mouse_input(input_data)

# Release all buttons
driver.send_mouse_input(MouseInput())
```

### Button with Movement

```python
# Drag operation: left button pressed while moving
input_data = MouseInput(
    buttons={MouseButton.BTN_LEFT},
    x=10,
    y=10,
)
driver.send_mouse_input(input_data)

# Release all buttons
driver.send_mouse_input(MouseInput())
```

### Mouse Scroll

```python
# Scroll up
input_data = MouseInput(scroll=5)
driver.send_mouse_input(input_data)

# Scroll down
input_data = MouseInput(scroll=-5)
driver.send_mouse_input(input_data)

# Scroll range: -127 to 127
```

### Complete Mouse Example

```python
# All parameters together
input_data = MouseInput(
    buttons={MouseButton.BTN_LEFT, MouseButton.BTN_RIGHT},
    x=10,
    y=-10,
    scroll=3,
)
driver.send_mouse_input(input_data)

# Release all buttons
driver.send_mouse_input(MouseInput())
```

## 🎵 Media Key Control

### Basic Media Keys

```python
from pych9329 import MediaKeyInput, MediaKey

# Play/pause
input_data = MediaKeyInput(keys=[MediaKey.KEY_PLAYPAUSE])
driver.send_media_key_input(input_data)

# Release (important for media keys!)
driver.send_media_key_input(MediaKeyInput())
```

### Volume Control

```python
# Volume up
input_data = MediaKeyInput(keys=[MediaKey.KEY_VOLUMEUP])
driver.send_media_key_input(input_data)
driver.send_media_key_input(MediaKeyInput())  # Release

# Volume down
input_data = MediaKeyInput(keys=[MediaKey.KEY_VOLUMEDOWN])
driver.send_media_key_input(input_data)
driver.send_media_key_input(MediaKeyInput())  # Release

# Mute
input_data = MediaKeyInput(keys=[MediaKey.KEY_MUTE])
driver.send_media_key_input(input_data)
driver.send_media_key_input(MediaKeyInput())  # Release
```

### Playback Control

```python
# Next track
input_data = MediaKeyInput(keys=[MediaKey.KEY_NEXTSONG])
driver.send_media_key_input(input_data)
driver.send_media_key_input(MediaKeyInput())  # Release

# Previous track
input_data = MediaKeyInput(keys=[MediaKey.KEY_PREVIOUSSONG])
driver.send_media_key_input(input_data)
driver.send_media_key_input(MediaKeyInput())  # Release

# Stop
input_data = MediaKeyInput(keys=[MediaKey.KEY_STOPCD])
driver.send_media_key_input(input_data)
driver.send_media_key_input(MediaKeyInput())  # Release

# Eject
input_data = MediaKeyInput(keys=[MediaKey.KEY_EJECTCD])
driver.send_media_key_input(input_data)
driver.send_media_key_input(MediaKeyInput())  # Release
```

**Note**: Media keys only support one key at a time (unlike keyboard which supports 6).

## 🏗️ Architecture

The library follows SOLID principles with a clean, layered architecture:

```text
pych9329/
├── models.py          # Data models (input states and enums)
├── protocol.py        # Protocol layer (packet building)
├── adapter.py         # Communication layer (serial abstraction)
├── driver.py          # Main driver (state-based API)
├── evdev_mapping.py   # evdev to USB HID code conversion
├── exceptions.py      # Custom exceptions
└── __init__.py        # Public API exports
```

### Key Design Principles

1. **State-based API**: Send complete input states rather than individual actions
2. **evdev compatibility**: All codes follow Linux evdev naming convention
3. **Type safety**: Pydantic models with validation
4. **Dependency injection**: Adapter pattern for testability
5. **Explicit over implicit**: No hidden state, everything is explicit

## 🔌 Custom Adapters

You can implement custom adapters for testing or alternative communication methods:

```python
from pych9329 import CH9329Driver, CommunicationAdapter

class CustomAdapter(CommunicationAdapter):
    def send(self, data: bytes) -> None:
        # Custom implementation (e.g., network, mock, logging)
        pass

    def close(self) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# Use your custom adapter
adapter = CustomAdapter()
driver = CH9329Driver(adapter)
```

## 🧪 Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/osoekawaitlab/pych9329.git
cd pych9329

# Install dependencies
uv sync
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/pych9329 --cov-report=html

# Run specific test file
uv run pytest tests/test_driver.py -v
```

### Code Quality Checks

```bash
# Type checking
uv run mypy src/pych9329

# Linting
uv run ruff check src/ tests/

# Format code
uv run ruff format src/ tests/
```

### Running with Nox

All development tasks are available through Nox:

```bash
# Run tests
uv run nox -s tests

# Run all quality checks
uv run nox -s quality

# Run everything
uv run nox -s check_all

# List all sessions
uv run nox --list
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- CH9329 chip manufacturer for the protocol documentation
- evdev project for the standardized key/button naming convention
- Python community for excellent libraries (pydantic, pytest, etc.)

## 📧 Support

For questions or issues, please open an issue on GitHub.
