"""
MCP Server entry point
Fixed to use the correct import path for the current directory structure.
"""
import uvicorn

if __name__ == "__main__":
    # Fixed: Use 'main:app' instead of 'mcp_server.main:app'
    # since main.py is in the current directory
    uvicorn.run("main:app", host="0.0.0.0", port=8900)
