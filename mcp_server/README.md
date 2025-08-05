# Aloha-Lite MCP Bridge (Playwright)

This service exposes a WebSocket bridge so Anthropic Claude Desktop can drive the
Aloha-Lite demo through the **Playwright MCP server**.

## Features

- 🔌 **WebSocket JSON-RPC** – one message per Playwright tool call
- 📡 **Live view streaming** at `/stream.mjpeg` (HTTP MJPEG) and `/stream_ws` (WebSocket PNG)
- 💓 **Health check** at `/health`

## Quick Start

```bash
# 1. Install Python deps
uv sync

# 2. Start the Playwright MCP server (defaults to ws://localhost:9010)
uvx playwright-mcp --port 9010

# 3. Run the bridge on port 8900
uv run main.py
```

### Environment Variables

| Variable            | Description                                             | Default              |
|---------------------|---------------------------------------------------------|----------------------|
| `PLAYWRIGHT_MCP_WS` | WebSocket URL where the Playwright MCP server is running | `ws://localhost:9010` |

## Claude Desktop Integration

Add the server to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "aloha-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/aloha-lite/mcp_server/",
        "run",
        "main.py"
      ]
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
