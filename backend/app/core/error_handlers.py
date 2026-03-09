from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.app.core.exceptions import AppError


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        details = exc.details or {}
        wb_status = details.get("wbStatus")
        wb_body = details.get("wbBody")
        has_wb_error = wb_status is not None
        request_id = getattr(request.state, "request_id", None)
        duration_ms = details.get("durationMs")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "ok": False,
                "error": (
                    {
                        "code": "WB_API_ERROR",
                        "message": "WB API returned error",
                        "wbStatus": wb_status,
                        "wbBody": wb_body,
                    }
                    if has_wb_error
                    else {
                        "code": exc.error_type,
                        "message": exc.message,
                        "details": details,
                    }
                ),
                "meta": {"requestId": request_id, "durationMs": duration_ms},
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "ok": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": exc.errors(),
                },
            },
        )
