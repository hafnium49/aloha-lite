@echo off
echo 🔧 ALOHA-Lite MCP Server Environment Fix
echo.

cd /d "C:\Users\h_fujiwara\Documents\git\aloha-lite\mcp_server"

echo 📦 Installing dependencies with UV...
"C:\Users\h_fujiwara\.local\bin\uv.exe" sync

echo ➕ Adding requests package...
"C:\Users\h_fujiwara\.local\bin\uv.exe" add requests

echo ✅ Testing MCP server...
"C:\Users\h_fujiwara\.local\bin\uv.exe" run python --version

echo.
echo 🎯 Environment setup complete!
echo Now update your Claude Desktop configuration to use UV.
pause
