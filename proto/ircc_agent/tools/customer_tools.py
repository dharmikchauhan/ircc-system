"""
tools/customer_tools.py
Customer loyalty profile retrieval and hyper-personalized offer generation.

DB_NEEDED / API_NEEDED annotations highlight integration points.
"""

from ircc_agent.utils import db_helper
from typing import Any

# -------------------------------
# Fetch customer loyalty
# -------------------------------
def get_customer_loyalty(customer_id: str) -> dict[str, Any]:
    """
    Retrieves a customer's loyalty profile including tier.

    Args:
        customer_id: Unique customer identifier, e.g. "CUST-001"

    Returns:
        dict with customer loyalty.
    """
    customer = db_helper._execute_read_query("select cu.id, lt.type, lt.priority_backorder from customers as cu JOIN loyalty_tiers as lt ON cu.loyalty_tier_id = lt.id where cu.id = ?", (customer_id,))
    if not customer:
        return {
            "status": "error",
            "message": f"Customer '{customer_id}' not found.",
        }
    return {
        "status": "success",
        **customer
    }