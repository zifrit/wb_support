from typing import Any

from fastapi import APIRouter, Depends

from backend.app.api.deps.auth import get_username_header
from backend.app.api.deps.services import get_wb_proxy_service
from backend.app.schemas.wb import (
    AdvertsRequest,
    FullstatsRequest,
    NormQueryMinusRequest,
    NormQueryStatsRequest,
    OrdersRequest,
    SearchTextsRequest,
    StopRequest,
)
from backend.app.services.wb_endpoints import WB_ENDPOINTS
from backend.app.services.wb_proxy_service import WbProxyService

router = APIRouter(prefix="/wb", tags=["wb"])


def _success(data: Any, request_id: str, duration_ms: int, status: int) -> dict[str, Any]:
    return {
        "ok": True,
        "data": data if isinstance(data, dict) else {"raw": data},
        "meta": {"requestId": request_id, "durationMs": duration_ms, "wbStatus": status},
    }


@router.post("/adverts")
async def wb_adverts(
    payload: AdvertsRequest,
    username: str = Depends(get_username_header),
    service: WbProxyService = Depends(get_wb_proxy_service),
) -> dict[str, Any]:
    method, url = WB_ENDPOINTS["wb_adverts"]
    query_params = payload.model_dump(exclude_none=True, exclude={"shop_id"})
    query_params = {k: v for k, v in query_params.items() if v is not None}
    data, wb_status, duration, request_id = await service.execute(
        username=username,
        endpoint_id="wb_adverts",
        method=method,
        shop_id=payload.shop_id,
        url=url,
        query_params=query_params,
    )
    return _success(data, request_id, duration, wb_status)


@router.post("/fullstats")
async def wb_fullstats(
    payload: FullstatsRequest,
    username: str = Depends(get_username_header),
    service: WbProxyService = Depends(get_wb_proxy_service),
) -> dict[str, Any]:
    method, url = WB_ENDPOINTS["wb_fullstats"]
    data, wb_status, duration, request_id = await service.execute(
        username=username,
        endpoint_id="wb_fullstats",
        method=method,
        shop_id=payload.shop_id,
        url=url,
        query_params=payload.model_dump(exclude={"shop_id"}),
    )
    return _success(data, request_id, duration, wb_status)


@router.post("/stop")
async def wb_stop(
    payload: StopRequest,
    username: str = Depends(get_username_header),
    service: WbProxyService = Depends(get_wb_proxy_service),
) -> dict[str, Any]:
    method, url = WB_ENDPOINTS["wb_stop"]
    data, wb_status, duration, request_id = await service.execute(
        username=username,
        endpoint_id="wb_stop",
        method=method,
        shop_id=payload.shop_id,
        url=url,
        query_params=payload.model_dump(exclude={"shop_id"}),
    )
    return _success(data, request_id, duration, wb_status)


@router.post("/normquery/stats")
async def wb_normquery_stats(
    payload: NormQueryStatsRequest,
    username: str = Depends(get_username_header),
    service: WbProxyService = Depends(get_wb_proxy_service),
) -> dict[str, Any]:
    method, url = WB_ENDPOINTS["wb_normquery_stats"]
    data, wb_status, duration, request_id = await service.execute(
        username=username,
        endpoint_id="wb_normquery_stats",
        method=method,
        shop_id=payload.shop_id,
        url=url,
        payload=payload.model_dump(by_alias=True, exclude={"shop_id"}),
    )
    return _success(data, request_id, duration, wb_status)


@router.post("/normquery/get-minus")
async def wb_normquery_get_minus(
    payload: NormQueryMinusRequest,
    username: str = Depends(get_username_header),
    service: WbProxyService = Depends(get_wb_proxy_service),
) -> dict[str, Any]:
    method, url = WB_ENDPOINTS["wb_normquery_get_minus"]
    data, wb_status, duration, request_id = await service.execute(
        username=username,
        endpoint_id="wb_normquery_get_minus",
        method=method,
        shop_id=payload.shop_id,
        url=url,
        payload=payload.model_dump(exclude={"shop_id"}),
    )
    return _success(data, request_id, duration, wb_status)


@router.post("/orders")
async def wb_orders(
    payload: OrdersRequest,
    username: str = Depends(get_username_header),
    service: WbProxyService = Depends(get_wb_proxy_service),
) -> dict[str, Any]:
    method, url = WB_ENDPOINTS["wb_orders"]
    data, wb_status, duration, request_id = await service.execute(
        username=username,
        endpoint_id="wb_orders",
        method=method,
        shop_id=payload.shop_id,
        url=url,
        query_params=payload.model_dump(exclude={"shop_id"}),
    )
    return _success(data, request_id, duration, wb_status)


@router.post("/search-report/product/search-texts")
async def wb_search_texts(
    payload: SearchTextsRequest,
    username: str = Depends(get_username_header),
    service: WbProxyService = Depends(get_wb_proxy_service),
) -> dict[str, Any]:
    method, url = WB_ENDPOINTS["wb_search_report_product_search_texts"]
    data, wb_status, duration, request_id = await service.execute(
        username=username,
        endpoint_id="wb_search_report_product_search_texts",
        method=method,
        shop_id=payload.shop_id,
        url=url,
        payload=payload.model_dump(exclude={"shop_id"}),
    )
    return _success(data, request_id, duration, wb_status)
