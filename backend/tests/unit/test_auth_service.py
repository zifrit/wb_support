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


class FakeAdvPgClient:
    def __init__(self):
        self.tokens = {}

    async def get_shop_token(self, shop_id: int) -> str | None:
        return self.tokens.get(shop_id)


@pytest.mark.asyncio
async def test_login_sends_otp_without_storing_token():
    repo = FakeRepo()
    auth_client = FakeAuthClient()
    adv_pg_client = FakeAdvPgClient()
    settings = Settings(db_user="wb", db_pass="wb", db_host="localhost", db_port=5432, db_name="wb_wrapper")
    service = AuthService(auth_client=auth_client, repository=repo, settings=settings, adv_pg_client=adv_pg_client)

    result = await service.login("alice")

    assert result is True
    assert auth_client.sent == ["alice"]
    assert repo.storage == {}


@pytest.mark.asyncio
async def test_verify_code_stores_token():
    repo = FakeRepo()
    auth_client = FakeAuthClient()
    adv_pg_client = FakeAdvPgClient()
    settings = Settings(db_user="wb", db_pass="wb", db_host="localhost", db_port=5432, db_name="wb_wrapper")
    service = AuthService(auth_client=auth_client, repository=repo, settings=settings, adv_pg_client=adv_pg_client)

    result = await service.verify_saved_token("alice", code="1234")

    assert result is True
    assert repo.storage["alice"] == "token-alice-1234"


@pytest.mark.asyncio
async def test_check_saved_token_returns_true_for_valid_saved_token():
    repo = FakeRepo()
    repo.storage["alice"] = "saved-token"
    auth_client = FakeAuthClient()
    adv_pg_client = FakeAdvPgClient()
    settings = Settings(db_user="wb", db_pass="wb", db_host="localhost", db_port=5432, db_name="wb_wrapper")
    service = AuthService(auth_client=auth_client, repository=repo, settings=settings, adv_pg_client=adv_pg_client)

    result = await service.check_saved_token("alice")

    assert result is True
    assert repo.storage["alice"] == "saved-token"


@pytest.mark.asyncio
async def test_check_saved_token_deletes_invalid_saved_token():
    repo = FakeRepo()
    repo.storage["alice"] = "saved-token"
    auth_client = FakeAuthClient()
    auth_client.invalid.add("saved-token")
    adv_pg_client = FakeAdvPgClient()
    settings = Settings(db_user="wb", db_pass="wb", db_host="localhost", db_port=5432, db_name="wb_wrapper")
    service = AuthService(auth_client=auth_client, repository=repo, settings=settings, adv_pg_client=adv_pg_client)

    with pytest.raises(AuthorizationError):
        await service.check_saved_token("alice")

    assert "alice" not in repo.storage


@pytest.mark.asyncio
async def test_check_saved_token_raises_when_saved_token_missing():
    settings = Settings(db_user="wb", db_pass="wb", db_host="localhost", db_port=5432, db_name="wb_wrapper")
    service = AuthService(
        auth_client=FakeAuthClient(),
        repository=FakeRepo(),
        settings=settings,
        adv_pg_client=FakeAdvPgClient(),
    )

    with pytest.raises(CredentialsNotFound):
        await service.check_saved_token("alice")


@pytest.mark.asyncio
async def test_resolve_missing_shop_token_raises():
    settings = Settings(db_user="wb", db_pass="wb", db_host="localhost", db_port=5432, db_name="wb_wrapper")
    service = AuthService(
        auth_client=FakeAuthClient(),
        repository=FakeRepo(),
        settings=settings,
        adv_pg_client=FakeAdvPgClient(),
    )

    with pytest.raises(CredentialsNotFound):
        await service.resolve_token_for_wb(404)


@pytest.mark.asyncio
async def test_resolve_shop_token_returns_value_from_adv_db():
    settings = Settings(db_user="wb", db_pass="wb", db_host="localhost", db_port=5432, db_name="wb_wrapper")
    adv_pg_client = FakeAdvPgClient()
    adv_pg_client.tokens[17] = "shop-token-17"
    service = AuthService(
        auth_client=FakeAuthClient(),
        repository=FakeRepo(),
        settings=settings,
        adv_pg_client=adv_pg_client,
    )

    assert await service.resolve_token_for_wb(17) == "shop-token-17"


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
    service = AuthService(
        auth_client=StrictAuthClient(),
        repository=FakeRepo(),
        settings=settings,
        adv_pg_client=FakeAdvPgClient(),
    )

    assert await service.login("admin") is True
    assert await service.verify_saved_token("admin", code="1234") is True


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
    service = AuthService(
        auth_client=StrictAuthClient(),
        repository=FakeRepo(),
        settings=settings,
        adv_pg_client=FakeAdvPgClient(),
    )

    assert await service.login("alice") is True
    assert await service.verify_saved_token("alice", code="1234") is True
    assert await service.resolve_token_for_wb(999) == "debug-fixed-token"
