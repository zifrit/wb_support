import uuid

import httpx
import pytest

from backend.app.external.auth_validator.client import ExternalAuthClient
from backend.app.external.wb_client.transport import HttpxTransport
from backend.app.repositories.adv.pg import AdvPgClient


@pytest.mark.usefixtures("test_client")
def test_wb_adverts_uses_db_token_in_authorization(monkeypatch, test_client):
    captured = {"headers": None}

    async def fake_send_code(self, username: str):
        return True

    async def fake_verify_code(self, username: str, code: str):
        return f"db-token-{username}"

    async def fake_verify(self, token: str):
        return True

    async def fake_get_shop_token(self, shop_id: int):
        assert shop_id == 10
        return f"db-token-{username}"

    async def fake_send(self, method, url, headers, query_params=None, payload=None):
        captured["headers"] = headers
        captured["query_params"] = query_params
        captured["payload"] = payload
        return httpx.Response(200, json={"ok": True, "echo": query_params or payload or {}})

    monkeypatch.setattr(ExternalAuthClient, "send_code", fake_send_code)
    monkeypatch.setattr(ExternalAuthClient, "verify_code", fake_verify_code)
    monkeypatch.setattr(ExternalAuthClient, "verify_token", fake_verify)
    monkeypatch.setattr(HttpxTransport, "send", fake_send)
    username = f"user-{uuid.uuid4().hex[:8]}"
    monkeypatch.setattr(AdvPgClient, "get_shop_token", fake_get_shop_token)
    test_client.post("/auth/login", json={"username": username})
    test_client.post("/auth/verify", json={"username": username, "code": "1234"})

    response = test_client.post("/wb/adverts", json={"shop_id": 10, "ids": "1,2"}, headers={"X-Username": username})

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert captured["headers"]["Authorization"] == f"db-token-{username}"
    assert captured["headers"]["user-agent"] == "wbas_xway"
    assert captured["query_params"] == {"ids": "1,2"}
    assert captured["payload"] is None


@pytest.mark.usefixtures("test_client")
def test_wb_401_requires_relogin(monkeypatch, test_client):
    attempts = {"send": 0}

    async def fake_send_code(self, username: str):
        return True

    async def fake_verify_code(self, username: str, code: str):
        return f"db-token-{username}"

    async def fake_verify(self, token: str):
        return True

    async def fake_get_shop_token(self, shop_id: int):
        assert shop_id == 10
        return f"db-token-{username}"

    async def fake_send(self, method, url, headers, query_params=None, payload=None):
        attempts["send"] += 1
        return httpx.Response(401, json={"message": "expired"})

    monkeypatch.setattr(ExternalAuthClient, "send_code", fake_send_code)
    monkeypatch.setattr(ExternalAuthClient, "verify_code", fake_verify_code)
    monkeypatch.setattr(ExternalAuthClient, "verify_token", fake_verify)
    monkeypatch.setattr(HttpxTransport, "send", fake_send)

    username = f"user-{uuid.uuid4().hex[:8]}"
    monkeypatch.setattr(AdvPgClient, "get_shop_token", fake_get_shop_token)
    test_client.post("/auth/login", json={"username": username})
    test_client.post("/auth/verify", json={"username": username, "code": "1234"})

    response = test_client.post("/wb/orders", json={"shop_id": 10, "dateFrom": "2026-03-01"}, headers={"X-Username": username})

    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Stored token was rejected by WB. Re-login is required"
    assert attempts["send"] == 1


@pytest.mark.usefixtures("test_client")
def test_wb_returns_422_when_shop_id_is_missing(monkeypatch, test_client):
    async def fake_send_code(self, username: str):
        return True

    async def fake_verify_code(self, username: str, code: str):
        return f"db-token-{username}"

    monkeypatch.setattr(ExternalAuthClient, "send_code", fake_send_code)
    monkeypatch.setattr(ExternalAuthClient, "verify_code", fake_verify_code)

    username = f"user-{uuid.uuid4().hex[:8]}"
    test_client.post("/auth/login", json={"username": username})
    test_client.post("/auth/verify", json={"username": username, "code": "1234"})

    response = test_client.post("/wb/adverts", json={"ids": "1,2"}, headers={"X-Username": username})

    assert response.status_code == 422
