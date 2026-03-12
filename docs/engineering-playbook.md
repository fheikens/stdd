
# The STDD Engineering Playbook
## Applying Specification & Test-Driven Development in Real Projects

Author: Frank Heikens
Version: 1.0
Date: 2026

---

## Table of Contents

- [1. Introduction](#1-introduction)
- [2. Repository Structure](#2-repository-structure)
- [3. Test-First Prompting (TFP)](#3-test-first-prompting-tfp)
- [4. Decomposition and the Specification Pyramid](#4-decomposition-and-the-specification-pyramid)
- [5. Continuous Specification Integrity (CSI)](#5-continuous-specification-integrity-csi)
- [6. Team Roles in STDD](#6-team-roles-in-stdd)
- [7. Conclusion](#7-conclusion)

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

# 2. Repository Structure

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

For detailed guidance on writing specifications, see [Writing Specifications](writing-specifications.md). For the core workflow and principles, see the [Method](method.md).

---

# 3. Test-First Prompting (TFP)

Test-First Prompting is the practice of giving AI the specification and failing tests, then letting it generate implementations until the tests pass.

## The Prompt Structure

An effective TFP prompt has four parts:

1. **Specification** — what the function/component must do
2. **Tests** — the failing test suite that defines correct behavior
3. **Constraints** — NFRs, language requirements, decomposition rules
4. **Context** — related components, contracts, integration points

## Example: Simple Function

```
Specification:
calculate_price accepts a section name, event identifier, and group size.
It returns a unit price and total price. Group discount of 10% applies for
groups of 4 or more. Prices are rounded to 2 decimal places.

Tests:
[paste the relevant test functions]

Constraints:
- Use Decimal arithmetic, not float
- Single responsibility, no more than 50 lines
- Raise ValueError for invalid inputs

Generate a Python function that passes all tests.
```

## Example: Component with Dependencies

```
Specification:
ReservationService manages seat holds, confirmations, and cancellations.
It depends on SeatInventory (tracks seat status) and PricingEngine
(calculates prices). It accepts a clock dependency for time operations.

Contracts:
- SeatInventory provides: get_seat_status, set_seat_status, list_available
- PricingEngine provides: calculate(section, event_id, group_size)
- Clock provides: now()

Tests:
[paste the full test suite]

Constraints:
- Each method has a single responsibility
- No method exceeds 50 lines
- All state changes must be atomic
- Use the injectable clock for all time comparisons

Generate a Python class that passes all tests.
```

## When Tests Fail

If AI generates code that fails tests:

1. **Check the test output.** The failing tests tell you which specification the AI violated.
2. **Refine the prompt.** Add more context, highlight the constraint that was missed, or break the task into smaller pieces.
3. **Never weaken the test.** The test represents the specification. If the AI cannot satisfy it, the prompt needs work — not the test.
4. **Decompose further.** If a component is too complex for AI to generate correctly, break it into smaller units with their own specs and tests. Generate each unit separately.

## What TFP Is Not

TFP is not "ask AI to write code and then add tests." The tests exist before the AI sees the task. The AI's job is to satisfy existing tests, not to co-create them.

---

# 4. Decomposition and the Specification Pyramid

STDD's regeneration model works because each unit of code is small enough to generate reliably. A 50-line function with a clear specification and 5 tests is trivially regenerable. A 5000-line function is not.

This is not accidental. The discipline of writing precise specifications naturally produces small, focused functions. If a function is hard to specify, it is doing too much.

## The Rule

**Every function has a single responsibility and fits within approximately 50 lines.** If a function is larger, decompose it into smaller functions, each with its own specification and tests.

This applies to both humans and AI. When prompting AI to generate implementations, include this constraint explicitly:

```
Each function must have a single responsibility.
No function should exceed approximately 50 lines.
If a task requires more, decompose it into smaller functions
that each have their own clear inputs, outputs, and tests.
```

## Testing the Composition

Small functions alone are not enough. They must be tested together.

The **specification pyramid** defines four levels of testing:

| Level | What it tests | Example |
|-------|--------------|---------|
| Unit | Single function in isolation | `calculate_price` returns correct decimal |
| Component | Multiple functions within one module | `ReservationService` handles hold-to-confirm flow |
| Integration | Multiple components collaborating | Confirmation uses pricing and updates inventory |
| System | Full end-to-end workflow | Customer lists seats, holds, confirms, seat disappears from list |

Each level has its own specifications and its own tests. The traceability matrix includes entries at all levels.

## Why This Matters for Regeneration

When you regenerate a function, the unit tests verify the function still works. But the integration and system tests verify it still works **within the larger system**. Without integration tests, a regenerated function could pass all its unit tests while breaking a workflow that depends on it.

The specification pyramid makes regeneration safe at any scale:

1. Regenerate one function → unit tests verify the function
2. Integration tests verify it still works with other components
3. System tests verify the end-to-end workflow still passes

For a detailed explanation of the pyramid model, see the [Method](method.md), Section 10. For a worked example, see [Seat Reservation API](../examples/seat-reservation.md).

---

# 5. Continuous Specification Integrity (CSI)

Continuous Specification Integrity is the CI/CD practice that ensures specifications, tests, and implementations never drift apart.

## The CSI Pipeline

A standard STDD CI pipeline enforces three gates:

```
┌─────────────────────────────────────────────────┐
│ 1. Specification Validation                      │
│    - Every spec has at least one test            │
│    - Every test maps to a spec (traceability)    │
│    - No orphaned tests or untested specs         │
├─────────────────────────────────────────────────┤
│ 2. Test Execution                                │
│    - All unit tests pass                         │
│    - All integration tests pass                  │
│    - All system tests pass                       │
├─────────────────────────────────────────────────┤
│ 3. Fingerprint Verification                      │
│    - Compute specification fingerprint           │
│    - Compare against previous fingerprint        │
│    - Flag if specs changed without test updates  │
│    - Flag if tests changed without spec updates  │
└─────────────────────────────────────────────────┘
```

## Example: GitHub Actions

```yaml
name: STDD CI
on: [push, pull_request]

jobs:
  specification-integrity:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate traceability matrix
        run: python scripts/validate_traceability.py

      - name: Run test suite
        run: pytest tests/ -v --tb=short

      - name: Compute specification fingerprint
        run: python scripts/compute_fingerprint.py --compare
```

## Specification Fingerprint in CI

The Specification Fingerprint is a hash of the knowledge layer that detects drift.

### Computing the Fingerprint

```python
import hashlib
import pathlib

def compute_fingerprint(spec_dir, test_dir, nfr_file):
    """Hash all specification and test files to produce a fingerprint."""
    hasher = hashlib.sha256()

    for directory in [spec_dir, test_dir]:
        for filepath in sorted(pathlib.Path(directory).rglob("*")):
            if filepath.is_file():
                hasher.update(filepath.read_bytes())

    if pathlib.Path(nfr_file).exists():
        hasher.update(pathlib.Path(nfr_file).read_bytes())

    return hasher.hexdigest()
```

### What the Fingerprint Detects

| Change | Fingerprint | Action |
|--------|------------|--------|
| Spec changed, tests updated | New fingerprint | Accept — intentional evolution |
| Spec changed, tests unchanged | New fingerprint | Warning — possible spec-to-test gap |
| Tests changed, spec unchanged | New fingerprint | Warning — tests may have drifted from spec |
| Implementation changed, spec and tests unchanged | Same fingerprint | Accept — regeneration, no behavioral change |
| Nothing changed | Same fingerprint | Accept — no action needed |

### Storing Fingerprints

Store the current fingerprint in a file committed alongside the knowledge layer:

```
features/
├── seat-reservation/
│   ├── specification.md
│   ├── acceptance_cases.yaml
│   ├── .fingerprint          ← computed hash
│   └── tests/
│       └── test_reservation.py
```

The CI pipeline computes a fresh fingerprint and compares it to the stored one. If they differ, the PR must include both spec and test changes — or explicitly justify why only one changed.

## Traceability Validation

A simple traceability check ensures every spec ID appears in at least one test docstring:

```python
import re
import pathlib

def validate_traceability(spec_file, test_dir):
    """Check that every spec ID in the traceability matrix has a test."""
    spec_ids = set(re.findall(r"^\| (\w+-\d+)", spec_file.read_text(), re.MULTILINE))
    test_content = "".join(
        f.read_text() for f in pathlib.Path(test_dir).rglob("test_*.py")
    )
    untested = {sid for sid in spec_ids if sid not in test_content}

    if untested:
        raise ValueError(f"Untested specifications: {untested}")
```

This is a basic implementation. More sophisticated validation can parse test docstrings and cross-reference them against the traceability matrix programmatically.

---

# 6. Team Roles in STDD

STDD changes how teams collaborate.

**Specification authors** (engineers, product owners, domain experts) define what the system must do. They write specifications, behavioral scenarios, invariants, and acceptance cases.

**Test authors** (engineers, QA) translate specifications into executable tests at all pyramid levels. They maintain the traceability matrix and close the spec-to-test gap.

**AI** generates implementations that pass the tests. It also assists with refactoring, optimization, and translation across languages.

**Reviewers** validate that specifications are precise, tests are faithful to specs, and the traceability matrix has no gaps. PR reviews in STDD focus on the knowledge layer first, implementation second.

---

# 7. Conclusion

This playbook covers the practical aspects of applying STDD: repository structure, test-first prompting, decomposition, CSI pipelines, and team roles. For the underlying principles, see the [Method](method.md). For a complete worked example, see the [Seat Reservation API](../examples/seat-reservation.md).
