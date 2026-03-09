from collections.abc import AsyncGenerator
from functools import lru_cache
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


class DatabaseHelper:
    def __init__(self, db_url: str, echo: bool = False):
        self.engine = create_async_engine(
            url=db_url,
            echo=echo,
            future=True,
            pool_pre_ping=True,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, Any]:
        async with self.session_factory() as session:
            try:
                yield session
            finally:
                await session.close()

    async def dispose(self) -> None:
        await self.engine.dispose()


@lru_cache
def get_database_helper(db_url: str, echo: bool = False) -> DatabaseHelper:
    return DatabaseHelper(db_url=db_url, echo=echo)
