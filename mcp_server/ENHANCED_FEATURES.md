# Enhanced ALOHA-Lite MCP Server

## 🚀 New Features

The ALOHA-Lite MCP Server has been enhanced with automatic Playwright server management:

### ✨ Key Enhancements

1. **Automatic Subprocess Management**
   - Automatically starts the Playwright MCP server when needed
   - No need to manually start `playwright-mcp` beforehand
   - Process group management for proper cleanup

2. **Health Checking**
   - Continuous monitoring of Playwright server health
   - Automatic restart if the server becomes unresponsive
   - Configurable timeout and retry logic

3. **Graceful Shutdown**
   - Proper signal handling (SIGTERM, SIGINT)
   - Clean termination of child processes
   - Resource cleanup on exit

## 🔧 Configuration

### Environment Variables

```bash
# Playwright server WebSocket URL (default: ws://localhost:9010)
export PLAYWRIGHT_MCP_WS="ws://localhost:9010"

# Playwright server port (default: 9010)
export PLAYWRIGHT_MCP_PORT="9010"

# Startup timeout in seconds (default: 30)
export PLAYWRIGHT_STARTUP_TIMEOUT="30"
```

## 📖 Usage

### For Claude Desktop (MCP Mode)

```bash
cd /home/hafnium/aloha-lite/mcp_server
python main.py
```

The server will:
1. Start the Playwright MCP server automatically
2. Wait for it to become healthy
3. Begin handling MCP requests from Claude Desktop

### For Development/Testing (Web Mode)

```bash
cd /home/hafnium/aloha-lite/mcp_server
python main.py --web
```

### Testing the Enhanced Features

```bash
cd /home/hafnium/aloha-lite/mcp_server
python test_enhanced_mcp.py
```

## 🔍 Monitoring

### Logs

The enhanced server provides detailed logging:

```
🤖 ALOHA-Lite Enhanced MCP Server v2.0.0
📋 Features:
   • Automatic Playwright server management
   • Health checking and auto-restart
   • Graceful shutdown with cleanup
   • Live screenshot streaming
   • Playwright server port: 9010
   • Startup timeout: 30s

Starting Playwright MCP server on port 9010
Playwright server started with PID 12345
Playwright server health check passed
Playwright server is healthy and ready
```

### Health Status

The server continuously monitors the Playwright subprocess:
- Connection testing every request
- Automatic restart on failure
- Graceful degradation with error responses

## 🛠️ Troubleshooting

### Playwright Command Not Found

If you get "playwright-mcp command not found":

```bash
# Install playwright MCP server
npm install -g @playwright/mcp-server
# or
pip install playwright-mcp
```

### Port Already in Use

If port 9010 is in use:

```bash
# Use a different port
export PLAYWRIGHT_MCP_PORT="9011"
python main.py
```

### Startup Timeout

If the server takes too long to start:

```bash
# Increase timeout
export PLAYWRIGHT_STARTUP_TIMEOUT="60"
python main.py
```

## 🔄 Migration from Previous Version

The enhanced server is backward compatible. Simply replace the old server with the new one:

### Before (Manual)
```bash
# Terminal 1
playwright-mcp --port 9010

# Terminal 2  
python main.py
```

### After (Automatic)
```bash
# Single terminal
python main.py
```

## 📊 Process Management Details

### Startup Process
1. Check if Playwright server is already running
2. Start `playwright-mcp --port <PORT>` subprocess
3. Wait for WebSocket connection to be available
4. Perform health check with ping request
5. Mark as ready for MCP requests

### Health Monitoring
- Health check before each Playwright request
- Automatic restart on connection failure
- Exponential backoff for restart attempts

### Shutdown Process
1. Receive SIGTERM/SIGINT signal
2. Send SIGTERM to Playwright process group
3. Wait 5 seconds for graceful shutdown
4. Force kill if necessary
5. Clean up resources and exit

## 🎯 Benefits

- **Simplified deployment**: One command instead of two
- **Increased reliability**: Automatic recovery from failures
- **Better resource management**: Proper cleanup prevents orphaned processes
- **Enhanced debugging**: Detailed logging for troubleshooting
- **Production ready**: Signal handling for proper service management
