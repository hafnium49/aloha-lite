"""
ALOHA-Lite MCP Server - Enhanced Playwright Browser Automation Bridge

• Implements Model Context Protocol for Claude Desktop
• Automatically starts and manages Playwright MCP server subprocess  
• Provides health checking and automatic restart capabilities
• Includes live screenshot streaming capabilities
• Enables Claude to control robot through web interface
• Graceful shutdown with proper cleanup

Environment Variables:
• PLAYWRIGHT_MCP_WS: WebSocket URL for Playwright server (default: ws://localhost:9010)
• PLAYWRIGHT_MCP_PORT: Port for Playwright server (default: 9010)
• PLAYWRIGHT_STARTUP_TIMEOUT: Startup timeout in seconds (default: 30)
"""

import os
import json
import sys
import uuid
import logging
import asyncio
import base64
import io
import subprocess
import signal
import time
import websockets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette.responses import StreamingResponse
from PIL import Image
from typing import Dict, Any, Optional

# ───────────────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, stream=sys.stderr,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("aloha-mcp-playwright")

# Where the Playwright MCP server is listening (e.g. `playwright-mcp --port 9010`)
PLAYWRIGHT_MCP_WS = os.getenv("PLAYWRIGHT_MCP_WS", "ws://localhost:9010")
PLAYWRIGHT_MCP_PORT = int(os.getenv("PLAYWRIGHT_MCP_PORT", "9010"))
PLAYWRIGHT_STARTUP_TIMEOUT = int(os.getenv("PLAYWRIGHT_STARTUP_TIMEOUT", "30"))

app = FastAPI(title="ALOHA-Lite MCP Server (Playwright)", 
              description="Browser automation bridge for Claude Desktop")
connected_clients: set[WebSocket] = set()

# Global process handle for Playwright server
playwright_process: Optional[subprocess.Popen] = None

# ────────────────────────────── Playwright Process Management ─────────────────────
async def start_playwright_server() -> bool:
    """Start the Playwright MCP server as a subprocess"""
    global playwright_process
    
    if playwright_process and playwright_process.poll() is None:
        logger.info("Playwright server already running")
        return True
    
    logger.info(f"Starting Playwright MCP server on port {PLAYWRIGHT_MCP_PORT}")
    
    try:
        # Try to start playwright-mcp command
        playwright_process = subprocess.Popen(
            ["playwright-mcp", "--port", str(PLAYWRIGHT_MCP_PORT)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid if os.name != 'nt' else None
        )
        
        logger.info(f"Playwright server started with PID {playwright_process.pid}")
        
        # Wait for server to be ready
        if await wait_for_playwright_health():
            logger.info("Playwright server is healthy and ready")
            return True
        else:
            logger.error("Playwright server failed to become healthy")
            await stop_playwright_server()
            return False
            
    except FileNotFoundError:
        logger.error("playwright-mcp command not found. Please install playwright MCP server.")
        return False
    except Exception as e:
        logger.error(f"Failed to start Playwright server: {e}")
        return False

async def wait_for_playwright_health() -> bool:
    """Wait for Playwright server to become healthy"""
    start_time = time.time()
    
    while time.time() - start_time < PLAYWRIGHT_STARTUP_TIMEOUT:
        try:
            # Try to connect and get a simple response
            async with websockets.connect(PLAYWRIGHT_MCP_WS, timeout=2) as ws:
                test_request = {
                    "jsonrpc": "2.0",
                    "id": "health-check",
                    "method": "ping"  # Simple ping to test connection
                }
                await ws.send(json.dumps(test_request))
                response = await asyncio.wait_for(ws.recv(), timeout=2)
                # If we get any response, the server is up
                logger.info("Playwright server health check passed")
                return True
        except Exception as e:
            logger.debug(f"Health check failed: {e}, retrying...")
            await asyncio.sleep(1)
    
    logger.error(f"Playwright server did not become healthy within {PLAYWRIGHT_STARTUP_TIMEOUT} seconds")
    return False

async def stop_playwright_server():
    """Stop the Playwright MCP server subprocess"""
    global playwright_process
    
    if playwright_process is None:
        return
    
    logger.info(f"Stopping Playwright server (PID: {playwright_process.pid})")
    
    try:
        if os.name == 'nt':  # Windows
            playwright_process.terminate()
        else:  # Unix-like systems
            # Send SIGTERM to the process group
            os.killpg(os.getpgid(playwright_process.pid), signal.SIGTERM)
        
        # Wait for graceful shutdown
        try:
            playwright_process.wait(timeout=5)
            logger.info("Playwright server stopped gracefully")
        except subprocess.TimeoutExpired:
            logger.warning("Playwright server did not stop gracefully, forcing kill")
            if os.name == 'nt':
                playwright_process.kill()
            else:
                os.killpg(os.getpgid(playwright_process.pid), signal.SIGKILL)
            playwright_process.wait()
            
    except Exception as e:
        logger.error(f"Error stopping Playwright server: {e}")
    finally:
        playwright_process = None

async def check_playwright_health() -> bool:
    """Check if Playwright server is still healthy"""
    try:
        async with websockets.connect(PLAYWRIGHT_MCP_WS, timeout=2) as ws:
            test_request = {
                "jsonrpc": "2.0", 
                "id": "health-check",
                "method": "ping"
            }
            await ws.send(json.dumps(test_request))
            await asyncio.wait_for(ws.recv(), timeout=2)
            return True
    except Exception:
        return False

def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(cleanup_and_exit())
    
    if os.name != 'nt':  # Unix-like systems
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

async def cleanup_and_exit():
    """Cleanup resources and exit gracefully"""
    logger.info("Performing cleanup...")
    await stop_playwright_server()
    logger.info("Cleanup completed")
    sys.exit(0)

# ────────────────────────────── MCP Protocol Implementation ─────────────────────
class AlohaLitePlaywrightMCP:
    """Consolidated MCP server for Playwright browser automation with process management"""
    
    def __init__(self):
        self.playwright_ws_url = PLAYWRIGHT_MCP_WS
        self.playwright_started = False
        
    async def ensure_playwright_running(self) -> bool:
        """Ensure Playwright server is running, start if necessary"""
        if not self.playwright_started:
            logger.info("Initializing Playwright server...")
            if await start_playwright_server():
                self.playwright_started = True
                return True
            else:
                return False
        
        # Check if it's still healthy
        if not await check_playwright_health():
            logger.warning("Playwright server appears to be down, attempting restart...")
            self.playwright_started = False
            return await self.ensure_playwright_running()
        
        return True
        
    async def handle_initialize(self, request: Dict) -> Dict:
        """Handle MCP initialize request"""
        logger.info("Handling initialize request")
        
        return {
            "jsonrpc": "2.0",
            "id": request["id"],
            "result": {
                "protocolVersion": "2025-06-18", 
                "capabilities": {
                    "tools": {},
                    "resources": {}
                },
                "serverInfo": {
                    "name": "aloha-lite-playwright-mcp-enhanced",
                    "version": "2.0.0",
                    "description": "ALOHA-Lite Enhanced Playwright browser automation server with process management"
                }
            }
        }
    
    async def handle_tools_list(self, request: Dict) -> Dict:
        """Forward tools list request to Playwright MCP"""
        try:
            if not await self.ensure_playwright_running():
                raise RuntimeError("Playwright server is not available")
                
            result = await self.call_playwright("tools/list")
            return {
                "jsonrpc": "2.0",
                "id": request["id"], 
                "result": result
            }
        except Exception as e:
            logger.error(f"Failed to get tools list: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request["id"],
                "result": {"tools": []}
            }
    
    async def handle_tool_call(self, request: Dict) -> Dict:
        """Forward tool call to Playwright MCP"""
        try:
            if not await self.ensure_playwright_running():
                raise RuntimeError("Playwright server is not available")
                
            tool_name = request["params"]["name"]
            arguments = request["params"].get("arguments", {})
            
            logger.info(f"Forwarding Playwright tool: {tool_name}")
            
            result = await self.call_playwright("tools/call", {
                "name": tool_name,
                "arguments": arguments
            })
            
            return {
                "jsonrpc": "2.0",
                "id": request["id"],
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return {
                "jsonrpc": "2.0", 
                "id": request["id"],
                "error": {
                    "code": -32603,
                    "message": f"Tool execution failed: {str(e)}"
                }
            }

    async def call_playwright(self, method: str, params: dict | None = None) -> dict:
        """Forward a single JSON-RPC 2.0 request to the Playwright MCP server."""
        request_id = str(uuid.uuid4())
        payload = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params or {}}

        async with websockets.connect(self.playwright_ws_url) as ws:
            await ws.send(json.dumps(payload))
            raw = await ws.recv()

        response = json.loads(raw)
        if "error" in response:
            raise RuntimeError(response["error"])
        return response.get("result")

    
    async def handle_request(self, request: Dict) -> Optional[Dict]:
        """Route MCP requests to appropriate handlers"""
        method = request.get("method")
        
        if method == "initialize":
            return await self.handle_initialize(request)
        elif method == "tools/list":
            return await self.handle_tools_list(request)
        elif method == "tools/call": 
            return await self.handle_tool_call(request)
        elif method == "notifications/initialized":
            logger.info("Client initialized")
            return None
        else:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
    
    async def run_stdio_server(self):
        """Run MCP server over stdio for Claude Desktop"""
        logger.info("ALOHA-Lite Playwright MCP Server starting...")
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers()
        
        try:
            while True:
                try:
                    line = sys.stdin.readline()
                    if not line:
                        break
                        
                    line = line.strip()
                    if not line:
                        continue
                    
                    request = json.loads(line)
                    logger.info(f"Received request: {request.get('method', 'unknown')}")
                    
                    response = await self.handle_request(request)
                    
                    if response:
                        print(json.dumps(response), flush=True)
                        logger.info(f"Sent response for: {request.get('method', 'unknown')}")
                        
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": "Parse error"
                        }
                    }
                    print(json.dumps(error_response), flush=True)
                except Exception as e:
                    logger.error(f"Server error: {e}")
                    break
        finally:
            logger.info("Shutting down server...")
            await stop_playwright_server()

async def call_playwright_global(method: str, params: dict | None = None) -> dict:
    """Global function to forward a single JSON-RPC 2.0 request to the Playwright MCP server."""
    # Ensure Playwright is running
    if not await check_playwright_health():
        if not await start_playwright_server():
            raise RuntimeError("Cannot connect to Playwright server")
    
    request_id = str(uuid.uuid4())
    payload = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params or {}}

    async with websockets.connect(PLAYWRIGHT_MCP_WS) as ws:
        await ws.send(json.dumps(payload))
        raw = await ws.recv()

    response = json.loads(raw)
    if "error" in response:
        raise RuntimeError(response["error"])
    return response.get("result")


async def grab_png() -> bytes:
    """Ask Playwright MCP for a full-page PNG screenshot."""
    result = await call_playwright_global("page.screenshot", {"fullPage": True, "type": "png"})
    return base64.b64decode(result["data"])

BOUNDARY = b"--frame"

async def mjpeg_frame_generator():
    while True:
        try:
            png_bytes = await grab_png()
            jpg_bytes_io = io.BytesIO()
            Image.open(io.BytesIO(png_bytes)).save(jpg_bytes_io, format="JPEG", quality=75)
            payload = (
                BOUNDARY + b"\r\n"
                + b"Content-Type: image/jpeg\r\n\r\n"
                + jpg_bytes_io.getvalue() + b"\r\n"
            )
            yield payload
        except Exception as exc:
            logger.error("Stream error: %s", exc)
            await asyncio.sleep(1.0)
        await asyncio.sleep(0.5)

# ────────────────────────────── Health probe ───────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok"}

# ───────────────────────────── Streaming routes ───────────────────────────────
@app.get("/stream.mjpeg")
async def stream_mjpeg():
    headers = {
        "Age": "0",
        "Cache-Control": "no-cache, private",
        "Pragma": "no-cache",
        "Content-Type": "multipart/x-mixed-replace; boundary=frame",
    }
    return StreamingResponse(mjpeg_frame_generator(), headers=headers)

@app.websocket("/stream_ws")
async def stream_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            try:
                png_bytes = await grab_png()
                b64 = base64.b64encode(png_bytes).decode()
                await websocket.send_json({"png_base64": b64})
            except Exception as exc:
                await websocket.send_json({"error": str(exc)})
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        pass

# ────────────────────────────── WebSocket API (Legacy - for testing) ──────────────
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Legacy WebSocket endpoint - use stdio for Claude Desktop"""
    await websocket.accept()
    connected_clients.add(websocket)
    await websocket.send_json({"status": "connected", "note": "Use stdio for Claude Desktop"})

    try:
        while True:
            text = await websocket.receive_text()
            try:
                cmd = json.loads(text)
                result = await call_playwright_global(cmd["method"], cmd.get("params"))
                await websocket.send_json({"status": "ok", "result": result})
            except Exception as exc:
                logger.exception("Playwright call failed")
                await websocket.send_json({"status": "error", "message": str(exc)})
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    finally:
        connected_clients.discard(websocket)

# ──────────────────────────── Main Entry Points ────────────────────────────────
async def main_mcp():
    """Main entry point for MCP server (stdio mode for Claude Desktop)"""
    logger.info("🤖 ALOHA-Lite Enhanced MCP Server v2.0.0")
    logger.info("📋 Features:")
    logger.info("   • Automatic Playwright server management")
    logger.info("   • Health checking and auto-restart")
    logger.info("   • Graceful shutdown with cleanup")
    logger.info("   • Live screenshot streaming")
    logger.info(f"   • Playwright server port: {PLAYWRIGHT_MCP_PORT}")
    logger.info(f"   • Startup timeout: {PLAYWRIGHT_STARTUP_TIMEOUT}s")
    
    server = AlohaLitePlaywrightMCP()
    try:
        await server.run_stdio_server()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        await cleanup_and_exit()

def main_web():
    """Web server entry point (development/testing only)"""
    try:
        import uvicorn
        logger.info("Starting web server mode (development only)")
        uvicorn.run("main:app", host="0.0.0.0", port=8900, log_level="info")
    except ImportError:
        logger.error("uvicorn not available for web server mode")
        sys.exit(1)

def main():
    """Main entry point - defaults to MCP stdio mode"""
    # Check if running in web server mode
    if len(sys.argv) > 1 and sys.argv[1] == "--web":
        main_web()
    else:
        # Default: MCP stdio mode for Claude Desktop
        asyncio.run(main_mcp())


if __name__ == "__main__":
    main()
