# Test-First Prompting (TFP) Prompt: [FEATURE_NAME]

Use this template to construct a prompt for AI code generation. Fill in each section, then provide the complete prompt to the AI. The AI's job is to generate an implementation that passes the tests -- not to co-create the tests.

---

## 1. Specification

Paste the relevant specification here. Include the description, inputs, outputs, rules, and invariants. The AI needs to know what the function or component must do.

```
[Paste specification content here]
```

---

## 2. Tests

Paste the failing test suite here. These tests define correct behavior. The AI must generate code that passes all of them.

```
[Paste test functions here]
```

---

## 3. Constraints

List non-functional requirements, coding constraints, and error handling expectations. These prevent the AI from generating code that passes tests but violates project standards.

- [Decimal arithmetic, not floating point]
- [Single responsibility per function, no function exceeds ~50 lines]
- [Error handling approach, e.g. raise ValueError for invalid inputs / return error tuple]
- [Any line or complexity limits]
- [Naming conventions]

---

## 4. Context

Describe related components, contracts, and integration points. If this function depends on other components or is depended upon, the AI needs to know the interfaces.

- Dependencies: [e.g. SeatInventory provides get_seat_status(), set_seat_status()]
- Contracts: [e.g. PricingEngine.calculate(section, event_id, group_size) -> PriceResult]
- Integration notes: [e.g. "Use the injectable clock for all time comparisons"]

---

## Prompt to AI

Combine the sections above into a single prompt, ending with:

```
Generate a [language] [function/class] that passes all tests.
```
