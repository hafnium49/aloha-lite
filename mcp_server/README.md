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
uv run python mcp_server.py

# 3. Alternative: Run the web server (for development/testing)
uv run python main.py
```

## Claude Desktop Integration

Add the server to your `claude_desktop_config.json`:

### Recommended Configuration (Using UV):
```json
{
  "mcpServers": {
    "aloha-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/aloha-lite/mcp_server",
        "run",
        "python",
        "mcp_server.py"
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
      "command": "C:\\Users\\username\\.local\\bin\\uv.exe",
      "args": [
        "--directory",
        "C:\\Users\\username\\Documents\\git\\aloha-lite\\mcp_server",
        "run",
        "python",
        "mcp_server.py"
      ],
      "cwd": "C:\\Users\\username\\Documents\\git\\aloha-lite\\mcp_server"
    }
  }
}
```

## Alternative Execution Methods

### Using UV (Recommended):
```bash
uv run python mcp_server.py
```

### Using the installed script:
```bash
uv run mcp-server
```

### Direct Python execution (if dependencies installed globally):
```bash
python mcp_server.py
```

### Web server for development/testing:
```bash
uv run python main.py
```

## Setup Instructions

1. **Install dependencies**: Run `uv sync` in the mcp_server directory
2. **Configure Claude Desktop**: Add the server configuration to `claude_desktop_config.json`
3. **Restart Claude Desktop**: Close and reopen Claude Desktop to load the new MCP server
4. **Test connection**: Look for the ALOHA-Lite robot control tools in Claude Desktop

## Troubleshooting

### Common Issues:

**"ModuleNotFoundError: No module named 'requests'"**
- Solution: Run `uv sync` to install dependencies
- Alternative: Run `uv add requests` to add missing package

**"spawn python ENOENT" (Windows)**
- Solution: Use UV-based configuration instead of direct Python
- Check the Windows Example configuration above

**Connection timeout**
- Ensure you're using `mcp_server.py` (not `main.py`)
- Verify the file path in your configuration is correct
- Check Claude Desktop logs for specific error messages

## Available Tools

Once connected, Claude Desktop will have access to these robot control tools:

- **🤖 move_robot_joints** - Move robot arms to specified positions
- **📊 read_joint_positions** - Read current robot joint positions  
- **🎬 execute_sequence** - Execute predefined robot sequences
- **🎨 dispense_solution** - Dispense colored solutions with ML optimization
- **👁️ analyze_beaker_color** - Analyze solution colors using computer vision
