# MCP Server Notebooks

This directory contains Jupyter notebooks related to MCP (Model Context Protocol) server development and debugging.

## Notebooks

### `aloha_mcp_server_fix.ipynb`
- Contains the original MCP server fix implementation
- Troubleshooting steps and solutions for MCP integration

### `mcp_protocol_fix.ipynb`
- Protocol mismatch analysis and fix
- Detailed explanation of MCP vs FastAPI/Uvicorn differences
- Implementation of proper MCP server that handles JSON-RPC over stdio

### `mcp_server_debug.ipynb`
- Comprehensive diagnostic tools for MCP server issues
- Environment testing and validation scripts
- Debugging procedures for Claude Desktop integration

### `mcp_server_environment_fix.ipynb`
- Environment setup and dependency management
- UV package manager configuration
- Windows-specific Python PATH and dependency resolution

## Usage

These notebooks document the development process and provide debugging tools for the ALOHA-Lite MCP server integration with Claude Desktop.

To use these notebooks:
1. Ensure you have Jupyter installed in your environment
2. Navigate to this directory
3. Start Jupyter: `jupyter notebook` or `jupyter lab`
4. Open the relevant notebook for your debugging needs

## Related Files

- `../mcp_server.py` - Main MCP server implementation
- `../README.md` - MCP server setup and usage documentation
- `../pyproject.toml` - Project dependencies and configuration
