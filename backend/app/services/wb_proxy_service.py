from dataclasses import dataclass
from time import perf_counter
from typing import Any

from backend.app.core.config import Settings
from backend.app.core.exceptions import AuthorizationError
from backend.app.external.wb_client.client import ExternalApiClient
from backend.app.external.wb_client.models import RequestContext
from backend.app.services.auth_service import AuthService


@dataclass
class WbProxyService:
    settings: Settings
    auth_service: AuthService
    client: ExternalApiClient

    async def execute(
        self,
        username: str,
        endpoint_id: str,
        method: str,
        shop_id: int,
        url: str,
        query_params: dict[str, Any] | None = None,
        payload: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], int, int, str]:
        request_context = RequestContext(
            rq_type=endpoint_id,
            method=method,
            shop_id=shop_id,
            url=url,
            username=username,
            query_params=query_params,
            payload=payload,
        )
        started = perf_counter()
        token = await self.auth_service.resolve_token_for_wb(shop_id=shop_id)

        headers = {
            "X-Client-Secret": self.settings.wb_client_secret,
            "user-agent": self.settings.wb_user_agent,
            "Authorization": token,
        }

        try:
            response, wb_status = await self.client.request(request_context, resolved_headers=headers)
            duration = int((perf_counter() - started) * 1000)
            return response, wb_status, duration, request_context.request_id
        except AuthorizationError:
            raise AuthorizationError(message="Stored token was rejected by WB. Re-login is required")
