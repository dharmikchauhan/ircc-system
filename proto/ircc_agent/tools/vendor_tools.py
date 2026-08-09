"""
tools/vendor_tools.py
Vendor backorder initiation tools.
"""
import uuid
from ircc_agent.utils import _execute_read_query
from typing import Any

REQUIRES_APPROVAL_THRESHOLD = 500.00

def submit_vendor_backorder(
    sku: str,
    quantity: int,
    customer_id: str,
) -> dict[str, Any]:
    """
    Initiates a vendor backorder for the specified SKU and quantity.

    In production this calls the vendor's REST API:
        POST {vendor.api_endpoint}/orders
        Body: { sku, quantity, customer_id }

    This mock simulates a successful API call with a random order reference.

    Args:
        sku:                    The SKU to restock.
        quantity:               Number of units to order.
        customer_id:            Customer id

    Returns:
        dict with backorder_id, expected_delivery, status
    """
    
    product = _execute_read_query(
        query="SELECT * FROM products WHERE sku = ?",
        params=[sku]
    )

    total_order_cost = product["price"] * quantity
    status = "APPROVAL_REQUIRED" if total_order_cost > REQUIRES_APPROVAL_THRESHOLD else "APPROVED"

    orderId = str(uuid.uuid4())
    response = {
        "status": status,
        "order_id": orderId,
        "requires_hitl": True if status == "APPROVAL_REQUIRED" else False,
        "approval_reason": f"Order total ${total_order_cost} exceeds ${REQUIRES_APPROVAL_THRESHOLD} threshold.",
        "workflow_execution_id": "projects/123/locations/us-central1/workflows/hitl-approval/executions/abc-456"
    }

    # print(response)

    return response
    