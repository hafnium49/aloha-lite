# Windows Troubleshooting Guide for ALOHA-Lite MCP Server

This guide addresses common Windows-specific issues with the enhanced MCP server.

## Fixed Issues in v2.0.0

### ✅ OS Error 3: "The specified path was not found"

**Problem**: The error `指定されたパスが見つかりません。 (os error 3)` occurs when starting the Playwright subprocess.

**Root Cause**: Windows subprocess execution requires proper executable path resolution and process group management.

**Fixed by**:
- ✅ Using `shutil.which()` for robust executable finding
- ✅ Adding `npx` fallback for global npm packages
- ✅ Proper Windows process group creation with `CREATE_NEW_PROCESS_GROUP`
- ✅ Better error logging with command details

## Installation Verification

### Check if playwright-mcp is properly installed:

```powershell
# Check if playwright-mcp is in PATH
where playwright-mcp

# Check npm global packages
npm list -g --depth=0 | findstr playwright

# Test playwright-mcp directly
playwright-mcp --help
```

### Expected output:
```
C:\Users\{username}\AppData\Roaming\npm\playwright-mcp.exe
```

## Common Windows Issues

### Issue 1: PATH not updated after npm install

**Symptoms**:
- `playwright-mcp` command not found
- Error "The specified path was not found"

**Solution**:
```powershell
# Refresh PATH in current session
$env:PATH = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Or restart PowerShell/Command Prompt
```

### Issue 2: npm global directory not in PATH

**Check global npm directory**:
```powershell
npm config get prefix
```

**Add to PATH if missing**:
```powershell
# Add to user PATH (replace {username})
$npmPath = "C:\Users\{username}\AppData\Roaming\npm"
$env:PATH += ";$npmPath"
```

### Issue 3: Node.js/npm not installed

**Install Node.js**:
1. Download from https://nodejs.org/
2. Use the Windows installer
3. Restart terminal after installation
4. Verify: `node --version` and `npm --version`

### Issue 4: Permission issues

**Run as Administrator** if you encounter permission errors during npm install:
```powershell
# Open PowerShell as Administrator, then:
npm install -g @anthropic-ai/playwright-mcp-server
```

## Debugging Steps

### 1. Environment Check
```powershell
# Check Node.js and npm
node --version
npm --version

# Check global npm packages
npm list -g --depth=0

# Check PATH environment variable
echo $env:PATH
```

### 2. Manual Playwright Test
```powershell
# Try to run playwright-mcp manually
playwright-mcp --help

# If not found, try with npx
npx playwright-mcp --help
```

### 3. MCP Server Startup Debug

The enhanced MCP server now shows detailed startup information:
- Platform details
- Executable paths found
- Available fallbacks

Look for these log messages when starting the server.

## Enhanced Error Handling

The v2.0.0 MCP server includes:

### Automatic Fallbacks
1. **Direct executable**: Tries `playwright-mcp` first
2. **NPX fallback**: Uses `npx playwright-mcp` if direct fails
3. **Clear error messages**: Shows exactly what's missing

### Better Process Management
- ✅ Windows-compatible process groups
- ✅ Proper subprocess termination
- ✅ Enhanced error logging
- ✅ Graceful cleanup on shutdown

### Startup Validation
- ✅ Executable availability check
- ✅ Path resolution logging  
- ✅ Platform detection
- ✅ Health monitoring

## Claude Desktop Configuration

Use the simplified configuration (no environment variables needed):

```json
{
  "mcpServers": {
    "aloha-playwright": {
      "command": "C:\\Users\\{username}\\.local\\bin\\uv.exe",
      "args": [
        "--directory",
        "C:\\Users\\{username}\\Documents\\git\\aloha-lite\\mcp_server",
        "run",
        "python",
        "main.py"
      ],
      "cwd": "C:\\Users\\{username}\\Documents\\git\\aloha-lite\\mcp_server"
    }
  }
}
```

## Verification

After the fixes, you should see:
1. ✅ No more "path not found" errors
2. ✅ Successful Playwright server startup
3. ✅ MCP tools available in Claude Desktop
4. ✅ Clean shutdown without errors

## Still Having Issues?

1. **Check the debug notebook**: Run `debug_windows_mcp.ipynb` for comprehensive diagnostics
2. **Verify installation**: `npm list -g @anthropic-ai/playwright-mcp-server`  
3. **Check logs**: Look at Claude Desktop logs for specific error details
4. **Try manual test**: Run `python main.py --web` for development mode testing

## Recovery Steps

If you still encounter issues:

```powershell
# 1. Reinstall playwright-mcp
npm uninstall -g @anthropic-ai/playwright-mcp-server
npm install -g @anthropic-ai/playwright-mcp-server

# 2. Refresh environment
refreshenv  # If using Chocolatey
# OR restart PowerShell

# 3. Verify installation
playwright-mcp --help

# 4. Test MCP server
cd path\to\aloha-lite\mcp_server
python main.py --web
```
