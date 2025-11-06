# ADR 0001: State-Based API Design

## Status

Accepted

## Date

2025-11-05

## Context

CH9329 uses USB HID protocol which works by sending complete device state (all pressed keys/buttons) rather than discrete press/release events.

## Decision

Implement state-based API with three core methods:

- `send_keyboard_input(input_data: KeyboardInput)`
- `send_mouse_input(input_data: MouseInput)`
- `send_media_key_input(input_data: MediaKeyInput)`

Users send complete input states. Driver maintains no internal state.

## Rationale

- **Matches USB HID protocol**: Direct mapping to hardware behavior
- **Predictable**: No hidden state, what you send is what device receives
- **Testable**: Each call is independent
- **Precise control**: Users control exact timing

## Implications

**Positive:**

- Efficient (one packet per state change)
- No state synchronization issues
- Supports complex scenarios (6-key rollover, simultaneous buttons)

**Concerns:**

- Verbose for simple operations (press + release requires two calls)
- Users must remember to release keys/buttons

## Alternatives

**Event-based API (press/release methods)**: Rejected because doesn't match HID semantics and requires driver to maintain state.

**Auto-release convenience methods**: Rejected because hides behavior and prevents precise timing control.

## References

- USB HID Specification: https://www.usb.org/hid
