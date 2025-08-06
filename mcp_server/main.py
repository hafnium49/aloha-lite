"""
ALOHA-Lite MCP Server - Playwright Browser Automation Bridge

• Implements Model Context Protocol for Claude Desktop
• Relays browser automation commands to Playwright MCP server
• Provides live screenshot streaming capabilities
• Enables Claude to control robot through web interface only
"""

import os
import json
import sys
import uuid
import logging
import asyncio
import base64
import io
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

app = FastAPI(title="ALOHA-Lite MCP Server (Playwright)", 
              description="Browser automation bridge for Claude Desktop")
connected_clients: set[WebSocket] = set()

# ────────────────────────────── MCP Protocol Implementation ─────────────────────
class AlohaLitePlaywrightMCP:
    """Consolidated MCP server for Playwright browser automation only"""
    
    def __init__(self):
        self.playwright_ws_url = PLAYWRIGHT_MCP_WS
        
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
                    "name": "aloha-lite-playwright-mcp",
                    "version": "1.0.0",
                    "description": "ALOHA-Lite Playwright browser automation server"
                }
            }
        }
    
    async def handle_tools_list(self, request: Dict) -> Dict:
        """Forward tools list request to Playwright MCP"""
        try:
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

async def call_playwright(method: str, params: dict | None = None) -> dict:
    """Forward a single JSON-RPC 2.0 request to the Playwright MCP server."""
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
    result = await call_playwright("page.screenshot", {"fullPage": True, "type": "png"})
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
                result = await call_playwright(cmd["method"], cmd.get("params"))
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
    server = AlohaLitePlaywrightMCP()
    await server.run_stdio_server()

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
