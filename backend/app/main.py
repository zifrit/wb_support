from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes.auth import router as auth_router
from backend.app.api.routes.meta import router as meta_router
from backend.app.api.routes.wb import router as wb_router
from backend.app.core.config import get_settings
from backend.app.core.error_handlers import register_error_handlers
from backend.app.core.logging import configure_logging, get_logger
from backend.app.db.session import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    await init_db()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)
app.include_router(auth_router)
app.include_router(meta_router)
app.include_router(wb_router)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id", str(uuid4()))
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-Id"] = request_id
    return response


@app.get("/health")
async def health() -> dict[str, bool]:
    get_logger("wb_wrapper").info("healthcheck", extra={"extra": {"service": "backend"}})
    return {"ok": True}
