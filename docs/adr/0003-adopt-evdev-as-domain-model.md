# ADR 003: Adopt evdev as Domain Model for Input Events

## Status

Accepted

## Date

2025-11-03

## Context

The CH9329 chip uses USB HID keycodes (e.g., 0x04 for 'A') internally. We need to choose a domain model for representing input events in the public API.

The target deployment environment is Linux systems, and we want to support:
- Keyboard input
- Mouse operations
- Game controller input
- AI-generated input sequences

## Decision

Adopt the Linux `evdev` event code system as our domain model for input events.

## Rationale

1. **Standardization** - evdev is the Linux standard for input events
2. **Broad Coverage** - Supports keyboard (KEY_*), mouse (BTN_*, REL_*, ABS_*), and game controllers (BTN_A, ABS_RX, etc.)
3. **AI-Friendly** - Well-documented, semantic names make it easier for AI to generate input sequences
4. **Developer-Friendly** - Linux developers are familiar with evdev concepts and naming

## Implications

### Positive

- Unified abstraction for diverse input devices
- Rich ecosystem and documentation
- Clear, semantic event names

### Concerns

- Requires translation layer from evdev codes to USB HID codes
- Not all evdev events are supported by CH9329
- Need clear error handling for unsupported events

## Alternatives

### Use USB HID Codes Directly

Keep the current approach using raw USB HID keycodes.

**Rejected because:**
- Less semantic (0x04 vs KEY_A)
- Harder for AI to generate correct sequences
- Limited to keyboard/mouse, doesn't extend well to controllers

### Create Custom Abstraction

Design our own event system.

**Rejected because:**
- Reinventing the wheel
- Less familiar to developers
- Would still need to map to something standard

## Future Direction

- Implement evdev to USB HID translation layer
- Define explicitly supported event types
- Add validation with clear error messages for unsupported events

## References

- Linux evdev documentation: https://www.kernel.org/doc/Documentation/input/event-codes.txt
- python-evdev library: https://python-evdev.readthedocs.io/
