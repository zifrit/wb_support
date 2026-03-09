from backend.app.core.exceptions import (
    BadGatewayError,
    BadRequestError,
    ConflictError,
    ForbiddenError,
    GatewayTimeoutError,
    InternalServerError,
    MethodNotAllowedError,
    NotFoundError,
    ServiceUnavailableError,
    TooManyRequestsError,
    UnprocessableEntityError,
    UnknownApiError,
    AuthorizationError,
)


class ErrorMapper:
    def map(self, status_code: int, error_body: dict | str) -> Exception:
        message = self._extract_message(error_body)
        details = {"wbStatus": status_code, "wbBody": error_body}
        mapping = {
            400: BadRequestError,
            401: AuthorizationError,
            403: ForbiddenError,
            404: NotFoundError,
            405: MethodNotAllowedError,
            409: ConflictError,
            422: UnprocessableEntityError,
            429: TooManyRequestsError,
            500: InternalServerError,
            502: BadGatewayError,
            503: ServiceUnavailableError,
            504: GatewayTimeoutError,
        }
        exc_cls = mapping.get(status_code)
        if exc_cls is None:
            return UnknownApiError(message=message or "Unknown API error", status_code=status_code, details=details)
        if exc_cls is AuthorizationError:
            return AuthorizationError(message=message or "Unauthorized", details=details)
        return exc_cls(message=message or exc_cls.__name__, details=details)

    @staticmethod
    def _extract_message(error_body: dict | str) -> str:
        if isinstance(error_body, str):
            return error_body
        for key in ("message", "error", "detail"):
            if key in error_body:
                return str(error_body[key])
        return ""
