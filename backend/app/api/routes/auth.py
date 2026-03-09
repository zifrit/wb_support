from fastapi import APIRouter, Depends

from backend.app.api.deps.auth import get_username_header
from backend.app.api.deps.services import get_auth_service
from backend.app.schemas.auth import LoginRequest, LoginResponse, VerifyResponse
from backend.app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, service: AuthService = Depends(get_auth_service)) -> LoginResponse:
    await service.login(username=payload.username)
    return LoginResponse(ok=True, username=payload.username)


@router.get("/verify", response_model=VerifyResponse)
async def verify(
    username: str = Depends(get_username_header),
    service: AuthService = Depends(get_auth_service),
) -> VerifyResponse:
    valid = await service.verify_saved_token(username=username)
    return VerifyResponse(ok=True, valid=valid)
