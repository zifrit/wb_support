import logging
from dataclasses import dataclass
from time import perf_counter
from typing import Any

from backend.app.core.exceptions import AppError, UnknownApiError
from backend.app.external.wb_client.error_mapper import ErrorMapper
from backend.app.external.wb_client.models import RequestContext, RequestLog
from backend.app.external.wb_client.retry import should_retry
from backend.app.external.wb_client.transport import HttpxTransport


@dataclass
class ExternalApiClient:
    transport: HttpxTransport
    error_mapper: ErrorMapper
    logger: logging.Logger
    retries: int = 0

    async def request(self, context: RequestContext, resolved_headers: dict[str, str]) -> tuple[Any, int]:
        attempt = 0
        while True:
            log = RequestLog(
                request_id=context.request_id,
                rq_type=context.rq_type,
                method=context.method,
                url=context.url,
                username=context.username,
                wb_url=context.url,
            )
            started = perf_counter()
            try:
                final_headers = {}
                final_headers.update(resolved_headers)
                if context.headers:
                    final_headers.update(context.headers)

                response = await self.transport.send(
                    method=context.method,
                    url=context.url,
                    headers=final_headers,
                    query_params=context.query_params,
                    payload=context.payload,
                )

                log.duration_ms = int((perf_counter() - started) * 1000)
                log.status_code = response.status_code
                log.wb_status = response.status_code
                log.content_length = len(response.content)

                if response.status_code >= 300:
                    body = self._parse_error_body(response)
                    err = self.error_mapper.map(response.status_code, body)
                    if should_retry(attempt=attempt, max_retries=self.retries, status_code=response.status_code):
                        attempt += 1
                        continue
                    raise err

                payload = self._parse_success(response)
                self._write_log(log=log, level=logging.INFO, msg="wb_request_ok")
                return payload, response.status_code
            except AppError as exc:
                log.duration_ms = log.duration_ms or int((perf_counter() - started) * 1000)
                log.error_message = exc.message
                self._write_log(log=log, level=logging.WARNING, msg="wb_request_failed", error_type=exc.error_type)
                if should_retry(attempt=attempt, max_retries=self.retries, error=exc):
                    attempt += 1
                    continue
                raise
            except Exception as exc:
                log.duration_ms = log.duration_ms or int((perf_counter() - started) * 1000)
                log.error_message = str(exc)
                self._write_log(log=log, level=logging.ERROR, msg="wb_request_unexpected", error_type="UNEXPECTED_ERROR")
                raise UnknownApiError(message="Unexpected client error", details={"reason": str(exc)}) from exc

    @staticmethod
    def _parse_success(response) -> Any:
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            return response.json()
        try:
            return response.json()
        except ValueError:
            return response.text

    @staticmethod
    def _parse_error_body(response) -> dict | str:
        try:
            return response.json()
        except ValueError:
            return response.text

    def _write_log(self, log: RequestLog, level: int, msg: str, error_type: str | None = None) -> None:
        payload = {
            "request_id": log.request_id,
            "rq_type": log.rq_type,
            "http_method": log.method,
            "http_path": log.url,
            "username": log.username,
            "wb_url": log.wb_url,
            "wb_status": log.wb_status,
            "duration_ms": log.duration_ms,
            "content_length": log.content_length,
            "error_message": log.error_message,
            "error_type": error_type,
        }
        self.logger.log(level, msg, extra={"extra": payload})
