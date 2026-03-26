from fastapi import APIRouter, Depends

from backend.app.api.deps.services import get_auth_service
from backend.app.schemas.auth import CheckRequest, CheckResponse, LoginRequest, LoginResponse, VerifyRequest, VerifyResponse
from backend.app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, service: AuthService = Depends(get_auth_service)) -> LoginResponse:
    await service.login(username=payload.username)
    return LoginResponse(ok=True, username=payload.username)


@router.post("/verify", response_model=VerifyResponse)
async def verify(payload: VerifyRequest, service: AuthService = Depends(get_auth_service)) -> VerifyResponse:
    valid = await service.verify_saved_token(username=payload.username, code=payload.code)
    return VerifyResponse(ok=True, valid=valid)


@router.post("/check", response_model=CheckResponse)
async def check(payload: CheckRequest, service: AuthService = Depends(get_auth_service)) -> CheckResponse:
    valid = await service.check_saved_token(username=payload.username)
    return CheckResponse(ok=True, valid=valid)
