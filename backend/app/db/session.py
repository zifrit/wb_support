from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import get_settings
from backend.app.db.base import Base
from backend.app.db.helper import get_database_helper

settings = get_settings()
db_helper = get_database_helper(settings.database_url_async)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in db_helper.get_session():
        yield session


async def init_db() -> None:
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
