import uuid

import pytest

from backend.app.api.deps import auth as auth_dep_module
from backend.app.core.config import Settings
from backend.app.external.auth_validator.client import ExternalAuthClient
from backend.app.main import app


@pytest.mark.usefixtures("test_client")
def test_auth_login_and_verify(monkeypatch, test_client):
    async def fake_send_code(self, username: str):
        return True

    async def fake_verify_code(self, username: str, code: str):
        return f"token-{username}-{code}"

    monkeypatch.setattr(ExternalAuthClient, "send_code", fake_send_code)
    monkeypatch.setattr(ExternalAuthClient, "verify_code", fake_verify_code)

    username = f"user-{uuid.uuid4().hex[:8]}"

    login_resp = test_client.post("/auth/login", json={"username": username})
    assert login_resp.status_code == 200
    assert login_resp.json()["ok"] is True

    verify_resp = test_client.post("/auth/verify", json={"username": username, "code": "1234"})
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
        config_response = test_client.get("/meta/config")
        assert config_response.status_code == 200
        config_payload = config_response.json()
        assert config_payload["debug"] is True
        assert config_payload["defaultUsername"] == "debug-user"

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
