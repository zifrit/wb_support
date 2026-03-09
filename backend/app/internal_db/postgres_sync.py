from sqlalchemy import create_engine, text

from backend.app.internal_db.sql_guard import ensure_safe_select


class PostgresSyncSelectClient:
    def __init__(self, database_url_sync: str):
        self.engine = create_engine(database_url_sync)

    def select(self, sql: str, params: dict | None = None) -> dict:
        safe_sql = ensure_safe_select(sql)
        with self.engine.connect() as conn:
            result = conn.execute(text(safe_sql), params or {})
            rows = [list(row) for row in result.fetchall()]
            columns = list(result.keys())
        return {"columns": columns, "rows": rows}
