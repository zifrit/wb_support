import uuid

import httpx
import pytest

from backend.app.external.auth_validator.client import ExternalAuthClient
from backend.app.external.wb_client.transport import HttpxTransport


@pytest.mark.usefixtures("test_client")
def test_wb_adverts_uses_db_token_in_authorization(monkeypatch, test_client):
    captured = {"headers": None}

    async def fake_issue(self, username: str):
        return f"db-token-{username}"

    async def fake_verify(self, token: str):
        return True

    async def fake_send(self, method, url, headers, query_params=None, payload=None):
        captured["headers"] = headers
        return httpx.Response(200, json={"ok": True, "echo": query_params or {}})

    monkeypatch.setattr(ExternalAuthClient, "issue_token", fake_issue)
    monkeypatch.setattr(ExternalAuthClient, "verify_token", fake_verify)
    monkeypatch.setattr(HttpxTransport, "send", fake_send)

    username = f"user-{uuid.uuid4().hex[:8]}"
    test_client.post("/auth/login", json={"username": username})

    response = test_client.get("/wb/adverts", params={"ids": "1,2"}, headers={"X-Username": username})

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert captured["headers"]["Authorization"] == f"db-token-{username}"
    assert captured["headers"]["User-Agent"] == "wbas_xway"


@pytest.mark.usefixtures("test_client")
def test_wb_401_triggers_refresh_and_retry(monkeypatch, test_client):
    attempts = {"send": 0, "issue": 0}

    async def fake_issue(self, username: str):
        attempts["issue"] += 1
        return f"db-token-{username}-{attempts['issue']}"

    async def fake_verify(self, token: str):
        return True

    async def fake_send(self, method, url, headers, query_params=None, payload=None):
        attempts["send"] += 1
        if attempts["send"] == 1:
            return httpx.Response(401, json={"message": "expired"})
        return httpx.Response(200, json={"data": "ok"})

    monkeypatch.setattr(ExternalAuthClient, "issue_token", fake_issue)
    monkeypatch.setattr(ExternalAuthClient, "verify_token", fake_verify)
    monkeypatch.setattr(HttpxTransport, "send", fake_send)

    username = f"user-{uuid.uuid4().hex[:8]}"
    test_client.post("/auth/login", json={"username": username})

    response = test_client.get("/wb/orders", params={"dateFrom": "2026-03-01"}, headers={"X-Username": username})

    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert attempts["send"] == 2
    assert attempts["issue"] == 2
