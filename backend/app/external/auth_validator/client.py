from dataclasses import dataclass

import httpx

from backend.app.core.config import Settings
from backend.app.core.exceptions import AuthorizationError, TransportError


@dataclass
class ExternalAuthClient:
    settings: Settings

    async def send_code(self, username: str) -> bool:
        try:
            async with httpx.AsyncClient(timeout=self.settings.auth_timeout_seconds) as client:
                response = await client.post(self.settings.send_code_url, json={"phone": username})
        except httpx.TimeoutException as exc:
            raise TransportError(message="Auth send code request timeout", status_code=504, details={"reason": str(exc)}) from exc
        except httpx.HTTPError as exc:
            raise TransportError(message="Auth send code request failed", status_code=502, details={"reason": str(exc)}) from exc

        if response.status_code >= 300:
            details = self._safe_json(response)
            raise AuthorizationError(message="Failed to send OTP code", details={"status": response.status_code, "body": details})

        return True

    async def verify_code(self, username: str, code: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=self.settings.auth_timeout_seconds) as client:
                response = await client.post(self.settings.verify_code_url, json={"phone": username, "otp": code})
        except httpx.TimeoutException as exc:
            raise TransportError(message="Auth verify code request timeout", status_code=504, details={"reason": str(exc)}) from exc
        except httpx.HTTPError as exc:
            raise TransportError(message="Auth verify code request failed", status_code=502, details={"reason": str(exc)}) from exc

        if response.status_code >= 300:
            details = self._safe_json(response)
            raise AuthorizationError(message="Failed to verify OTP code", details={"status": response.status_code, "body": details})

        payload = self._safe_json(response)
        token = (
            payload.get("token")
            or payload.get("access_token")
            or payload.get("accessToken")
            or payload.get("jwt")
        )
        if not token:
            raise AuthorizationError(message="Token was not returned by auth service", details={"body": payload})
        return str(token)

    async def verify_token(self, token: str) -> bool:
        try:
            async with httpx.AsyncClient(timeout=self.settings.auth_timeout_seconds) as client:
                response = await client.post(self.settings.verify_token_url, json={"token": token})
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
        if "valid" in payload:
            return bool(payload["valid"])
        if "ok" in payload:
            return bool(payload["ok"])
        return True

    @staticmethod
    def _safe_json(response: httpx.Response) -> dict:
        try:
            value = response.json()
            if isinstance(value, dict):
                return value
            return {"raw": value}
        except ValueError:
            return {"raw": response.text}
