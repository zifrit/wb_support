from fastapi import FastAPI, Header, HTTPException

app = FastAPI(title="Token Validator Mock")


@app.post("/api/authentication/send-otp")
async def send_otp(payload: dict) -> dict:
    username = payload.get("username")
    if not username:
        raise HTTPException(status_code=400, detail="username is required")
    return {"ok": True}


@app.post("/api/authentication/check-otp")
async def check_otp(payload: dict) -> dict:
    username = payload.get("username")
    code = payload.get("code")
    if not username:
        raise HTTPException(status_code=400, detail="username is required")
    if not code:
        raise HTTPException(status_code=400, detail="code is required")
    if str(code) == "0000":
        raise HTTPException(status_code=401, detail="invalid code")
    return {"token": f"token-for-{username}"}


@app.post("/api/authentication/verify-token")
async def verify_token(payload: dict) -> dict:
    token = payload.get("token")
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    if token.startswith("invalid"):
        raise HTTPException(status_code=401, detail="invalid token")
    return {"valid": True}


@app.get("/health")
async def health() -> dict:
    return {"ok": True}
