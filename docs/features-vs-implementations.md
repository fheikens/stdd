# Features vs Implementations in STDD
## Language Independence in Specification & Test-Driven Development

Author: Frank Heikens
Version: 1.0
Date: 2026

---

## Table of Contents

- [1. Introduction](#1-introduction)
- [2. The Core Principle](#2-the-core-principle)
- [3. What Is a Feature?](#3-what-is-a-feature)
- [4. What Is an Implementation?](#4-what-is-an-implementation)
- [5. Why Language Independence Matters](#5-why-language-independence-matters)
- [6. Canonical Behavior Tests](#6-canonical-behavior-tests)
- [7. Language-Specific Executable Tests](#7-language-specific-executable-tests)
- [8. Recommended Repository Structure](#8-recommended-repository-structure)
- [9. Regeneration Across Languages](#9-regeneration-across-languages)
- [10. Conclusion](#10-conclusion)

---

# 1. Introduction

Specification & Test-Driven Development (STDD) separates **behavior** from **implementation**.

Traditional development often couples features tightly with a specific programming language.
In STDD, the goal is to ensure that **behavior remains stable even if the implementation or language changes**.

This requires a clear distinction between:

- **Features** – the behavior of the system
- **Implementations** – language-specific realizations of that behavior

---

# 2. The Core Principle

A central idea of STDD is:

**A feature is defined once.
It may be implemented many times.**

Or more simply:

**The feature is permanent.
The implementation is replaceable.**

Specifications and tests define the behavior.
Implementations simply satisfy that behavior.

---

# 3. What Is a Feature?

A feature describes **what the system must do**, independent of technology or programming language.

A feature typically contains:

- specification
- behavior scenarios
- invariants
- acceptance criteria
- canonical test cases

Example feature:

Shopping Cart Total

The system must calculate the total price of items in a shopping cart including tax.

The tax rate must be configurable.

Edge cases:

- empty cart returns zero
- tax rate zero returns subtotal

This definition is **language neutral**.

---

# 4. What Is an Implementation?

An implementation is a **language-specific realization of a feature**.

Examples:

- Python implementation
- Go implementation
- Java implementation
- Rust implementation

Each implementation must satisfy the same specification and behavioral tests.

Example implementations:

Python:

```python
def calculate_total(items, tax_rate):
    subtotal = sum(items)
    return subtotal + subtotal * tax_rate
```

Go:

```go
func CalculateTotal(items []float64, taxRate float64) float64 {
    subtotal := 0.0
    for _, v := range items {
        subtotal += v
    }
    return subtotal + subtotal * taxRate
}
```

Both implementations satisfy the same feature definition.

> **Note:** These simplified examples use floating-point arithmetic for clarity. In production systems involving monetary calculations, the [NFR Framework](nfr-framework.md) requires decimal types with defined precision. Go implementations would use a decimal library such as `shopspring/decimal`.

---

# 5. Why Language Independence Matters

Separating features from implementations provides several advantages.

### Portability

The same feature can be implemented in multiple languages.

### Regeneration

AI can regenerate implementations without changing the system definition.

### Comparison

Different implementations can be compared for:

- performance
- readability
- maintainability

### Longevity

If a language becomes obsolete, the feature definition remains valid.

---

# 6. Canonical Behavior Tests

Canonical tests belong to the **feature definition**.

They describe behavior in a language-neutral format.

Example:

```yaml
- name: total with tax
  input:
    items: [10, 20]
    tax_rate: 0.10
  expected:
    total: 33

- name: empty cart
  input:
    items: []
    tax_rate: 0.10
  expected:
    total: 0
```

These tests define the behavior that every implementation must satisfy.

---

# 7. Language-Specific Executable Tests

Each implementation contains executable tests written in the target language.

Python example:

```python
def test_total_with_tax():
    assert calculate_total([10,20], 0.10) == 33
```

Go example:

```go
func TestTotalWithTax(t *testing.T) {
    result := CalculateTotal([]float64{10,20}, 0.10)
    if result != 33 {
        t.Fatalf("expected 33, got %v", result)
    }
}
```

Both implementations verify the same behavior.

---

# 8. Recommended Repository Structure

An STDD repository separates **behavior definition** (features, specifications, acceptance cases) from **implementation** (language-specific source and tests). Each feature has a single specification and may have multiple implementations in different languages.

For the canonical repository structure and examples, see [Engineering Playbook](engineering-playbook.md), Section 2.

---

# 9. Regeneration Across Languages

Because behavior is defined independently of implementation, STDD allows implementations to be regenerated.

Examples:

- regenerate Python implementation
- generate a new Rust implementation
- generate a high-performance C++ version

All implementations must satisfy the same canonical tests.

This ensures that **behavior remains stable even when implementations change**.

---

# 10. Conclusion

STDD separates **what the system must do** from **how the system is implemented**.

Features define behavior.
Implementations realize that behavior in specific languages.

By maintaining this separation, STDD enables:

- portable feature definitions
- safe regeneration of implementations
- multi-language support
- long-term system stability

In STDD, the feature is permanent.

The implementation is replaceable.

---

For guidance on writing feature specifications, see [Writing Specifications](writing-specifications.md). For non-functional quality constraints, see the [NFR Framework](nfr-framework.md). For a complete multi-language example, see the [Seat Reservation API](../examples/seat-reservation.md).
