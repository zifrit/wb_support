from dataclasses import dataclass
from time import perf_counter
from typing import Any

from backend.app.core.config import Settings
from backend.app.core.exceptions import AuthorizationError
from backend.app.external.wb_client.client import ExternalApiClient
from backend.app.external.wb_client.credentials_resolver import WbCredentialsResolver
from backend.app.external.wb_client.models import RequestContext
from backend.app.services.auth_service import AuthService


@dataclass
class WbProxyService:
    settings: Settings
    auth_service: AuthService
    credentials_resolver: WbCredentialsResolver
    client: ExternalApiClient

    async def execute(
        self,
        username: str,
        endpoint_id: str,
        method: str,
        url: str,
        query_params: dict[str, Any] | None = None,
        payload: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], int, int, str]:
        request_context = RequestContext(
            rq_type=endpoint_id,
            method=method,
            url=url,
            username=username,
            query_params=query_params,
            payload=payload,
        )
        started = perf_counter()
        token = await self.auth_service.resolve_token_for_wb(username=username)
        credentials = self.credentials_resolver.resolve(username=username, token=token)

        headers = {
            "X-Client-Secret": credentials.client_secret,
            "User-Agent": credentials.user_agent,
            "Authorization": credentials.authorization,
        }

        try:
            response, wb_status = await self.client.request(request_context, resolved_headers=headers)
            duration = int((perf_counter() - started) * 1000)
            return response, wb_status, duration, request_context.request_id
        except AuthorizationError:
            raise AuthorizationError(message="Stored token was rejected by WB. Re-login is required")
