# Aloha-Lite MCP Server

A lightweight bridge that exposes the Aloha-Lite frontend over the Model Context Protocol (MCP). It allows Anthropic Claude Desktop to control the robotics stack through simple HTTP and WebSocket commands.

## Features

- 🔌 **WebSocket Command Channel** for real-time communication with Claude Desktop
- 🌐 **HTTP Proxy** that forwards requests to the Aloha-Lite frontend
- 💓 **Health Check** endpoint for monitoring
- 🛠️ **Minimal Dependencies**: FastAPI, httpx, websockets, uvicorn

## Quick Start

```bash
uv sync
cd mcp_server
python -m uvicorn main:app --host 0.0.0.0 --port 8900
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FRONTEND_URL` | URL of the Aloha-Lite frontend service | `http://frontend` |

## Claude Desktop Integration

Add the MCP server to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "aloha-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/aloha-lite/mcp_server/",
        "run",
        "server.py"
      ]
    }
  }
}
```

1. Ensure dependencies are installed with `uv sync`.
2. Update the path above to the location of your `aloha-lite` checkout.
3. Restart Claude Desktop to load the new tools.

## API Endpoints

### `GET /health`
Simple health check returning `{ "status": "ok" }`.

### `WS /ws`
Bidirectional channel for sending commands to the frontend.

### `/{path}` (HTTP Proxy)
Proxies arbitrary HTTP requests to `FRONTEND_URL`.

## Architecture

```
Claude Desktop → MCP Server → Aloha-Lite Frontend → Robot Service → Vision Bridge
```
