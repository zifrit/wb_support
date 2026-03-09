from dataclasses import dataclass

import httpx

from backend.app.core.config import Settings
from backend.app.core.exceptions import AuthorizationError, TransportError


@dataclass
class ExternalAuthClient:
    settings: Settings

    async def issue_token(self, username: str) -> str:
        url = f"{self.settings.auth_base_url.rstrip('/')}/{self.settings.auth_issue_path.lstrip('/')}"
        try:
            async with httpx.AsyncClient(timeout=self.settings.auth_timeout_seconds) as client:
                response = await client.post(url, json={"username": username})
        except httpx.TimeoutException as exc:
            raise TransportError(message="Auth issue request timeout", status_code=504, details={"reason": str(exc)}) from exc
        except httpx.HTTPError as exc:
            raise TransportError(message="Auth issue request failed", status_code=502, details={"reason": str(exc)}) from exc

        if response.status_code >= 300:
            details = self._safe_json(response)
            raise AuthorizationError(message="Failed to issue user token", details={"status": response.status_code, "body": details})

        payload = self._safe_json(response)
        token = payload.get("token") or payload.get("access_token")
        if not token:
            raise AuthorizationError(message="Token was not returned by auth service", details={"body": payload})
        return str(token)

    async def verify_token(self, token: str) -> bool:
        url = f"{self.settings.auth_base_url.rstrip('/')}/{self.settings.auth_verify_path.lstrip('/')}"
        try:
            async with httpx.AsyncClient(timeout=self.settings.auth_timeout_seconds) as client:
                response = await client.get(url, headers={"Authorization": f"Bearer {token}"})
        except httpx.TimeoutException as exc:
            raise TransportError(message="Auth verify request timeout", status_code=504, details={"reason": str(exc)}) from exc
        except httpx.HTTPError as exc:
            raise TransportError(message="Auth verify request failed", status_code=502, details={"reason": str(exc)}) from exc

        if response.status_code == 401:
            return False

        if response.status_code >= 300:
            details = self._safe_json(response)
            raise AuthorizationError(message="Failed to verify user token", details={"status": response.status_code, "body": details})

        payload = self._safe_json(response)
        return bool(payload.get("valid", True))

    @staticmethod
    def _safe_json(response: httpx.Response) -> dict:
        try:
            value = response.json()
            if isinstance(value, dict):
                return value
            return {"raw": value}
        except ValueError:
            return {"raw": response.text}
