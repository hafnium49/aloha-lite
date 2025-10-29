# SO-101 MCP Server - Quick Start Guide

Get your SO-101 robot controlled by Claude Desktop in 5 minutes.

## Step 1: Install UV Package Manager

### macOS/Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows (PowerShell)
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify installation:
```bash
uv --version
```

## Step 2: Install Dependencies

```bash
cd /home/hafnium/aloha-lite/so101_mcp_server
uv sync
```

This installs:
- `mcp[cli]==1.10.0` - MCP SDK with CLI tools
- `requests>=2.31.0` - HTTP client
- `pillow>=10.0.0` - Image processing

## Step 3: Start Phosphobot Server

The SO-101 MCP server requires Phosphobot to be running:

```bash
cd /home/hafnium/aloha-lite/phosphobot
python -m uvicorn phosphobot.server:app --host 0.0.0.0 --port 80
```

**Keep this terminal open!**

## Step 4: Test MCP Server

### Option A: Interactive Inspector (Recommended)

Open MCP inspector in your browser:

```bash
cd /home/hafnium/aloha-lite/so101_mcp_server
uv run mcp dev server.py
```

This opens `http://localhost:5173` where you can:
- View all 15 MCP tools
- Test tool execution interactively
- See request/response JSON
- Debug before deploying to Claude

### Option B: Test Suite

Run automated tests:

```bash
python test_mcp_server.py
```

Expected output:
```
🧪 Testing configuration loading...
  • Sequences loaded: 21
  ✅ All 21 sequences loaded
  • Robot arms configured: 2
    - Left arm: robot_id=2, device_id=5A68011529
    - Right arm: robot_id=3, device_id=5A68009540

🧪 Testing Phosphobot client...
  • Base URL: http://localhost:80
  ✅ Phosphobot server connected

✅ Test suite completed
```

## Step 5: Install to Claude Desktop

### Option A: Automatic Installation (Easiest)

```bash
uv run mcp install server.py
```

This automatically:
1. Detects your Claude Desktop config location
2. Adds the MCP server configuration
3. Shows confirmation message

### Option B: Manual Installation

1. **Locate Claude Desktop config file:**

   - **macOS:** `~/.claude/claude_desktop_config.json`
   - **Linux:** `~/.config/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

2. **Add MCP server configuration:**

   Open the config file and add:

   ```json
   {
     "mcpServers": {
       "so101-robot": {
         "command": "uv",
         "args": [
           "--directory",
           "/home/hafnium/aloha-lite/so101_mcp_server",
           "run",
           "python",
           "server.py"
         ],
         "cwd": "/home/hafnium/aloha-lite/so101_mcp_server"
       }
     }
   }
   ```

   **Windows users:** Use full paths like `C:\\Users\\username\\aloha-lite\\so101_mcp_server`

3. **Save and restart Claude Desktop**

## Step 6: Verify in Claude Desktop

1. **Open Claude Desktop**
2. **Start new conversation**
3. **Look for MCP indicator** - You should see a tool icon or "so101-robot" indicator
4. **Test with a simple command:**

   > "What's the robot configuration?"

   Claude should call `get_robot_config()` and show you the robot arm details.

## Step 7: Test Robot Control

Try these Claude prompts:

### List Available Sequences
> "What robot sequences are available?"

### Execute a Sequence
> "Run the full laboratory procedure with smooth movements"

### Direct Control
> "Initialize the left arm to safe position"

### Camera Capture
> "Show me what the robot camera sees"

### Emergency Stop
> "Emergency stop the robot!"

## Troubleshooting

### "Cannot connect to Phosphobot server"

**Symptom:** Error messages about connection refused on port 80

**Solution:** Start Phosphobot server:
```bash
cd /home/hafnium/aloha-lite/phosphobot
python -m uvicorn phosphobot.server:app --host 0.0.0.0 --port 80
```

### "MCP server not appearing in Claude Desktop"

**Solutions:**
1. **Restart Claude Desktop completely** (quit and reopen)
2. **Check config file location:**
   ```bash
   # macOS/Linux
   cat ~/.claude/claude_desktop_config.json

   # Windows
   type %APPDATA%\Claude\claude_desktop_config.json
   ```
3. **Verify UV in PATH:**
   ```bash
   which uv  # macOS/Linux
   where uv  # Windows
   ```
4. **Check Claude Desktop logs** (look for MCP errors)

### "No sequences loaded"

**Symptom:** `list_sequences()` returns 0 sequences

**Solution:** Verify config files exist:
```bash
ls -l /home/hafnium/aloha-lite/temp_rules/sequential_sequences.json
ls -l /home/hafnium/aloha-lite/temp_rules/robot_arm_config.json
```

### "Permission denied on port 80"

**Symptom:** Phosphobot fails to start on port 80

**Solutions:**
1. **Use sudo (Linux/macOS):**
   ```bash
   sudo python -m uvicorn phosphobot.server:app --host 0.0.0.0 --port 80
   ```

2. **Change port (if port 80 unavailable):**
   ```bash
   python -m uvicorn phosphobot.server:app --host 0.0.0.0 --port 8080
   ```

   Then set environment variable:
   ```bash
   export PHOSPHOBOT_URL="http://localhost:8080"
   ```

### "Camera capture failed"

**Solution:** Test camera directly:
```bash
curl http://localhost:80/frames
```

If this fails, check camera connections and permissions.

## Next Steps

### Advanced Usage

1. **Read the full README:** [README.md](README.md)
2. **Explore all 21 sequences:** [Sequential Sequences](../temp_rules/sequential_sequences.json)
3. **Learn about special functions:** Squeeze, await, camera, beaker analysis
4. **Customize sequences:** Edit JSON files in `temp_rules/`

### Integration with Other Services

The SO-101 MCP server can be used alongside:
- **Vision Processing Service** (port 8003) - For beaker color analysis
- **Frontend ML Service** (port 8002) - For ML optimization
- **Robot Control Service** (port 8001) - For high-level procedures

### Development

To modify or extend the MCP server:

1. **Edit `server.py`** - Add new tools or modify existing ones
2. **Test changes:**
   ```bash
   uv run mcp dev server.py
   ```
3. **Run test suite:**
   ```bash
   python test_mcp_server.py
   ```
4. **Restart Claude Desktop** to load changes

## Example Conversation

Here's a sample conversation with Claude Desktop:

**You:** "What robot sequences are available?"

**Claude:** *Calls `list_sequences()` tool*
> I can see 21 predefined sequences available. Here are some key ones:
> - full_lab_procedure: Complete laboratory procedure
> - multi_color_dispensing_workflow: Red, yellow, blue solution dispensing
> - pick_paper_workflow: Bilateral paper manipulation
> - calibration_red_solution: Red solution calibration
>
> Would you like me to execute any of these sequences?

**You:** "Run the full lab procedure with smooth movements"

**Claude:** *Calls `execute_sequence("full_lab_procedure", smooth=True)` tool*
> I'll execute the full laboratory procedure with smooth trajectory planning.
> This sequence includes:
> 1. Move to standoff position
> 2. Move to dispensing position
> 3. Return to standoff position
>
> Execution started...

**You:** "Show me what the camera sees"

**Claude:** *Calls `capture_camera_frame(camera_id=0)` tool*
> Here's the current view from camera 0:
> [Image displayed in chat]

**You:** "Emergency stop!"

**Claude:** *Calls `emergency_stop()` tool*
> 🛑 EMERGENCY STOP ACTIVATED - All motors disabled (freewheel mode)
> The robot is now safe to manually manipulate.

## Command Reference

### Installation & Setup
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
cd so101_mcp_server && uv sync

# Start Phosphobot
cd phosphobot && python -m uvicorn phosphobot.server:app --port 80
```

### Testing
```bash
# Interactive inspector
uv run mcp dev server.py

# Test suite
python test_mcp_server.py

# Manual test
uv run python server.py
```

### Installation
```bash
# Automatic
uv run mcp install server.py

# Manual: Edit claude_desktop_config.json
```

### Maintenance
```bash
# Update dependencies
uv sync

# View config
cat ~/.claude/claude_desktop_config.json

# Check logs
# (Claude Desktop menu → View Logs)
```

## Support

**Need help?**
1. Check [README.md](README.md) for detailed documentation
2. Run `python test_mcp_server.py` to diagnose issues
3. Test with `uv run mcp dev server.py` for interactive debugging
4. Check Claude Desktop logs for MCP errors
5. Verify Phosphobot is running: `curl http://localhost:80/health`

---

## Credits & References

This MCP server implementation is based on patterns from:
- **[phospho-app/phospho-mcp-server](https://github.com/phospho-app/phospho-mcp-server)** - Reference implementation for FastMCP patterns
- **[FastMCP Framework](https://github.com/jlowin/fastmcp)** - Simplified MCP server framework
- **[Model Context Protocol](https://modelcontextprotocol.io/)** - MCP protocol specification

---

**Ready to go!** Start controlling your SO-101 robot with natural language through Claude Desktop.

For advanced features and customization, see [README.md](README.md).
