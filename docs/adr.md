# Architecture Decision Records (ADR)

Key design decisions for ch9329py.

## ADR-0001: State-Based API Design

**Decision:** Use state-based API (send complete input states) instead of event-based (press/release).

**Why:** Matches USB HID protocol directly, no hidden state, predictable behavior.

[Read full ADR →](adr/0001-state-based-api-design.md)

## ADR-0002: Adopt Pydantic for Data Models

**Decision:** Use Pydantic v2 for input validation.

**Why:** Runtime validation, type safety, clear error messages.

[Read full ADR →](adr/0002-adopt-pydantic-for-data-models.md)

## ADR-0003: Adopt evdev as Domain Model

**Decision:** Use Linux evdev codes (KEY_A, BTN_LEFT) instead of raw USB HID codes.

**Why:** Semantic naming, Linux standard, familiar to developers.

[Read full ADR →](adr/0003-adopt-evdev-as-domain-model.md)
