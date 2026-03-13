import uuid

import pytest

from backend.app.api.deps import auth as auth_dep_module
from backend.app.core.config import Settings
from backend.app.external.auth_validator.client import ExternalAuthClient
from backend.app.main import app


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


@pytest.mark.usefixtures("test_client")
def test_meta_reports_debug_mode(monkeypatch, test_client):
    debug_settings = Settings(
        debug=True,
        debug_username="debug-user",
        db_user="wb",
        db_pass="wb",
        db_host="localhost",
        db_port=5432,
        db_name="wb_wrapper",
    )
    from backend.app.core.config import get_settings

    app.dependency_overrides[get_settings] = lambda: debug_settings
    try:
        response = test_client.get("/meta/endpoints")

        assert response.status_code == 200
        payload = response.json()
        assert payload["debug"] is True
        assert payload["defaultUsername"] == "debug-user"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_username_header_returns_debug_user_without_header(monkeypatch):
    debug_settings = Settings(
        debug=True,
        debug_username="debug-user",
        db_user="wb",
        db_pass="wb",
        db_host="localhost",
        db_port=5432,
        db_name="wb_wrapper",
    )
    monkeypatch.setattr(auth_dep_module, "get_settings", lambda: debug_settings)

    resolved = await auth_dep_module.get_username_header(None)

    assert resolved == "debug-user"
