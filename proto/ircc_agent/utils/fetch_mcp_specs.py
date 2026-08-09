import asyncio
import json
import os
import sys
from google.adk.tools.mcp_tool.mcp_toolset import (
    McpToolset,
    StdioConnectionParams,
    StdioServerParameters,
)

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROTO_DIR = os.path.abspath(os.path.join(_HERE, "..", ".."))
if _PROTO_DIR not in sys.path:
    sys.path.insert(0, _PROTO_DIR)

_MCP_SERVER_SCRIPT = os.path.abspath(
    os.path.join(
        _HERE,
        "..",
        "xyzmart_mcp_server.py",
    )
)
_OUTPUT_JSON_PATH = os.path.abspath(
    os.path.join(
        _HERE,
        "..",
        "xyzmart_mcp_server_specs.json",
    )
)

async def fetch_mcp_specs():
    # Configure transport parameters for local python stdio server
    connection_params = StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=[_MCP_SERVER_SCRIPT],
        )
    )
    
    toolset = McpToolset(connection_params=connection_params)
    
    # Executes the internal tools/list JSON-RPC call over stdio transport
    tools = await toolset.get_tools()
    
    mcp_tools = []
    for tool in tools:
        decl = tool._get_declaration()
        mcp_tools.append({
            "name": tool.name,
            "description": tool.description,
            "inputSchema": decl.parameters_json_schema or {}
        })
    
    # Format according to JSON-RPC 2.0 specification for MCP tools/list response
    json_rpc_spec = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "tools": mcp_tools
        }
    }
    
    with open(_OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(json_rpc_spec, f, indent=2)
        
    print(f"✅ Successfully exported JSON-RPC 2.0 MCP spec to: {_OUTPUT_JSON_PATH}")

if __name__ == "__main__":
    asyncio.run(fetch_mcp_specs())