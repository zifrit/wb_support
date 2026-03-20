from fastapi import APIRouter, Depends

from backend.app.core.config import Settings, get_settings
from backend.app.schemas.meta import MetaConfigResponse, MetaResponse
from backend.app.services.meta_catalog import get_endpoint_catalog

router = APIRouter(prefix="/meta", tags=["meta"])


@router.get("/config", response_model=MetaConfigResponse)
async def config(settings: Settings = Depends(get_settings)) -> MetaConfigResponse:
    return MetaConfigResponse(
        debug=settings.debug,
        defaultUsername=settings.debug_username if settings.debug else None,
    )


@router.get("/endpoints", response_model=MetaResponse)
async def endpoints(settings: Settings = Depends(get_settings)) -> MetaResponse:
    return MetaResponse(
        endpoints=get_endpoint_catalog(),
        debug=settings.debug,
        defaultUsername=settings.debug_username if settings.debug else None,
    )
