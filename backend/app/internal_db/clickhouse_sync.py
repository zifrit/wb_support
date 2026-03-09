import httpx

from backend.app.core.exceptions import TransportError
from backend.app.internal_db.sql_guard import ensure_safe_select


class ClickHouseSyncSelectClient:
    def __init__(self, base_url: str, user: str, password: str, database: str, timeout: int = 30):
        self.base_url = base_url
        self.auth = (user, password)
        self.database = database
        self.timeout = timeout

    def select(self, sql: str, params: dict | None = None) -> dict:
        safe_sql = ensure_safe_select(sql)
        final_sql = f"{safe_sql} FORMAT JSON"
        try:
            response = httpx.post(
                self.base_url,
                params={"database": self.database, **(params or {})},
                content=final_sql.encode("utf-8"),
                auth=self.auth,
                timeout=self.timeout,
            )
        except httpx.HTTPError as exc:
            raise TransportError(message="ClickHouse sync select failed", details={"reason": str(exc)}) from exc
        response.raise_for_status()
        payload = response.json()
        columns = [item["name"] for item in payload.get("meta", [])]
        rows = [[row.get(col) for col in columns] for row in payload.get("data", [])]
        return {"columns": columns, "rows": rows}
