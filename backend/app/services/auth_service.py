from dataclasses import dataclass

from backend.app.core.config import Settings
from backend.app.core.exceptions import AuthorizationError, CredentialsNotFound
from backend.app.external.auth_validator.client import ExternalAuthClient
from backend.app.repositories.user_tokens import UserTokenRepository
from backend.app.repositories.adv.pg import AdvPgClient


@dataclass
class AuthService:
    auth_client: ExternalAuthClient
    repository: UserTokenRepository
    settings: Settings
    adv_pg_client: AdvPgClient

    async def login(self, username: str) -> bool:
        if self.settings.debug or username == self.settings.admin_username:
            return True
        await self.auth_client.send_code(username=username)
        return True

    async def verify_saved_token(self, username: str, code: str | None = None) -> bool:
        if self.settings.debug or username == self.settings.admin_username:
            return True

        if code:
            token = await self.auth_client.verify_code(username=username, code=code)
            await self.repository.upsert(username=username, token=token, refreshed=False)
            await self.repository.mark_verified(username=username)
            return True

        saved = await self.repository.get_by_username(username=username)
        if saved is None:
            raise CredentialsNotFound()

        valid = await self.auth_client.verify_token(saved.token)
        if valid:
            await self.repository.mark_verified(username=username)
            return True

        await self.repository.delete(username=username)
        raise AuthorizationError(message="User token is invalid. Re-login is required")

    async def resolve_token_for_wb(self, shop_id: int) -> str:
        if self.settings.debug:
            return self.settings.debug_authorization_token

        token = await self.adv_pg_client.get_shop_token(shop_id=shop_id)
        if token:
            return token

        raise CredentialsNotFound(message="Shop token not found")
