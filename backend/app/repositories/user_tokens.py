from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.models import UserToken


class UserTokenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_username(self, username: str) -> UserToken | None:
        stmt = select(UserToken).where(UserToken.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert(self, username: str, token: str, refreshed: bool = False) -> UserToken:
        now = datetime.now(timezone.utc)
        row = await self.get_by_username(username=username)
        if row is None:
            row = UserToken(
                username=username,
                token=token,
                created_at=now,
                updated_at=now,
                last_refresh_at=now if refreshed else None,
            )
            self.session.add(row)
        else:
            row.token = token
            row.updated_at = now
            if refreshed:
                row.last_refresh_at = now
        await self.session.commit()
        await self.session.refresh(row)
        return row

    async def mark_verified(self, username: str) -> None:
        row = await self.get_by_username(username=username)
        if row is None:
            return
        row.last_verified_at = datetime.now(timezone.utc)
        await self.session.commit()

    async def delete(self, username: str) -> None:
        row = await self.get_by_username(username=username)
        if row is None:
            return
        await self.session.delete(row)
        await self.session.commit()
