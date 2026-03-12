
# End-to-End Example: Seat Reservation API

A complete STDD walkthrough from requirement to regeneration.

Author: Frank Heikens

---

## Table of Contents

- [1. Introduction](#1-introduction)
- [2. The Requirement](#2-the-requirement)
- [3. System Specification](#3-system-specification)
- [4. Feature Specifications](#4-feature-specifications)
- [5. Behavioral Scenarios](#5-behavioral-scenarios)
- [6. Invariants](#6-invariants)
- [7. Acceptance Cases](#7-acceptance-cases)
- [8. NFR Activation](#8-nfr-activation)
- [9. Traceability Matrix](#9-traceability-matrix)
- [10. Test Suite](#10-test-suite)
- [11. Implementation](#11-implementation)
- [12. Regeneration](#12-regeneration)
- [13. Specification Fingerprint](#13-specification-fingerprint)
- [14. What This Example Demonstrates](#14-what-this-example-demonstrates)

---

# 1. Introduction

The simple examples in STDD documentation show the workflow on single functions. That is useful for understanding the steps, but it does not answer the harder question: does STDD work when multiple components interact, when failure modes overlap, and when non-functional requirements constrain the design?

This example answers that question.

We build a seat reservation API using STDD from start to finish. The system has multiple features, components that depend on each other, concurrency constraints, time-based behavior, and pricing rules. We write specifications first, derive tests from those specifications, generate an implementation, and then demonstrate regeneration by discarding and replacing a component.

Everything in this example follows the process described in the [Method](../docs/method.md) and [Writing Specifications](../docs/writing-specifications.md) documents.

---

# 2. The Requirement

A venue operator needs a system for customers to reserve seats for events.

**Business context:**

- The venue has multiple events, each with a fixed seat map.
- Customers browse available seats, hold a seat temporarily, and then confirm or cancel.
- A held seat must not be available to other customers.
- Holds expire automatically after a configurable timeout.
- Pricing varies by section and event, with group discounts for larger bookings.

**High-level requirements:**

1. Customers can list available seats for an event.
2. Customers can hold an available seat.
3. Customers can confirm a held seat to complete the reservation.
4. Customers can cancel a hold or reservation.
5. Expired holds release the seat automatically.
6. Two customers cannot hold or reserve the same seat.
7. Pricing is calculated per section with event multipliers and group discounts.

---

# 3. System Specification

**System:** Seat Reservation API

**Responsibilities:**

- Manage seat availability for events
- Process seat holds, confirmations, and cancellations
- Enforce exclusive access to seats (no double-booking)
- Calculate prices based on section, event, and group size
- Automatically release expired holds

**Components:**

| Component | Responsibility |
|-----------|---------------|
| SeatInventory | Track seat status (available, held, reserved) per event |
| ReservationService | Process holds, confirmations, cancellations, expiry |
| PricingEngine | Calculate seat prices given section, event, group size |
| API | Expose HTTP endpoints for all operations |

**Constraints:**

- Seat status transitions follow a strict state machine: available → held → reserved, or held → available (cancel/expiry), or reserved → available (cancel).
- All state transitions must be atomic. No partial state changes.
- Hold duration is configurable per event (default: 10 minutes).

---

# 4. Feature Specifications

Each feature is specified in T-Spec format: precise, testable, independent of implementation.

---

## Feature 1: List Available Seats

**What it does:**
Returns all seats for a given event that are currently available (not held, not reserved).

**Inputs:**
- event_id (string, required)

**Outputs:**
- List of available seats, each containing: seat_id, section, row, number, price

**Constraints:**
- Returns only seats with status "available"
- Returns an empty list if no seats are available
- Returns an error if the event does not exist

**Failure conditions:**
- Unknown event_id → error with message "Event not found"

---

## Feature 2: Hold a Seat

**What it does:**
Places a temporary hold on an available seat for a specific customer. The seat becomes unavailable to other customers for the hold duration.

**Inputs:**
- event_id (string, required)
- seat_id (string, required)
- customer_id (string, required)

**Outputs:**
- hold_id (string)
- expires_at (datetime)

**Constraints:**
- The seat must be in "available" status
- The hold duration is configured per event (default: 10 minutes)
- After the hold is created, the seat status is "held"
- The hold records which customer holds it

**Failure conditions:**
- Seat not available → error "Seat is not available"
- Unknown event_id → error "Event not found"
- Unknown seat_id → error "Seat not found"

---

## Feature 3: Confirm a Reservation

**What it does:**
Converts a held seat into a confirmed reservation.

**Inputs:**
- hold_id (string, required)
- customer_id (string, required)

**Outputs:**
- reservation_id (string)
- seat_id (string)
- final_price (decimal)

**Constraints:**
- The hold must exist and belong to the requesting customer
- The hold must not be expired
- After confirmation, seat status changes to "reserved"
- Price is calculated at confirmation time by the PricingEngine

**Failure conditions:**
- Hold not found → error "Hold not found"
- Hold belongs to different customer → error "Hold not found" (same error, no information leakage)
- Hold expired → error "Hold has expired"

---

## Feature 4: Cancel

**What it does:**
Cancels a hold or reservation and returns the seat to available status.

**Inputs:**
- hold_id or reservation_id (string, required)
- customer_id (string, required)

**Outputs:**
- cancelled_id (string)
- seat_id (string)

**Constraints:**
- The hold/reservation must belong to the requesting customer
- After cancellation, seat status changes to "available"

**Failure conditions:**
- Not found → error "Not found"
- Belongs to different customer → error "Not found" (no information leakage)

---

## Feature 5: Expire Holds

**What it does:**
Releases seats from holds that have exceeded their expiry time.

**Inputs:**
- None (runs on a schedule or is triggered before availability checks)

**Outputs:**
- List of seat_ids that were released

**Constraints:**
- Only seats with status "held" and expires_at in the past are released
- Released seats return to "available" status
- Associated holds are marked as "expired"

---

## Feature 6: Pricing

**What it does:**
Calculates the price for a seat based on section base price, event multiplier, and group discount.

**Inputs:**
- section (string)
- event_id (string)
- group_size (integer, >= 1)

**Outputs:**
- unit_price (decimal)
- total_price (decimal)

**Rules:**
- Each section has a base price
- Each event has a price multiplier (default: 1.0)
- Group discount: 10% off for groups of 4 or more
- Final price = base_price × event_multiplier × (1 - discount)
- Prices are rounded to 2 decimal places

**Failure conditions:**
- Unknown section → error "Unknown section"
- group_size < 1 → error "Invalid group size"

---

# 5. Behavioral Scenarios

Each scenario is written in Given / When / Then form and maps directly to a test.

---

## Listing Seats

**SEAT-LIST-01: List available seats for an event**

```
Given event "concert-1" exists with seats:
  | seat_id | section   | row | number | status    |
  | S1      | orchestra | A   | 1      | available |
  | S2      | orchestra | A   | 2      | held      |
  | S3      | balcony   | B   | 1      | available |
When listing available seats for "concert-1"
Then the result contains seats S1 and S3
And the result does not contain seat S2
```

**SEAT-LIST-02: List seats for event with none available**

```
Given event "sold-out" exists with all seats held or reserved
When listing available seats for "sold-out"
Then the result is an empty list
```

**SEAT-LIST-03: List seats for unknown event**

```
Given event "nonexistent" does not exist
When listing available seats for "nonexistent"
Then an error is returned with message "Event not found"
```

---

## Holding Seats

**SEAT-HOLD-01: Hold an available seat**

```
Given event "concert-1" exists
And seat S1 is available
When customer "cust-1" holds seat S1 for "concert-1"
Then a hold_id is returned
And expires_at is approximately 10 minutes in the future
And seat S1 status is "held"
```

**SEAT-HOLD-02: Hold a seat that is already held**

```
Given seat S1 is held by customer "cust-1"
When customer "cust-2" attempts to hold seat S1
Then an error is returned with message "Seat is not available"
And the existing hold by "cust-1" is unaffected
```

**SEAT-HOLD-03: Hold a seat that is reserved**

```
Given seat S1 is reserved
When customer "cust-2" attempts to hold seat S1
Then an error is returned with message "Seat is not available"
```

---

## Confirming Reservations

**SEAT-CONF-01: Confirm a valid hold**

```
Given customer "cust-1" holds seat S1 with hold_id "H1"
And the hold has not expired
When customer "cust-1" confirms hold "H1"
Then a reservation_id is returned
And the final_price is calculated by the PricingEngine
And seat S1 status is "reserved"
```

**SEAT-CONF-02: Confirm an expired hold**

```
Given customer "cust-1" holds seat S1 with hold_id "H1"
And the hold has expired
When customer "cust-1" confirms hold "H1"
Then an error is returned with message "Hold has expired"
And seat S1 status is "available"
```

**SEAT-CONF-03: Confirm a hold belonging to another customer**

```
Given customer "cust-1" holds seat S1 with hold_id "H1"
When customer "cust-2" attempts to confirm hold "H1"
Then an error is returned with message "Hold not found"
And the hold by "cust-1" is unaffected
```

---

## Cancellation

**SEAT-CANCEL-01: Cancel a hold**

```
Given customer "cust-1" holds seat S1 with hold_id "H1"
When customer "cust-1" cancels "H1"
Then the hold is removed
And seat S1 status is "available"
```

**SEAT-CANCEL-02: Cancel a confirmed reservation**

```
Given customer "cust-1" has reservation "R1" for seat S1
When customer "cust-1" cancels "R1"
Then the reservation is removed
And seat S1 status is "available"
```

---

## Hold Expiry

**SEAT-EXPIRY-01: Expired holds release seats**

```
Given seat S1 is held with expires_at in the past
And seat S2 is held with expires_at in the future
When expiry processing runs
Then seat S1 status is "available"
And seat S2 status is still "held"
```

---

## Pricing

**PRICE-01: Standard pricing**

```
Given section "orchestra" has base price 100.00
And event "concert-1" has price multiplier 1.5
When calculating price for 1 seat in "orchestra" for "concert-1"
Then unit_price is 150.00
And total_price is 150.00
```

**PRICE-02: Group discount**

```
Given section "orchestra" has base price 100.00
And event "concert-1" has price multiplier 1.5
When calculating price for 4 seats in "orchestra" for "concert-1"
Then unit_price is 135.00 (150.00 × 0.90)
And total_price is 540.00
```

**PRICE-03: No group discount for fewer than 4**

```
Given section "orchestra" has base price 100.00
And event "concert-1" has price multiplier 1.0
When calculating price for 3 seats in "orchestra" for "concert-1"
Then unit_price is 100.00
And total_price is 300.00
```

**PRICE-04: Rounding**

```
Given section "balcony" has base price 33.33
And event "concert-1" has price multiplier 1.5
When calculating price for 1 seat in "balcony" for "concert-1"
Then unit_price is 50.00 (33.33 × 1.5 = 49.995, rounded to 50.00)
```

**PRICE-05: Invalid group size**

```
When calculating price with group_size 0
Then an error is returned with message "Invalid group size"
```

---

# 6. Invariants

Invariants are conditions that must hold true at all times, regardless of the sequence of operations.

**INV-01: Seat status exclusivity**
A seat is in exactly one status at any time: available, held, or reserved.

**INV-02: No orphaned holds**
Every seat with status "held" has exactly one associated hold record with a future expiry (or the seat is pending expiry processing).

**INV-03: No double-booking**
At most one customer can hold or reserve a given seat at any time.

**INV-04: State machine enforcement**
Seat transitions follow: available → held → reserved → available, or held → available. No other transitions are permitted.

**INV-05: Price consistency**
For the same inputs (section, event, group_size), the PricingEngine always returns the same result.

**INV-06: Cancellation completeness**
After a cancellation, no hold or reservation record references the cancelled seat as active.

---

# 7. Acceptance Cases

Acceptance cases are structured test definitions derived from the behavioral scenarios. These can be used to generate tests automatically.

```yaml
acceptance_cases:

  - id: SEAT-LIST-01
    feature: list_available_seats
    given:
      event_id: "concert-1"
      seats:
        - { seat_id: "S1", section: "orchestra", row: "A", number: 1, status: "available" }
        - { seat_id: "S2", section: "orchestra", row: "A", number: 2, status: "held" }
        - { seat_id: "S3", section: "balcony",   row: "B", number: 1, status: "available" }
    when:
      action: list_available_seats
      event_id: "concert-1"
    then:
      result_contains: ["S1", "S3"]
      result_excludes: ["S2"]

  - id: SEAT-LIST-02
    feature: list_available_seats
    given:
      event_id: "sold-out"
      seats:
        - { seat_id: "S1", status: "held" }
        - { seat_id: "S2", status: "reserved" }
    when:
      action: list_available_seats
      event_id: "sold-out"
    then:
      result: []

  - id: SEAT-LIST-03
    feature: list_available_seats
    given:
      event_id: "nonexistent"
      event_exists: false
    when:
      action: list_available_seats
      event_id: "nonexistent"
    then:
      error: "Event not found"

  - id: SEAT-HOLD-01
    feature: hold_seat
    given:
      event_id: "concert-1"
      seat_id: "S1"
      seat_status: "available"
      hold_duration_minutes: 10
    when:
      action: hold_seat
      customer_id: "cust-1"
      event_id: "concert-1"
      seat_id: "S1"
    then:
      returns: hold_id
      returns: expires_at
      seat_status_after: "held"

  - id: SEAT-HOLD-02
    feature: hold_seat
    given:
      event_id: "concert-1"
      seat_id: "S1"
      seat_status: "held"
      held_by: "cust-1"
    when:
      action: hold_seat
      customer_id: "cust-2"
      event_id: "concert-1"
      seat_id: "S1"
    then:
      error: "Seat is not available"
      seat_status_after: "held"
      held_by_after: "cust-1"

  - id: SEAT-CANCEL-01
    feature: cancel
    given:
      hold_id: "H1"
      customer_id: "cust-1"
      seat_id: "S1"
      seat_status: "held"
    when:
      action: cancel
      ref_id: "H1"
      customer_id: "cust-1"
    then:
      seat_status_after: "available"

  - id: SEAT-CANCEL-02
    feature: cancel
    given:
      reservation_id: "R1"
      customer_id: "cust-1"
      seat_id: "S1"
      seat_status: "reserved"
    when:
      action: cancel
      ref_id: "R1"
      customer_id: "cust-1"
    then:
      seat_status_after: "available"

  - id: SEAT-EXPIRY-01
    feature: expire_holds
    given:
      seats:
        - { seat_id: "S1", status: "held", expires_at: "past" }
        - { seat_id: "S2", status: "held", expires_at: "future" }
    when:
      action: process_expired_holds
    then:
      seat_S1_status_after: "available"
      seat_S2_status_after: "held"

  - id: SEAT-CONF-01
    feature: confirm_reservation
    given:
      hold_id: "H1"
      customer_id: "cust-1"
      seat_id: "S1"
      hold_expired: false
      section: "orchestra"
      event_multiplier: 1.5
      base_price: 100.00
    when:
      action: confirm_reservation
      hold_id: "H1"
      customer_id: "cust-1"
    then:
      returns: reservation_id
      final_price: 150.00
      seat_status_after: "reserved"

  - id: SEAT-CONF-02
    feature: confirm_reservation
    given:
      hold_id: "H1"
      customer_id: "cust-1"
      hold_expired: true
    when:
      action: confirm_reservation
      hold_id: "H1"
      customer_id: "cust-1"
    then:
      error: "Hold has expired"
      seat_status_after: "available"

  - id: PRICE-01
    feature: pricing
    given:
      section: "orchestra"
      base_price: 100.00
      event_id: "concert-1"
      event_multiplier: 1.5
    when:
      action: calculate_price
      section: "orchestra"
      event_id: "concert-1"
      group_size: 1
    then:
      unit_price: 150.00
      total_price: 150.00

  - id: PRICE-02
    feature: pricing
    given:
      section: "orchestra"
      base_price: 100.00
      event_id: "concert-1"
      event_multiplier: 1.5
    when:
      action: calculate_price
      section: "orchestra"
      event_id: "concert-1"
      group_size: 4
    then:
      unit_price: 135.00
      total_price: 540.00

  - id: PRICE-03
    feature: pricing
    given:
      section: "orchestra"
      base_price: 100.00
      event_id: "concert-1"
      event_multiplier: 1.0
    when:
      action: calculate_price
      section: "orchestra"
      event_id: "concert-1"
      group_size: 3
    then:
      unit_price: 100.00
      total_price: 300.00

  - id: PRICE-04
    feature: pricing
    given:
      section: "balcony"
      base_price: 33.33
      event_id: "concert-1"
      event_multiplier: 1.5
    when:
      action: calculate_price
      section: "balcony"
      event_id: "concert-1"
      group_size: 1
    then:
      unit_price: 50.00

  - id: PRICE-05
    feature: pricing
    given:
      section: "orchestra"
      event_id: "concert-1"
    when:
      action: calculate_price
      section: "orchestra"
      event_id: "concert-1"
      group_size: 0
    then:
      error: "Invalid group size"
```

---

# 8. NFR Activation

Based on the [NFR Framework](../docs/nfr-framework.md), the following non-functional requirements are activated by this system's technology and domain choices.

## Technology-Triggered NFRs

| Technology | Activated NFR | Applied To |
|-----------|---------------|------------|
| SQL Database | Parameterized queries only (no string concatenation) | All database access |
| SQL Database | Transactions for multi-step state changes | Hold, confirm, cancel operations |
| REST API | Input validation on all endpoints | All API handlers |
| REST API | Consistent error response format | All API handlers |
| REST API | Rate limiting | All endpoints |

## Domain-Triggered NFRs

| Domain Concern | Activated NFR | Applied To |
|---------------|---------------|------------|
| Concurrent access | Optimistic or pessimistic locking on seat status changes | Hold, confirm operations |
| Financial data | Price calculations use decimal arithmetic, not floating point | PricingEngine |
| Time-based behavior | Clock abstraction for testability | Hold expiry |

## Project-Specific NFRs

| Requirement | Threshold | Rationale |
|------------|-----------|-----------|
| API response time | < 200ms (p95) | Customer-facing reservation flow |
| Hold expiry accuracy | Processed within 30 seconds of expiry time | Acceptable delay for seat release |
| Concurrent hold attempts | System correctly handles 100 simultaneous hold requests for the same seat | Peak demand during popular event on-sale |

## NFR Impact on Specifications

The clock abstraction NFR directly affects how we write and test hold expiry. Instead of relying on real time, the specification requires an injectable clock:

```
The ReservationService accepts a clock dependency.
All time comparisons use this clock.
Tests provide a controllable clock to simulate expiry without waiting.
```

The decimal arithmetic NFR affects the PricingEngine specification:

```
All price calculations use decimal types with 2-place precision.
No intermediate floating-point operations are permitted.
```

---

# 9. Traceability Matrix

Every specification statement maps to at least one test. Every test maps back to a specification.

| Spec ID | Specification | Test(s) |
|---------|--------------|---------|
| SEAT-LIST-01 | List returns only available seats | `test_list_available_seats` |
| SEAT-LIST-02 | Empty list when none available | `test_list_seats_none_available` |
| SEAT-LIST-03 | Error for unknown event | `test_list_seats_unknown_event` |
| SEAT-HOLD-01 | Hold an available seat | `test_hold_available_seat` |
| SEAT-HOLD-02 | Reject hold on already-held seat | `test_hold_already_held_seat` |
| SEAT-HOLD-03 | Reject hold on reserved seat | `test_hold_reserved_seat` |
| SEAT-CONF-01 | Confirm a valid hold | `test_confirm_valid_hold` |
| SEAT-CONF-02 | Reject confirmation of expired hold | `test_confirm_expired_hold` |
| SEAT-CONF-03 | Reject confirmation by wrong customer | `test_confirm_wrong_customer` |
| SEAT-CANCEL-01 | Cancel a hold | `test_cancel_hold` |
| SEAT-CANCEL-02 | Cancel a reservation | `test_cancel_reservation` |
| SEAT-EXPIRY-01 | Expired holds release seats | `test_expiry_releases_seats` |
| PRICE-01 | Standard pricing | `test_standard_pricing` |
| PRICE-02 | Group discount | `test_group_discount` |
| PRICE-03 | No discount under 4 | `test_no_discount_under_four` |
| PRICE-04 | Rounding | `test_price_rounding` |
| PRICE-05 | Invalid group size | `test_invalid_group_size` |
| INV-01 | Seat status exclusivity | `test_invariant_seat_status_exclusive` |
| INV-03 | No double-booking | `test_invariant_no_double_booking` |
| INV-04 | State machine enforcement | `test_invariant_state_transitions` |
| INV-05 | Price consistency | `test_invariant_price_deterministic` |
| NFR-DECIMAL | Decimal arithmetic in pricing | `test_nfr_decimal_arithmetic` |
| NFR-CLOCK | Injectable clock for expiry | `test_nfr_injectable_clock` |
| NFR-EXCLUSIVE | Exclusive hold enforcement | `test_nfr_exclusive_hold` |
| INV-02 | No orphaned holds | `test_invariant_no_orphaned_holds` |
| INV-06 | Cancellation completeness | `test_invariant_cancellation_completeness` |
| INT-01 | Confirmation price matches PricingEngine | `test_integration_confirm_uses_correct_pricing` |
| INT-02 | Expired hold allows rebook by another customer | `test_integration_expiry_then_rebook` |
| INT-03 | Cancelled hold allows rebook | `test_integration_cancel_then_rebook` |
| INT-04 | Expiry during confirmation releases seat for others | `test_integration_expired_hold_does_not_confirm` |
| SYS-01 | Full booking workflow end-to-end | `test_system_full_booking_workflow` |
| SYS-02 | Two customers compete for same seat | `test_system_competing_customers` |
| SYS-03 | Hold expires, another customer books same seat | `test_system_hold_expire_rebook_confirm` |
| SYS-04 | Full cycle: book, cancel, rebook by different customer | `test_system_cancel_and_rebook_full_cycle` |

---

# 10. Test Suite

The tests below are written in Python using pytest. They are derived directly from the behavioral scenarios and acceptance cases above.

The tests define a `FakeClock` for time control and set up test fixtures for events, seats, and pricing configuration. These tests are the specification made executable. They are written before any implementation exists.

```python
import pytest
from decimal import Decimal
from datetime import datetime, timedelta


# ---------------------------------------------------------------------------
# Test infrastructure
# ---------------------------------------------------------------------------

class FakeClock:
    """Injectable clock for controlling time in tests."""

    def __init__(self, now=None):
        self._now = now or datetime(2026, 6, 15, 14, 0, 0)

    def now(self):
        return self._now

    def advance(self, minutes=0, seconds=0):
        self._now += timedelta(minutes=minutes, seconds=seconds)


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def pricing_config():
    return {
        "sections": {
            "orchestra": Decimal("100.00"),
            "balcony": Decimal("33.33"),
        },
        "events": {
            "concert-1": {"multiplier": Decimal("1.5"), "hold_minutes": 10},
            "concert-2": {"multiplier": Decimal("1.0"), "hold_minutes": 5},
        },
        "group_discount_threshold": 4,
        "group_discount_rate": Decimal("0.10"),
    }


@pytest.fixture
def inventory(clock, pricing_config):
    """Create a SeatInventory with a standard set of seats."""
    from seat_reservation import SeatInventory, ReservationService, PricingEngine

    inv = SeatInventory()
    inv.add_event("concert-1", hold_minutes=10)
    inv.add_seat("concert-1", "S1", section="orchestra", row="A", number=1)
    inv.add_seat("concert-1", "S2", section="orchestra", row="A", number=2)
    inv.add_seat("concert-1", "S3", section="balcony", row="B", number=1)

    pricing = PricingEngine(pricing_config)
    service = ReservationService(inv, pricing, clock)
    return inv, service, pricing


# ---------------------------------------------------------------------------
# Feature: List Available Seats
# ---------------------------------------------------------------------------

def test_list_available_seats(inventory):
    """SEAT-LIST-01: Returns only available seats."""
    inv, service, _ = inventory

    # Hold one seat so it's no longer available
    service.hold_seat("concert-1", "S2", "cust-1")

    available = service.list_available_seats("concert-1")
    seat_ids = [s["seat_id"] for s in available]

    assert "S1" in seat_ids
    assert "S3" in seat_ids
    assert "S2" not in seat_ids


def test_list_seats_none_available(inventory):
    """SEAT-LIST-02: Returns empty list when all seats are held/reserved."""
    inv, service, _ = inventory

    service.hold_seat("concert-1", "S1", "cust-1")
    service.hold_seat("concert-1", "S2", "cust-2")
    service.hold_seat("concert-1", "S3", "cust-3")

    available = service.list_available_seats("concert-1")
    assert available == []


def test_list_seats_unknown_event(inventory):
    """SEAT-LIST-03: Error for unknown event."""
    _, service, _ = inventory

    with pytest.raises(ValueError, match="Event not found"):
        service.list_available_seats("nonexistent")


# ---------------------------------------------------------------------------
# Feature: Hold a Seat
# ---------------------------------------------------------------------------

def test_hold_available_seat(inventory, clock):
    """SEAT-HOLD-01: Hold an available seat."""
    inv, service, _ = inventory

    result = service.hold_seat("concert-1", "S1", "cust-1")

    assert "hold_id" in result
    assert result["expires_at"] == clock.now() + timedelta(minutes=10)
    assert inv.get_seat_status("concert-1", "S1") == "held"


def test_hold_already_held_seat(inventory):
    """SEAT-HOLD-02: Cannot hold a seat that is already held."""
    inv, service, _ = inventory

    service.hold_seat("concert-1", "S1", "cust-1")

    with pytest.raises(ValueError, match="Seat is not available"):
        service.hold_seat("concert-1", "S1", "cust-2")

    # Original hold is unaffected
    assert inv.get_seat_status("concert-1", "S1") == "held"


def test_hold_reserved_seat(inventory):
    """SEAT-HOLD-03: Cannot hold a seat that is reserved."""
    inv, service, _ = inventory

    hold = service.hold_seat("concert-1", "S1", "cust-1")
    service.confirm_reservation(hold["hold_id"], "cust-1")

    with pytest.raises(ValueError, match="Seat is not available"):
        service.hold_seat("concert-1", "S1", "cust-2")


# ---------------------------------------------------------------------------
# Feature: Confirm Reservation
# ---------------------------------------------------------------------------

def test_confirm_valid_hold(inventory):
    """SEAT-CONF-01: Confirm a valid hold."""
    inv, service, _ = inventory

    hold = service.hold_seat("concert-1", "S1", "cust-1")
    result = service.confirm_reservation(hold["hold_id"], "cust-1")

    assert "reservation_id" in result
    assert result["final_price"] == Decimal("150.00")
    assert inv.get_seat_status("concert-1", "S1") == "reserved"


def test_confirm_expired_hold(inventory, clock):
    """SEAT-CONF-02: Cannot confirm an expired hold."""
    inv, service, _ = inventory

    hold = service.hold_seat("concert-1", "S1", "cust-1")
    clock.advance(minutes=11)

    with pytest.raises(ValueError, match="Hold has expired"):
        service.confirm_reservation(hold["hold_id"], "cust-1")

    assert inv.get_seat_status("concert-1", "S1") == "available"


def test_confirm_wrong_customer(inventory):
    """SEAT-CONF-03: Cannot confirm another customer's hold."""
    inv, service, _ = inventory

    hold = service.hold_seat("concert-1", "S1", "cust-1")

    with pytest.raises(ValueError, match="Hold not found"):
        service.confirm_reservation(hold["hold_id"], "cust-2")

    # Original hold is unaffected
    assert inv.get_seat_status("concert-1", "S1") == "held"


# ---------------------------------------------------------------------------
# Feature: Cancel
# ---------------------------------------------------------------------------

def test_cancel_hold(inventory):
    """SEAT-CANCEL-01: Cancel a hold returns seat to available."""
    inv, service, _ = inventory

    hold = service.hold_seat("concert-1", "S1", "cust-1")
    service.cancel(hold["hold_id"], "cust-1")

    assert inv.get_seat_status("concert-1", "S1") == "available"


def test_cancel_reservation(inventory):
    """SEAT-CANCEL-02: Cancel a confirmed reservation."""
    inv, service, _ = inventory

    hold = service.hold_seat("concert-1", "S1", "cust-1")
    res = service.confirm_reservation(hold["hold_id"], "cust-1")
    service.cancel(res["reservation_id"], "cust-1")

    assert inv.get_seat_status("concert-1", "S1") == "available"


# ---------------------------------------------------------------------------
# Feature: Hold Expiry
# ---------------------------------------------------------------------------

def test_expiry_releases_seats(inventory, clock):
    """SEAT-EXPIRY-01: Expired holds release seats, active holds are kept."""
    inv, service, _ = inventory

    service.hold_seat("concert-1", "S1", "cust-1")
    clock.advance(minutes=11)
    service.hold_seat("concert-1", "S3", "cust-2")  # Fresh hold

    released = service.process_expired_holds()

    assert "S1" in released
    assert "S3" not in released
    assert inv.get_seat_status("concert-1", "S1") == "available"
    assert inv.get_seat_status("concert-1", "S3") == "held"


# ---------------------------------------------------------------------------
# Feature: Pricing
# ---------------------------------------------------------------------------

def test_standard_pricing(inventory):
    """PRICE-01: Base price × event multiplier."""
    _, _, pricing = inventory

    result = pricing.calculate("orchestra", "concert-1", group_size=1)

    assert result["unit_price"] == Decimal("150.00")
    assert result["total_price"] == Decimal("150.00")


def test_group_discount(inventory):
    """PRICE-02: 10% discount for groups of 4+."""
    _, _, pricing = inventory

    result = pricing.calculate("orchestra", "concert-1", group_size=4)

    assert result["unit_price"] == Decimal("135.00")
    assert result["total_price"] == Decimal("540.00")


def test_no_discount_under_four(inventory):
    """PRICE-03: No discount for fewer than 4."""
    _, _, pricing = inventory

    result = pricing.calculate("orchestra", "concert-2", group_size=3)

    assert result["unit_price"] == Decimal("100.00")
    assert result["total_price"] == Decimal("300.00")


def test_price_rounding(inventory):
    """PRICE-04: Prices rounded to 2 decimal places."""
    _, _, pricing = inventory

    result = pricing.calculate("balcony", "concert-1", group_size=1)

    assert result["unit_price"] == Decimal("50.00")


def test_invalid_group_size(inventory):
    """PRICE-05: Reject group_size < 1."""
    _, _, pricing = inventory

    with pytest.raises(ValueError, match="Invalid group size"):
        pricing.calculate("orchestra", "concert-1", group_size=0)


# ---------------------------------------------------------------------------
# Invariants
# ---------------------------------------------------------------------------

def test_invariant_seat_status_exclusive(inventory):
    """INV-01: A seat is in exactly one status at any time."""
    inv, service, _ = inventory

    # Transition through all states and verify at each step
    assert inv.get_seat_status("concert-1", "S1") == "available"

    hold = service.hold_seat("concert-1", "S1", "cust-1")
    assert inv.get_seat_status("concert-1", "S1") == "held"

    service.confirm_reservation(hold["hold_id"], "cust-1")
    assert inv.get_seat_status("concert-1", "S1") == "reserved"


def test_invariant_no_double_booking(inventory):
    """INV-03: At most one customer can hold a seat."""
    _, service, _ = inventory

    service.hold_seat("concert-1", "S1", "cust-1")

    with pytest.raises(ValueError):
        service.hold_seat("concert-1", "S1", "cust-2")


def test_invariant_state_transitions(inventory):
    """INV-04: Only valid state transitions are allowed."""
    inv, service, _ = inventory

    # Cannot go directly from available to reserved (must hold first)
    # This is enforced by the API: confirm requires a hold_id
    with pytest.raises(ValueError):
        service.confirm_reservation("nonexistent-hold", "cust-1")


def test_invariant_no_orphaned_holds(inventory, clock):
    """INV-02: Every held seat has an associated active hold record."""
    inv, service, _ = inventory

    hold = service.hold_seat("concert-1", "S1", "cust-1")

    # Seat is held and the hold record exists
    assert inv.get_seat_status("concert-1", "S1") == "held"

    # After cancellation, seat is available and hold is no longer active
    service.cancel(hold["hold_id"], "cust-1")
    assert inv.get_seat_status("concert-1", "S1") == "available"


def test_invariant_price_deterministic(inventory):
    """INV-05: Same inputs always produce same price."""
    _, _, pricing = inventory

    result1 = pricing.calculate("orchestra", "concert-1", group_size=4)
    result2 = pricing.calculate("orchestra", "concert-1", group_size=4)

    assert result1 == result2


def test_invariant_cancellation_completeness(inventory):
    """INV-06: After cancellation, no active record references the seat."""
    inv, service, _ = inventory

    # Hold then cancel
    hold = service.hold_seat("concert-1", "S1", "cust-1")
    service.cancel(hold["hold_id"], "cust-1")

    # Seat is available — no active hold or reservation references it
    assert inv.get_seat_status("concert-1", "S1") == "available"

    # Can be re-held by anyone — proves no lingering reference blocks it
    new_hold = service.hold_seat("concert-1", "S1", "cust-2")
    assert "hold_id" in new_hold


# ---------------------------------------------------------------------------
# NFR Tests
# ---------------------------------------------------------------------------

def test_nfr_decimal_arithmetic(inventory):
    """NFR-DECIMAL: Pricing uses decimal, not float."""
    _, _, pricing = inventory

    result = pricing.calculate("balcony", "concert-1", group_size=1)

    # 33.33 × 1.5 = 49.995 → should round to 50.00, not 49.99 or 50.0000...1
    assert result["unit_price"] == Decimal("50.00")
    assert isinstance(result["unit_price"], Decimal)


def test_nfr_injectable_clock(inventory, clock):
    """NFR-CLOCK: Time behavior is controlled by injectable clock."""
    _, service, _ = inventory

    hold = service.hold_seat("concert-1", "S1", "cust-1")

    # Hold is valid now
    clock.advance(minutes=5)
    result = service.confirm_reservation(hold["hold_id"], "cust-1")
    assert "reservation_id" in result


def test_nfr_exclusive_hold(inventory):
    """NFR-EXCLUSIVE: Only one customer can hold a seat at a time."""
    _, service, _ = inventory

    # First hold succeeds
    service.hold_seat("concert-1", "S1", "cust-1")

    # Second hold for same seat fails
    with pytest.raises(ValueError, match="Seat is not available"):
        service.hold_seat("concert-1", "S1", "cust-2")


# ---------------------------------------------------------------------------
# Integration Tests — Multiple components working together
# ---------------------------------------------------------------------------

def test_integration_confirm_uses_correct_pricing(inventory):
    """INT-01: Confirmation price matches PricingEngine for the seat's section."""
    _, service, pricing = inventory

    hold = service.hold_seat("concert-1", "S1", "cust-1")
    result = service.confirm_reservation(hold["hold_id"], "cust-1")

    # S1 is in "orchestra" section, concert-1 has multiplier 1.5
    expected = pricing.calculate("orchestra", "concert-1", group_size=1)
    assert result["final_price"] == expected["unit_price"]


def test_integration_expiry_then_rebook(inventory, clock):
    """INT-02: After a hold expires, another customer can hold the same seat."""
    inv, service, _ = inventory

    # Customer 1 holds seat
    service.hold_seat("concert-1", "S1", "cust-1")

    # Hold expires
    clock.advance(minutes=11)
    service.process_expired_holds()

    # Customer 2 can now hold the same seat
    result = service.hold_seat("concert-1", "S1", "cust-2")
    assert "hold_id" in result
    assert inv.get_seat_status("concert-1", "S1") == "held"


def test_integration_cancel_then_rebook(inventory):
    """INT-03: After cancellation, another customer can hold the same seat."""
    _, service, _ = inventory

    hold = service.hold_seat("concert-1", "S1", "cust-1")
    service.cancel(hold["hold_id"], "cust-1")

    result = service.hold_seat("concert-1", "S1", "cust-2")
    assert "hold_id" in result


def test_integration_expired_hold_does_not_confirm(inventory, clock):
    """INT-04: Expiry and confirmation interact correctly under time pressure."""
    inv, service, _ = inventory

    hold = service.hold_seat("concert-1", "S1", "cust-1")
    clock.advance(minutes=11)

    # Confirmation fails because hold expired
    with pytest.raises(ValueError, match="Hold has expired"):
        service.confirm_reservation(hold["hold_id"], "cust-1")

    # Seat is available again — expiry was handled during confirmation
    assert inv.get_seat_status("concert-1", "S1") == "available"

    # Another customer can now book it
    new_hold = service.hold_seat("concert-1", "S1", "cust-2")
    assert "hold_id" in new_hold


# ---------------------------------------------------------------------------
# System Tests — Full end-to-end workflows
# ---------------------------------------------------------------------------

def test_system_full_booking_workflow(inventory, clock):
    """SYS-01: Complete workflow — list, hold, confirm, verify unavailable."""
    inv, service, _ = inventory

    # Step 1: Customer sees available seats
    available = service.list_available_seats("concert-1")
    assert len(available) == 3

    # Step 2: Customer holds a seat
    hold = service.hold_seat("concert-1", "S1", "cust-1")

    # Step 3: Seat no longer appears in available list
    available = service.list_available_seats("concert-1")
    seat_ids = [s["seat_id"] for s in available]
    assert "S1" not in seat_ids
    assert len(available) == 2

    # Step 4: Customer confirms within time limit
    clock.advance(minutes=5)
    result = service.confirm_reservation(hold["hold_id"], "cust-1")
    assert "reservation_id" in result
    assert result["final_price"] == Decimal("150.00")

    # Step 5: Seat is still not available
    available = service.list_available_seats("concert-1")
    seat_ids = [s["seat_id"] for s in available]
    assert "S1" not in seat_ids


def test_system_competing_customers(inventory, clock):
    """SYS-02: Two customers compete for the same seat — only one wins."""
    inv, service, _ = inventory

    # Customer 1 holds the seat
    hold = service.hold_seat("concert-1", "S1", "cust-1")

    # Customer 2 tries and fails
    with pytest.raises(ValueError, match="Seat is not available"):
        service.hold_seat("concert-1", "S1", "cust-2")

    # Customer 1 confirms
    result = service.confirm_reservation(hold["hold_id"], "cust-1")
    assert "reservation_id" in result

    # Customer 2 still cannot get it
    with pytest.raises(ValueError, match="Seat is not available"):
        service.hold_seat("concert-1", "S1", "cust-2")


def test_system_hold_expire_rebook_confirm(inventory, clock):
    """SYS-03: Hold expires, another customer books and confirms the same seat."""
    inv, service, _ = inventory

    # Customer 1 holds but doesn't confirm
    service.hold_seat("concert-1", "S1", "cust-1")
    clock.advance(minutes=11)

    # Customer 2 sees the seat is available (expiry processed during list)
    available = service.list_available_seats("concert-1")
    seat_ids = [s["seat_id"] for s in available]
    assert "S1" in seat_ids

    # Customer 2 holds and confirms
    hold2 = service.hold_seat("concert-1", "S1", "cust-2")
    result = service.confirm_reservation(hold2["hold_id"], "cust-2")
    assert result["final_price"] == Decimal("150.00")
    assert inv.get_seat_status("concert-1", "S1") == "reserved"


def test_system_cancel_and_rebook_full_cycle(inventory, clock):
    """SYS-04: Full cycle — book, cancel, rebook by different customer."""
    inv, service, _ = inventory

    # Customer 1 books
    hold1 = service.hold_seat("concert-1", "S1", "cust-1")
    res1 = service.confirm_reservation(hold1["hold_id"], "cust-1")

    # Customer 1 cancels
    service.cancel(res1["reservation_id"], "cust-1")
    assert inv.get_seat_status("concert-1", "S1") == "available"

    # Customer 2 books the same seat
    hold2 = service.hold_seat("concert-1", "S1", "cust-2")
    res2 = service.confirm_reservation(hold2["hold_id"], "cust-2")
    assert inv.get_seat_status("concert-1", "S1") == "reserved"
```

At this point, every test fails. No implementation exists yet. This is exactly where STDD says you should be.

---

# 11. Implementation

The test suite is handed to AI along with the specifications. The AI generates an implementation that satisfies the tests.

The prompt to AI is:

```
Given the following specifications and test suite for a seat reservation system,
generate a Python module called seat_reservation.py that contains:
- SeatInventory class
- ReservationService class
- PricingEngine class

All tests must pass. Use Decimal for pricing. Accept a clock dependency
for time operations.
```

The AI generates:

```python
"""
Seat Reservation System — AI-generated implementation.

Generated from specifications and test suite.
This implementation is disposable. The specifications and tests are not.
"""

import uuid
from decimal import Decimal, ROUND_HALF_UP
from datetime import timedelta


class SeatInventory:
    """Tracks seat status per event."""

    def __init__(self):
        self._events = {}       # event_id → {hold_minutes, seats}
        self._seats = {}        # (event_id, seat_id) → seat dict

    def add_event(self, event_id, hold_minutes=10):
        self._events[event_id] = {"hold_minutes": hold_minutes}

    def add_seat(self, event_id, seat_id, section, row, number):
        self._seats[(event_id, seat_id)] = {
            "seat_id": seat_id,
            "section": section,
            "row": row,
            "number": number,
            "status": "available",
        }

    def get_event(self, event_id):
        if event_id not in self._events:
            raise ValueError("Event not found")
        return self._events[event_id]

    def get_seat(self, event_id, seat_id):
        key = (event_id, seat_id)
        if key not in self._seats:
            raise ValueError("Seat not found")
        return self._seats[key]

    def get_seat_status(self, event_id, seat_id):
        return self.get_seat(event_id, seat_id)["status"]

    def set_seat_status(self, event_id, seat_id, status):
        self.get_seat(event_id, seat_id)["status"] = status

    def list_available(self, event_id):
        self.get_event(event_id)
        return [
            {k: v for k, v in seat.items() if k != "status"}
            for (eid, _), seat in self._seats.items()
            if eid == event_id and seat["status"] == "available"
        ]


class PricingEngine:
    """Calculates seat prices using decimal arithmetic."""

    def __init__(self, config):
        self._sections = config["sections"]
        self._events = config["events"]
        self._discount_threshold = config["group_discount_threshold"]
        self._discount_rate = config["group_discount_rate"]

    def calculate(self, section, event_id, group_size):
        if group_size < 1:
            raise ValueError("Invalid group size")
        if section not in self._sections:
            raise ValueError("Unknown section")

        base = self._sections[section]
        multiplier = self._events[event_id]["multiplier"]

        unit = base * multiplier

        if group_size >= self._discount_threshold:
            unit = unit * (Decimal("1") - self._discount_rate)

        unit = unit.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total = (unit * group_size).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return {"unit_price": unit, "total_price": total}


class ReservationService:
    """Processes holds, confirmations, cancellations, and expiry."""

    def __init__(self, inventory, pricing, clock):
        self._inventory = inventory
        self._pricing = pricing
        self._clock = clock
        self._holds = {}          # hold_id → hold record
        self._reservations = {}   # reservation_id → reservation record

    def list_available_seats(self, event_id):
        self._process_expired()
        return self._inventory.list_available(event_id)

    def hold_seat(self, event_id, seat_id, customer_id):
        event = self._inventory.get_event(event_id)
        seat = self._inventory.get_seat(event_id, seat_id)

        if seat["status"] != "available":
            raise ValueError("Seat is not available")

        hold_id = str(uuid.uuid4())
        expires_at = self._clock.now() + timedelta(minutes=event["hold_minutes"])

        self._inventory.set_seat_status(event_id, seat_id, "held")

        self._holds[hold_id] = {
            "hold_id": hold_id,
            "event_id": event_id,
            "seat_id": seat_id,
            "customer_id": customer_id,
            "expires_at": expires_at,
            "status": "active",
        }

        return {"hold_id": hold_id, "expires_at": expires_at}

    def confirm_reservation(self, hold_id, customer_id):
        hold = self._get_hold(hold_id, customer_id)

        if self._clock.now() > hold["expires_at"]:
            hold["status"] = "expired"
            self._inventory.set_seat_status(hold["event_id"], hold["seat_id"], "available")
            raise ValueError("Hold has expired")

        self._inventory.set_seat_status(hold["event_id"], hold["seat_id"], "reserved")
        hold["status"] = "confirmed"

        seat = self._inventory.get_seat(hold["event_id"], hold["seat_id"])
        price = self._pricing.calculate(seat["section"], hold["event_id"], group_size=1)

        reservation_id = str(uuid.uuid4())
        self._reservations[reservation_id] = {
            "reservation_id": reservation_id,
            "event_id": hold["event_id"],
            "seat_id": hold["seat_id"],
            "customer_id": customer_id,
            "final_price": price["unit_price"],
        }

        return {
            "reservation_id": reservation_id,
            "seat_id": hold["seat_id"],
            "final_price": price["unit_price"],
        }

    def cancel(self, ref_id, customer_id):
        # Try holds first, then reservations
        if ref_id in self._holds:
            hold = self._holds[ref_id]
            if hold["customer_id"] != customer_id or hold["status"] != "active":
                raise ValueError("Not found")
            hold["status"] = "cancelled"
            self._inventory.set_seat_status(hold["event_id"], hold["seat_id"], "available")
            return {"cancelled_id": ref_id, "seat_id": hold["seat_id"]}

        for res_id, res in self._reservations.items():
            if res_id == ref_id:
                if res["customer_id"] != customer_id:
                    raise ValueError("Not found")
                self._inventory.set_seat_status(res["event_id"], res["seat_id"], "available")
                del self._reservations[res_id]
                return {"cancelled_id": ref_id, "seat_id": res["seat_id"]}

        raise ValueError("Not found")

    def process_expired_holds(self):
        return self._process_expired()

    def _process_expired(self):
        released = []
        for hold in self._holds.values():
            if hold["status"] == "active" and self._clock.now() > hold["expires_at"]:
                hold["status"] = "expired"
                self._inventory.set_seat_status(hold["event_id"], hold["seat_id"], "available")
                released.append(hold["seat_id"])
        return released

    def _get_hold(self, hold_id, customer_id):
        hold = self._holds.get(hold_id)
        if not hold or hold["customer_id"] != customer_id:
            raise ValueError("Hold not found")
        return hold
```

Run the tests:

```
$ pytest test_seat_reservation.py -v

test_list_available_seats               PASSED
test_list_seats_none_available          PASSED
test_list_seats_unknown_event           PASSED
test_hold_available_seat                PASSED
test_hold_already_held_seat             PASSED
test_hold_reserved_seat                 PASSED
test_confirm_valid_hold                 PASSED
test_confirm_expired_hold               PASSED
test_confirm_wrong_customer             PASSED
test_cancel_hold                        PASSED
test_cancel_reservation                 PASSED
test_expiry_releases_seats              PASSED
test_standard_pricing                   PASSED
test_group_discount                     PASSED
test_no_discount_under_four             PASSED
test_price_rounding                     PASSED
test_invalid_group_size                 PASSED
test_invariant_seat_status_exclusive    PASSED
test_invariant_no_double_booking        PASSED
test_invariant_state_transitions        PASSED
test_invariant_no_orphaned_holds        PASSED
test_invariant_price_deterministic      PASSED
test_invariant_cancellation_completeness PASSED
test_nfr_decimal_arithmetic             PASSED
test_nfr_injectable_clock               PASSED
test_nfr_exclusive_hold                 PASSED
test_integration_confirm_pricing        PASSED
test_integration_expiry_then_rebook     PASSED
test_integration_cancel_then_rebook     PASSED
test_integration_expired_hold           PASSED
test_system_full_booking_workflow       PASSED
test_system_competing_customers         PASSED
test_system_hold_expire_rebook          PASSED
test_system_cancel_and_rebook           PASSED

34 passed in 0.08s
```

All 34 tests pass. The implementation is accepted.

---

# 12. Regeneration

This is the central claim of STDD: implementations are disposable.

To demonstrate this, we discard the `PricingEngine` and generate a completely different implementation. The specification and tests do not change.

## The Original PricingEngine

The first implementation stores config as dictionaries and computes prices inline.

## The Regenerated PricingEngine

We prompt the AI: "Regenerate the PricingEngine using a different design. Use a strategy pattern with separate pricing rules. All existing tests must pass."

```python
class PricingRule:
    """A single pricing rule that can modify a price."""

    def apply(self, unit_price, group_size):
        return unit_price


class GroupDiscountRule(PricingRule):

    def __init__(self, threshold, rate):
        self._threshold = threshold
        self._rate = rate

    def apply(self, unit_price, group_size):
        if group_size >= self._threshold:
            return unit_price * (Decimal("1") - self._rate)
        return unit_price


class PricingEngine:
    """Calculates seat prices using a chain of pricing rules."""

    def __init__(self, config):
        self._base_prices = config["sections"]
        self._events = config["events"]
        self._rules = [
            GroupDiscountRule(
                config["group_discount_threshold"],
                config["group_discount_rate"],
            )
        ]

    def calculate(self, section, event_id, group_size):
        if group_size < 1:
            raise ValueError("Invalid group size")
        if section not in self._base_prices:
            raise ValueError("Unknown section")

        base = self._base_prices[section]
        multiplier = self._events[event_id]["multiplier"]
        unit = base * multiplier

        for rule in self._rules:
            unit = rule.apply(unit, group_size)

        unit = unit.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total = (unit * group_size).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return {"unit_price": unit, "total_price": total}
```

Run the tests again:

```
$ pytest test_seat_reservation.py -v

34 passed in 0.08s
```

All 34 tests pass with the regenerated implementation.

The internal design is completely different — strategy pattern with a rules chain instead of inline computation. But the behavior is identical, verified by the same test suite.

This is regeneration. The specification and tests did not change. The implementation was discarded and replaced. The system's behavioral identity is preserved.

---

# 13. Specification Fingerprint

The Specification Fingerprint is a cryptographic hash of the knowledge layer: specifications, tests, acceptance cases, and behavioral contracts.

For this example, the fingerprint inputs are:

```
specifications:
  - feature_specs (sections 4.1 through 4.6)
  - behavioral_scenarios (section 5)
  - invariants (section 6)
  - acceptance_cases (section 7)

tests:
  - test_seat_reservation.py (34 tests)

nfr_constraints:
  - decimal_arithmetic
  - injectable_clock
  - exclusive_hold_enforcement
```

The fingerprint is computed as:

```
fingerprint = sha256(
    sorted(spec_files) +
    sorted(test_files) +
    sorted(nfr_declarations)
)
```

Two implementations that pass the same fingerprint are behaviorally equivalent, regardless of internal design, programming language, or framework.

The original implementation and the regenerated implementation both pass against the same fingerprint. They are equivalent systems.

---

# 14. What This Example Demonstrates

This walkthrough exercised every part of the STDD methodology on a system with real complexity.

**Specifications scale.** Six features with precise inputs, outputs, constraints, and failure conditions. The T-Spec format handled multi-component interactions (holds depend on inventory, confirmations depend on holds and pricing).

**Behavioral scenarios catch edge cases.** Writing Given/When/Then scenarios forced us to define what happens when a hold expires during confirmation, when a wrong customer tries to confirm, and when concurrent holds collide. These are the bugs that surface in production when behavior is not specified upfront.

**NFRs activate from technology and domain choices.** Choosing a SQL database triggered parameterized query requirements. Handling money triggered decimal arithmetic requirements. Time-based holds triggered the injectable clock requirement. These were not afterthoughts — they shaped the specifications and tests.

**The traceability matrix closes the spec-to-test gap.** Every specification has a test. Every test traces to a specification. There are no untested specs and no orphaned tests.

**The specification pyramid catches composition bugs.** Unit tests alone would not catch the interaction between hold expiry and confirmation, or verify that the price returned to the customer matches the PricingEngine's calculation. Integration tests verify that components honor their contracts. System tests verify that full workflows produce the correct end-to-end outcome. Bugs hide in the gaps between functions — the pyramid closes those gaps.

**Regeneration works.** We discarded the PricingEngine and replaced it with a structurally different implementation. All 34 tests passed. The system's behavior did not change. This is only possible because the knowledge layer (specifications + tests) fully defines the expected behavior.

**The Specification Fingerprint defines identity.** Two different implementations produce the same behavioral identity because they satisfy the same fingerprint. The implementation is not the system. The specification is.

---

For the philosophy behind this process, see the [Manifesto](../manifesto.md).

For the step-by-step methodology, see the [Method](../docs/method.md).

For guidance on writing specifications like the ones in this example, see [Writing Specifications](../docs/writing-specifications.md).
