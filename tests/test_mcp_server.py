import asyncio
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient

from mcp_server import main as mcp_main

client = TestClient(mcp_main.app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_handle_command_get(monkeypatch):
    class FakeResp:
        status_code = 200
        headers = {"content-type": "application/json"}

        def json(self):
            return {"hello": "world"}

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def get(self, url):
            return FakeResp()

        async def post(self, url, json=None):
            return FakeResp()

    monkeypatch.setattr(mcp_main.httpx, "AsyncClient", lambda *a, **kw: FakeClient())
    res = asyncio.run(mcp_main.handle_command({"endpoint": "/"}))
    assert res["payload"] == {"hello": "world"}


def test_proxy_frontend(monkeypatch):
    class FakeResp:
        status_code = 200
        headers = {"content-type": "text/html"}
        content = b"<html>ok</html>"

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def request(self, method, url, params=None, content=None, headers=None):
            return FakeResp()

    monkeypatch.setattr(mcp_main.httpx, "AsyncClient", lambda *a, **kw: FakeClient())
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.text == "<html>ok</html>"
