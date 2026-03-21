import pytest

from backend.app.core.config import Settings
from backend.app.core.exceptions import AuthorizationError, TooManyRequestsError
from backend.app.external.wb_client.error_mapper import ErrorMapper
from backend.app.services.wb_proxy_service import WbProxyService


class FakeAuthService:
    async def resolve_token_for_wb(self, shop_id: int) -> str:
        assert shop_id == 42
        return "token-42"


class FakeClient:
    def __init__(self):
        self.calls = []

    async def request(self, context, resolved_headers):
        self.calls.append((context, resolved_headers))
        return {"ok": True}, 200


@pytest.mark.asyncio
async def test_wb_proxy_service_composes_headers():
    client = FakeClient()
    settings = Settings(
        WB_CLIENT_SECRET="secret",
        wb_user_agent="wbas_xway",
        db_user="wb",
        db_pass="wb",
        db_host="localhost",
        db_port=5432,
        db_name="wb_wrapper",
    )
    service = WbProxyService(
        settings=settings,
        auth_service=FakeAuthService(),
        client=client,
    )

    response, status, _, _ = await service.execute(
        username="alice",
        endpoint_id="wb_orders",
        method="GET",
        shop_id=42,
        url="https://example.com",
        query_params={"dateFrom": "2026-03-20"},
    )

    _, headers = client.calls[0]
    assert response == {"ok": True}
    assert status == 200
    assert headers["X-Client-Secret"] == "secret"
    assert headers["user-agent"] == "wbas_xway"
    assert headers["Authorization"] == "token-42"


def test_error_mapper_maps_status_and_body():
    mapper = ErrorMapper()

    err = mapper.map(401, {"message": "unauthorized"})
    assert isinstance(err, AuthorizationError)
    assert err.details["wbStatus"] == 401

    rate_err = mapper.map(429, {"error": "slow down"})
    assert isinstance(rate_err, TooManyRequestsError)
    assert rate_err.details["wbBody"]["error"] == "slow down"
