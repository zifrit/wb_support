import pytest

from backend.app.core.config import Settings
from backend.app.core.exceptions import CredentialsNotFound
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


class FakeAuthClient:
    def __init__(self):
        self.issued = 0
        self.invalid = set()

    async def issue_token(self, username: str) -> str:
        self.issued += 1
        return f"token-{username}-{self.issued}"

    async def verify_token(self, token: str) -> bool:
        return token not in self.invalid


@pytest.mark.asyncio
async def test_login_and_store_token():
    repo = FakeRepo()
    auth_client = FakeAuthClient()
    service = AuthService(auth_client=auth_client, repository=repo, settings=Settings())

    token = await service.login("alice")

    assert token.startswith("token-alice")
    assert repo.storage["alice"] == token


@pytest.mark.asyncio
async def test_resolve_missing_token_raises():
    service = AuthService(auth_client=FakeAuthClient(), repository=FakeRepo(), settings=Settings())

    with pytest.raises(CredentialsNotFound):
        await service.resolve_token_for_wb("alice")


@pytest.mark.asyncio
async def test_refresh_token_when_invalid():
    repo = FakeRepo()
    auth_client = FakeAuthClient()
    service = AuthService(auth_client=auth_client, repository=repo, settings=Settings())

    first = await service.login("alice")
    auth_client.invalid.add(first)

    resolved = await service.resolve_token_for_wb("alice")

    assert resolved != first
    assert repo.storage["alice"] == resolved


@pytest.mark.asyncio
async def test_admin_bypass_skips_external_calls():
    class StrictAuthClient(FakeAuthClient):
        async def issue_token(self, username: str) -> str:
            raise AssertionError("issue_token must not be called for admin")

        async def verify_token(self, token: str) -> bool:
            raise AssertionError("verify_token must not be called for admin")

    settings = Settings(admin_username="admin", ADMIN_AUTHORIZATION_TOKEN="admin-fixed-token")
    service = AuthService(auth_client=StrictAuthClient(), repository=FakeRepo(), settings=settings)

    assert await service.login("admin") == "admin-fixed-token"
    assert await service.verify_saved_token("admin") is True
    assert await service.resolve_token_for_wb("admin") == "admin-fixed-token"


@pytest.mark.asyncio
async def test_debug_bypass_skips_external_calls():
    class StrictAuthClient(FakeAuthClient):
        async def issue_token(self, username: str) -> str:
            raise AssertionError("issue_token must not be called in debug mode")

        async def verify_token(self, token: str) -> bool:
            raise AssertionError("verify_token must not be called in debug mode")

    settings = Settings(debug=True, debug_username="debug-user", DEBUG_AUTHORIZATION_TOKEN="debug-fixed-token")
    service = AuthService(auth_client=StrictAuthClient(), repository=FakeRepo(), settings=settings)

    assert await service.login("alice") == "debug-fixed-token"
    assert await service.verify_saved_token("alice") is True
    assert await service.resolve_token_for_wb("alice") == "debug-fixed-token"
