from dataclasses import dataclass
from typing import Any

import httpx

from backend.app.core.exceptions import TransportError


@dataclass
class HttpxTransport:
    timeout_seconds: int

    async def send(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        query_params: dict[str, Any] | None = None,
        payload: Any | None = None,
    ) -> httpx.Response:
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                return await client.request(method=method, url=url, headers=headers, params=query_params, json=payload)
        except httpx.TimeoutException as exc:
            raise TransportError(message="Request timeout", status_code=504, details={"reason": str(exc)}) from exc
        except httpx.HTTPError as exc:
            raise TransportError(message="Request transport error", status_code=502, details={"reason": str(exc)}) from exc
