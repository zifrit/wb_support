from datetime import date
from typing import Any

from pydantic import BaseModel, Field


class NormQueryItem(BaseModel):
    advert_id: int
    nm_id: int


class AdvertsRequest(BaseModel):
    ids: str | None = None
    statuses: str | None = None
    payment_type: str | None = None


class FullstatsRequest(BaseModel):
    ids: str
    beginDate: str
    endDate: str


class StopRequest(BaseModel):
    id: str


class OrdersRequest(BaseModel):
    dateFrom: str
    flag: int = 0


class NormQueryStatsRequest(BaseModel):
    from_: date = Field(alias="from")
    to: date
    items: list[NormQueryItem]


class NormQueryMinusRequest(BaseModel):
    items: list[NormQueryItem]


class SearchPeriod(BaseModel):
    start: date
    end: date


class SearchOrder(BaseModel):
    field: str
    mode: str


class SearchTextsRequest(BaseModel):
    currentPeriod: SearchPeriod
    pastPeriod: SearchPeriod
    nmIds: list[int]
    limit: int = 30
    offset: int = 0
    topOrderBy: str | None = None
    orderBy: SearchOrder | None = None


class WbSuccessResponse(BaseModel):
    ok: bool = True
    data: dict[str, Any]
    meta: dict[str, Any]


class WbErrorResponse(BaseModel):
    ok: bool = False
    error: dict[str, Any]
    meta: dict[str, Any]
