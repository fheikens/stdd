
# Writing Specifications in STDD
## From Vague Ideas to Testable Behavioral Definitions

Author: Frank Heikens
Version: 1.0
Date: 2026

---

## Table of Contents

- [1. Introduction](#1-introduction)
- [2. The Specification Problem](#2-the-specification-problem)
- [3. What a Specification Must Contain](#3-what-a-specification-must-contain)
- [4. Specification Levels](#4-specification-levels)
- [5. Anatomy of a Feature Specification](#5-anatomy-of-a-feature-specification)
- [6. Writing Behavioral Scenarios](#6-writing-behavioral-scenarios)
- [7. Writing Invariants](#7-writing-invariants)
- [8. Defining Acceptance Cases](#8-defining-acceptance-cases)
- [9. Declaring Technology and Domain Context](#9-declaring-technology-and-domain-context)
- [10. From Vague to Precise](#10-from-vague-to-precise)
- [11. Specification Templates](#11-specification-templates)
- [12. Specification Review Checklist](#12-specification-review-checklist)
- [13. Closing the Specification‑to‑Test Gap](#13-closing-the-specificationtotest-gap)
- [14. Common Specification Mistakes](#14-common-specification-mistakes)
- [15. Conclusion](#15-conclusion)

---

# 1. Introduction

In Specification & Test-Driven Development, the specification is the foundation.

Tests verify behavior. AI generates implementations. But both depend on the quality of the specification.

A vague specification produces vague tests. Vague tests allow incorrect implementations to pass.

The entire STDD loop depends on specifications being precise enough to produce meaningful tests.

Previous STDD documents describe this requirement clearly:

- Specifications must be precise
- Specifications must be unambiguous
- Specifications must be testable

However, knowing that specifications must be precise is not the same as knowing how to make them precise.

This document provides the practical guidance for writing specifications that are strong enough to drive the STDD process.

---

# 2. The Specification Problem

Writing good specifications is harder than writing code.

Code has a compiler or interpreter that enforces correctness. A function either runs or it does not.

Specifications have no such enforcement. A vague specification can look complete while leaving critical questions unanswered.

Consider this specification:

> The system must handle user login.

This is not a specification. It is a wish.

It does not define:

- what inputs are required
- what a valid login means
- what happens on failure
- what the response format is
- whether there are rate limits
- how sessions are managed

A developer reading this specification will make assumptions. AI reading this specification will make different assumptions.

The result is an implementation that works by accident rather than by design.

**The purpose of a specification is to eliminate assumptions.**

Every question that the specification leaves unanswered is a question that the implementation will answer arbitrarily.

---

# 3. What a Specification Must Contain

A complete STDD specification answers six questions.

## 3.1 What Does the System Do?

A short description of the feature or component and its purpose.

This should be one to three sentences. It establishes context, not detail.

## 3.2 What Are the Inputs and Outputs?

Every operation must define what it receives and what it returns.

Inputs include:

- parameters
- request bodies
- configuration values
- environmental context

Outputs include:

- return values
- response bodies
- side effects (data written, events emitted, notifications sent)

## 3.3 What Are the Behavioral Scenarios?

Scenarios describe the system's behavior under specific conditions.

Each scenario defines a precondition, an action, and an expected outcome.

Scenarios cover:

- the normal case
- important variations
- edge cases

## 3.4 What Are the Invariants?

Invariants are rules that must always hold, regardless of the scenario.

Examples:

- a balance must never be negative
- a deleted user must not appear in search results
- a session must expire after the configured timeout

Invariants apply across all scenarios. They are not tied to a single test case.

## 3.5 What Are the Failure Conditions?

The specification must define what happens when things go wrong.

This includes:

- invalid input
- missing data
- external service failures
- timeout conditions
- authorization failures

Failure conditions are not exceptions to the specification. They are part of the specification.

## 3.6 What Are the Constraints?

Constraints define boundaries and limitations.

Examples:

- maximum input size
- allowed character sets
- rate limits
- precision requirements
- ordering guarantees

---

# 4. Specification Levels

Not all specifications operate at the same level of detail. STDD defines four levels that align with the [specification pyramid](method.md) (Section 10).

| Level | Scope | Testable? | Example |
|-------|-------|-----------|---------|
| System | End-to-end workflows | Yes — system tests | "Customer holds seat, confirms, receives ticket" |
| Integration | Multiple components collaborating | Yes — integration tests | "Confirmation uses pricing and updates inventory" |
| Component | One module or class | Yes — component tests | "PricingEngine calculates prices" |
| Unit | One function | Yes — unit tests | "calculate_price returns correct decimal" |

## 4.1 System Specification

Describes an end-to-end workflow as the user experiences it.

Example:

> The customer browses available seats for an event, holds a seat, confirms the reservation within the hold period, and receives a confirmation with the final price. After confirmation, the seat no longer appears in the available list.

System specifications are testable. They produce system-level tests that verify the full workflow across all components.

## 4.2 Integration Specification

Describes how multiple components work together to deliver a user-facing capability.

Example:

> When a hold is confirmed, the ReservationService retrieves the seat's section from SeatInventory, calculates the price via PricingEngine, and updates the seat status to reserved. The final price returned to the customer matches the PricingEngine calculation.

Integration specifications are the primary unit of work in STDD. They produce integration tests that verify components collaborate correctly, and behavioral tests that drive implementation generation.

## 4.3 Component Specification

Describes a single technical component, module, or class.

Example:

> The pricing engine must calculate the total cost of a set of line items including applicable taxes and discounts. It must accept a list of items and a pricing context and return a breakdown of subtotal, tax, discount, and total.

Component specifications are used when a feature is large enough to require multiple independent parts. They produce component tests that verify internal function interactions within the module.

## 4.4 Unit Specification

Describes a single function with a single responsibility.

Example:

> calculate_price accepts a section name, event identifier, and group size. It returns a unit price and total price. Group discount of 10% applies for groups of 4 or more. Prices are rounded to 2 decimal places. Returns an error for unknown sections or group sizes below 1.

Unit specifications are the most common level. Every function that has non-trivial logic should have one. They produce unit tests — the base of the pyramid.

## Contracts Between Components

When two components interact, their shared interface should be specified explicitly. A contract defines what one component provides and what the other expects.

Example:

> The payment service accepts a PaymentRequest containing amount, currency, and payment method. It returns a PaymentResult containing status (success, declined, error) and a transaction identifier.

Contracts are tested at the integration level. They enable independent testing and regeneration of each side — as long as both sides honor the contract, either can be replaced.

---

# 5. Anatomy of a Feature Specification

A feature specification follows a consistent structure.

```
Feature: [Name]
Version: [x.y]
Status: [draft | review | accepted]

---

## Description

[1-3 sentences describing the feature purpose]

## Inputs

[List of inputs with types and constraints]

## Outputs

[List of outputs with types and structure]

## Behavioral Scenarios

### Scenario: [name]
  Given: [precondition]
  When: [action]
  Then: [expected outcome]

## Invariants

- [Rule that must always hold]

## Constraints

- [Boundary or limitation]

## Failure Conditions

- [Condition]: [expected behavior]

## Acceptance Cases

[Structured test data in YAML format]

## Technologies

[List of technologies used]

## Domain

[Business domain context]

## NFR Overrides

[Any project-specific threshold changes]
```

Each section serves a specific purpose. Omitting a section means the specification has a gap.

The **Status** field tracks the specification through its lifecycle. A specification in `draft` status may still have open questions. A specification in `accepted` status is considered complete enough to drive test creation and implementation generation.

---

# 6. Writing Behavioral Scenarios

Behavioral scenarios are the bridge between the specification and the test suite.

A scenario defines three things:

- **Given**: the precondition or starting state
- **When**: the action or event
- **Then**: the expected outcome

## Example: Seat Reservation

```
Scenario: Reserve an available seat
  Given: Seat A1 is available
  When: User requests to reserve Seat A1
  Then: Seat A1 is marked as reserved
  Then: The reservation expires in 10 minutes

Scenario: Reserve an already reserved seat
  Given: Seat A1 is reserved by another user
  When: User requests to reserve Seat A1
  Then: The request is rejected
  Then: The response indicates the seat is unavailable

Scenario: Reserve a seat after reservation expires
  Given: Seat A1 was reserved but the reservation has expired
  When: User requests to reserve Seat A1
  Then: Seat A1 is marked as reserved
  Then: A new reservation is created

Scenario: Reserve a sold seat
  Given: Seat A1 has been sold
  When: User requests to reserve Seat A1
  Then: The request is rejected
  Then: The response indicates the seat is sold
```

## Scenario Guidelines

Each scenario should be independent. One scenario must not depend on the outcome of another.

Scenarios should cover the normal case first, then edge cases, then failure conditions.

Each **Then** clause must be verifiable. If a **Then** clause cannot be checked by a test, it must be rewritten.

Avoid scenarios that describe implementation. Do not write:

```
Then: The system calls the database to update the seat status
```

Write instead:

```
Then: Seat A1 is marked as reserved
```

The first describes how. The second describes what.

---

# 7. Writing Invariants

Invariants are rules that must hold across all scenarios and all states of the system.

Unlike scenarios, which describe specific situations, invariants describe universal truths about the system.

## Example: Seat Reservation Invariants

```
Invariant: A seat can be in exactly one state at any time:
           available, reserved, or sold.

Invariant: A sold seat cannot transition to any other state.

Invariant: A reservation must have an expiration time.

Invariant: No more than one active reservation may exist
           for a single seat at any time.
```

## How Invariants Differ from Scenarios

A scenario says: "When X happens, Y should result."

An invariant says: "Regardless of what happens, Z must always be true."

Invariants are particularly valuable for catching edge cases that individual scenarios might miss.

When AI generates an implementation, invariant tests verify that no combination of operations violates the fundamental rules of the system.

---

# 8. Defining Acceptance Cases

Acceptance cases translate behavioral scenarios into structured, language-neutral test data.

They serve two purposes:

- They define the canonical test cases that any implementation must satisfy.
- They provide concrete data that can be used to generate executable tests in any language.

## Format

Acceptance cases use a simple YAML structure.

```yaml
acceptance_cases:

  - name: reserve available seat
    given:
      seat_status: available
      hold_until: null
    when:
      action: reserve
      user: user_1
      time: "2026-01-01T10:00:00"
    then:
      seat_status: reserved
      reserved_by: user_1
      hold_until: "2026-01-01T10:10:00"

  - name: reject reservation of reserved seat
    given:
      seat_status: reserved
      reserved_by: user_2
      hold_until: "2026-01-01T10:05:00"
    when:
      action: reserve
      user: user_1
      time: "2026-01-01T10:00:00"
    then:
      result: rejected
      reason: seat_unavailable

  - name: reserve seat with expired reservation
    given:
      seat_status: reserved
      reserved_by: user_2
      hold_until: "2026-01-01T09:55:00"
    when:
      action: reserve
      user: user_1
      time: "2026-01-01T10:00:00"
    then:
      seat_status: reserved
      reserved_by: user_1
      hold_until: "2026-01-01T10:10:00"

  - name: reject reservation of sold seat
    given:
      seat_status: sold
    when:
      action: reserve
      user: user_1
      time: "2026-01-01T10:00:00"
    then:
      result: rejected
      reason: seat_sold
```

## Why YAML

YAML is human-readable and language-neutral.

The same acceptance cases can generate tests in Python, Go, Java, or any other language.

This aligns with the STDD principle that features are defined once and implemented many times.

Other formats may be used. The requirement is that acceptance cases are structured, machine-readable, and independent of any implementation language.

---

# 9. Declaring Technology and Domain Context

A specification must declare its technology and domain context so that the correct non-functional requirements activate automatically.

This connects the specification to the [NFR Framework](nfr-framework.md).

## Technology Declaration

List the technologies that the feature uses or implies.

```
Technologies: PostgreSQL, REST API, HTML
```

This declaration triggers the relevant technology NFRs:

- SQL Database requirements (parameterized queries, connection pooling)
- REST API requirements (schema validation, rate limiting)
- HTML requirements (output encoding, security headers)

## Domain Declaration

Identify the business domain context.

```
Domain: User-Facing Web Application
```

This triggers:

- Performance thresholds (page load time)
- Accessibility requirements (WCAG compliance)
- Browser compatibility requirements

## NFR Overrides

If the project requires different thresholds than the defaults, declare them explicitly.

```
NFR Overrides:
  - Page load threshold: 1.0 seconds (trading dashboard requires faster response)
  - Rate limit: 500 requests per minute (internal users only)
```

Overrides must include a justification.

---

# 10. From Vague to Precise

The most practical skill in STDD is the ability to take a vague idea and refine it into a precise specification.

This section walks through that process.

## Starting Point

A stakeholder says:

> "We need a discount system for the shopping cart."

This is a feature request, not a specification.

## Step 1: Ask What the System Must Do

What kinds of discounts exist?

- percentage discount on the entire cart
- fixed amount discount on the entire cart
- buy-one-get-one on specific items

Each type is a separate behavioral scenario.

## Step 2: Define Inputs and Outputs

```
Input:
  - cart_items: list of {product_id, quantity, unit_price}
  - discount_code: string

Output:
  - subtotal: decimal
  - discount_amount: decimal
  - total: decimal
  - applied_discount: {type, value} or null
```

## Step 3: Write Behavioral Scenarios

```
Scenario: Apply percentage discount
  Given: Cart contains items totaling 100.00
  Given: Discount code SAVE10 provides 10% off
  When: Discount is applied
  Then: Discount amount is 10.00
  Then: Total is 90.00

Scenario: Apply fixed amount discount
  Given: Cart contains items totaling 100.00
  Given: Discount code FLAT20 provides 20.00 off
  When: Discount is applied
  Then: Discount amount is 20.00
  Then: Total is 80.00

Scenario: Discount exceeds cart total
  Given: Cart contains items totaling 15.00
  Given: Discount code FLAT20 provides 20.00 off
  When: Discount is applied
  Then: Discount amount is 15.00
  Then: Total is 0.00
  Then: Discount does not produce a negative total

Scenario: Invalid discount code
  Given: Cart contains items totaling 100.00
  Given: Discount code INVALID does not exist
  When: Discount is applied
  Then: No discount is applied
  Then: Total equals subtotal

Scenario: Expired discount code
  Given: Cart contains items totaling 100.00
  Given: Discount code EXPIRED has passed its valid date
  When: Discount is applied
  Then: No discount is applied
  Then: Response indicates the code has expired
```

## Step 4: Define Invariants

```
Invariant: The total must never be negative.

Invariant: At most one discount code may be applied per cart.

Invariant: Discount calculations must use decimal precision.
           Floating point must not be used.
```

## Step 5: Define Failure Conditions

```
Failure: Discount service unavailable
  Expected: Cart total is calculated without discount.
  Expected: Response indicates discount could not be applied.

Failure: Malformed discount code (special characters, excessive length)
  Expected: Input is rejected with a validation error.
```

## Step 6: Write Acceptance Cases

```yaml
acceptance_cases:

  - name: percentage discount
    given:
      cart_items:
        - {product_id: "A", quantity: 2, unit_price: "50.00"}
      discount_code: "SAVE10"
      discount_rules:
        SAVE10: {type: "percentage", value: "10", valid_until: "2027-01-01"}
    when:
      action: apply_discount
    then:
      subtotal: "100.00"
      discount_amount: "10.00"
      total: "90.00"

  - name: discount exceeds total
    given:
      cart_items:
        - {product_id: "B", quantity: 1, unit_price: "15.00"}
      discount_code: "FLAT20"
      discount_rules:
        FLAT20: {type: "fixed", value: "20.00", valid_until: "2027-01-01"}
    when:
      action: apply_discount
    then:
      subtotal: "15.00"
      discount_amount: "15.00"
      total: "0.00"
```

## Result

The vague request "we need a discount system" has become a precise specification with:

- clear inputs and outputs
- five behavioral scenarios
- three invariants
- two failure conditions
- structured acceptance cases

This specification is strong enough to produce meaningful tests. Those tests are strong enough to verify any AI-generated implementation.

---

# 11. Specification Templates

The following templates can be used as starting points.

## Feature Specification Template

```markdown
Feature: [Name]
Version: 1.0
Status: draft

---

## Description

[1-3 sentences describing the feature purpose]

## Inputs

- [input_name]: [type] - [description]

## Outputs

- [output_name]: [type] - [description]

## Behavioral Scenarios

### Scenario: [normal case]
  Given: [precondition]
  When: [action]
  Then: [expected outcome]

### Scenario: [edge case]
  Given: [precondition]
  When: [action]
  Then: [expected outcome]

## Invariants

- [Rule that must always hold]

## Constraints

- [Boundary or limitation]

## Failure Conditions

- [Condition]: [expected behavior]

## Acceptance Cases

See: acceptance_cases.yaml

## Technologies

[List of technologies]

## Domain

[Business domain]

## NFR Overrides

[Any threshold changes with justification]
```

## Unit Specification Template

```markdown
Unit: [Function Name]
Component: [Parent component]
Version: 1.0

---

## Description

[What this function does in one sentence]

## Inputs

- [param]: [type] - [description and constraints]

## Output

- [return]: [type] - [description]

## Behavioral Scenarios

### Scenario: [normal case]
  Given: [precondition]
  When: [action]
  Then: [expected outcome]

## Invariants

- [Rule that must always hold]

## Failure Conditions

- [Condition]: [expected behavior]
```

## Integration Contract Template

```markdown
Contract: [Name]
Version: 1.0
Status: draft

---

## Description

[Interface being defined and its purpose]

## Request

- [field]: [type] - [description and constraints]

## Response

- [field]: [type] - [description]

## Status Codes / Result States

- [state]: [when this occurs]

## Invariants

- [Rule that must always hold]

## Failure Modes

- [Condition]: [expected response]
```

---

# 12. Specification Review Checklist

Before a specification moves from `draft` to `accepted`, it should pass this checklist.

## Completeness

- [ ] Description clearly states the feature purpose
- [ ] All inputs are defined with types and constraints
- [ ] All outputs are defined with types and structure
- [ ] Normal case scenarios are defined
- [ ] Edge case scenarios are defined
- [ ] Failure condition scenarios are defined
- [ ] Invariants are defined
- [ ] Acceptance cases exist in structured format

## Precision

- [ ] No ambiguous terms (avoid "should handle", "appropriate", "properly")
- [ ] Boundary values are explicit (use "less than 30" not "around 30")
- [ ] Error responses are specified, not just "return an error"
- [ ] Data types are explicit (decimal, integer, string with max length)

## Testability

- [ ] Every scenario can be verified by a test
- [ ] Every invariant can be verified by a test
- [ ] Every failure condition can be verified by a test
- [ ] Acceptance cases provide concrete input and expected output

## Independence

- [ ] Specification does not describe implementation details
- [ ] Specification does not reference specific code or libraries
- [ ] Specification could be implemented in any programming language
- [ ] Scenarios are independent of each other

## NFR Coverage

- [ ] Technologies are declared
- [ ] Domain is declared
- [ ] NFR overrides are documented with justification

---

# 13. Closing the Specification-to-Test Gap

A specification can be precise. Tests can pass. And the system can still be wrong.

This happens when the tests do not faithfully represent the specification. The translation from specification to test suite is where bugs hide.

This is the **specification-to-test gap**: the risk that the test suite does not fully cover the behavioral intent expressed in the specification.

## Why the Gap Exists

Specifications describe behavior in natural language and structured scenarios. Tests express behavior in executable code. The translation between these two representations is manual and error-prone.

Common failure modes:

- A scenario is defined in the specification but no corresponding test exists.
- An invariant is stated but never verified by any test.
- A failure condition is described but the test suite only covers the happy path.
- An edge case is documented but the test uses a value that does not actually exercise the boundary.

## Strategy 1: Traceability Matrix

Every scenario, invariant, and failure condition in the specification should map to at least one test.

A traceability matrix makes this mapping explicit.

Example:

| Specification Element | Type | Test |
|---|---|---|
| Reserve available seat | Scenario | test_available_seat_can_be_held |
| Reserve already reserved seat | Scenario | test_active_hold_blocks_new_hold |
| Reserve seat with expired hold | Scenario | test_expired_hold_allows_new_hold |
| Reserve sold seat | Scenario | test_sold_seat_cannot_be_held |
| Seat in exactly one state | Invariant | test_seat_state_is_always_singular |
| Sold seat cannot transition | Invariant | test_sold_seat_is_final |
| No more than one active hold | Invariant | test_single_active_hold_per_seat |
| Seat does not exist | Failure | test_nonexistent_seat_returns_error |

If a specification element has no corresponding test, the gap is visible immediately.

The traceability matrix can be maintained as a simple table in the specification directory or generated automatically from test annotations.

## Strategy 2: Acceptance Cases as the Bridge

Acceptance cases (Section 8) serve as a mechanical bridge between the specification and the test suite.

Because acceptance cases are structured data with explicit inputs and expected outputs, they can be used to **generate** test cases rather than relying on manual translation.

A test generator reads the acceptance cases and produces executable tests:

```python
# Generated from acceptance_cases.yaml
@pytest.mark.parametrize("case", load_acceptance_cases("seat_reservation"))
def test_acceptance(case):
    result = reserve_seat(case["given"], case["when"])
    assert_matches(result, case["then"])
```

When tests are generated from acceptance cases, the specification-to-test gap narrows to the gap between behavioral scenarios and acceptance cases. This is a smaller, more reviewable translation.

## Strategy 3: Coverage Audit

After the test suite is written, audit it against the specification using the review checklist (Section 12).

For each specification element, ask:

- Does at least one test exercise this scenario?
- Does at least one test verify this invariant?
- Does at least one test trigger this failure condition?
- Are the test inputs and expected outputs consistent with the acceptance cases?

If the answer to any of these is no, the gap must be closed before the specification moves to `accepted` status.

## Strategy 4: Invariant Tests as Safety Nets

Scenario tests verify specific input-output pairs. They can miss behaviors that only appear under unusual combinations.

Invariant tests take a different approach. Instead of checking a single scenario, they verify that a rule holds across many inputs.

Example:

```python
from hypothesis import given, strategies as st

@given(
    items=st.lists(st.decimals(min_value=0, max_value=10000), max_size=500),
    tax_rate=st.decimals(min_value=0, max_value=1)
)
def test_total_is_never_negative(items, tax_rate):
    result = calculate_total(items, tax_rate)
    assert result >= 0
```

This test does not check a specific input. It checks that the invariant "total must never be negative" holds across thousands of random inputs.

Property-based tests like this are particularly effective at catching edge cases that manual scenario tests miss.

## Strategy 5: Specification Review Includes Test Review

When a specification is reviewed (Section 12), the test suite should be reviewed at the same time.

Reviewers check not only whether the specification is complete, but whether the tests faithfully represent it.

The review question is:

> If I gave this specification and these tests to a new AI with no knowledge of the current implementation, would the tests be sufficient to verify any correct implementation and reject any incorrect one?

If the answer is no, either the specification has gaps or the tests have gaps.

## The Gap Cannot Be Fully Eliminated

The specification-to-test gap can be narrowed but not eliminated entirely.

Natural language specifications will always contain nuance that executable tests cannot fully capture. The goal is not perfection. The goal is to make the gap as small and as visible as possible.

The combination of traceability matrices, generated tests from acceptance cases, invariant tests, and paired specification-test reviews makes the gap manageable.

---

# 14. Common Specification Mistakes

## Describing Implementation Instead of Behavior

Wrong:

> The system must use a HashMap to store discount codes.

Right:

> The system must look up discount codes and return the associated discount rule.

Implementation details belong in the implementation, not the specification.

## Using Ambiguous Language

Wrong:

> The system should handle large carts gracefully.

Right:

> The system must process carts with up to 500 items within 2 seconds.

Ambiguous language produces ambiguous tests. Ambiguous tests allow incorrect implementations.

## Forgetting Failure Conditions

A specification that only describes the happy path is incomplete.

If the specification does not define what happens when the discount service is unavailable, the implementation will decide for itself. Different implementations will decide differently. The system becomes unpredictable.

## Mixing Multiple Features in One Specification

Each specification should describe one feature or one component.

A specification that covers "discounts, loyalty points, and gift cards" is three specifications. Combining them creates confusion about boundaries and responsibilities.

## Omitting Edge Cases

The edge cases are often where bugs live.

Common edge cases to consider:

- empty input (empty cart, empty string, zero quantity)
- boundary values (exactly at a threshold)
- maximum values (largest allowed input)
- concurrent operations (two users acting on the same resource)
- timing (expired data, clock differences)

## Writing Scenarios That Test Implementation

Wrong:

```
Scenario: Database query for discount
  Given: Discount is in the database
  When: System queries the discount table
  Then: System receives the discount row
```

Right:

```
Scenario: Apply valid discount
  Given: Discount code SAVE10 exists and is valid
  When: Discount is applied to the cart
  Then: Cart total reflects the discount
```

Scenarios describe behavior visible from outside the system. Internal operations are not part of the specification.

---

# 15. Conclusion

Specifications are the foundation of STDD.

Tests can only verify what the specification defines. AI can only generate what the tests cover.

A weak specification produces weak tests. Weak tests allow incorrect implementations to pass. The regeneration loop becomes unreliable.

A strong specification produces strong tests. Strong tests reject incorrect implementations. The regeneration loop becomes safe.

The quality of the entire STDD process depends on the quality of the specification.

This document provides the structure, templates, and review process needed to write specifications that are precise enough to drive reliable AI-generated implementations.

**Specifications define the system.
Tests verify the specification.
AI generates the implementation.
The specification must be strong enough to support the entire chain.**
