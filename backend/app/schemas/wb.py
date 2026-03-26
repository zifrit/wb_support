from datetime import date
from typing import Any

from pydantic import BaseModel, Field, field_validator


class NormQueryItem(BaseModel):
    advert_id: int
    nm_id: int


class ShopScopedRequest(BaseModel):
    shop_id: int


class AdvertsRequest(ShopScopedRequest):
    ids: str | None = None
    statuses: str | None = None
    payment_type: str | None = None

    @field_validator("payment_type")
    def check_age(cls, v: str | None):
        if v is None:
            return v  # пропускаем None
        if v.lower() not in ("cpm", "cpc"):
            raise ValueError("payment_type must be either 'cpm' or 'cpc'")
        return v


class FullstatsRequest(ShopScopedRequest):
    ids: str
    beginDate: str
    endDate: str


class OrdersRequest(ShopScopedRequest):
    dateFrom: str
    flag: int = 0


class NormQueryStatsRequest(ShopScopedRequest):
    from_: date = Field(alias="from")
    to: date
    items: list[NormQueryItem]


class NormQueryMinusRequest(ShopScopedRequest):
    items: list[NormQueryItem]


class SearchPeriod(BaseModel):
    start: date
    end: date


class SearchOrder(BaseModel):
    field: str
    mode: str


class SearchTextsRequest(ShopScopedRequest):
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
