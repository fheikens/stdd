"""Test suite for Order Cancellation.

Every test references a specification ID from specification.md.
Tests are organized into three groups:
  1. Happy path (rules ORD-CANCEL-01 through ORD-CANCEL-02)
  2. Failure conditions (rules ORD-CANCEL-03 through ORD-CANCEL-08)
  3. Invariants (ORD-INV-01 through ORD-INV-03)
"""

from datetime import datetime

import pytest

from cancel_order import CancelOrderError, cancel_order


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

FIXED_TIME = datetime(2026, 3, 12, 14, 30, 0)


@pytest.fixture
def orders():
    """Provide a fresh order store for each test."""
    return {
        "ORD-100": {"status": "pending"},
        "ORD-200": {"status": "confirmed"},
        "ORD-300": {"status": "shipped"},
        "ORD-400": {"status": "delivered"},
        "ORD-500": {"status": "cancelled"},
    }


# ---------------------------------------------------------------------------
# Happy path tests
# ---------------------------------------------------------------------------


def test_cancel_pending_order_no_refund(orders):
    """ORD-CANCEL-01: A pending order can be cancelled without a refund."""
    result = cancel_order(orders, "ORD-100", "Changed my mind", now=FIXED_TIME)

    assert result["order_id"] == "ORD-100"
    assert result["previous_status"] == "pending"
    assert result["new_status"] == "cancelled"
    assert result["refund_triggered"] is False
    assert result["cancelled_at"] == FIXED_TIME
    assert result["reason"] == "Changed my mind"
    assert orders["ORD-100"]["status"] == "cancelled"


def test_cancel_confirmed_order_triggers_refund(orders):
    """ORD-CANCEL-02: A confirmed order can be cancelled and triggers a refund."""
    result = cancel_order(orders, "ORD-200", "Found cheaper alternative", now=FIXED_TIME)

    assert result["order_id"] == "ORD-200"
    assert result["previous_status"] == "confirmed"
    assert result["new_status"] == "cancelled"
    assert result["refund_triggered"] is True
    assert result["cancelled_at"] == FIXED_TIME
    assert result["reason"] == "Found cheaper alternative"
    assert orders["ORD-200"]["status"] == "cancelled"


# ---------------------------------------------------------------------------
# Failure condition tests
# ---------------------------------------------------------------------------


def test_cancel_shipped_order_rejected(orders):
    """ORD-CANCEL-03 / ORD-FAIL-02: A shipped order cannot be cancelled."""
    with pytest.raises(CancelOrderError) as exc_info:
        cancel_order(orders, "ORD-300", "No longer needed", now=FIXED_TIME)

    assert exc_info.value.code == "ORDER_NOT_CANCELLABLE"
    assert orders["ORD-300"]["status"] == "shipped"


def test_cancel_delivered_order_rejected(orders):
    """ORD-CANCEL-04 / ORD-FAIL-02: A delivered order cannot be cancelled."""
    with pytest.raises(CancelOrderError) as exc_info:
        cancel_order(orders, "ORD-400", "Wrong item", now=FIXED_TIME)

    assert exc_info.value.code == "ORDER_NOT_CANCELLABLE"
    assert orders["ORD-400"]["status"] == "delivered"


def test_cancel_already_cancelled_order_rejected(orders):
    """ORD-CANCEL-05 / ORD-FAIL-03: A cancelled order cannot be cancelled again."""
    with pytest.raises(CancelOrderError) as exc_info:
        cancel_order(orders, "ORD-500", "Duplicate request", now=FIXED_TIME)

    assert exc_info.value.code == "ORDER_ALREADY_CANCELLED"
    assert orders["ORD-500"]["status"] == "cancelled"


def test_cancellation_records_timestamp_and_reason(orders):
    """ORD-CANCEL-06: Cancellation records a timestamp and the provided reason."""
    result = cancel_order(orders, "ORD-100", "Changed my mind", now=FIXED_TIME)

    assert result["cancelled_at"] == FIXED_TIME
    assert result["reason"] == "Changed my mind"
    assert orders["ORD-100"]["cancelled_at"] == FIXED_TIME
    assert orders["ORD-100"]["reason"] == "Changed my mind"


def test_cancel_with_empty_reason_rejected(orders):
    """ORD-CANCEL-07 / ORD-FAIL-04: An empty reason is rejected."""
    with pytest.raises(CancelOrderError) as exc_info:
        cancel_order(orders, "ORD-100", "", now=FIXED_TIME)

    assert exc_info.value.code == "INVALID_REASON"
    assert orders["ORD-100"]["status"] == "pending"


def test_cancel_nonexistent_order_rejected(orders):
    """ORD-CANCEL-08 / ORD-FAIL-01: A non-existent order is rejected."""
    with pytest.raises(CancelOrderError) as exc_info:
        cancel_order(orders, "ORD-999", "Cancel please", now=FIXED_TIME)

    assert exc_info.value.code == "ORDER_NOT_FOUND"


# ---------------------------------------------------------------------------
# Invariant tests
# ---------------------------------------------------------------------------


def test_invariant_only_cancellable_statuses_transition(orders):
    """ORD-INV-01: Only 'pending' and 'confirmed' can transition to 'cancelled'.

    Verify that every non-cancellable status is rejected and remains unchanged.
    """
    non_cancellable = {"ORD-300": "shipped", "ORD-400": "delivered"}

    for oid, expected_status in non_cancellable.items():
        with pytest.raises(CancelOrderError):
            cancel_order(orders, oid, "Attempt to cancel", now=FIXED_TIME)
        assert orders[oid]["status"] == expected_status

    # Verify cancellable statuses do transition
    cancel_order(orders, "ORD-100", "Reason", now=FIXED_TIME)
    assert orders["ORD-100"]["status"] == "cancelled"

    cancel_order(orders, "ORD-200", "Reason", now=FIXED_TIME)
    assert orders["ORD-200"]["status"] == "cancelled"


def test_invariant_cancelled_is_terminal(orders):
    """ORD-INV-02: Once cancelled, an order cannot change status again."""
    cancel_order(orders, "ORD-100", "First cancellation", now=FIXED_TIME)
    assert orders["ORD-100"]["status"] == "cancelled"

    with pytest.raises(CancelOrderError) as exc_info:
        cancel_order(orders, "ORD-100", "Second attempt", now=FIXED_TIME)

    assert exc_info.value.code == "ORDER_ALREADY_CANCELLED"
    assert orders["ORD-100"]["status"] == "cancelled"


def test_invariant_result_contains_reason_and_timestamp(orders):
    """ORD-INV-03: Every successful cancellation result includes reason and timestamp."""
    for oid in ["ORD-100", "ORD-200"]:
        result = cancel_order(orders, oid, "Valid reason", now=FIXED_TIME)

        assert "cancelled_at" in result
        assert isinstance(result["cancelled_at"], datetime)
        assert "reason" in result
        assert len(result["reason"]) > 0
