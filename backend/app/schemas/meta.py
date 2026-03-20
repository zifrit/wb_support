from pydantic import BaseModel


class FieldMeta(BaseModel):
    name: str
    type: str
    required: bool
    description: str


class EndpointMeta(BaseModel):
    id: str
    title: str
    method: str
    path: str
    requiresUsername: bool
    query: list[FieldMeta] | None = None
    body: dict | None = None


class MetaConfigResponse(BaseModel):
    debug: bool = False
    defaultUsername: str | None = None


class MetaResponse(MetaConfigResponse):
    endpoints: list[EndpointMeta]
