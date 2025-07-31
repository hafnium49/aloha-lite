import os
import json
import logging
import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://frontend")

app = FastAPI(title="MCP Server", description="Bridge for Anthropic Claude Desktop")

connected_clients = set()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    await websocket.send_json({"status": "connected"})
    try:
        while True:
            msg = await websocket.receive_text()
            try:
                cmd = json.loads(msg)
            except json.JSONDecodeError:
                await websocket.send_json({"error": "invalid json"})
                continue
            response = await handle_command(cmd)
            await websocket.send_json(response)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    finally:
        connected_clients.discard(websocket)

async def handle_command(cmd: dict):
    method = cmd.get("method", "get").lower()
    endpoint = cmd.get("endpoint", "/")
    data = cmd.get("data")
    url = f"{FRONTEND_URL}{endpoint}"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            if method == "post":
                resp = await client.post(url, json=data)
            else:
                resp = await client.get(url)
            content_type = resp.headers.get("content-type", "")
            if content_type.startswith("application/json"):
                payload = resp.json()
            else:
                payload = resp.text
            return {"status": "ok", "code": resp.status_code, "payload": payload}
        except Exception as e:
            logger.error(f"Error contacting frontend: {e}")
            return {"status": "error", "message": str(e)}


# Uvicorn entry point is ``mcp_server.main:app``
if __name__ == "__main__":  # pragma: no cover - convenience for manual runs
    import uvicorn
    uvicorn.run("mcp_server.main:app", host="0.0.0.0", port=8900)
