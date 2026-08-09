"""
xyzmart_mcp_server.py

Model Context Protocol (MCP) server for xyzMart's IRCC system.
Exposes three tools to the ADK agent via JSON-RPC 2.0 over stdio transport:
  - inventory_search      → find in-stock alternatives for an out-of-stock SKU
  - submit_backorder      → initiate a vendor backorder for a given SKU
  - get_customer_loyalty  → retrieve a customer's loyalty tier

Transport: stdio (spawned as a subprocess by the ADK agent via McpToolset)
"""

import sys
import os

# Ensure the proto/ directory is on sys.path so ircc_agent package is importable
# when this script is run as a subprocess from proto/ or any working directory.
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROTO_DIR = os.path.abspath(os.path.join(_HERE, ".."))
if _PROTO_DIR not in sys.path:
    sys.path.insert(0, _PROTO_DIR)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from mcp.server.fastmcp import FastMCP
from ircc_agent.tools.inventory_tools import find_alternative_products
from ircc_agent.tools.vendor_tools import submit_vendor_backorder
from ircc_agent.tools.customer_tools import get_customer_loyalty

# ---------------------------------------------------------------------------
# Server initialisation
# ---------------------------------------------------------------------------
mcp = FastMCP(
    name="xyzmart-ircc",
    instructions=(
        "This MCP server exposes xyzMart's Inventory Recovery & Customer "
        "Compensation (IRCC) APIs. Use 'inventory_search' to find in-stock "
        "alternatives for a stockout SKU, 'submit_backorder' to place a "
        "vendor backorder, and 'get_customer_loyalty' to retrieve a "
        "customer's loyalty tier and priority status."
    ),
)

# -------------------------------------
# Tool: inventory_search
# Wraps: find_alternative_products()
# -------------------------------------
@mcp.tool(
    name="inventory_search",
    description=(
        "Search xyzMart's inventory for in-stock alternative products "
        "similar to a given out-of-stock SKU. Matches are ranked by "
        "category and tag overlap. "
        "Returns a list of candidate SKUs with relevance scores."
    ),
)
def inventory_search(sku: str, required_quantity: int, max_results: int = 3) -> dict:
    """
    Args:
        sku:               The out-of-stock SKU to find alternatives for.
        required_quantity: Minimum stock quantity the alternative must have.
        max_results:       Maximum number of alternatives to return (default 3).
    """
    return find_alternative_products(
        sku=sku,
        required_quantity=required_quantity,
        max_results=max_results,
    )


# -----------------------------------
# Tool: submit_backorder
# Wraps: submit_vendor_backorder()
# -----------------------------------
@mcp.tool(
    name="submit_backorder",
    description=(
        "Submit a vendor backorder request for a specific SKU and quantity "
        "via xyzMart's backorder submission API. "
        "Returns a backorder confirmation with status."
    ),
)
def submit_backorder(
    sku: str,
    quantity: int,
    customer_id: str,
) -> dict:
    """
    Args:
        sku:         The SKU to restock.
        quantity:    Number of units to order.
        customer_id: customer ID.
    """
    return submit_vendor_backorder(
        sku=sku,
        quantity=quantity,
        customer_id=customer_id,
    )


# ------------------------------------
# Tool: get_customer_loyalty
# Wraps: get_customer_loyalty()
# -------------------------------------
@mcp.tool(
    name="get_customer_loyalty",
    description=(
        "Retrieve a customer's loyalty profile from xyzMart's customer "
        "database. Returns the loyalty tier (e.g., STANDARD, GOLD, PLATINUM) "
        "and whether the customer qualifies for priority backorder processing."
    ),
)
def customer_loyalty(customer_id: str) -> dict:
    """
    Args:
        customer_id: Unique customer identifier, e.g. 'CUST-001'.
    """
    return get_customer_loyalty(customer_id=customer_id)


# ---------------------------------------------------------------------------
# Entrypoint — stdio transport
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    mcp.run(transport="stdio")
