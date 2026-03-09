from dataclasses import dataclass

from backend.app.core.config import Settings
from backend.app.core.exceptions import AuthorizationError, CredentialsNotFound
from backend.app.external.auth_validator.client import ExternalAuthClient
from backend.app.repositories.user_tokens import UserTokenRepository


@dataclass
class AuthService:
    auth_client: ExternalAuthClient
    repository: UserTokenRepository
    settings: Settings

    async def login(self, username: str) -> str:
        if username == self.settings.admin_username:
            return self.settings.admin_authorization_token
        token = await self.auth_client.issue_token(username=username)
        await self.repository.upsert(username=username, token=token, refreshed=False)
        return token

    async def verify_saved_token(self, username: str) -> bool:
        if username == self.settings.admin_username:
            return True
        saved = await self.repository.get_by_username(username=username)
        if saved is None:
            raise CredentialsNotFound()

        valid = await self.auth_client.verify_token(saved.token)
        if valid:
            await self.repository.mark_verified(username=username)
            return True

        token = await self.auth_client.issue_token(username=username)
        await self.repository.upsert(username=username, token=token, refreshed=True)
        valid_after_refresh = await self.auth_client.verify_token(token)
        if valid_after_refresh:
            await self.repository.mark_verified(username=username)
            return True
        raise AuthorizationError(message="User token is invalid after refresh")

    async def resolve_token_for_wb(self, username: str) -> str:
        if username == self.settings.admin_username:
            return self.settings.admin_authorization_token
        saved = await self.repository.get_by_username(username=username)
        if saved is None:
            raise CredentialsNotFound()

        valid = await self.auth_client.verify_token(saved.token)
        if valid:
            await self.repository.mark_verified(username=username)
            return saved.token

        token = await self.auth_client.issue_token(username=username)
        await self.repository.upsert(username=username, token=token, refreshed=True)
        return token
