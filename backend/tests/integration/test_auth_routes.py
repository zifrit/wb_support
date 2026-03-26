import uuid

import pytest

from backend.app.api.deps import auth as auth_dep_module
from backend.app.api.deps.services import get_auth_service
from backend.app.core.config import Settings
from backend.app.main import app


@pytest.mark.usefixtures("test_client")
def test_auth_login_and_verify(test_client):
    class FakeAuthService:
        def __init__(self):
            self.saved_tokens = {}

        async def login(self, username: str):
            return True

        async def verify_saved_token(self, username: str, code: str | None = None):
            if code:
                self.saved_tokens[username] = f"token-{username}-{code}"
                return True
            return username in self.saved_tokens

        async def check_saved_token(self, username: str):
            return username in self.saved_tokens

    service = FakeAuthService()
    app.dependency_overrides[get_auth_service] = lambda: service

    username = f"user-{uuid.uuid4().hex[:8]}"
    try:
        login_resp = test_client.post("/auth/login", json={"username": username})
        assert login_resp.status_code == 200
        assert login_resp.json()["ok"] is True

        verify_resp = test_client.post("/auth/verify", json={"username": username, "code": "1234"})
        assert verify_resp.status_code == 200
        body = verify_resp.json()
        assert body["ok"] is True
        assert body["valid"] is True

        check_resp = test_client.post("/auth/check", json={"username": username})
        assert check_resp.status_code == 200
        check_body = check_resp.json()
        assert check_body["ok"] is True
        assert check_body["valid"] is True
    finally:
        app.dependency_overrides.clear()


@pytest.mark.usefixtures("test_client")
def test_auth_check_requires_saved_token(test_client):
    class MissingTokenService:
        async def check_saved_token(self, username: str):
            from backend.app.core.exceptions import CredentialsNotFound

            raise CredentialsNotFound()

    app.dependency_overrides[get_auth_service] = lambda: MissingTokenService()
    try:
        response = test_client.post("/auth/check", json={"username": f"user-{uuid.uuid4().hex[:8]}"})

        assert response.status_code == 401
        payload = response.json()
        assert payload["ok"] is False
        assert payload["error"]["code"] == "USER_TOKEN_NOT_FOUND"
    finally:
        app.dependency_overrides.clear()


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
    class DummyRequest:
        url = "http://testserver/wb/orders"

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

    resolved = await auth_dep_module.get_username_header(DummyRequest(), None)

    assert resolved == "debug-user"
