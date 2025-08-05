# ALOHA-Lite MCP Server

This service implements the **Model Context Protocol (MCP)** to enable Claude Desktop to control the ALOHA-Lite robot system through natural language commands.

## 🤖 What is MCP?

MCP (Model Context Protocol) allows AI assistants like Claude to interact with external systems through standardized tools. This server bridges Claude Desktop to the ALOHA-Lite robot control system.

## Features

- 🔌 **MCP Protocol** – JSON-RPC over stdio communication with Claude Desktop
- 🤖 **Robot Control Tools** – Joint movement, sequence execution, and position reading
- 🎨 **Color Dispensing** – ML-optimized solution mixing with volume splitting
- �️ **Vision Analysis** – Beaker color analysis using computer vision
- 📊 **Service Integration** – Bridges to robot_service, frontend, and vision_bridge

## Quick Start

```bash
# 1. Install Python dependencies
uv sync

# 2. Run the MCP server directly (for Claude Desktop)
python mcp_server.py

# 3. Alternative: Run the web server (for development/testing)
python main.py
```

## Claude Desktop Integration

Add the server to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "aloha-mcp": {
      "command": "python",
      "args": [
        "/path/to/your/aloha-lite/mcp_server/mcp_server.py"
      ],
      "cwd": "/path/to/your/aloha-lite/mcp_server"
    }
  }
}
```

### Windows Example:
```json
{
  "mcpServers": {
    "aloha-mcp": {
      "command": "python",
      "args": [
        "C:\\Users\\username\\Documents\\git\\aloha-lite\\mcp_server\\mcp_server.py"
      ],
      "cwd": "C:\\Users\\username\\Documents\\git\\aloha-lite\\mcp_server"
    }
  }
}
```

## Alternative Execution Methods

### Using the installed script (after `uv sync`):
```bash
uv run mcp-server
```

### Direct Python execution:
```bash
python main.py
```

### Using uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8900
```

## Setup Instructions

1. Ensure dependencies are installed with `uv sync`.
2. Start the Playwright MCP server separately (step 2 above) or set `PLAYWRIGHT_MCP_WS`.
3. Restart Claude Desktop to load the new tools.

## API Endpoints

- **WebSocket API**: `ws://localhost:8900/ws` - JSON-RPC commands from Claude Desktop
- **Health Check**: `http://localhost:8900/health` - Service status
- **Live Stream (MJPEG)**: `http://localhost:8900/stream.mjpeg` - HTTP video stream
- **Live Stream (WebSocket)**: `ws://localhost:8900/stream_ws` - WebSocket PNG frames

## Development

The server runs on port 8900 by default and provides real-time screenshot streaming for visual feedback during robot operations.
