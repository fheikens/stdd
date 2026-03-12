"""Order Cancellation — reference implementation.

This module implements the order cancellation logic as specified
in specification.md. It is intentionally simple and stateless:
order storage is represented as a plain dictionary passed in by
the caller, making the function easy to test and regenerate.
"""

from datetime import datetime


class CancelOrderError(Exception):
    """Raised when an order cannot be cancelled."""

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


CANCELLABLE_STATUSES = {"pending", "confirmed"}
REFUND_STATUSES = {"confirmed"}


def cancel_order(
    orders: dict,
    order_id: str,
    reason: str,
    now: datetime | None = None,
) -> dict:
    """Cancel an order and return the cancellation result.

    Args:
        orders: dict mapping order_id to order dict with at least a
                "status" key.
        order_id: identifier of the order to cancel.
        reason: non-empty string explaining why the order is cancelled.
        now: optional timestamp override; defaults to datetime.now().

    Returns:
        dict with keys: order_id, previous_status, new_status,
        refund_triggered, cancelled_at, reason.

    Raises:
        CancelOrderError: when the order cannot be cancelled.
    """
    if not reason or not reason.strip():
        raise CancelOrderError("INVALID_REASON", "A cancellation reason is required.")

    if order_id not in orders:
        raise CancelOrderError("ORDER_NOT_FOUND", f"Order {order_id} does not exist.")

    order = orders[order_id]
    status = order["status"]

    if status == "cancelled":
        raise CancelOrderError(
            "ORDER_ALREADY_CANCELLED",
            f"Order {order_id} has already been cancelled.",
        )

    if status not in CANCELLABLE_STATUSES:
        raise CancelOrderError(
            "ORDER_NOT_CANCELLABLE",
            f"Order {order_id} cannot be cancelled (status: {status}).",
        )

    cancelled_at = now or datetime.now()
    previous_status = status

    order["status"] = "cancelled"
    order["cancelled_at"] = cancelled_at
    order["reason"] = reason

    return {
        "order_id": order_id,
        "previous_status": previous_status,
        "new_status": "cancelled",
        "refund_triggered": previous_status in REFUND_STATUSES,
        "cancelled_at": cancelled_at,
        "reason": reason,
    }
