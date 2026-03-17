# Worked Example: The STDD Core Model in Practice
## Seat Reservation System Through the Lens of STDD v2

Author: Frank Heikens
Version: 1.0
Date: 2026

---

This document shows how the [STDD Core Model](stdd-core-model.md) applies to a real system. It uses the seat reservation API — the same system from [the end-to-end example](../examples/seat-reservation.md) — and annotates it with the v2 concepts: specification types, test types, lifecycle states, traceability columns, and execution flows.

If you want to understand what changed in STDD v2 and how it works in practice, this is the document to read.

---

## 1. Metadata Headers

Every specification now carries a metadata header that identifies its type and lifecycle state. Here is how the seat reservation specifications look with v2 metadata.

### Behavioral specification

```
Feature: Seat Hold and Confirmation
Version: 1.2
Type: behavioral
Status: ACTIVE

---

## Description

Customers hold available seats temporarily and confirm within the hold period.
Expired holds release seats automatically.

## Rules

| ID | Description |
|----|-------------|
| SEAT-HOLD-01 | A customer can hold an available seat. The seat becomes unavailable. |
| SEAT-HOLD-02 | A seat that is already held cannot be held by another customer. |
| SEAT-CONF-01 | A valid, unexpired hold can be confirmed into a reservation. |
| SEAT-CONF-02 | An expired hold cannot be confirmed. The seat returns to available. |

## Invariants

| ID | Description |
|----|-------------|
| INV-01 | A seat is in exactly one state at any time: available, held, or reserved. |
| INV-03 | At most one customer can hold or reserve a given seat at any time. |
| INV-04 | State transitions follow: available → held → reserved, held → available, reserved → available. No others. |
```

The `Type: behavioral` field tells you this specification defines correctness — what the system must do. Every rule must have a test.

### Integration mapping

```
Contract: ReservationService → PricingEngine
Version: 1.0
Type: integration-mapping
Status: ACTIVE

---

## Description

When a hold is confirmed, ReservationService calls PricingEngine to
calculate the final price. This contract defines what ReservationService
expects from PricingEngine and what PricingEngine must provide.

## Interface

  PricingEngine.calculate(section: str, event_id: str, group_size: int)
    → { unit_price: Decimal, total_price: Decimal }

## Contract rules

| ID | Description |
|----|-------------|
| CTR-PRICE-01 | calculate() returns unit_price and total_price as Decimal with 2 decimal places. |
| CTR-PRICE-02 | Same inputs always produce the same output (deterministic). |
| CTR-PRICE-03 | Unknown section raises ValueError("Unknown section"). |
| CTR-PRICE-04 | group_size < 1 raises ValueError("Invalid group size"). |

## Error handling

ReservationService catches PricingEngine errors and reports them to the
caller. It does not retry pricing failures.
```

The `Type: integration-mapping` field tells you this defines how two components connect — the contract between them. Both sides must test against it.

### Configuration decision

```
Decision: Hold Duration Default
Version: 1.0
Type: configuration-decision
Status: ACTIVE

---

## Choice

Default hold duration: 10 minutes per event.

## Alternatives considered

- 5 minutes: Too short — customers complained in user testing that they could
  not complete payment forms in time.
- 30 minutes: Too long — popular events would have too many seats locked up
  by customers who abandoned the process.
- Configurable per event with no default: Puts the burden on event operators
  who do not have data to make the decision.

## Rationale

10 minutes balances conversion (most customers complete within 7 minutes)
against availability (seats are not locked beyond a reasonable window).

## Implications

- SEAT-HOLD-01 references this duration as the default.
- The hold_minutes parameter on each event can override this default.
- Changing this default does not change the system's correctness — it changes
  its tuning. The behavioral specification (hold expiry rules) remains valid
  for any positive duration.
```

A configuration decision has no mandatory tests. The 10-minute default is not a correctness rule — any positive duration is correct. The behavioral rules about expiry are in the behavioral specification, not here.

---

## 2. Spec Classification: What Goes Where

The seat reservation system has all three specification types. Here is how to tell them apart.

### The distinction in one sentence

- **Behavioral:** "Duplicate holds must be rejected." → Defines correctness. If violated, the system is wrong.
- **Integration mapping:** "PricingEngine.calculate() returns Decimal with 2 places." → Defines a contract. If violated, the wiring is broken.
- **Configuration decision:** "Default hold duration is 10 minutes." → Documents a choice. If changed, the system is tuned differently but not broken.

### Concrete examples from the seat reservation system

| Statement | Type | Why |
|---|---|---|
| "A held seat cannot be held by another customer" | Behavioral | Defines a correctness rule. Violating it means double-booking. |
| "Expired holds release the seat to available" | Behavioral | Defines intended system behavior. |
| "PricingEngine raises ValueError for unknown sections" | Integration mapping | Defines the error contract between ReservationService and PricingEngine. |
| "ReservationService catches pricing errors and reports them" | Integration mapping | Defines how the caller handles dependency failures. |
| "Use `shopspring/decimal` for Go monetary calculations" | Configuration decision | Documents a library choice. Any correct decimal library would work. |
| "Hold duration defaults to 10 minutes" | Configuration decision | Documents tuning. 5 or 15 minutes would also be correct. |

### The boundary case

Some statements live at the boundary. Consider:

> "All price calculations use Decimal arithmetic, not float."

This is a **behavioral constraint** (part of a behavioral specification), not a configuration decision. It defines a correctness invariant — using float would produce incorrect rounding. The *library* used to achieve decimal arithmetic is a configuration decision. The *requirement* for decimal arithmetic is behavioral.

---

## 3. Numbered Requirements

The seat reservation system has these behavioral requirements. Each has a spec ID, and each is tested.

| Spec ID | Requirement | Behavioral? |
|---|---|---|
| SEAT-LIST-01 | List returns only available seats for an event | Yes |
| SEAT-LIST-03 | Unknown event returns "Event not found" | Yes |
| SEAT-HOLD-01 | Customer can hold an available seat | Yes |
| SEAT-HOLD-02 | Held seat cannot be held by another customer | Yes |
| SEAT-CONF-01 | Valid unexpired hold can be confirmed | Yes |
| SEAT-CONF-02 | Expired hold cannot be confirmed | Yes |
| SEAT-CANCEL-01 | Customer can cancel their hold | Yes |
| PRICE-01 | Price = base × event multiplier | Yes |
| PRICE-02 | 10% group discount for 4+ seats | Yes |
| INV-01 | Seat in exactly one state at any time | Yes (invariant) |
| INV-03 | No double-booking | Yes (invariant) |
| CTR-PRICE-01 | PricingEngine returns Decimal with 2 places | No — this is a contract rule |
| CTR-PRICE-02 | PricingEngine is deterministic | No — contract rule |

All spec IDs starting with `SEAT-`, `PRICE-`, or `INV-` are behavioral — they define what the system must do. Spec IDs starting with `CTR-` are contract rules from integration mappings — they define how components connect.

---

## 4. Test Classification

The seat reservation test suite contains all three test types. Here is what each type proves and what it does not prove.

### Requirement tests

Requirement tests verify behavioral specification rules directly.

```python
def test_hold_already_held_seat(inventory):
    """SEAT-HOLD-02: Cannot hold a seat that is already held."""
    inv, service, _ = inventory
    service.hold_seat("concert-1", "S1", "cust-1")

    with pytest.raises(ValueError, match="Seat is not available"):
        service.hold_seat("concert-1", "S1", "cust-2")

    assert inv.get_seat_status("concert-1", "S1") == "held"
```

**What it proves:** The system rejects a second hold on an already-held seat (SEAT-HOLD-02).

**What it does not prove:** That the rejection works correctly when two hold requests arrive simultaneously. That is a separate concern (concurrency), addressed by INV-03 and NFR-EXCLUSIVE.

```python
def test_invariant_no_double_booking(inventory):
    """INV-03: At most one customer can hold a seat."""
    _, service, _ = inventory
    service.hold_seat("concert-1", "S1", "cust-1")

    with pytest.raises(ValueError):
        service.hold_seat("concert-1", "S1", "cust-2")
```

**What it proves:** The no-double-booking invariant holds across the tested scenario.

**What it does not prove:** That it holds for all possible sequences of operations. Property-based tests would strengthen this. This test provides COVERED status for INV-03 in the traceability matrix.

### Integration tests

Integration tests verify that components work correctly together.

```python
def test_integration_confirm_uses_correct_pricing(inventory):
    """INT-01: Confirmation price matches PricingEngine for the seat's section."""
    _, service, pricing = inventory

    hold = service.hold_seat("concert-1", "S1", "cust-1")
    result = service.confirm_reservation(hold["hold_id"], "cust-1")

    expected = pricing.calculate("orchestra", "concert-1", group_size=1)
    assert result["final_price"] == expected["unit_price"]
```

**What it proves:** ReservationService actually calls PricingEngine correctly and the returned price flows through to the confirmation response (INT-01, which validates CTR-PRICE-01 in practice).

**What it does not prove:** That PricingEngine calculates the correct price — that is PRICE-01, verified by a separate requirement test. This test only verifies the wiring.

```python
def test_integration_expiry_then_rebook(inventory, clock):
    """INT-02: After a hold expires, another customer can hold the same seat."""
    inv, service, _ = inventory
    service.hold_seat("concert-1", "S1", "cust-1")
    clock.advance(minutes=11)
    service.process_expired_holds()

    result = service.hold_seat("concert-1", "S1", "cust-2")
    assert "hold_id" in result
```

**What it proves:** The expiry system and the hold system work together — expired holds genuinely release seats for new customers (INT-02).

**What it does not prove:** That expiry processing itself is correct in isolation — that is SEAT-EXPIRY-01.

### Regression artifact (hypothetical example)

The seat reservation system does not currently use golden files, but here is what one would look like:

```python
def test_api_response_format_golden(inventory):
    """GOLDEN-01: API response structure matches approved baseline."""
    _, service, _ = inventory
    hold = service.hold_seat("concert-1", "S1", "cust-1")
    result = service.confirm_reservation(hold["hold_id"], "cust-1")

    # Compare against golden file
    expected = load_golden_file("confirm_response.json")
    assert normalize(result) == expected
```

**What it proves:** The response structure has not changed since the baseline was approved.

**What it does not prove:** That the response is *correct*. The golden file might contain an incorrect baseline. This is why regression artifacts provide PARTIALLY COVERED status, not full COVERED status.

**When to use this:** When the response structure is complex enough that writing individual assertions for every field would be impractical. For the seat reservation system, the response is simple enough that individual assertions (as in the requirement tests) are preferable.

---

## 5. Traceability Matrix with v2 Columns

The v2 traceability matrix adds spec type, spec status, and test type columns. Here is a representative subset from the seat reservation system.

| Spec ID | Spec Type | Spec Status | Test | Test Type | Coverage |
|---|---|---|---|---|---|
| SEAT-HOLD-01 | behavioral | ACTIVE | test_hold_available_seat | requirement | COVERED |
| SEAT-HOLD-02 | behavioral | ACTIVE | test_hold_already_held_seat | requirement | COVERED |
| SEAT-CONF-01 | behavioral | ACTIVE | test_confirm_valid_hold | requirement | COVERED |
| SEAT-CONF-02 | behavioral | ACTIVE | test_confirm_expired_hold | requirement | COVERED |
| INV-01 | behavioral | ACTIVE | test_invariant_seat_status_exclusive | requirement | COVERED |
| INV-03 | behavioral | ACTIVE | test_invariant_no_double_booking | requirement | COVERED |
| PRICE-01 | behavioral | ACTIVE | test_standard_pricing | requirement | COVERED |
| PRICE-02 | behavioral | ACTIVE | test_group_discount | requirement | COVERED |
| CTR-PRICE-01 | contract | ACTIVE | test_integration_confirm_uses_correct_pricing | integration | COVERED |
| CTR-PRICE-02 | contract | ACTIVE | test_invariant_price_deterministic | integration | COVERED |
| INT-01 | contract | ACTIVE | test_integration_confirm_uses_correct_pricing | integration | COVERED |
| INT-02 | contract | ACTIVE | test_integration_expiry_then_rebook | integration | COVERED |
| SYS-01 | behavioral | ACTIVE | test_system_full_booking_workflow | integration | COVERED |
| SYS-02 | behavioral | ACTIVE | test_system_competing_customers | integration | COVERED |
| NFR-DECIMAL | behavioral | ACTIVE | test_nfr_decimal_arithmetic | requirement | COVERED |
| GOLDEN-01 | behavioral | ACTIVE | test_api_response_format_golden | regression | PARTIALLY COVERED |

### Reading this matrix

**Requirement coverage** (behavioral rules verified by requirement tests):
SEAT-HOLD-01, SEAT-HOLD-02, SEAT-CONF-01, SEAT-CONF-02, INV-01, INV-03, PRICE-01, PRICE-02, NFR-DECIMAL → all COVERED.

**Integration coverage** (contracts verified by integration tests):
CTR-PRICE-01, CTR-PRICE-02, INT-01, INT-02, SYS-01, SYS-02 → all COVERED.

**Regression coverage:**
GOLDEN-01 → PARTIALLY COVERED. This rule needs a requirement test to reach full COVERED status.

The key insight: requirement coverage and integration coverage are tracked independently. A system can have 100% requirement coverage and 0% integration coverage — meaning every component works in isolation but the wiring is untested. The v2 matrix makes this visible.

---

## 6. Bug-Fix Flow in Practice

Here is a concrete example of the bug-fix flow applied to the seat reservation system.

### The bug

A tester reports: "When I hold seat S1 and the hold expires, I try to confirm and get `Hold has expired`. But the seat stays in `held` status instead of returning to `available`."

### Diagnosis

Look at the specification:

> **SEAT-CONF-02:** An expired hold cannot be confirmed. The seat returns to available.

The spec already defines the correct behavior. The seat should be available after a failed confirmation of an expired hold. This is a **bug in the implementation**, not a gap in the specification.

### Check for test coverage

Look at the test:

```python
def test_confirm_expired_hold(inventory, clock):
    """SEAT-CONF-02: Cannot confirm an expired hold."""
    inv, service, _ = inventory
    hold = service.hold_seat("concert-1", "S1", "cust-1")
    clock.advance(minutes=11)

    with pytest.raises(ValueError, match="Hold has expired"):
        service.confirm_reservation(hold["hold_id"], "cust-1")

    assert inv.get_seat_status("concert-1", "S1") == "available"  # ← This assertion
```

The test exists and asserts the correct behavior. Run it — it fails. The assertion `seat_status == "available"` fails because the implementation leaves the seat in `held` status.

### The fix

```
1. ✓ Spec already correct (SEAT-CONF-02 defines the behavior)
2. ✓ Test already exists and correctly catches the bug
3. → Fix the implementation: in confirm_reservation(), when the hold is
     expired, set seat status to "available" before raising HoldExpiredError
4. → Run full test pyramid → all tests pass
5. → Commit the fix
```

### What did NOT happen

- No specification update. The spec was already right.
- No new spec rules. SEAT-CONF-02 already covered this behavior.
- No new test. The existing test already caught the bug.

This is the bug-fix flow: **the specification defined the intended behavior before the bug was found, so the fix proceeds directly without rewriting the spec.** The spec-first principle is not violated — the spec was written first, the implementation just failed to follow it.

### When the test does NOT exist

If the tester had reported the same bug but `test_confirm_expired_hold` did not include the `assert seat_status == "available"` line, the flow would be:

```
1. ✓ Spec already correct (SEAT-CONF-02 defines the behavior)
2. ✗ Test exists but does not assert seat status → test gap
3. → Strengthen the test: add the missing assertion
4. → Fix the implementation
5. → Run full test pyramid
6. → Commit both the test improvement and the fix
```

This is still the bug-fix flow, not the new-feature flow. The spec was already right. The test was incomplete. The fix and the test improvement go together.

---

## 7. Lifecycle in Practice

### Current state

All seat reservation specifications are **ACTIVE**. They have passed review, have full test coverage, and are the current definition of correctness.

### How supersession would work

Suppose the venue operator requests a new feature: tiered hold durations based on customer loyalty status (standard: 10 min, premium: 20 min, VIP: 30 min). This changes the hold behavior fundamentally enough to warrant a new specification version.

**Before:**

```
Feature: Seat Hold and Confirmation
Version: 1.2
Type: behavioral
Status: ACTIVE                            ← currently authoritative
```

**After the change:**

The original specification is superseded:

```
Feature: Seat Hold and Confirmation
Version: 1.2
Type: behavioral
Status: SUPERSEDED                        ← no longer authoritative
Superseded-by: features/seat-hold-v2/specification.md
```

The new specification replaces it:

```
Feature: Seat Hold and Confirmation (Tiered)
Version: 2.0
Type: behavioral
Status: ACTIVE                            ← now authoritative
Supersedes: features/seat-hold-v1/specification.md
```

The superseded specification is kept for reference. Its tests are migrated to the new specification or removed. The traceability matrix shows the old spec IDs as SUPERSEDED and the new spec IDs as ACTIVE.

The configuration decision about hold duration would also be superseded, since the single default is replaced by a tiered model:

```
Decision: Hold Duration Default
Version: 1.0
Type: configuration-decision
Status: SUPERSEDED
Superseded-by: decisions/tiered-hold-duration.md
```

---

## 8. Putting It All Together

The STDD v2 model adds structure that was previously implicit:

1. **Metadata headers** make type and lifecycle machine-readable.
2. **Specification types** distinguish correctness rules (behavioral) from wiring contracts (integration mapping) from documented choices (configuration decision).
3. **Test types** distinguish correctness verification (requirement test) from wiring verification (integration test) from change detection (regression artifact).
4. **The traceability matrix** tracks these types separately, making coverage gaps visible by category.
5. **Execution flows** allow pragmatic handling of bug fixes and discovery work without forcing everything through the spec-first pipeline.
6. **Lifecycle states** provide an explicit model for how specifications evolve, are replaced, or are retired.

None of this changes what STDD is. Specifications still define intent. Tests still verify behavior. Implementations are still disposable. The v2 model makes the method more precise, more teachable, and better prepared for teams working at scale.

---

For the full seat reservation example (specifications, tests, implementation, regeneration), see [End-to-End Example: Seat Reservation API](../examples/seat-reservation.md).

For the complete core model definition, see [STDD Core Model](stdd-core-model.md).

For guidance on transitioning from earlier STDD practices, see [v2 Transition Notes](stdd-v2-transition-notes.md).
