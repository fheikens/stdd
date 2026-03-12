
# Traceability Matrix: Order Cancellation

Every specification element maps to at least one test. Every test maps to a specification element.

## Rules

| Spec ID | Description | Test(s) |
|---------|-------------|---------|
| ORD-CANCEL-01 | Pending order can be cancelled, no refund | test_cancel_pending_order_no_refund |
| ORD-CANCEL-02 | Confirmed order can be cancelled, refund triggered | test_cancel_confirmed_order_triggers_refund |
| ORD-CANCEL-03 | Shipped order cannot be cancelled | test_cancel_shipped_order_rejected |
| ORD-CANCEL-04 | Delivered order cannot be cancelled | test_cancel_delivered_order_rejected |
| ORD-CANCEL-05 | Already cancelled order cannot be cancelled again | test_cancel_already_cancelled_order_rejected |
| ORD-CANCEL-06 | Cancellation records timestamp and reason | test_cancellation_records_timestamp_and_reason |
| ORD-CANCEL-07 | Empty reason is rejected | test_cancel_with_empty_reason_rejected |
| ORD-CANCEL-08 | Non-existent order is rejected | test_cancel_nonexistent_order_rejected |

## Invariants

| Spec ID | Description | Test(s) |
|---------|-------------|---------|
| ORD-INV-01 | Only pending or confirmed can transition to cancelled | test_invariant_only_cancellable_statuses_transition |
| ORD-INV-02 | Cancelled is a terminal state | test_invariant_cancelled_is_terminal |
| ORD-INV-03 | Cancellation result always has reason and timestamp | test_invariant_result_contains_reason_and_timestamp |

## Failure Conditions

| Spec ID | Description | Test(s) |
|---------|-------------|---------|
| ORD-FAIL-01 | Order not found | test_cancel_nonexistent_order_rejected |
| ORD-FAIL-02 | Order not in cancellable status | test_cancel_shipped_order_rejected, test_cancel_delivered_order_rejected |
| ORD-FAIL-03 | Order already cancelled | test_cancel_already_cancelled_order_rejected |
| ORD-FAIL-04 | Empty or missing reason | test_cancel_with_empty_reason_rejected |

## Coverage Summary

- Specification elements: 15 (8 rules + 3 invariants + 4 failure conditions)
- Tests: 11
- Untested specifications: 0
- Orphaned tests: 0
