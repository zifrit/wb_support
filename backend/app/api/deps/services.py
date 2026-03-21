import logging

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import Settings, get_settings
from backend.app.db.session import get_db_session
from backend.app.external.auth_validator.client import ExternalAuthClient
from backend.app.external.wb_client.client import ExternalApiClient
from backend.app.external.wb_client.error_mapper import ErrorMapper
from backend.app.external.wb_client.transport import HttpxTransport
from backend.app.repositories.user_tokens import UserTokenRepository
from backend.app.services.auth_service import AuthService
from backend.app.services.wb_proxy_service import WbProxyService
from backend.app.repositories.adv.pg import AdvPgClient
from backend.app.internal_db.postgres_async import PostgresAsyncSelectClient

def get_logger() -> logging.Logger:
    return logging.getLogger("wb_wrapper")


def get_auth_client(settings: Settings = Depends(get_settings)) -> ExternalAuthClient:
    return ExternalAuthClient(settings=settings)


async def get_user_token_repository(session: AsyncSession = Depends(get_db_session)) -> UserTokenRepository:
    return UserTokenRepository(session)

async def get_adv_pg_client(settings: Settings = Depends(get_settings)) -> AdvPgClient:
    return AdvPgClient(PostgresAsyncSelectClient(settings.adv_database_url_asyncpg))


async def get_auth_service(
    settings: Settings = Depends(get_settings),
    auth_client: ExternalAuthClient = Depends(get_auth_client),
    repository: UserTokenRepository = Depends(get_user_token_repository),
    adv_pg_client: AdvPgClient = Depends(get_adv_pg_client),
) -> AuthService:
    return AuthService(auth_client=auth_client, repository=repository, settings=settings, adv_pg_client=adv_pg_client)


async def get_external_api_client(
    settings: Settings = Depends(get_settings),
    logger: logging.Logger = Depends(get_logger),
) -> ExternalApiClient:
    return ExternalApiClient(
        transport=HttpxTransport(timeout_seconds=settings.wb_timeout_seconds),
        error_mapper=ErrorMapper(),
        logger=logger,
        retries=settings.wb_retries,
    )


async def get_wb_proxy_service(
    settings: Settings = Depends(get_settings),
    auth_service: AuthService = Depends(get_auth_service),
    client: ExternalApiClient = Depends(get_external_api_client),
) -> WbProxyService:
    return WbProxyService(settings=settings, auth_service=auth_service, client=client)
