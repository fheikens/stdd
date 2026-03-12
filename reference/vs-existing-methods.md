
# STDD vs Existing Methods
## How Specification & Test‑Driven Development Compares to Other Approaches

Author: Frank Heikens
Version: 1.1
Date: 2026

---

## Table of Contents

- [1. Introduction](#1-introduction)
- [2. Why Comparisons Matter](#2-why-comparisons-matter)
- [3. STDD vs Test‑Driven Development (TDD)](#3-stdd-vs-test-driven-development-tdd)
- [4. STDD vs Behavior‑Driven Development (BDD)](#4-stdd-vs-behavior-driven-development-bdd)
- [5. STDD vs Clean Architecture](#5-stdd-vs-clean-architecture)
- [6. STDD vs Traditional Development](#6-stdd-vs-traditional-development)
- [7. STDD vs AI “Vibe Coding”](#7-stdd-vs-ai-vibe-coding)
- [8. Where STDD Fits](#8-where-stdd-fits)
- [9. Migration Paths from TDD and BDD to STDD](#9-migration-paths-from-tdd-and-bdd-to-stdd)
- [10. Side‑by‑Side Worked Example](#10-side-by-side-worked-example)
- [11. When STDD Is Not the Right Choice](#11-when-stdd-is-not-the-right-choice)
- [12. Hybrid Approaches](#12-hybrid-approaches)
- [13. Conclusion](#13-conclusion)

---

# 1. Introduction

Specification & Test‑Driven Development (STDD) is not intended to replace all existing development practices.

Instead, it builds on ideas that already exist in software engineering and adapts them for a world where **AI can generate implementations instantly**.

To understand STDD clearly, it helps to compare it with well‑known approaches such as:

- Test‑Driven Development (TDD)
- Behavior‑Driven Development (BDD)
- Clean Architecture
- Traditional development models
- AI‑assisted coding practices

These comparisons show both the similarities and the differences.

---

# 2. Why Comparisons Matter

New methodologies are often misunderstood.

Engineers typically ask questions like:

- Is this just TDD with AI?
- Is this the same as BDD?
- Does this replace architecture practices?
- Is this just prompt‑driven coding?

Understanding how STDD relates to existing methods makes it easier to adopt and apply in real systems.

---

# 3. STDD vs Test‑Driven Development (TDD)

Test‑Driven Development introduced the idea that **tests should be written before implementation**.

Typical TDD workflow:

1. Write a failing test
2. Write the minimal code to pass the test
3. Refactor the code

TDD focuses on improving design and preventing regressions.

STDD builds directly on TDD. It inherits the core idea that tests come before implementation. This is not a difference. It is a shared foundation.

### What STDD Shares with TDD

- Tests are written before implementation
- Tests are a core artifact
- Behavioral verification drives development

### What STDD Adds

The question "who writes the implementation" (human vs AI) is an operational change, not a deep methodological one. TDD works regardless of who or what produces the code.

The genuine difference is the **regeneration model**.

In TDD, code is written incrementally and maintained over time. Refactoring improves existing code. The implementation accumulates history, context, and implicit knowledge. Developers become attached to the code because it represents significant investment.

In STDD, code is **deliberately disposable**. Implementations are not maintained. They are discarded and regenerated. This changes the relationship between the team and the codebase in a fundamental way.

This shift requires something TDD does not provide: a **specification layer above the tests**.

TDD tests verify behavior, but they do not capture the full intent of the system. A test suite can tell you that `calculate_total([10, 20], 0.10)` must equal `33`. It cannot tell you why, what the business rules are, what the edge cases should be, or what invariants must hold across all scenarios.

STDD adds this specification layer: behavioral scenarios, invariants, acceptance cases, failure conditions, and constraints. Together with the tests, these form a **knowledge layer** that is strong enough to safely regenerate any implementation from scratch.

### Summary

TDD gave us: tests before code.

STDD adds: a specification layer that makes code safely disposable through regeneration.

---

# 4. STDD vs Behavior‑Driven Development (BDD)

Behavior‑Driven Development focuses on describing system behavior in human‑readable language.

BDD scenarios often follow this pattern:

```
Given some initial context
When an event occurs
Then a result should happen
```

BDD helps align developers, testers, and stakeholders.

### Similarities

- Both focus on behavior
- Both encourage clear expectations
- Both treat tests as executable documentation

### Differences

BDD focuses primarily on **communication and collaboration**.

STDD focuses on **system stability in an AI‑generated code environment**.

BDD scenarios may describe behavior, but STDD requires **precise, testable specifications that drive regeneration**.

---

# 5. STDD vs Clean Architecture

Clean Architecture focuses on designing systems with clear separation of concerns.

It emphasizes:

- dependency control
- domain isolation
- layered architecture

### Similarities

- Both value clear boundaries
- Both encourage testable components
- Both aim to reduce system fragility

### Differences

Clean Architecture primarily addresses **system structure**.

STDD addresses **development workflow in the presence of AI‑generated code**.

Clean Architecture can complement STDD by providing a structure that allows implementations to be regenerated safely.

---

# 6. STDD vs Traditional Development

Traditional development workflows often follow this pattern:

1. Design system
2. Write implementation
3. Write tests
4. Fix defects

In many projects tests are written late or are incomplete.

### Problems with Traditional Development

- implementation becomes the system definition
- tests may lag behind behavior
- refactoring becomes risky
- code becomes difficult to replace

### STDD Difference

STDD reverses the order:

1. Define specification
2. Define behavior
3. Define tests
4. Generate implementation

The implementation is never the source of truth.

The **tests and specifications define the system**.

---

# 7. STDD vs AI “Vibe Coding”

A growing trend in AI‑assisted development is sometimes called *vibe coding*.

In this model developers describe what they want and AI generates code interactively.

While this approach is powerful, it introduces risks:

- behavior may not be clearly defined
- generated code may accumulate hidden defects
- long‑term stability becomes uncertain

### STDD Difference

STDD introduces **structure and verification**.

Instead of:

```
Idea → AI code → manual adjustments
```

STDD enforces:

```
Specification → Tests → AI implementation → Verification
```

This ensures that AI remains a controlled tool rather than an uncontrolled generator of code.

---

# 8. Where STDD Fits

STDD builds on ideas that already exist in software engineering.

- TDD established that tests come before code
- BDD established that behavior matters more than implementation details
- Clean Architecture established structural discipline for testable systems

STDD does not claim to invent these ideas. It inherits them.

What STDD adds is the **regeneration model**: a development workflow where implementations are deliberately disposable because the specification and test layers are strong enough to verify any new implementation from scratch.

This requires two things that previous methods did not emphasize:

1. A **specification layer** above the tests that captures invariants, failure conditions, acceptance cases, and constraints. This layer makes it safe to regenerate rather than refactor.

2. A **regeneration loop** where discarding and regenerating implementations is a normal operation, not an emergency measure.

The combination of these ideas creates a workflow designed for an environment where AI can generate code instantly but cannot guarantee long‑term stability on its own.

---

# 9. Migration Paths from TDD and BDD to STDD

Adopting STDD does not require abandoning existing practices. Migration is **additive, not replacement**. Existing tests remain. Existing Gherkin scenarios remain. STDD adds the specification layer and regeneration capability on top.

### From TDD

Teams already practicing TDD have the strongest foundation for STDD adoption. The tests already exist. The work is making the intent explicit.

1. **Add specifications above existing tests.** For each test file, write the behavioral specification that the tests verify. Capture the "why" that the test code cannot express on its own.
2. **Create a traceability matrix** linking specifications to existing tests. Each test should trace back to a specific acceptance case or invariant.
3. **Add invariants.** TDD tests verify individual cases. Invariants capture properties that must hold across all cases. Identify these and document them in the specification.
4. **Add acceptance cases.** Formalize the expected inputs and outputs as canonical acceptance cases in the specification, separate from the test implementation.
5. **Verify regeneration readiness.** The specification and tests are strong enough when you can delete the implementation, regenerate it, and have all tests pass without modification.

### From BDD

BDD teams have the **smallest gap to close**. Gherkin scenarios map directly to STDD behavioral scenarios. The Given/When/Then structure already captures behavior in a human-readable format.

The main additions are:

- **Formal invariants.** BDD scenarios describe individual behaviors. STDD requires explicit invariants that hold across all scenarios.
- **Failure condition specifications.** BDD scenarios typically describe the happy path and selected error paths. STDD requires systematic specification of what happens when things go wrong.
- **Traceability matrix.** Link each Gherkin scenario to the corresponding STDD specification element and test implementation.
- **The regeneration mindset.** BDD teams maintain implementations over time. STDD treats implementations as disposable outputs that can be regenerated from the specification and test layers.

### From No Methodology

Teams without an existing test-driven practice face the largest transition but gain the most immediate value.

Start with the [Adoption Guide](../docs/adoption-guide.md). The full STDD workflow is new, but the investment pays off immediately in specification clarity. Begin with a single feature, write the specification first, define acceptance cases, write tests, and generate the implementation. The discipline builds from there.

### The Key Insight

Migration to STDD is always additive. Nothing is thrown away. Existing tests gain a specification layer above them. Existing Gherkin scenarios gain invariants and traceability. Existing code gains the property of being safely disposable because the knowledge layer above it is now strong enough to regenerate from.

---

# 10. Side‑by‑Side Worked Example

To make the differences concrete, consider a single feature implemented three ways: a **discount calculator** with these rules:

- 10% discount on orders over $100
- 20% discount on orders over $500
- No discount otherwise

### TDD Approach

The TDD workflow starts with a failing test:

```python
def test_no_discount_below_threshold():
    assert calculate_discount(50) == 0

def test_ten_percent_discount():
    assert calculate_discount(150) == 15.0

def test_twenty_percent_discount():
    assert calculate_discount(600) == 120.0
```

The developer writes the minimal implementation to pass these tests, then refactors.

**What TDD produces:** Working code with regression tests.

**What is missing:** The tests say *what* the function returns for specific inputs. They do not say *why* the thresholds are $100 and $500. They do not capture the invariant that exactly one discount tier applies per order. They do not specify what happens with negative order amounts or boundary values like exactly $100. A new developer reading these tests can verify behavior but cannot reconstruct the business rules with confidence.

### BDD Approach

The BDD workflow starts with Gherkin scenarios:

```gherkin
Feature: Order Discount

  Scenario: No discount for small orders
    Given an order totaling $50
    When the discount is calculated
    Then the discount should be $0

  Scenario: 10% discount for medium orders
    Given an order totaling $150
    When the discount is calculated
    Then the discount should be $15.00

  Scenario: 20% discount for large orders
    Given an order totaling $600
    When the discount is calculated
    Then the discount should be $120.00
```

Step definitions are implemented, then the code is written to satisfy the scenarios.

**What BDD produces:** Working code with human-readable behavioral scenarios that stakeholders can review.

**What is missing:** BDD captures intent better than TDD. The scenarios are readable and describe behavior clearly. But they still lack formal invariants (discount never exceeds order total, exactly one tier applies), systematic failure conditions (negative amounts, zero, boundary values), and traceability. The scenarios cannot drive regeneration because they do not fully constrain the implementation.

### STDD Approach

The STDD workflow starts with a specification:

```
Feature: Order Discount Calculator

Business Rules:
  - Orders over $100 receive a 10% discount
  - Orders over $500 receive a 20% discount (supersedes 10% tier)
  - Orders of $100 or less receive no discount
  - Thresholds are inclusive of the boundary value for the lower tier
    ($100.00 exactly receives no discount; $100.01 receives 10%)

Invariants:
  INV-1: Exactly one discount tier applies per order
  INV-2: Discount amount never exceeds order total
  INV-3: Discount amount is never negative
  INV-4: Discount percentage is always 0%, 10%, or 20%

Failure Conditions:
  FC-1: Negative order amount → reject with error
  FC-2: Non-numeric input → reject with error

Acceptance Cases:
  AC-1: order_amount=50.00    → discount=0.00     (no discount)
  AC-2: order_amount=100.00   → discount=0.00     (boundary, no discount)
  AC-3: order_amount=100.01   → discount=10.00    (just above boundary, 10%)
  AC-4: order_amount=150.00   → discount=15.00    (mid-range, 10%)
  AC-5: order_amount=500.00   → discount=50.00    (boundary, 10%)
  AC-6: order_amount=500.01   → discount=100.00   (just above boundary, 20%)
  AC-7: order_amount=600.00   → discount=120.00   (mid-range, 20%)
  AC-8: order_amount=-10.00   → error             (FC-1)
  AC-9: order_amount=0.00     → discount=0.00     (zero, no discount)
```

Tests are written with traceability IDs linking each test to a specific acceptance case and invariant:

```python
def test_no_discount_below_threshold():          # AC-1, INV-1, INV-4
    assert calculate_discount(50.00) == 0.00

def test_boundary_no_discount():                 # AC-2, INV-1
    assert calculate_discount(100.00) == 0.00

def test_just_above_boundary_ten_percent():       # AC-3, INV-1, INV-4
    assert calculate_discount(100.01) == approx(10.001)

def test_negative_amount_rejected():              # AC-8, FC-1, INV-3
    with pytest.raises(ValueError):
        calculate_discount(-10.00)

def test_discount_never_exceeds_total():          # INV-2 (property-based)
    for amount in [0.01, 50, 100, 100.01, 500, 500.01, 999]:
        discount = calculate_discount(amount)
        assert discount <= amount
```

The implementation is then generated from the specification and verified by the tests.

**What STDD produces:** Working code, human-readable behavioral specification, formal invariants, systematic boundary and failure coverage, traceability from every test back to the specification, and the ability to regenerate the implementation at any time.

### The Contrast

All three approaches produce working code. The difference is in what survives when the code is discarded:

| Artifact | TDD | BDD | STDD |
|---|---|---|---|
| Working implementation | Yes | Yes | Yes |
| Regression tests | Yes | Yes | Yes |
| Human-readable behavior | Partial | Yes | Yes |
| Formal invariants | No | No | Yes |
| Failure condition spec | No | Partial | Yes |
| Boundary coverage | Ad hoc | Ad hoc | Systematic |
| Traceability | No | No | Yes |
| Regeneration-ready | No | No | Yes |

Only STDD produces a specification strong enough to regenerate from. The knowledge layer — specification plus tests — is the permanent artifact. The implementation is temporary.

---

# 11. When STDD Is Not the Right Choice

STDD is designed for systems where behavior must be stable, verifiable, and regenerable. Not every situation requires these properties. Being honest about where STDD adds overhead without proportional value is important for credibility and practical adoption.

### Prototyping and Exploration

When you do not yet know what the system should do, writing specifications is premature. The purpose of a prototype is to discover behavior through experimentation. Locking down specifications before the behavior is understood produces specifications that will be immediately rewritten.

**The right approach:** Prototype first. Explore freely. Once the desired behavior crystallizes, capture it as STDD specifications. The prototype served its purpose; the specification captures what was learned.

### Throwaway Scripts

One-time data migrations, ad-hoc analysis scripts, quick-and-dirty data transformations — the overhead of formal specification is not justified when the code will run once and be discarded. The regeneration model adds no value to code that will never be regenerated.

### UI Layout and Visual Design

STDD specifications describe **behavior**, not appearance. CSS positioning, color schemes, typography choices, and visual aesthetics are not well-suited to behavioral specification. There is no meaningful invariant for "this button looks right."

However, UI **behavior** is well-suited to STDD. Form validation rules, navigation flows, state transitions in interactive components, error message display logic — these are behavioral contracts that benefit from specification and testing.

### Extremely Stable, Never-Changing Code

If a function has not been modified in years and is unlikely to change, retroactively adding STDD specifications provides little value. The cost of writing the specification is not recovered through regeneration or change management if the code never changes.

This is a pragmatic judgment. If the stable code is part of a larger system undergoing active development, specifying it may still be worthwhile for completeness and traceability.

### The Key Message

STDD adds the most value where behavior must be **stable** (the system must do the same thing reliably), **verifiable** (you can prove it does the right thing), and **regenerable** (you can discard and recreate the implementation). If none of those properties matter for a particular piece of work, a lighter approach is appropriate. Apply STDD where it earns its keep.

---

# 12. Hybrid Approaches

STDD is a specification and testing methodology. It does not prescribe domain modeling, stakeholder communication, or architectural patterns. This makes it naturally composable with other approaches.

### STDD + BDD

Use Gherkin for **stakeholder-facing scenarios** and STDD specifications for **engineering-level precision**. The Gherkin scenarios become a subset of the STDD acceptance cases — the ones written in a language that non-technical stakeholders can review.

The STDD specification adds what Gherkin alone cannot express: formal invariants, systematic failure conditions, boundary analysis, and traceability. Stakeholders see the Gherkin scenarios. Engineers see the full specification. Both views describe the same system.

### STDD + Domain‑Driven Design

Bounded contexts map naturally to STDD feature boundaries. Each bounded context defines a set of behaviors that can be specified, tested, and regenerated independently.

Aggregate invariants become STDD invariants. The business rules that an aggregate enforces — "an order cannot exceed the customer's credit limit," "a reservation cannot overlap with another reservation for the same seat" — are exactly the kind of behavioral contracts that STDD specifications capture.

The ubiquitous language informs specification terminology. When the domain model uses precise terms, the STDD specification inherits that precision. This alignment reduces ambiguity and ensures that specifications speak the language of the domain.

### STDD + Event Sourcing

Events are behavioral facts. "OrderPlaced," "PaymentReceived," "SeatReserved" — each event represents something that happened in the system. These map directly to STDD behavioral scenarios.

Event schemas become part of the specification. The structure and constraints of each event type are behavioral contracts: what fields must be present, what values are valid, what relationships must hold between events.

Projection logic is regenerable. Read models built from event streams are pure functions from event history to current state. These are ideal candidates for STDD: specify the projection rules, write tests against the expected read model state, and regenerate the projection implementation whenever needed.

### The General Principle

STDD adds a **specification layer** to any development approach. It does not replace domain modeling, stakeholder communication, or architectural patterns. It makes the behavioral contracts explicit and testable.

Any methodology that produces behavioral requirements can feed into STDD specifications. Any architecture that supports testable components can host STDD-verified implementations. The specification layer sits above the implementation and below the domain model, connecting intent to verification.

---

# 13. Conclusion

STDD does not replace existing engineering practices. It builds on them.

TDD, BDD, and Clean Architecture remain valuable foundations. STDD inherits their core ideas and extends them with the **regeneration model**: a specification layer and a regeneration loop that together make implementations safely disposable.

This is not simply "TDD with AI." The ability to discard and regenerate code at will changes the relationship between the team and the codebase. Code is no longer an asset to protect. It is an output to verify.

The specification and tests become the permanent artifacts. The implementation is temporary.

This makes STDD particularly well suited for modern software development where AI can generate code instantly but cannot guarantee that the code will remain stable over time.

---

For the complete methodology, see the [Method](../docs/method.md). For the regeneration model in practice, see the [Seat Reservation API](../examples/seat-reservation.md). For common mistakes when adopting STDD, see [Anti-Patterns](anti-patterns.md). For step-by-step adoption guidance, see the [Adoption Guide](../docs/adoption-guide.md).
