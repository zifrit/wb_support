from fastapi import Header, Request, Query

from backend.app.core.config import get_settings
from backend.app.core.exceptions import AuthorizationError


async def get_username_header(
        request: Request,
        x_username: str = Header(alias="X-Username"),
) -> str | None:
    settings = get_settings()
    if settings.debug:
        return x_username or settings.debug_username
    if not x_username:
        raise AuthorizationError(message="X-Username header is required")
    return x_username



async def get_shop_id_query(
        request: Request,
        shop_id: int = Query(),
) -> int:
    return shop_id
