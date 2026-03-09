from fastapi import APIRouter

from backend.app.schemas.meta import MetaResponse
from backend.app.services.meta_catalog import get_endpoint_catalog

router = APIRouter(prefix="/meta", tags=["meta"])


@router.get("/endpoints", response_model=MetaResponse)
async def endpoints() -> MetaResponse:
    return MetaResponse(endpoints=get_endpoint_catalog())
