from ircc_agent.utils.db_helper import _init_database
import os
import sys
from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool.mcp_toolset import (
    McpToolset,
    StdioConnectionParams,
    StdioServerParameters,
)

# Resolve absolute path to the MCP server script so McpToolset can spawn it
# regardless of the working directory.
_MCP_SERVER_SCRIPT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "xyzmart_mcp_server.py",
    )
)

# Set "LOCAL" for local SQLite mock testing, "PROD" for live system APIs
ENV = os.getenv("APP_ENV", "LOCAL")
if(ENV == "LOCAL"):
    _init_database()

llm_model = os.getenv('ADK_MODEL_NAME', 'gemini-3.1-flash-lite')

root_agent = Agent(
    model=llm_model,
    name='ircc_agent',
    description="""
        Inventory Recovery & Customer Compensation (IRCC) Agent for xyzMart. 
        Detects out-of-stock events via pub/sub event, initiates vendor backorders on based of customer loyalty profile.
    """,
    instruction="""
        You are the primary inventory orchestrator for xyzMart.
        Your job is to analyze real-time stockouts using the following process:
        1. Query customer loyalty tier using `get_customer_loyalty`.
        2. Decision Logic:
        - For VIP Tier Customers (GOLD/PLATINUM):
            * Always attempt to issue a high-priority backorder (`submit_backorder`).
        - For Standard Tier Customers:
            * First query for alternative in-stock SKUs using `inventory_search`.
            * If an in-stock alternative exists, suggest the replacement SKU to the customer.
            * If no alternative exists, issue a backorder (`submit_backorder`).
        - If submit_backorder tool response indicates status: APPROVAL_REQUIRED, explain to the user that the order has been submitted for manager approval and share the order_id.
    """,
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command=sys.executable,
                    args=[_MCP_SERVER_SCRIPT],
                )
            )
        )
    ],
)