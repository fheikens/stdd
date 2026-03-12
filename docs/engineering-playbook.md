
# The STDD Engineering Playbook
## Applying Specification & Test-Driven Development in Real Projects

Author: Frank Heikens
Version: 1.2
Date: 2026

---

## Table of Contents

- [1. Introduction](#1-introduction)
- [2. Repository Structure](#2-repository-structure)
- [3. Test-First Prompting (TFP)](#3-test-first-prompting-tfp)
  - [TFP for Integration and System Tests](#tfp-for-integration-and-system-tests)
  - [TFP Across Languages](#tfp-across-languages)
- [4. Decomposition and the Specification Pyramid](#4-decomposition-and-the-specification-pyramid)
  - [When Decomposition Reveals Specification Gaps](#when-decomposition-reveals-specification-gaps)
- [5. Continuous Specification Integrity (CSI)](#5-continuous-specification-integrity-csi)
  - [Fingerprint Operations](#fingerprint-operations)
- [6. Team Roles in STDD](#6-team-roles-in-stdd)
- [7. Failure Mode Catalog](#7-failure-mode-catalog)
- [8. Pre-Flight Checklists](#8-pre-flight-checklists)
- [9. Conclusion](#9-conclusion)

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

## TFP for Integration and System Tests

The TFP examples above target unit-level generation. The same structure applies at integration and system levels, with two key differences: the prompt includes contracts between real components, and the tests exercise actual collaboration rather than isolated behavior.

### Integration-Level TFP Prompt

```
Specification:
ReservationService.confirm_reservation accepts a hold ID. It must:
1. Look up the hold via SeatInventory.get_hold(hold_id)
2. Calculate the final price via PricingEngine.calculate(section, event_id, group_size)
3. Mark seats as confirmed via SeatInventory.confirm_seats(seat_ids)
4. Return a Confirmation with the calculated price and confirmed seat IDs

If the hold has expired, raise HoldExpiredError before any price calculation
or seat confirmation occurs.

Contracts:
- SeatInventory provides: get_hold(hold_id) -> Hold, confirm_seats(seat_ids) -> None
- PricingEngine provides: calculate(section, event_id, group_size) -> PriceResult
- Hold contains: seat_ids, section, event_id, expiry_time

Integration Tests:
[paste tests that use real SeatInventory and real PricingEngine instances]

Example assertions:
  result = service.confirm_reservation(hold_id)
  assert result.total_price == Decimal("180.00")
  assert inventory.get_seat_status("A1") == SeatStatus.CONFIRMED
  assert inventory.get_seat_status("A2") == SeatStatus.CONFIRMED

Constraints:
- Use real dependencies, not mocks. Integration tests verify actual collaboration.
- SeatInventory and PricingEngine must be initialized with test data.
- All state changes must be atomic: if pricing fails, seats must not be confirmed.
- Use Decimal arithmetic throughout.

Generate the confirm_reservation method that passes all integration tests.
```

The critical difference from unit TFP: the instruction to use real dependencies. At the unit level, you test `calculate_price` in isolation. At the integration level, you verify that `ReservationService` actually calls `PricingEngine` correctly and that the returned price flows through to the confirmation.

### System-Level TFP Prompt

```
Specification:
Full seat reservation workflow from listing through confirmation.
The system must support this exact sequence:
1. List available seats for event E1 → returns seats including A1, A2
2. Hold seats A1, A2 → returns hold_id with 15-minute expiry
3. Confirm hold → returns confirmation with calculated price
4. List available seats again → A1, A2 no longer appear

System Tests:
[paste end-to-end test that exercises the full stack]

Example test:
  def test_full_reservation_workflow():
      api = ReservationAPI(inventory, pricing, clock)

      available = api.list_available("E1", "Orchestra")
      assert "A1" in available
      assert "A2" in available

      hold = api.hold_seats("E1", ["A1", "A2"])
      assert hold.expiry_time == clock.now() + timedelta(minutes=15)

      confirmation = api.confirm(hold.hold_id)
      assert confirmation.total_price == Decimal("180.00")
      assert confirmation.seats == ["A1", "A2"]

      available_after = api.list_available("E1", "Orchestra")
      assert "A1" not in available_after
      assert "A2" not in available_after

Constraints:
- This test exercises the full stack: API layer, service layer, inventory, pricing.
- No mocks at any level.
- Clock is injectable for deterministic time behavior.

Generate the ReservationAPI class that passes the system test.
```

System-level TFP prompts are larger because they include the full context. This is intentional. The AI needs to see the entire workflow to generate code that satisfies end-to-end behavior.

## TFP Across Languages

The specification is language-independent. When you move from Python to Go (or any other language), the specification stays identical. Only the test syntax and constraints section change.

### Go TFP Prompt for calculate_price

```
Specification:
calculate_price accepts a section name, event identifier, and group size.
It returns a unit price and total price. Group discount of 10% applies for
groups of 4 or more. Prices are rounded to 2 decimal places.

Tests:
[paste Go table-driven tests]

Example test structure:
  func TestCalculatePrice(t *testing.T) {
      tests := []struct {
          name      string
          section   string
          eventID   string
          groupSize int
          wantUnit  decimal.Decimal
          wantTotal decimal.Decimal
          wantErr   bool
      }{
          {
              name:      "standard pricing no discount",
              section:   "Orchestra",
              eventID:   "E1",
              groupSize: 2,
              wantUnit:  decimal.NewFromInt(100),
              wantTotal: decimal.NewFromInt(200),
          },
          {
              name:      "group discount applied",
              section:   "Orchestra",
              eventID:   "E1",
              groupSize: 4,
              wantUnit:  decimal.NewFromInt(100),
              wantTotal: decimal.RequireFromString("360.00"),
          },
          {
              name:      "invalid section",
              section:   "Nonexistent",
              eventID:   "E1",
              groupSize: 1,
              wantErr:   true,
          },
      }

      for _, tt := range tests {
          t.Run(tt.name, func(t *testing.T) {
              unit, total, err := CalculatePrice(tt.section, tt.eventID, tt.groupSize)
              if tt.wantErr {
                  assert.Error(t, err)
                  return
              }
              assert.NoError(t, err)
              assert.True(t, tt.wantUnit.Equal(unit))
              assert.True(t, tt.wantTotal.Equal(total))
          })
      }
  }

Constraints:
- Use shopspring/decimal for all price arithmetic, not float64
- Return (unitPrice, totalPrice, error) — use explicit error returns, not panics
- Single responsibility, function body approximately 50 lines
- Group size < 1 returns an error

Generate a Go function that passes all tests.
```

### What Changes Across Languages

| Aspect | Python | Go |
|--------|--------|-----|
| Specification | Identical | Identical |
| Test structure | Individual test functions | Table-driven tests |
| Error handling | `raise ValueError` | Return `error` |
| Decimal library | `decimal.Decimal` | `shopspring/decimal` |
| Line constraint | ~50 lines | ~50 lines (Go is more verbose, so this may mean fewer logical steps) |

The specification is the invariant. The tests are its translation into a specific language's idioms. This is why STDD treats the specification — not the implementation — as the source of truth.

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

## When Decomposition Reveals Specification Gaps

Decomposition often exposes behaviors that were never specified. This is not a failure — it is one of the most valuable outcomes of the process.

### A Concrete Example

You are decomposing `ReservationService` into its constituent methods: `hold_seats`, `confirm_reservation`, `cancel_hold`, and `expire_holds`. While writing the specification for `confirm_reservation`, you realize a question has no answer:

**What happens when a hold expires at the exact moment a confirmation request arrives?**

The specification says holds expire after 15 minutes. The specification says confirmation requires a valid hold. But the specification says nothing about the race condition between expiry and confirmation. Does the confirmation succeed because the hold was valid when the request started? Does it fail because the hold expired during processing? Is there a grace period?

This is a specification gap. No test covers it because no one specified the behavior.

### The Procedure

When you discover a specification gap during decomposition:

1. **Stop generation.** Do not generate code that handles an unspecified case. Any implementation would be a guess, and guesses are not specifications.

2. **Add the missing behavioral scenario to the specification.** Define the exact behavior:
   ```
   HOLD-EXP-RACE: If a hold expires during confirmation processing,
   the confirmation must fail with HoldExpiredError. The expiry check
   occurs at confirmation time, not at request receipt time. There is
   no grace period.
   ```

3. **Add the corresponding test.**
   ```python
   def test_hold_expires_during_confirmation(clock, service):
       """HOLD-EXP-RACE: Hold that expires during confirmation fails."""
       hold = service.hold_seats("E1", ["A1"])
       clock.advance(minutes=15)  # Hold has now expired
       with pytest.raises(HoldExpiredError):
           service.confirm_reservation(hold.hold_id)
       assert service.inventory.get_seat_status("A1") == SeatStatus.AVAILABLE
   ```

4. **Update the traceability matrix.** Add the new spec ID (`HOLD-EXP-RACE`) and link it to the test.

5. **Resume generation with the strengthened specification.** The AI now has an unambiguous requirement for this edge case.

### Why This Matters

Discovering gaps during decomposition is normal and expected. It means the process is working. The alternative — discovering these gaps in production when a customer's confirmation silently succeeds on an expired hold — is far more expensive.

Every gap you find and specify before generation is a bug that will never exist.

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
        run: >
          python scripts/validate_traceability.py
          --spec-dir features/
          --test-dir tests/

      - name: Run test suite
        run: pytest tests/ -v --tb=short

      - name: Verify specification fingerprint
        run: >
          python scripts/compute_fingerprint.py
          --spec-dir features/
          --test-dir tests/
          --nfr-file features/nfr.md
          --compare
```

## Specification Fingerprint in CI

The Specification Fingerprint is a hash of the knowledge layer that detects drift.

### Computing the Fingerprint — `compute_fingerprint.py`

```python
#!/usr/bin/env python3
"""Compute the specification fingerprint for an STDD project.

Usage:
    python compute_fingerprint.py --spec-dir features/ --test-dir tests/ --nfr-file features/nfr.md
    python compute_fingerprint.py --spec-dir features/ --test-dir tests/ --compare
    python compute_fingerprint.py --spec-dir features/ --test-dir tests/ --update

Exit codes:
    0  Fingerprint matches stored value, or update succeeded, or first run
    1  Fingerprint mismatch (knowledge layer changed)
"""

import argparse
import hashlib
import pathlib
import sys

FINGERPRINT_FILE = ".fingerprint"


def compute_fingerprint(spec_dir: str, test_dir: str, nfr_file: str | None = None) -> str:
    """Hash all specification and test files to produce a fingerprint."""
    hasher = hashlib.sha256()

    for directory in [spec_dir, test_dir]:
        path = pathlib.Path(directory)
        if not path.exists():
            print(f"Warning: directory {directory} does not exist", file=sys.stderr)
            continue
        for filepath in sorted(path.rglob("*")):
            if filepath.is_file():
                hasher.update(str(filepath.relative_to(path)).encode())
                hasher.update(filepath.read_bytes())

    if nfr_file:
        nfr_path = pathlib.Path(nfr_file)
        if nfr_path.exists():
            hasher.update(nfr_path.read_bytes())

    return hasher.hexdigest()


def main():
    parser = argparse.ArgumentParser(description="STDD Specification Fingerprint")
    parser.add_argument("--spec-dir", required=True, help="Directory containing specifications")
    parser.add_argument("--test-dir", required=True, help="Directory containing tests")
    parser.add_argument("--nfr-file", default=None, help="Path to NFR file")
    parser.add_argument("--compare", action="store_true",
                        help="Compare against stored fingerprint, exit 1 on mismatch")
    parser.add_argument("--update", action="store_true",
                        help="Write new fingerprint to .fingerprint file")
    args = parser.parse_args()

    fingerprint = compute_fingerprint(args.spec_dir, args.test_dir, args.nfr_file)
    print(fingerprint)

    if args.compare:
        fp_path = pathlib.Path(FINGERPRINT_FILE)
        if not fp_path.exists():
            print("No .fingerprint file found. This appears to be the first run.",
                  file=sys.stderr)
            print("Run with --update to create the .fingerprint file.", file=sys.stderr)
            sys.exit(0)

        stored = fp_path.read_text().strip()
        if stored != fingerprint:
            print("MISMATCH: specification fingerprint has changed.", file=sys.stderr)
            print(f"  Stored:  {stored}", file=sys.stderr)
            print(f"  Current: {fingerprint}", file=sys.stderr)
            sys.exit(1)
        else:
            print("Fingerprint matches.", file=sys.stderr)

    if args.update:
        pathlib.Path(FINGERPRINT_FILE).write_text(fingerprint + "\n")
        print(f"Updated {FINGERPRINT_FILE}", file=sys.stderr)


if __name__ == "__main__":
    main()
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

## Traceability Validation — `validate_traceability.py`

```python
#!/usr/bin/env python3
"""Validate that every specification ID has at least one corresponding test.

Usage:
    python validate_traceability.py --spec-dir features/ --test-dir tests/

Scans all .md files in spec-dir for spec IDs (pattern: | WORD-NUMBER in tables).
Scans all test files in test-dir for references to those IDs in docstrings,
comments, or test names.

Exit codes:
    0  All specifications have tests
    1  One or more specifications are untested
"""

import argparse
import pathlib
import re
import sys

SPEC_ID_PATTERN = re.compile(r"^\|\s*(\w+-\d+)", re.MULTILINE)
TEST_FILE_PATTERNS = ["test_*.py", "*_test.py", "*_test.go", "test_*.go"]


def find_spec_ids(spec_dir: str) -> dict[str, str]:
    """Find all spec IDs in .md files. Returns {id: source_file}."""
    spec_ids = {}
    spec_path = pathlib.Path(spec_dir)
    if not spec_path.exists():
        print(f"Error: spec directory {spec_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    for md_file in sorted(spec_path.rglob("*.md")):
        for match in SPEC_ID_PATTERN.finditer(md_file.read_text()):
            spec_ids[match.group(1)] = str(md_file)
    return spec_ids


def find_tested_ids(test_dir: str) -> set[str]:
    """Scan test files for spec ID references."""
    tested = set()
    test_path = pathlib.Path(test_dir)
    if not test_path.exists():
        print(f"Error: test directory {test_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    for pattern in TEST_FILE_PATTERNS:
        for test_file in sorted(test_path.rglob(pattern)):
            content = test_file.read_text()
            for match in re.finditer(r"\b(\w+-\d+)\b", content):
                tested.add(match.group(1))
    return tested


def main():
    parser = argparse.ArgumentParser(description="STDD Traceability Validator")
    parser.add_argument("--spec-dir", required=True, help="Directory containing specifications")
    parser.add_argument("--test-dir", required=True, help="Directory containing tests")
    args = parser.parse_args()

    spec_ids = find_spec_ids(args.spec_dir)
    tested_ids = find_tested_ids(args.test_dir)

    covered = []
    missing = []

    for spec_id, source in sorted(spec_ids.items()):
        if spec_id in tested_ids:
            covered.append((spec_id, source))
        else:
            missing.append((spec_id, source))

    print(f"Specifications found: {len(spec_ids)}")
    print(f"Covered by tests:     {len(covered)}")
    print(f"Missing tests:        {len(missing)}")
    print()

    if covered:
        print("COVERED:")
        for spec_id, source in covered:
            print(f"  {spec_id}  ({source})")
        print()

    if missing:
        print("MISSING TESTS:")
        for spec_id, source in missing:
            print(f"  {spec_id}  ({source})")
        print()
        print("FAILED: untested specifications found.", file=sys.stderr)
        sys.exit(1)
    else:
        print("All specifications have corresponding tests.")


if __name__ == "__main__":
    main()
```

## Fingerprint Operations

The `.fingerprint` file anchors the knowledge layer to a known state. Here is how it fits into the development workflow.

**First run.** When `--compare` finds no `.fingerprint` file, it succeeds (exit code 0) and prints a recommendation to run `--update`. This avoids blocking CI on a brand-new project that has not yet established a baseline.

**After intentional spec changes.** When you add a new specification, modify an existing one, or update tests, the fingerprint changes. Run `--update` to record the new baseline:

```
python scripts/compute_fingerprint.py --spec-dir features/ --test-dir tests/ --nfr-file features/nfr.md --update
```

Commit the updated `.fingerprint` file alongside the spec and test changes in the same PR. This makes the intent explicit: "I changed the knowledge layer and I know it."

**CI on every PR.** The CI pipeline runs `--compare`. If the fingerprint differs from the committed `.fingerprint` file, the build fails. The developer must either run `--update` (if the change is intentional) or revert the unintended spec/test modification.

**The `.fingerprint` file is committed to version control.** It belongs in the repository alongside the specifications and tests. It is part of the knowledge layer.

**Pure implementation changes do not change the fingerprint.** If you regenerate `calculate_price` with a different algorithm but the same specification and tests, the fingerprint stays the same. This is the entire point. The fingerprint tracks behavioral intent, not implementation details. Regeneration is invisible to the fingerprint — exactly as it should be.

---

# 6. Team Roles in STDD

STDD changes how teams collaborate.

**Specification authors** (engineers, product owners, domain experts) define what the system must do. They write specifications, behavioral scenarios, invariants, and acceptance cases.

**Test authors** (engineers, QA) translate specifications into executable tests at all pyramid levels. They maintain the traceability matrix and close the spec-to-test gap.

**AI** generates implementations that pass the tests. It also assists with refactoring, optimization, and translation across languages.

**Reviewers** validate that specifications are precise, tests are faithful to specs, and the traceability matrix has no gaps. PR reviews in STDD focus on the knowledge layer first, implementation second.

---

# 7. Failure Mode Catalog

STDD is a disciplined process, but things still go wrong. This catalog documents the most common failure modes, their symptoms, and the recovery procedures. Treat this as a diagnostic reference when something breaks.

### 7.1 AI generates code that passes tests but violates an unspecified invariant

- **Symptom**: Code works in tests but fails in production or integration.
- **Cause**: Missing invariant in specification.
- **Recovery**: Add the invariant, add a test for it, regenerate.

### 7.2 Specification is ambiguous — AI picks one interpretation, team expected another

- **Symptom**: Tests pass but the behavior is not what was intended.
- **Cause**: Specification language allows multiple valid interpretations.
- **Recovery**: Rewrite the ambiguous clause with concrete examples, add boundary tests.

### 7.3 Component too large for reliable generation

- **Symptom**: AI generates code with subtle bugs, requires many attempts, or produces inconsistent results.
- **Cause**: Component has too many responsibilities or exceeds ~50 lines.
- **Recovery**: Decompose into smaller functions, each with own spec and tests.

### 7.4 Tests pass but integration breaks

- **Symptom**: Unit tests pass after regeneration, but integration or system tests fail.
- **Cause**: The regenerated component satisfies its own contract but violates assumptions of dependent components.
- **Recovery**: Add integration tests that exercise the collaboration, verify contracts between components.

### 7.5 Specification drift — spec and implementation diverge over time

- **Symptom**: Fingerprint check fails, or regeneration produces different behavior than the running system.
- **Cause**: Implementation was modified without updating the specification.
- **Recovery**: Treat the fingerprint failure as a blocking CI gate, update spec to match intended behavior, regenerate.

### 7.6 Over-specification — spec is so detailed it constrains implementation unnecessarily

- **Symptom**: AI can only generate one possible implementation, or trivial refactoring breaks tests.
- **Cause**: Specification describes HOW instead of WHAT.
- **Recovery**: Rewrite specification to focus on inputs, outputs, and invariants — not on internal steps or data structures.

---

# 8. Pre-Flight Checklists

These checklists codify the verification steps that teams perform at three critical moments in the STDD workflow. Use them as gate checks — do not proceed until every item is satisfied.

### Before Generation

- [ ] Specification has inputs, outputs, invariants, and failure conditions
- [ ] Every behavioral scenario has a corresponding test
- [ ] Traceability matrix is complete (no untested spec IDs)
- [ ] NFR constraints are included in the prompt (decimal precision, line limits, error handling)
- [ ] Component fits within ~50 lines; if not, decompose first

### Before Review

- [ ] All tests pass (unit, integration, system)
- [ ] Specification fingerprint is current
- [ ] Generated code is readable (no obfuscated AI output)
- [ ] No behavior exists in the implementation that is not in the specification
- [ ] Traceability matrix matches between spec IDs and test names

### Before Merge

- [ ] PR includes specification, tests, and implementation together
- [ ] CI pipeline passes all three gates (traceability, tests, fingerprint)
- [ ] Specification changes have been reviewed for precision and completeness
- [ ] No orphaned tests (tests without spec IDs) or untested specs
- [ ] Regeneration has been validated: discard implementation, regenerate, tests still pass

---

# 9. Conclusion

This playbook covers the practical aspects of applying STDD: repository structure, test-first prompting, decomposition, CSI pipelines, team roles, failure mode recovery, and pre-flight checklists. For the underlying principles, see the [Method](method.md). For a complete worked example, see the [Seat Reservation API](../examples/seat-reservation.md).
