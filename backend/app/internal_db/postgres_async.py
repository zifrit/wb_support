from sqlalchemy import text

from backend.app.db.helper import get_database_helper
from backend.app.internal_db.sql_guard import ensure_safe_select


class PostgresAsyncSelectClient:
    def __init__(self, database_url_async: str):
        self.db_helper = get_database_helper(database_url_async)

    async def select(self, sql: str, params: dict | None = None) -> dict:
        safe_sql = ensure_safe_select(sql)
        async with self.db_helper.engine.connect() as conn:
            result = await conn.execute(text(safe_sql), params or {})
            rows = [list(row) for row in result.fetchall()]
            columns = list(result.keys())
        return {"columns": columns, "rows": rows}
