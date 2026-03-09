from typing import Any

from fastapi import APIRouter, Depends, Query

from backend.app.api.deps.auth import get_username_header
from backend.app.api.deps.services import get_wb_proxy_service
from backend.app.schemas.wb import NormQueryMinusRequest, NormQueryStatsRequest, SearchTextsRequest
from backend.app.services.wb_endpoints import WB_ENDPOINTS
from backend.app.services.wb_proxy_service import WbProxyService

router = APIRouter(prefix="/wb", tags=["wb"])


def _success(data: Any, request_id: str, duration_ms: int, status: int) -> dict[str, Any]:
    return {
        "ok": True,
        "data": data if isinstance(data, dict) else {"raw": data},
        "meta": {"requestId": request_id, "durationMs": duration_ms, "wbStatus": status},
    }


@router.get("/adverts")
async def wb_adverts(
    ids: str | None = Query(default=None),
    statuses: str | None = Query(default=None),
    payment_type: str | None = Query(default=None),
    username: str = Depends(get_username_header),
    service: WbProxyService = Depends(get_wb_proxy_service),
) -> dict[str, Any]:
    method, url = WB_ENDPOINTS["wb_adverts"]
    query_params = {"ids": ids, "statuses": statuses, "payment_type": payment_type}
    query_params = {k: v for k, v in query_params.items() if v is not None}
    data, wb_status, duration, request_id = await service.execute(
        username=username,
        endpoint_id="wb_adverts",
        method=method,
        url=url,
        query_params=query_params,
    )
    return _success(data, request_id, duration, wb_status)


@router.get("/fullstats")
async def wb_fullstats(
    ids: str,
    beginDate: str,
    endDate: str,
    username: str = Depends(get_username_header),
    service: WbProxyService = Depends(get_wb_proxy_service),
) -> dict[str, Any]:
    method, url = WB_ENDPOINTS["wb_fullstats"]
    data, wb_status, duration, request_id = await service.execute(
        username=username,
        endpoint_id="wb_fullstats",
        method=method,
        url=url,
        query_params={"ids": ids, "beginDate": beginDate, "endDate": endDate},
    )
    return _success(data, request_id, duration, wb_status)


@router.get("/stop")
async def wb_stop(
    id: str,
    username: str = Depends(get_username_header),
    service: WbProxyService = Depends(get_wb_proxy_service),
) -> dict[str, Any]:
    method, url = WB_ENDPOINTS["wb_stop"]
    data, wb_status, duration, request_id = await service.execute(
        username=username,
        endpoint_id="wb_stop",
        method=method,
        url=url,
        query_params={"id": id},
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
        url=url,
        payload=payload.model_dump(by_alias=True),
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
        url=url,
        payload=payload.model_dump(),
    )
    return _success(data, request_id, duration, wb_status)


@router.get("/orders")
async def wb_orders(
    dateFrom: str,
    flag: int = 0,
    username: str = Depends(get_username_header),
    service: WbProxyService = Depends(get_wb_proxy_service),
) -> dict[str, Any]:
    method, url = WB_ENDPOINTS["wb_orders"]
    data, wb_status, duration, request_id = await service.execute(
        username=username,
        endpoint_id="wb_orders",
        method=method,
        url=url,
        query_params={"dateFrom": dateFrom, "flag": flag},
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
        url=url,
        payload=payload.model_dump(),
    )
    return _success(data, request_id, duration, wb_status)
