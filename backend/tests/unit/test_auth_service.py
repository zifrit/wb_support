import pytest

from backend.app.core.config import Settings
from backend.app.core.exceptions import AuthorizationError, CredentialsNotFound
from backend.app.services.auth_service import AuthService


class FakeTokenRow:
    def __init__(self, username: str, token: str):
        self.username = username
        self.token = token


class FakeRepo:
    def __init__(self):
        self.storage = {}

    async def get_by_username(self, username: str):
        token = self.storage.get(username)
        if not token:
            return None
        return FakeTokenRow(username=username, token=token)

    async def upsert(self, username: str, token: str, refreshed: bool = False):
        self.storage[username] = token
        return FakeTokenRow(username=username, token=token)

    async def mark_verified(self, username: str):
        return None

    async def delete(self, username: str):
        self.storage.pop(username, None)


class FakeAuthClient:
    def __init__(self):
        self.sent = []
        self.invalid = set()

    async def send_code(self, username: str) -> bool:
        self.sent.append(username)
        return True

    async def verify_code(self, username: str, code: str) -> str:
        return f"token-{username}-{code}"

    async def verify_token(self, token: str) -> bool:
        return token not in self.invalid


@pytest.mark.asyncio
async def test_login_sends_otp_without_storing_token():
    repo = FakeRepo()
    auth_client = FakeAuthClient()
    settings = Settings(db_user="wb", db_pass="wb", db_host="localhost", db_port=5432, db_name="wb_wrapper")
    service = AuthService(auth_client=auth_client, repository=repo, settings=settings)

    result = await service.login("alice")

    assert result is True
    assert auth_client.sent == ["alice"]
    assert repo.storage == {}


@pytest.mark.asyncio
async def test_verify_code_stores_token():
    repo = FakeRepo()
    auth_client = FakeAuthClient()
    settings = Settings(db_user="wb", db_pass="wb", db_host="localhost", db_port=5432, db_name="wb_wrapper")
    service = AuthService(auth_client=auth_client, repository=repo, settings=settings)

    result = await service.verify_saved_token("alice", code="1234")

    assert result is True
    assert repo.storage["alice"] == "token-alice-1234"


@pytest.mark.asyncio
async def test_resolve_missing_token_raises():
    settings = Settings(db_user="wb", db_pass="wb", db_host="localhost", db_port=5432, db_name="wb_wrapper")
    service = AuthService(auth_client=FakeAuthClient(), repository=FakeRepo(), settings=settings)

    with pytest.raises(CredentialsNotFound):
        await service.resolve_token_for_wb("alice")


@pytest.mark.asyncio
async def test_invalid_saved_token_requires_relogin():
    repo = FakeRepo()
    auth_client = FakeAuthClient()
    settings = Settings(db_user="wb", db_pass="wb", db_host="localhost", db_port=5432, db_name="wb_wrapper")
    service = AuthService(auth_client=auth_client, repository=repo, settings=settings)

    first = await auth_client.verify_code("alice", "1234")
    await repo.upsert("alice", first)
    auth_client.invalid.add(first)

    with pytest.raises(AuthorizationError):
        await service.resolve_token_for_wb("alice")
    assert repo.storage == {}


@pytest.mark.asyncio
async def test_admin_bypass_skips_external_calls():
    class StrictAuthClient(FakeAuthClient):
        async def send_code(self, username: str) -> bool:
            raise AssertionError("send_code must not be called for admin")

        async def verify_code(self, username: str, code: str) -> str:
            raise AssertionError("verify_code must not be called for admin")

        async def verify_token(self, token: str) -> bool:
            raise AssertionError("verify_token must not be called for admin")

    settings = Settings(
        admin_username="admin",
        ADMIN_AUTHORIZATION_TOKEN="admin-fixed-token",
        db_user="wb",
        db_pass="wb",
        db_host="localhost",
        db_port=5432,
        db_name="wb_wrapper",
    )
    service = AuthService(auth_client=StrictAuthClient(), repository=FakeRepo(), settings=settings)

    assert await service.login("admin") is True
    assert await service.verify_saved_token("admin", code="1234") is True
    assert await service.resolve_token_for_wb("admin") == "admin-fixed-token"


@pytest.mark.asyncio
async def test_debug_bypass_skips_external_calls():
    class StrictAuthClient(FakeAuthClient):
        async def send_code(self, username: str) -> bool:
            raise AssertionError("send_code must not be called in debug mode")

        async def verify_code(self, username: str, code: str) -> str:
            raise AssertionError("verify_code must not be called in debug mode")

        async def verify_token(self, token: str) -> bool:
            raise AssertionError("verify_token must not be called in debug mode")

    settings = Settings(
        debug=True,
        debug_username="debug-user",
        DEBUG_AUTHORIZATION_TOKEN="debug-fixed-token",
        db_user="wb",
        db_pass="wb",
        db_host="localhost",
        db_port=5432,
        db_name="wb_wrapper",
    )
    service = AuthService(auth_client=StrictAuthClient(), repository=FakeRepo(), settings=settings)

    assert await service.login("alice") is True
    assert await service.verify_saved_token("alice", code="1234") is True
    assert await service.resolve_token_for_wb("alice") == "debug-fixed-token"
