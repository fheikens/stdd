
# The STDD Engineering Playbook
## Applying Specification & Test-Driven Development in Real Projects

Author: Frank Heikens
Version: 1.0
Date: 2026

---

## Table of Contents

- [1. Introduction](#1-introduction)
- [2. STDD in a Real Development Workflow](#2-stdd-in-a-real-development-workflow)
- [3. Typical Repository Structure](#3-typical-repository-structure)
- [4. Writing Specifications](#4-writing-specifications)
- [5. Writing Behavioral Tests](#5-writing-behavioral-tests)
- [6. Using AI to Generate Implementations](#6-using-ai-to-generate-implementations)
- [7. Continuous Integration with STDD](#7-continuous-integration-with-stdd)
- [8. Regeneration in Practice](#8-regeneration-in-practice)
- [9. Team Roles in STDD](#9-team-roles-in-stdd)
- [10. Example Development Cycle](#10-example-development-cycle)
- [11. Conclusion](#11-conclusion)

---

# 1. Introduction

The previous STDD documents describe the philosophy, method, architecture, and principles behind Specification & Test‑Driven Development.

This playbook explains how STDD is **applied in real engineering environments**.

It focuses on practical questions such as:

- How projects are structured
- How specifications are written
- How tests define behavior
- How AI generates implementations
- How teams integrate STDD with CI pipelines

The goal is to make STDD usable in everyday software engineering.

---

# 2. STDD in a Real Development Workflow

Traditional development often follows this pattern:

Design → Code → Test → Fix

STDD changes the order.

The STDD workflow is:

Specification → Behavior → Tests → AI Implementation → Verification

In practice this means:

1. Engineers define the specification.
2. Engineers write tests describing the expected behavior.
3. AI generates the implementation.
4. Tests verify the implementation.
5. If tests fail, the implementation is regenerated.

The key idea is that **tests define the system behavior before the code exists**.

---

# 3. Typical Repository Structure

An STDD project benefits from a clear repository structure.

Example:

project
```
features
│
└── cart_total
    ├── specification.md
    ├── scenarios.md
    ├── invariants.md
    └── acceptance_cases.yaml

implementations
│
└── cart_total
    ├── python
    │   ├── src
    │   └── tests
    │
    ├── go
    │   ├── src
    │   └── tests
    │
    └── java
        ├── src
        └── tests
```
Specifications define behavior.

Tests enforce behavior.

The implementation satisfies the tests.

---

# 4. Writing Specifications

Specifications describe **what the system must do**.

They must be:

- precise
- unambiguous
- testable
- independent of implementation details

A specification answers six questions:

1. What does the system do?
2. What are the inputs and outputs?
3. What are the behavioral scenarios?
4. What are the invariants?
5. What are the failure conditions?
6. What are the constraints?

Example specification:

```
Feature: Shopping Cart Total
Version: 1.0
Status: accepted

## Description

The system must calculate the total price of items in a shopping cart including tax.
The tax rate must be configurable per request.

## Inputs

- items: list of numeric prices
- tax_rate: decimal between 0 and 1

## Outputs

- total: decimal

## Behavioral Scenarios

Scenario: Normal cart with tax
  Given: Items [10, 20] and tax rate 0.10
  When: Total is calculated
  Then: Result is 33

Scenario: Empty cart
  Given: Items [] and tax rate 0.10
  When: Total is calculated
  Then: Result is 0

Scenario: Zero tax rate
  Given: Items [10, 20] and tax rate 0.0
  When: Total is calculated
  Then: Result is 30

## Invariants

- The total must never be negative.
- The total must equal subtotal + (subtotal * tax_rate).

## Failure Conditions

- Negative prices: rejected with validation error.
- Tax rate outside 0-1 range: rejected with validation error.
```

For comprehensive guidance on writing specifications, see [Writing Specifications](writing-specifications.md).

---

# 5. Writing Behavioral Tests

Tests translate specifications into executable checks.

Example test:

```python
def test_total_price():
    assert calculate_total([10,20], 0.10) == 33
```

Tests should cover:

- normal behavior
- edge cases
- boundary conditions
- failure scenarios

Tests define the **true behavior of the system**.

---

# 6. Using AI to Generate Implementations

Once specifications and tests exist, AI can generate implementations.

Example prompt to AI:

"Generate a Python function that satisfies the provided tests."

Possible implementation:

```python
def calculate_total(items, tax_rate):
    subtotal = sum(items)
    return subtotal + subtotal * tax_rate
```

The implementation is accepted only if all tests pass.

---

# 7. Continuous Integration with STDD

STDD integrates naturally with CI pipelines.

Typical pipeline:

1. Run test suite
2. Verify all tests pass
3. Reject failing implementations

Example CI workflow:

- push code
- run tests
- accept or reject build

Tests act as the gatekeeper for system behavior.

---

# 8. Regeneration in Practice

If an implementation becomes complex or difficult to maintain, it can be regenerated.

Process:

1. Keep the specification
2. Keep the tests
3. Regenerate the implementation
4. Run tests
5. Accept if tests pass

This allows systems to evolve without risking behavioral regressions.

---

# 9. Team Roles in STDD

STDD changes how teams collaborate.

Engineers focus on:

- defining behavior
- designing specifications
- writing tests

AI focuses on:

- generating implementations
- refactoring code
- optimizing performance

This creates a clear separation between **system definition** and **system implementation**.

---

# 10. Example Development Cycle

A typical STDD development cycle:

1. Write specification
2. Write tests
3. Generate implementation with AI
4. Run tests
5. Accept implementation if tests pass
6. Regenerate if tests fail

This loop can repeat as the system evolves.

---

# 11. Conclusion

STDD provides a structured way to combine human engineering insight with AI code generation.

By placing **behavior at the center of development**, STDD ensures that systems remain stable even as implementations evolve.

Specifications define the system.

Tests enforce the behavior.

AI generates the implementation.

This allows engineering teams to build reliable software in an era where code can be generated instantly.
