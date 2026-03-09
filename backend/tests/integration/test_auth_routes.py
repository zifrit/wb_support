import uuid

import pytest

from backend.app.external.auth_validator.client import ExternalAuthClient


@pytest.mark.usefixtures("test_client")
def test_auth_login_and_verify(monkeypatch, test_client):
    async def fake_issue(self, username: str):
        return f"token-{username}"

    async def fake_verify(self, token: str):
        return token.startswith("token-")

    monkeypatch.setattr(ExternalAuthClient, "issue_token", fake_issue)
    monkeypatch.setattr(ExternalAuthClient, "verify_token", fake_verify)

    username = f"user-{uuid.uuid4().hex[:8]}"

    login_resp = test_client.post("/auth/login", json={"username": username})
    assert login_resp.status_code == 200
    assert login_resp.json()["ok"] is True

    verify_resp = test_client.get("/auth/verify", headers={"X-Username": username})
    assert verify_resp.status_code == 200
    body = verify_resp.json()
    assert body["ok"] is True
    assert body["valid"] is True
