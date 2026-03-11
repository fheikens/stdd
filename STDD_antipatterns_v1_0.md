
# STDD Anti‑Patterns
## Common Mistakes in Specification & Test‑Driven Development

Author: Frank Heikens
Version: 1.0
Date: 2026

---

## Table of Contents

- [1. Introduction](#1-introduction)
- [2. Writing Code Before Specifications](#2-writing-code-before-specifications)
- [3. Vague or Ambiguous Specifications](#3-vague-or-ambiguous-specifications)
- [4. Tests That Do Not Verify Behavior](#4-tests-that-do-not-verify-behavior)
- [5. Over‑Fitting the Implementation](#5-over-fitting-the-implementation)
- [6. Hidden State and Side Effects](#6-hidden-state-and-side-effects)
- [7. Non‑Deterministic Tests](#7-non-deterministic-tests)
- [8. Weak Test Coverage](#8-weak-test-coverage)
- [9. Treating Generated Code as Untouchable](#9-treating-generated-code-as-untouchable)
- [10. Mixing Architecture and Behavior](#10-mixing-architecture-and-behavior)
- [11. Ignoring Regeneration](#11-ignoring-regeneration)
- [12. Conclusion](#12-conclusion)

---

# 1. Introduction

Specification & Test‑Driven Development (STDD) relies on a simple idea:

Behavior defines the system.

Specifications describe the behavior.  
Tests verify the behavior.  
AI generates the implementation.

However, several common mistakes can undermine this model.

These mistakes are called **anti‑patterns**.

An anti‑pattern is a practice that appears reasonable but leads to unstable or fragile systems.

Understanding these anti‑patterns helps teams avoid the most common pitfalls when applying STDD.

---

# 2. Writing Code Before Specifications

One of the most common mistakes is starting with the implementation.

Developers may ask an AI system to generate code before defining the expected behavior.

This reverses the STDD process.

Incorrect workflow:

1. Generate code
2. Add tests later
3. Adjust tests to match the code

Correct STDD workflow:

1. Define specification
2. Define behavior
3. Define tests
4. Generate implementation

When code is generated before behavior is defined, the implementation becomes the accidental definition of the system.

---

# 3. Vague or Ambiguous Specifications

Specifications must be precise.

A vague specification leads to multiple possible implementations.

Example of a vague specification:

> Calculate the total price of a shopping cart.

Missing information:

- Are taxes included?
- How are discounts applied?
- What happens with empty carts?
- What currency rounding rules apply?

Ambiguity leads to unstable implementations and failing tests.

STDD requires **explicit behavior definitions**.

---

# 4. Tests That Do Not Verify Behavior

Tests must verify observable behavior.

A common anti‑pattern is writing tests that verify internal implementation details.

Example of a bad test:

```python
assert cart.subtotal == 30
```

This test assumes a specific implementation structure.

Better test:

```python
assert calculate_total([10,20], 0.10) == 33
```

Tests should verify outcomes, not internal mechanics.

---

# 5. Over‑Fitting the Implementation

Another mistake is creating tests that mirror a specific implementation.

Example:

If the implementation uses three internal steps, tests should not depend on those steps.

Tests should verify **results**, not intermediate calculations.

Over‑fitted tests prevent regeneration because they lock the system to a specific implementation.

---

# 6. Hidden State and Side Effects

Hidden state breaks predictability.

Examples:

- global variables
- shared mutable objects
- background processes modifying data

Side effects also introduce instability.

Examples:

- writing files
- calling external APIs
- updating databases

In STDD architectures, side effects must be isolated behind clear interfaces.

---

# 7. Non‑Deterministic Tests

Tests must always produce the same result for the same input.

Non‑deterministic tests break the regeneration loop.

Common causes:

- random number generation
- system time
- external API calls
- asynchronous race conditions

Example of a problematic test:

```python
assert generate_id() == 12345
```

The output may change every run.

Instead, the behavior must be controlled or mocked.

---

# 8. Weak Test Coverage

Tests define the boundaries of system behavior.

If important scenarios are not tested, implementations may behave incorrectly without detection.

Weak coverage allows AI‑generated implementations to pass tests while violating expectations.

Tests should cover:

- normal cases
- edge cases
- boundary conditions
- failure scenarios

---

# 9. Treating Generated Code as Untouchable

In traditional development, code is often treated as a long‑lived artifact.

In STDD this assumption changes.

Generated code should be treated as **replaceable**.

If the code becomes complex, inefficient, or difficult to maintain, it should be regenerated.

The tests remain the true definition of the system.

---

# 10. Mixing Architecture and Behavior

Behavior definitions should not depend on architectural decisions.

Example of a problematic specification:

> The system must use a relational database to store cart items.

This is an implementation detail.

Better specification:

> The system must persist cart items and allow them to be retrieved.

Architecture may change later without affecting the system behavior.

---

# 11. Ignoring Regeneration

Regeneration is a key capability of STDD.

Some teams fall back to traditional practices and manually modify generated code.

This re‑introduces the risks of fragile implementations.

Instead, the proper STDD approach is:

1. Update the specification
2. Update the tests
3. Regenerate the implementation

This ensures the behavior remains the source of truth.

---

# 12. Conclusion

STDD works best when its principles are followed consistently.

The most common anti‑patterns arise when teams revert to traditional code‑first thinking.

Avoiding these anti‑patterns ensures that:

- behavior remains clearly defined
- implementations remain replaceable
- regeneration remains safe

When applied correctly, STDD provides a stable foundation for building software in the age of AI‑generated code.
