# API Reference

Complete API documentation for ch9329py.

## Modules

- [Driver](driver.md) - High-level API for controlling the CH9329 device
- [Adapter](adapter.md) - Communication layer for serial connections
- [Protocol](protocol.md) - Low-level packet building
- [Models](models.md) - Data models and enums

## Quick Links

### Main Classes

- [`CH9329Driver`](driver.md) - Main driver class
- [`SerialAdapter`](adapter.md) - Serial communication adapter
- [`CommunicationAdapter`](adapter.md) - Abstract adapter base class

### Data Models

- [`KeyboardInput`](models.md) - Keyboard input state
- [`MouseInput`](models.md) - Mouse input state
- [`MediaKeyInput`](models.md) - Media key input state

### Enums

- [`KeyCode`](models.md) - Keyboard key codes
- [`ModifierKey`](models.md) - Keyboard modifiers (Ctrl, Shift, etc.)
- [`MouseButton`](models.md) - Mouse button constants
- [`MediaKey`](models.md) - Media control keys

### Protocol

- [`CH9329Protocol`](protocol.md) - Protocol packet builder

## Usage Pattern

The typical usage pattern involves three main components:

```python
from ch9329py import CH9329Driver, SerialAdapter, KeyboardInput, KeyCode

# 1. Create adapter (communication layer)
adapter = SerialAdapter("/dev/ttyUSB0", 9600)

# 2. Create driver (high-level API)
driver = CH9329Driver(adapter)

# 3. Use the driver (state-based API)
driver.send_keyboard_input(KeyboardInput(keys=[KeyCode.KEY_H, KeyCode.KEY_I]))
driver.send_keyboard_input(KeyboardInput())  # Release
driver.close()
```

Or with context managers (recommended):

```python
from ch9329py import CH9329Driver, SerialAdapter, KeyboardInput, KeyCode

with SerialAdapter("/dev/ttyUSB0", 9600) as adapter:
    with CH9329Driver(adapter) as driver:
        # Press keys
        driver.send_keyboard_input(KeyboardInput(keys=[KeyCode.KEY_A]))
        # Release keys
        driver.send_keyboard_input(KeyboardInput())
```

## Type Safety

All classes and functions in ch9329py are fully type-annotated and checked with mypy in strict mode. This means you get:

- Autocomplete in IDEs
- Type checking at development time
- Better documentation
- Fewer runtime errors

Example:

```python
from ch9329py import CH9329Driver, KeyboardInput, KeyCode

def automate_task(driver: CH9329Driver) -> None:
    """Automate a task with type checking."""
    # ✓ Type checks - KeyboardInput with KeyCode enum
    driver.send_keyboard_input(KeyboardInput(keys=[KeyCode.KEY_A]))

    # ✗ Type error: str is not KeyCode
    # driver.send_keyboard_input(KeyboardInput(keys=["A"]))
```

## Error Handling

The library uses custom exceptions from the `exceptions` module:

- `CH9329PyError` - Base exception for all library errors
- `UnsupportedEvdevCodeError` - For unsupported evdev codes

Standard Python exceptions are also raised:

- `ValueError` - For invalid input values (e.g., out of range mouse movement)
- `TypeError` - For type mismatches

Example:

```python
from ch9329py import (
    CH9329Driver,
    SerialAdapter,
    KeyboardInput,
    KeyCode,
    CH9329PyError,
)

try:
    adapter = SerialAdapter("/dev/invalid", 9600)
except Exception as e:
    print(f"Failed to connect: {e}")

try:
    # Invalid mouse movement (out of range)
    from ch9329py import MouseInput
    driver.send_mouse_input(MouseInput(x=200))  # Max is 127
except ValueError as e:
    print(f"Invalid value: {e}")
```

## Extension Points

### Custom Adapters

You can create custom communication adapters by implementing the `CommunicationAdapter` interface:

```python
from ch9329py import CommunicationAdapter, CH9329Driver

class NetworkAdapter(CommunicationAdapter):
    """Send commands over network instead of serial."""

    def send(self, data: bytes) -> bytes:
        # Your network implementation
        pass

    def close(self) -> None:
        # Cleanup
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# Use your custom adapter
adapter = NetworkAdapter()
driver = CH9329Driver(adapter)
```

## Performance Considerations

### Command Timing

Each command is sent immediately to the device. For proper timing between keystrokes, use `time.sleep()`:

```python
import time
from ch9329py import KeyboardInput, KeyCode

# Type with delay between keys
driver.send_keyboard_input(KeyboardInput(keys=[KeyCode.KEY_A]))
driver.send_keyboard_input(KeyboardInput())
time.sleep(0.05)

driver.send_keyboard_input(KeyboardInput(keys=[KeyCode.KEY_B]))
driver.send_keyboard_input(KeyboardInput())
```

### Multiple Keys at Once

The CH9329 supports up to 6 simultaneous keys, which is more efficient than pressing keys individually:

```python
# Efficient: Press multiple keys at once
driver.send_keyboard_input(KeyboardInput(
    keys=[KeyCode.KEY_A, KeyCode.KEY_B, KeyCode.KEY_C]
))
driver.send_keyboard_input(KeyboardInput())
```

## Thread Safety

The library is **not thread-safe**. If you need concurrent access, use proper locking:

```python
import threading
from ch9329py import CH9329Driver, SerialAdapter, KeyboardInput, KeyCode

adapter = SerialAdapter("/dev/ttyUSB0", 9600)
driver = CH9329Driver(adapter)
lock = threading.Lock()

def task1():
    with lock:
        driver.send_keyboard_input(KeyboardInput(keys=[KeyCode.KEY_A]))
        driver.send_keyboard_input(KeyboardInput())

def task2():
    with lock:
        driver.send_keyboard_input(KeyboardInput(keys=[KeyCode.KEY_B]))
        driver.send_keyboard_input(KeyboardInput())

# Run tasks in threads
t1 = threading.Thread(target=task1)
t2 = threading.Thread(target=task2)
t1.start()
t2.start()
t1.join()
t2.join()
```

## Best Practices

1. **Always use context managers** for automatic cleanup:
   ```python
   with SerialAdapter("/dev/ttyUSB0", 9600) as adapter:
       with CH9329Driver(adapter) as driver:
           driver.send_keyboard_input(KeyboardInput(keys=[KeyCode.KEY_A]))
           driver.send_keyboard_input(KeyboardInput())
   ```

2. **Always release keys/buttons** after pressing:
   ```python
   # Press
   driver.send_keyboard_input(KeyboardInput(keys=[KeyCode.KEY_A]))
   # Release (DON'T FORGET!)
   driver.send_keyboard_input(KeyboardInput())
   ```

3. **Handle errors gracefully**:
   ```python
   try:
       from ch9329py import MouseInput
       driver.send_mouse_input(MouseInput(x=10, y=10))
   except ValueError as e:
       print(f"Invalid input: {e}")
   ```

4. **Use type hints** in your code:
   ```python
   def my_function(driver: CH9329Driver) -> None:
       from ch9329py import KeyboardInput, KeyCode
       driver.send_keyboard_input(KeyboardInput(keys=[KeyCode.KEY_A]))
       driver.send_keyboard_input(KeyboardInput())
   ```

## See Also

- [Home](../index.md) - Getting started and examples
- [Installation](../installation.md) - Installation instructions
