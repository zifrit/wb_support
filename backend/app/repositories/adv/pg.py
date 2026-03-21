from backend.app.internal_db.postgres_async import PostgresAsyncSelectClient


class AdvPgClient:
    def __init__(self, db: PostgresAsyncSelectClient) -> None:
        self.db = db

    async def get_shop_token(self, shop_id: int) -> str | None:
        sql = "SELECT token_adv_api FROM adv_wbshopdata WHERE shop_id = :shop_id"
        result = await self.db.select(sql, params={"shop_id": shop_id})
        if not result["rows"]:
            return None
        return result["rows"][0][0]
