# ch9329py

Modern Python driver for the CH9329 USB HID device with a state-based API.

## Features

- 🔌 **State-based API** - Direct control matching USB HID protocol
- 🐧 **Linux-tested** - Tested on Linux (may work on other platforms via pyserial)
- 🎯 **Type-safe** - Full type hints with mypy strict mode
- 🎮 **Complete HID support** - Keyboard, mouse, and media keys

## Installation

```bash
# From GitHub
uv add git+https://github.com/osoekawaitlab/ch9329py.git

# Or with pip
pip install git+https://github.com/osoekawaitlab/ch9329py.git
```

See [Installation Guide](installation.md) for details.

## Quick Start

### Basic Keyboard Input

```python
from ch9329py import CH9329Driver, SerialAdapter, KeyboardInput, KeyCode

with SerialAdapter("/dev/ttyUSB0", 9600) as adapter:
    with CH9329Driver(adapter) as driver:
        # Press 'A' key
        driver.send_keyboard_input(KeyboardInput(keys=[KeyCode.KEY_A]))
        # Release (important!)
        driver.send_keyboard_input(KeyboardInput())
```

### Using Modifiers

```python
from ch9329py import ModifierKey

# Ctrl+C
driver.send_keyboard_input(KeyboardInput(
    modifiers={ModifierKey.KEY_LEFTCTRL},
    keys=[KeyCode.KEY_C]
))
driver.send_keyboard_input(KeyboardInput())
```

### Mouse Control

```python
from ch9329py import MouseInput, MouseButton

# Move mouse
driver.send_mouse_input(MouseInput(x=10, y=10))

# Click
driver.send_mouse_input(MouseInput(buttons={MouseButton.BTN_LEFT}))
driver.send_mouse_input(MouseInput())  # Release

# Scroll
driver.send_mouse_input(MouseInput(scroll=5))
```

### Media Keys

```python
from ch9329py import MediaKeyInput, MediaKey

# Play/pause
driver.send_media_key_input(MediaKeyInput(keys=[MediaKey.KEY_PLAYPAUSE]))
driver.send_media_key_input(MediaKeyInput())  # Release
```

## State-Based API

This library uses a **state-based API** where you send complete input states:

```python
# Set state: A pressed
driver.send_keyboard_input(KeyboardInput(keys=[KeyCode.KEY_A]))

# Set state: nothing pressed
driver.send_keyboard_input(KeyboardInput())
```

**Key concepts:**
- Always release keys/buttons by sending empty input
- Each input represents complete state, not a change
- No automatic behavior - you control everything

## Architecture

```
┌─────────────────────────────┐
│   CH9329Driver              │  ← Three methods: send_keyboard_input,
├─────────────────────────────┤     send_mouse_input, send_media_key_input
│   Protocol Layer            │  ← Packet building
├─────────────────────────────┤
│   Communication Adapter     │  ← Serial abstraction
├─────────────────────────────┤
│   Data Models (Pydantic)    │  ← KeyboardInput, MouseInput, MediaKeyInput
└─────────────────────────────┘
```

## Documentation

- [Installation Guide](installation.md) - Setup and configuration
- [API Reference](api/index.md) - Complete API documentation

## Use Cases

- Automated testing
- Accessibility tools
- Remote control systems
- Embedded system interfaces
- Home automation

## Contributing

Contributions welcome! Especially for:
- Windows/macOS testing
- Additional examples
- Bug fixes

## License

MIT License - see LICENSE file for details.
