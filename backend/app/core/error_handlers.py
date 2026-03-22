from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.app.core.exceptions import AppError


def _format_validation_path(path: tuple) -> str:
    relevant = [str(part) for part in path if part != "body"]
    return ".".join(relevant) if relevant else "body"


def _format_validation_details(exc: RequestValidationError) -> tuple[str, list[str], list[dict]]:
    missing_fields: list[str] = []
    invalid_fields: list[dict] = []

    for error in exc.errors():
        field_path = _format_validation_path(tuple(error.get("loc", ())))
        error_type = error.get("type", "")
        message = error.get("msg", "Invalid value")

        if error_type == "missing":
            missing_fields.append(field_path)
            continue

        invalid_fields.append(
            {
                "field": field_path,
                "message": message,
                "type": error_type,
            }
        )

    unique_missing_fields = list(dict.fromkeys(missing_fields))
    if unique_missing_fields:
        message = f"Missing required fields: {', '.join(unique_missing_fields)}"
    else:
        message = "Request validation failed"

    return message, unique_missing_fields, invalid_fields


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
    async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        message, missing_fields, invalid_fields = _format_validation_details(exc)
        return JSONResponse(
            status_code=422,
            content={
                "ok": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": message,
                    "details": {
                        "missingFields": missing_fields,
                        "invalidFields": invalid_fields,
                    },
                },
                "meta": {"requestId": getattr(request.state, "request_id", None)},
            },
        )
