# ADR 0002: Adopt Pydantic for Data Models

## Status

Accepted

## Date

2025-11-05

## Context

Input state models (`KeyboardInput`, `MouseInput`, `MediaKeyInput`) need validation to prevent invalid data from reaching the device (e.g., more than 6 keys, out-of-range mouse movement).

## Decision

Use Pydantic v2 for all input data models with Field validation.

## Rationale

- **Runtime validation**: Catches errors before sending to device
- **Type safety**: Integrates with mypy
- **Clear error messages**: ValidationError explains what's wrong
- **Self-documenting**: Field constraints serve as documentation

## Implications

**Positive:**
- Invalid input caught early with clear errors
- No need for manual validation code
- Good developer experience (IDE autocomplete, type checking)

**Concerns:**
- Adds dependency on Pydantic
- Slight performance overhead (negligible for HID use case)

## Alternatives

**Manual validation**: Rejected because error-prone and requires writing/maintaining validation logic.

**Dataclasses with custom validators**: Rejected because reinventing what Pydantic already does well.

## References

- Pydantic documentation: https://docs.pydantic.dev/
