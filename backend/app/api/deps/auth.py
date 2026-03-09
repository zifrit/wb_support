from fastapi import Header

from backend.app.core.exceptions import AuthorizationError


async def get_username_header(x_username: str | None = Header(default=None, alias="X-Username")) -> str:
    if not x_username:
        raise AuthorizationError(message="X-Username header is required")
    return x_username
