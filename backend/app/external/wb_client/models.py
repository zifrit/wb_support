from dataclasses import dataclass, field
from time import perf_counter
from typing import Any
from uuid import uuid4


@dataclass
class RequestContext:
    rq_type: str
    method: str
    shop_id: int
    url: str
    username: str
    query_params: dict[str, Any] | None = None
    payload: Any | None = None
    headers: dict[str, str] | None = None
    request_id: str = field(default_factory=lambda: str(uuid4()))
    started_at: float = field(default_factory=perf_counter)


@dataclass
class RequestLog:
    request_id: str
    rq_type: str
    method: str
    url: str
    username: str
    status_code: int | None = None
    duration_ms: int | None = None
    content_length: int | None = None
    error_message: str | None = None
    wb_url: str | None = None
    wb_status: int | None = None


@dataclass
class Credentials:
    username: str
    authorization: str
    client_secret: str
    user_agent: str
