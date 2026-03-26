from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=255)


class VerifyRequest(BaseModel):
    username: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=32)


class CheckRequest(BaseModel):
    username: str = Field(min_length=1, max_length=255)


class LoginResponse(BaseModel):
    ok: bool = True
    username: str


class VerifyResponse(BaseModel):
    ok: bool = True
    valid: bool


class CheckResponse(BaseModel):
    ok: bool = True
    valid: bool
