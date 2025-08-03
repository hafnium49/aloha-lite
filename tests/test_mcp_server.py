import os
import json
import asyncio
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient

from mcp_server import main as mcp_main

client = TestClient(mcp_main.app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_call_playwright(monkeypatch):
    class DummyWS:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def send(self, msg):
            self.sent = json.loads(msg)

        async def recv(self):
            return json.dumps({"result": {"echo": self.sent}})

    monkeypatch.setattr(mcp_main.websockets, "connect", lambda url: DummyWS())
    res = asyncio.run(mcp_main.call_playwright("page.test", {"foo": "bar"}))
    assert res["echo"]["method"] == "page.test"
    assert res["echo"]["params"] == {"foo": "bar"}
