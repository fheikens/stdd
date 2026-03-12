# STDD Examples
## Practical Examples of Specification & Test-Driven Development

Author: Frank Heikens
Version: 1.0
Date: 2026

---

## Table of Contents

- [1. Introduction](#1-introduction)
- [2. Why Examples Matter](#2-why-examples-matter)
- [3. Example 1: Shopping Cart Total](#3-example-1-shopping-cart-total)
- [4. Example 2: User Login Validation](#4-example-2-user-login-validation)
- [5. Example 3: Seat Reservation Hold](#5-example-3-seat-reservation-hold)
- [6. Example 4: Fraud Score Classification](#6-example-4-fraud-score-classification)
- [7. What These Examples Show](#7-what-these-examples-show)

---

# 1. Introduction

A methodology becomes easier to understand when people can see it applied to concrete problems.

The purpose of this document is to show how **Specification & Test-Driven Development (STDD)** works in practice.

Each example follows the same pattern:

1. Define the specification
2. Define the expected behavior
3. Define the tests
4. Generate the implementation
5. Execute the tests
6. Accept or regenerate the implementation

The examples are intentionally simple.

The goal is not to show advanced software engineering, but to show how STDD turns behavior into the stable center of development.

Each example includes a structured specification following the format described in [Writing Specifications](../docs/writing-specifications.md).

---

# 2. Why Examples Matter

The idea behind STDD is simple:

- specifications define what the system must do
- tests verify that behavior
- AI generates the implementation

Examples make that concrete.

They show that the implementation is not the starting point.

The starting point is always the expected behavior of the system.

---

# 3. Example 1: Shopping Cart Total

## Specification

```
Feature: Shopping Cart Total
Version: 1.0
Status: accepted

Description:
  The system must calculate the total price of items
  in a shopping cart including tax.
  The tax rate must be configurable per request.

Inputs:
  - items: list of numeric prices
  - tax_rate: decimal between 0 and 1

Outputs:
  - total: decimal

Invariants:
  - The total must never be negative.
  - The total must equal subtotal + (subtotal * tax_rate).
```

## Expected Behavior

- A cart with items `10` and `20` and tax rate `0.10` returns `33`
- An empty cart returns `0`
- A tax rate of `0` returns the subtotal

## Example Tests

```python
def test_total_price_with_tax():
    assert calculate_total([10, 20], 0.10) == 33

def test_empty_cart():
    assert calculate_total([], 0.10) == 0

def test_total_price_without_tax():
    assert calculate_total([10, 20], 0.0) == 30
```

## Possible Generated Implementation

```python
def calculate_total(items, tax_rate):
    subtotal = sum(items)
    return subtotal + (subtotal * tax_rate)
```

## STDD Observation

The important artifact is not the function itself.

The important artifact is the behavior described by the tests.

If the code is regenerated later, the same tests still define the required behavior.

---

# 4. Example 2: User Login Validation

## Specification

```
Feature: User Login Validation
Version: 1.0
Status: accepted

Description:
  The system must validate a username and password combination.
  If the credentials are valid, access is granted.
  If either value is invalid, access is denied.

Inputs:
  - username: string
  - password: string

Outputs:
  - result: boolean (True if access granted, False if denied)

Invariants:
  - The system must not reveal whether the username
    or the password was incorrect.

Failure Conditions:
  - Empty username or password: rejected, returns False.
```

## Expected Behavior

- Valid username and password returns `True`
- Invalid password returns `False`
- Unknown username returns `False`

## Example Tests

```python
def test_valid_login():
    assert validate_login("frank", "secret123") is True

def test_invalid_password():
    assert validate_login("frank", "wrongpass") is False

def test_unknown_user():
    assert validate_login("unknown", "secret123") is False
```

## Possible Generated Implementation

```python
USERS = {
    "frank": "secret123"
}

def validate_login(username, password):
    return USERS.get(username) == password
```

## STDD Observation

Even in a simple example, behavior comes first.

The implementation can later move to a database, external identity provider, or hashed-password system.

As long as the tests remain valid, the behavior stays stable.

---

# 5. Example 3: Seat Reservation Hold

## Specification

```
Feature: Seat Reservation Hold
Version: 1.0
Status: accepted

Description:
  The system must place a temporary hold on a seat
  for a fixed number of minutes. A seat that is already
  held or sold cannot be held again. An expired hold
  must no longer block a new hold.

Inputs:
  - seat: {status, hold_until}
  - current_time: datetime

Outputs:
  - result: boolean (True if seat can be held)

Invariants:
  - A seat can be in exactly one state: available, held, or sold.
  - A sold seat cannot transition to any other state.
  - No more than one active hold may exist for a single seat.

Failure Conditions:
  - Seat does not exist: rejected with error.
```

## Expected Behavior

- An available seat can be held
- A held seat cannot be held again before expiration
- An expired hold allows a new hold
- A sold seat can never be held

## Example Tests

```python
from datetime import datetime, timedelta

def test_available_seat_can_be_held():
    seat = {"status": "available", "hold_until": None}
    now = datetime(2026, 1, 1, 10, 0, 0)

    assert can_hold_seat(seat, now) is True

def test_active_hold_blocks_new_hold():
    seat = {
        "status": "held",
        "hold_until": datetime(2026, 1, 1, 10, 5, 0)
    }
    now = datetime(2026, 1, 1, 10, 0, 0)

    assert can_hold_seat(seat, now) is False

def test_expired_hold_allows_new_hold():
    seat = {
        "status": "held",
        "hold_until": datetime(2026, 1, 1, 9, 55, 0)
    }
    now = datetime(2026, 1, 1, 10, 0, 0)

    assert can_hold_seat(seat, now) is True

def test_sold_seat_cannot_be_held():
    seat = {"status": "sold", "hold_until": None}
    now = datetime(2026, 1, 1, 10, 0, 0)

    assert can_hold_seat(seat, now) is False
```

## Possible Generated Implementation

```python
def can_hold_seat(seat, now):
    if seat["status"] == "sold":
        return False

    if seat["status"] == "available":
        return True

    if seat["status"] == "held":
        return seat["hold_until"] <= now

    return False
```

## STDD Observation

This example shows that STDD is useful for workflow logic, not only for mathematical functions.

The behavior is still defined before the implementation exists.

---

# 6. Example 4: Fraud Score Classification

## Specification

```
Feature: Fraud Score Classification
Version: 1.0
Status: accepted

Description:
  The system must classify a transaction score
  into one of three risk categories.

Inputs:
  - score: integer (0-100)

Outputs:
  - classification: string (low, medium, or high)

Rules:
  - score below 30: low
  - score from 30 up to but not including 70: medium
  - score 70 or higher: high

Invariants:
  - Every valid score must produce exactly one classification.
  - The classification must be one of: low, medium, high.

Constraints:
  - Score must be between 0 and 100 inclusive.

Failure Conditions:
  - Score outside 0-100 range: rejected with validation error.
```

## Expected Behavior

- `10` returns `low`
- `30` returns `medium`
- `69` returns `medium`
- `70` returns `high`

## Example Tests

```python
def test_low_score():
    assert classify_score(10) == "low"

def test_medium_score_lower_bound():
    assert classify_score(30) == "medium"

def test_medium_score_upper_bound():
    assert classify_score(69) == "medium"

def test_high_score():
    assert classify_score(70) == "high"
```

## Possible Generated Implementation

```python
def classify_score(score):
    if score < 30:
        return "low"
    if score < 70:
        return "medium"
    return "high"
```

## STDD Observation

This example is close to real scoring logic.

The implementation is small, but the important part is that the boundaries are defined and verified by tests.

This avoids ambiguity and protects the system against regressions.

---

# 7. What These Examples Show

These examples demonstrate the core STDD pattern.

## 1. Specification comes first

The required behavior is defined before code exists.

## 2. Tests make behavior executable

The system is not defined only by text, but by verifiable checks.

## 3. Implementation is replaceable

The code can be regenerated as long as the tests continue to pass.

## 4. Stability comes from behavior, not code

The tests remain the source of truth.

---

# Conclusion

STDD is not only a theory.

It is a practical development method that can be applied to simple functions, workflow rules, validation logic, and scoring systems.

In every case, the principle remains the same:

- define the behavior
- express the behavior as tests
- generate the implementation
- verify with tests
- regenerate if necessary

That is what makes software stable in an era of AI-generated code.
