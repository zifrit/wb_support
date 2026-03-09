from fastapi import FastAPI, Header, HTTPException

app = FastAPI(title="Token Validator Mock")


@app.post("/auth/issue")
async def issue(payload: dict) -> dict:
    username = payload.get("username")
    if not username:
        raise HTTPException(status_code=400, detail="username is required")
    return {"token": f"token-for-{username}"}


@app.get("/auth/verify")
async def verify(authorization: str | None = Header(default=None, alias="Authorization")) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.removeprefix("Bearer ")
    if token.startswith("invalid"):
        raise HTTPException(status_code=401, detail="invalid token")
    return {"valid": True}


@app.get("/health")
async def health() -> dict:
    return {"ok": True}
