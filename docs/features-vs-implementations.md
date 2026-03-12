# Features vs Implementations in STDD
## Language Independence in Specification & Test-Driven Development

Author: Frank Heikens
Version: 1.1
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
- [10. Multi-Language Test Runner](#10-multi-language-test-runner)
- [11. Canonical-to-Executable Test Translation](#11-canonical-to-executable-test-translation)
- [12. When to Use Multiple Languages](#12-when-to-use-multiple-languages)
- [13. Contract Compatibility Across Languages](#13-contract-compatibility-across-languages)
- [14. Conclusion](#14-conclusion)

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

# 10. Multi-Language Test Runner

Canonical acceptance cases (Section 6) define behavior in YAML. When a feature has implementations in multiple languages, each language needs a **test runner** that loads and executes the same YAML cases. The YAML file is the single source of truth. Each language's runner is a thin adapter that translates YAML data into native function calls and assertions.

### Canonical Acceptance Cases

Using the `cart_total` feature from earlier sections:

```yaml
# features/cart_total/acceptance_cases.yaml
feature: cart_total
cases:
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

  - name: zero tax rate
    input:
      items: [10, 20]
      tax_rate: 0.0
    expected:
      total: 30
```

### Python Test Runner

```python
# implementations/python/test_cart_total.py
import yaml
import pytest
from cart_total import calculate_total

def load_cases():
    with open("../../features/cart_total/acceptance_cases.yaml") as f:
        data = yaml.safe_load(f)
    return data["cases"]

@pytest.mark.parametrize("case", load_cases(), ids=lambda c: c["name"])
def test_cart_total(case):
    result = calculate_total(case["input"]["items"], case["input"]["tax_rate"])
    assert result == case["expected"]["total"], (
        f"Case '{case['name']}': expected {case['expected']['total']}, got {result}"
    )
```

### Go Test Runner

```go
// implementations/go/cart_total_test.go
package cart

import (
    "os"
    "testing"

    "gopkg.in/yaml.v3"
)

type AcceptanceSuite struct {
    Feature string `yaml:"feature"`
    Cases   []struct {
        Name     string `yaml:"name"`
        Input    struct {
            Items   []float64 `yaml:"items"`
            TaxRate float64   `yaml:"tax_rate"`
        } `yaml:"input"`
        Expected struct {
            Total float64 `yaml:"total"`
        } `yaml:"expected"`
    } `yaml:"cases"`
}

func loadCases(t *testing.T) AcceptanceSuite {
    t.Helper()
    data, err := os.ReadFile("../../features/cart_total/acceptance_cases.yaml")
    if err != nil {
        t.Fatalf("failed to read acceptance cases: %v", err)
    }
    var suite AcceptanceSuite
    if err := yaml.Unmarshal(data, &suite); err != nil {
        t.Fatalf("failed to parse acceptance cases: %v", err)
    }
    return suite
}

func TestCartTotal(t *testing.T) {
    suite := loadCases(t)
    for _, tc := range suite.Cases {
        t.Run(tc.Name, func(t *testing.T) {
            result := CalculateTotal(tc.Input.Items, tc.Input.TaxRate)
            if result != tc.Expected.Total {
                t.Fatalf("expected %v, got %v", tc.Expected.Total, result)
            }
        })
    }
}
```

### How It Works

The YAML file contains every acceptance case for the feature. Each language's test runner performs the same steps:

1. Load the YAML file
2. Iterate over the cases
3. Call the implementation function with the inputs from each case
4. Assert that the result matches the expected output

No test logic lives in the YAML. No behavior logic lives in the runner. The runner is a mechanical adapter between the canonical format and the language's test framework.

If a new acceptance case is added to the YAML file, every language's test suite picks it up automatically on the next run. This guarantees that all implementations are tested against the same behavioral expectations.

---

# 11. Canonical-to-Executable Test Translation

Section 10 shows how test runners load YAML cases at runtime. An alternative approach is to **translate** canonical YAML cases into language-specific test files ahead of time. This is useful when teams prefer static, committed test files over dynamic YAML loading, or when the target test framework does not easily support data-driven tests.

### The Translation Workflow

1. **Read** canonical cases from the YAML file
2. **Map inputs** to language-specific types (e.g., YAML lists become Python lists or Go slices)
3. **Map expected outputs** to language-specific assertions (e.g., `assert ==` in Python, `if result != expected` in Go)
4. **Handle language-specific error conventions** (e.g., Python raises exceptions, Go returns error values)

### Source YAML Case

```yaml
# features/cart_total/acceptance_cases.yaml (excerpt)
- name: negative item price
  input:
    items: [-5, 20]
    tax_rate: 0.10
  expected:
    error: "negative item price not allowed"
```

### Translated to Python (pytest)

```python
def test_negative_item_price():
    with pytest.raises(ValueError, match="negative item price not allowed"):
        calculate_total([-5, 20], 0.10)
```

Python uses exceptions for error conditions. The translator maps the `error` field in the YAML to a `pytest.raises` block with a match on the error message.

### Translated to Go (table-driven test)

```go
func TestNegativeItemPrice(t *testing.T) {
    _, err := CalculateTotal([]float64{-5, 20}, 0.10)
    if err == nil {
        t.Fatal("expected error, got nil")
    }
    expected := "negative item price not allowed"
    if err.Error() != expected {
        t.Fatalf("expected error %q, got %q", expected, err.Error())
    }
}
```

Go uses error return values instead of exceptions. The translator maps the `error` field to a check on the returned `error` value. Note that the Go function signature changes to `(float64, error)` when error cases are part of the specification.

### Translation Rules

| YAML field | Python | Go |
|---|---|---|
| `input.items` (list) | `list` | `[]float64` |
| `input.tax_rate` (float) | `float` | `float64` |
| `expected.total` (number) | `assert result == expected` | `if result != expected` |
| `expected.error` (string) | `pytest.raises(ValueError)` | `if err == nil` / `err.Error()` |

The translation can be done manually or automated with a script. In either case, the YAML remains the authoritative source. If a translated test diverges from the YAML, the YAML wins and the translated test must be updated.

---

# 12. When to Use Multiple Languages

STDD's separation of features from implementations makes multi-language support possible. That does not mean every project should use it.

### When Multiple Implementations Are Valuable

- **Performance comparison.** Implementing a computationally intensive feature in both Python and Rust to benchmark and choose the right tool for production.
- **Platform requirements.** A mobile SDK that must ship native libraries for iOS (Swift) and Android (Kotlin), both satisfying the same behavioral specification.
- **Team skills.** A data science team writes prototypes in Python while the platform team writes production services in Go. Both implementations share the same acceptance cases.
- **Migration.** Porting a legacy Java service to a modern language. The canonical tests verify that the new implementation preserves all existing behavior.

### When a Single Language Is Sufficient

Most projects do not need multiple implementations. If the team uses one language, the system runs on one platform, and there is no concrete plan to change languages, a single implementation is the right choice. STDD still provides value in this case: the canonical specification and tests protect against regressions and support future regeneration within the same language.

### The Overhead of Multiple Implementations

Each additional language implementation requires:

- A test runner or translated test suite (Section 10, Section 11)
- CI/CD pipeline configuration for each language
- Dependency management for each language ecosystem
- Code review capacity across language boundaries

This overhead is justified only when the benefits (performance, platform coverage, migration safety) outweigh the maintenance cost.

### Decision Criteria

If you do not have a concrete reason to maintain multiple implementations, do not maintain them. STDD's language independence is about **capability**, not obligation. The specification and canonical tests are always language-neutral, which means you can add a second implementation later if the need arises. You do not have to plan for it upfront.

The question to ask is: **"Does maintaining this additional implementation solve a real problem today?"** If the answer is no, keep a single implementation and move on.

---

# 13. Contract Compatibility Across Languages

When a system does use multiple language implementations, verifying that they all satisfy the same contracts becomes critical. Shared acceptance cases are the foundation, but cross-language integration introduces additional concerns.

### Shared Acceptance Cases as the Compatibility Layer

The canonical YAML acceptance cases (Section 6) serve as the compatibility contract. If Implementation A in Python and Implementation B in Go both pass the same acceptance cases, they are behaviorally equivalent for the scenarios covered by those cases.

This is sufficient when the implementations are independent (e.g., two separate services that do not call each other). Run each implementation's test suite against the shared YAML and verify that all cases pass.

### Integration Testing Across Language Boundaries

When implementations interact across language boundaries, acceptance cases alone are not enough. Common integration patterns include:

- **HTTP/gRPC boundaries.** A Python service calls a Go service over HTTP. Integration tests verify that request/response serialization preserves the contract.
- **FFI (Foreign Function Interface).** A Python application calls a Go library via C bindings. Integration tests verify that type marshaling across the FFI boundary preserves values.
- **Message queues.** A Go producer writes messages that a Python consumer reads. Integration tests verify that serialization formats (JSON, Protobuf) are compatible.

For each integration pattern, the test strategy is:

1. Define the expected inputs and outputs in the canonical YAML
2. Test each side independently against the YAML (unit-level contract verification)
3. Test the integration point with end-to-end cases that cross the language boundary

### When Cross-Language Compatibility Matters

- **Microservices.** Services written in different languages must agree on API contracts. Canonical acceptance cases define the expected behavior at each service boundary.
- **Polyglot systems.** A system that uses Python for data processing, Go for API serving, and Rust for compute-intensive modules must verify that data flows correctly across language boundaries.
- **Shared libraries.** A core algorithm implemented in multiple languages (e.g., for mobile and server) must produce identical results for identical inputs. The canonical cases serve as the cross-platform correctness guarantee.

### Compatibility Verification Strategy

```
Canonical YAML Cases
        |
        +---> Python tests pass?  [YES/NO]
        |
        +---> Go tests pass?      [YES/NO]
        |
        +---> Integration tests pass across boundaries?  [YES/NO]
        |
        All YES = Contract compatibility verified
```

If any implementation fails a canonical case, the contract is broken. Fix the implementation, not the case. The YAML is the source of truth.

---

# 14. Conclusion

STDD separates **what the system must do** from **how the system is implemented**.

Features define behavior.
Implementations realize that behavior in specific languages.

By maintaining this separation, STDD enables:

- portable feature definitions
- safe regeneration of implementations
- multi-language support through shared test runners and canonical cases
- contract compatibility verification across language boundaries
- long-term system stability

Multi-language support is a capability, not a requirement. Most projects benefit from a single implementation backed by language-neutral specifications. When multiple implementations are needed, the canonical acceptance cases provide the compatibility guarantee, and thin test runners or translated test files bridge the gap between the specification and each language's test framework.

In STDD, the feature is permanent.

The implementation is replaceable.

---

For guidance on writing feature specifications, see [Writing Specifications](writing-specifications.md). For non-functional quality constraints, see the [NFR Framework](nfr-framework.md). For a complete multi-language example, see the [Seat Reservation API](../examples/seat-reservation.md).
