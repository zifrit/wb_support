from collections.abc import AsyncGenerator
import asyncio
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import get_settings
from backend.app.db.helper import get_database_helper

settings = get_settings()
db_helper = get_database_helper(settings.database_url_async)
ALEMBIC_INI_PATH = str(Path(__file__).resolve().parents[2] / "alembic.ini")


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in db_helper.get_session():
        yield session


async def init_db() -> None:
    await asyncio.to_thread(run_migrations)


def run_migrations() -> None:
    alembic_cfg = Config(ALEMBIC_INI_PATH)
    sync_engine = create_engine(settings.database_url_sync)
    try:
        tables = set(inspect(sync_engine).get_table_names())
    finally:
        sync_engine.dispose()

    if "user_tokens" in tables and "alembic_version" not in tables:
        command.stamp(alembic_cfg, "head")
    command.upgrade(alembic_cfg, "head")
