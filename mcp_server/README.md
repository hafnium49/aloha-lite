# ALOHA-Lite Playwright MCP Server

This service implements the **Model Context Protocol (MCP)** to enable Claude Desktop to control the ALOHA-Lite robot system **through the web browser interface only**. All robot control is performed by browser automation via Playwright.

## 🎭 What is this MCP Server?

This MCP server is a **Playwright browser automation bridge** that allows Claude Desktop to:
- Navigate and interact with the ALOHA-Lite web interface
- Control robots by clicking buttons and filling forms in the browser
- Take screenshots and analyze the web interface
- **NOT make direct API calls** to robot services

## 🏗️ Architecture

```
Claude Desktop
    ↓ MCP Protocol (stdio)
Playwright MCP Server (This)
    ↓ JSON-RPC WebSocket  
Playwright MCP (playwright-mcp)
    ↓ Browser Automation
Web Browser → ALOHA-Lite Frontend
```

## Features

- 🔌 **MCP Protocol** – JSON-RPC over stdio communication with Claude Desktop
- 🎭 **Playwright Bridge** – Forwards all commands to external Playwright MCP server
- � **Automatic Process Management** – Starts and manages Playwright server subprocess automatically
- ❤️ **Health Monitoring** – Monitors Playwright server health with automatic restart capability  
- 🛡️ **Graceful Shutdown** – Proper signal handling and cleanup on exit
- �🖼️ **Live Screenshots** – Real-time browser screenshot streaming
- 🌐 **Web-Only Control** – Robot control only through browser interface
- 🚫 **No Direct APIs** – No direct HTTP calls to robot_service or vision_bridge

## Quick Start

### Prerequisites

1. **Install Playwright MCP Server**:
```bash
npm install -g @anthropic-ai/playwright-mcp-server
```

2. **Install Python dependencies**:
```bash
cd /path/to/aloha-lite/mcp_server
uv sync
```

> **📝 Note**: The enhanced MCP server automatically starts and manages the Playwright server process. You no longer need to manually run `playwright-mcp --port 9010`!

### Running the Server

#### For Claude Desktop (Recommended):
```bash
uv run python main.py
```

#### For Development/Testing (Web server mode):
```bash
uv run python main.py --web
```

## Claude Desktop Integration

Add the server to your `claude_desktop_config.json`:

### Recommended Configuration (Using UV):
```json
{
  "mcpServers": {
    "aloha-playwright": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/aloha-lite/mcp_server",
        "run",
        "python",
        "main.py"
      ],
      "cwd": "/path/to/your/aloha-lite/mcp_server"
    }
  }
}
```

### Direct Python (if python is in PATH):
```json
{
  "mcpServers": {
    "aloha-playwright": {
      "command": "python",
      "args": [
        "/path/to/your/aloha-lite/mcp_server/main.py"
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
    "aloha-playwright": {
      "command": "C:\\Users\\username\\.local\\bin\\uv.exe",
      "args": [
        "--directory",
        "C:\\Users\\username\\Documents\\git\\aloha-lite\\mcp_server",
        "run",
        "python",
        "main.py"
      ],
      "cwd": "C:\\Users\\username\\Documents\\git\\aloha-lite\\mcp_server"
    }
  }
}
```

### Advanced Configuration (Optional)

For custom Playwright server settings, you can add environment variables:

```json
{
  "mcpServers": {
    "aloha-playwright": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/aloha-lite/mcp_server",
        "run",
        "python",
        "main.py"
      ],
      "cwd": "/path/to/your/aloha-lite/mcp_server",
      "env": {
        "PLAYWRIGHT_MCP_PORT": "9010",
        "PLAYWRIGHT_STARTUP_TIMEOUT": "15",
        "PLAYWRIGHT_MCP_WS": "ws://localhost:9010"
      }
    }
  }
}
```

## Setup Instructions

1. **Install Playwright MCP Server**:
   ```bash
   npm install -g @anthropic-ai/playwright-mcp-server
   ```

2. **Install dependencies**: Run `uv sync` in the mcp_server directory

3. **Start ALOHA-Lite services**: Ensure frontend, robot_service, and vision_bridge are running

4. **Configure Claude Desktop**: Add the server configuration to `claude_desktop_config.json`

5. **Restart Claude Desktop**: Close and reopen Claude Desktop to load the new MCP server

6. **Test connection**: Look for Playwright browser automation tools in Claude Desktop

> **🚀 Enhanced Features**: The MCP server now automatically:
> - Starts the Playwright server subprocess when needed
> - Monitors Playwright server health and restarts if necessary  
> - Handles graceful shutdown and cleanup
> - No manual process management required!

## Available Capabilities

Once connected, Claude Desktop will have access to all Playwright browser automation tools:

- **🖱️ Browser Navigation** - Navigate to web pages and interact with elements
- **📝 Form Interaction** - Fill forms, click buttons, select options
- **📷 Screenshots** - Take full-page or element screenshots  
- **🔍 Element Detection** - Find and interact with page elements
- **⌨️ Keyboard Input** - Type text and keyboard shortcuts
- **🖼️ Visual Analysis** - Analyze page content and screenshots
- **🤖 Robot Control** - Control robots **only through the web interface**

### Robot Control Workflow

Claude can control the ALOHA-Lite robot by:
1. Taking screenshots of the web interface
2. Clicking control buttons and adjusting sliders
3. Filling in color mixing ratios and parameters
4. Monitoring execution status through the web UI
5. Analyzing results displayed in the browser

**Note**: All robot control happens through browser automation - no direct API calls are made.

## Troubleshooting

### Common Issues:

**"Playwright MCP server not responding"**
- Solution: The enhanced MCP server automatically manages the Playwright process
- If issues persist, check that port 9010 is not blocked by firewall
- The server will automatically restart Playwright if it becomes unresponsive

**"ModuleNotFoundError"** 
- Solution: Run `uv sync` to install dependencies
- Alternative: Run `uv add <missing-package>` to add specific packages

**"spawn python ENOENT" (Windows)**
- Solution: Use UV-based configuration instead of direct Python
- Check the Windows Example configuration above

**Connection timeout**
- Ensure `main.py` is being used (not `mcp_server.py`)
- Verify the file path in your configuration is correct
- Check Claude Desktop logs for specific error messages
- The server automatically handles Playwright connection issues

**Browser automation not working**
- Verify the ALOHA-Lite frontend is running on http://localhost:3000
- The enhanced server automatically starts Playwright with browser access
- Take a screenshot first to verify browser connection
- Check server logs for Playwright subprocess status

### Environment Variables

- `PLAYWRIGHT_MCP_WS`: WebSocket URL for Playwright MCP server (default: `ws://localhost:9010`)
- `PLAYWRIGHT_MCP_PORT`: Port for Playwright server (default: `9010`) 
- `PLAYWRIGHT_STARTUP_TIMEOUT`: Timeout for Playwright startup in seconds (default: `10`)

> **📝 Note**: Environment variables are optional with the enhanced server - it automatically manages Playwright with sensible defaults.

### Logs and Debugging

- Check Claude Desktop logs for MCP connection issues
- Server logs go to stderr and appear in Claude Desktop logs
- Use `--web` mode for development testing with HTTP endpoints

## Development Notes

### Two Modes of Operation:

1. **MCP Mode** (Default): Communicates with Claude Desktop via stdio
   ```bash
   python main.py
   ```

2. **Web Server Mode**: For development and testing
   ```bash
   python main.py --web
   ```

### Testing without Claude Desktop:

You can test the web server mode by visiting:
- `http://localhost:8900/health` - Health check
- `http://localhost:8900/stream.mjpeg` - Live browser screenshots
- `ws://localhost:8900/ws` - WebSocket for manual testing

### File Structure:

- `main.py` - Consolidated MCP server (Playwright only)
- `mcp_server.py` - **DEPRECATED** - Old robot control server
- `README.md` - This documentation
