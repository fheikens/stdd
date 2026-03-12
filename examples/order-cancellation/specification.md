
# Order Cancellation

Feature: Order Cancellation
Version: 1.0
Status: accepted

---

## Description

The system must cancel an order when requested, subject to the order's current status. Cancellation behavior depends on whether payment has been processed: confirmed orders trigger a refund, while pending orders do not. The system records the cancellation timestamp and reason for audit purposes.

## Inputs

| Field | Type | Constraints |
|-------|------|-------------|
| order_id | string | Non-empty, must reference an existing order |
| reason | string | Non-empty, maximum 500 characters |

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| order_id | string | The cancelled order's identifier |
| previous_status | string | The order's status before cancellation |
| new_status | string | Always "cancelled" on success |
| refund_triggered | boolean | True if the order required a refund |
| cancelled_at | datetime | Timestamp of the cancellation |
| reason | string | The cancellation reason provided |

On failure, the system returns an error with a machine-readable error code and a human-readable message.

## Rules

| ID | Rule |
|----|------|
| ORD-CANCEL-01 | An order with status "pending" can be cancelled. No refund is triggered. |
| ORD-CANCEL-02 | An order with status "confirmed" can be cancelled. A refund is triggered. |
| ORD-CANCEL-03 | An order with status "shipped" cannot be cancelled. The system returns an error with code `ORDER_NOT_CANCELLABLE`. |
| ORD-CANCEL-04 | An order with status "delivered" cannot be cancelled. The system returns an error with code `ORDER_NOT_CANCELLABLE`. |
| ORD-CANCEL-05 | An order with status "cancelled" cannot be cancelled again. The system returns an error with code `ORDER_ALREADY_CANCELLED`. |
| ORD-CANCEL-06 | Cancellation must record a timestamp (cancelled_at) and the provided reason on the order. |
| ORD-CANCEL-07 | The reason field must not be empty. If empty, the system returns an error with code `INVALID_REASON`. |
| ORD-CANCEL-08 | If the order_id does not match any existing order, the system returns an error with code `ORDER_NOT_FOUND`. |

## Behavioral Scenarios

### Scenario: Cancel a pending order
  Given: Order ORD-100 has status "pending"
  When: Cancellation is requested with reason "Changed my mind"
  Then: Order status changes to "cancelled"
  Then: refund_triggered is False
  Then: cancelled_at is recorded
  Then: reason is "Changed my mind"

### Scenario: Cancel a confirmed order
  Given: Order ORD-200 has status "confirmed"
  When: Cancellation is requested with reason "Found cheaper alternative"
  Then: Order status changes to "cancelled"
  Then: refund_triggered is True
  Then: cancelled_at is recorded
  Then: reason is "Found cheaper alternative"

### Scenario: Attempt to cancel a shipped order
  Given: Order ORD-300 has status "shipped"
  When: Cancellation is requested with reason "No longer needed"
  Then: The request is rejected with error code ORDER_NOT_CANCELLABLE
  Then: Order status remains "shipped"

### Scenario: Attempt to cancel a delivered order
  Given: Order ORD-400 has status "delivered"
  When: Cancellation is requested with reason "Wrong item"
  Then: The request is rejected with error code ORDER_NOT_CANCELLABLE
  Then: Order status remains "delivered"

### Scenario: Attempt to cancel an already cancelled order
  Given: Order ORD-500 has status "cancelled"
  When: Cancellation is requested with reason "Duplicate request"
  Then: The request is rejected with error code ORDER_ALREADY_CANCELLED
  Then: Order status remains "cancelled"

### Scenario: Cancel with empty reason
  Given: Order ORD-100 has status "pending"
  When: Cancellation is requested with reason ""
  Then: The request is rejected with error code INVALID_REASON
  Then: Order status remains "pending"

### Scenario: Cancel non-existent order
  Given: Order ORD-999 does not exist
  When: Cancellation is requested with reason "Cancel please"
  Then: The request is rejected with error code ORDER_NOT_FOUND

## Invariants

| ID | Invariant |
|----|-----------|
| ORD-INV-01 | An order's status can only transition to "cancelled" from "pending" or "confirmed". No other status may transition to "cancelled". |
| ORD-INV-02 | Once an order is cancelled, its status must never change again. Cancelled is a terminal state. |
| ORD-INV-03 | A cancellation result must always include a non-empty reason and a valid cancelled_at timestamp. |

## Failure Conditions

| ID | Condition | Expected Behavior |
|----|-----------|-------------------|
| ORD-FAIL-01 | Order not found | Return error with code `ORDER_NOT_FOUND` and message indicating the order does not exist. |
| ORD-FAIL-02 | Order not in cancellable status | Return error with code `ORDER_NOT_CANCELLABLE` and message indicating the current status. |
| ORD-FAIL-03 | Order already cancelled | Return error with code `ORDER_ALREADY_CANCELLED` and message indicating the order was previously cancelled. |
| ORD-FAIL-04 | Empty or missing reason | Return error with code `INVALID_REASON` and message indicating a reason is required. |

## State Model

```
pending ──────► confirmed ──────► shipped ──────► delivered
   │                │
   │ cancel         │ cancel
   │ (no refund)    │ (refund)
   ▼                ▼
cancelled ◄────────┘
(terminal state)
```

Valid cancellation transitions:
- pending -> cancelled (no refund)
- confirmed -> cancelled (refund triggered)

Invalid cancellation attempts:
- shipped -> cancelled (rejected)
- delivered -> cancelled (rejected)
- cancelled -> cancelled (rejected)

## Acceptance Cases

See: acceptance-cases.yaml

## Technologies

Python (reference implementation)

## Domain

E-commerce order management
