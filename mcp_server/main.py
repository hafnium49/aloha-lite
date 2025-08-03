"""
Playwright-backed MCP bridge for Claude Desktop

• Listens on /ws (JSON-RPC over WebSocket) for Claude
• Relays each call to a local Playwright MCP server (JSON-RPC over WebSocket)
• Provides a simple /health endpoint for probes
• Optional: live screenshot streaming over HTTP MJPEG and WebSocket
"""

import os
import json
import uuid
import logging
import asyncio
import base64
import io
import websockets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette.responses import StreamingResponse
from PIL import Image

# ───────────────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_bridge")

# Where the Playwright MCP server is listening (e.g. `playwright-mcp --port 9010`)
PLAYWRIGHT_MCP_WS = os.getenv("PLAYWRIGHT_MCP_WS", "ws://localhost:9010")

app = FastAPI(title="MCP Bridge (Playwright)", description="For Anthropic Claude Desktop")
connected_clients: set[WebSocket] = set()

# ────────────────────────────── Utilities ──────────────────────────────────────
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

# ───────────────────────────── WebSocket API ───────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Relay JSON-RPC commands from Claude to Playwright MCP."""
    await websocket.accept()
    connected_clients.add(websocket)
    await websocket.send_json({"status": "connected"})

    try:
        while True:
            text = await websocket.receive_text()
            try:
                cmd = json.loads(text)
                result = await call_playwright(cmd["method"], cmd.get("params"))
                await websocket.send_json({"status": "ok", "result": result})
            except Exception as exc:
                logger.exception("MCP call failed")
                await websocket.send_json({"status": "error", "message": str(exc)})
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    finally:
        connected_clients.discard(websocket)

# ──────────────────────────── Local launcher (dev only) ────────────────────────
if __name__ == "__main__":  # pragma: no cover
    import uvicorn
    uvicorn.run("mcp_server.main:app", host="0.0.0.0", port=8900)
