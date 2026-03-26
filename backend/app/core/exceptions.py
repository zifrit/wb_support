class AppError(Exception):
    def __init__(self, message: str, status_code: int = 500, error_type: str = "APP_ERROR", details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_type = error_type
        self.details = details or {}


class CredentialsNotFound(AppError):
    def __init__(self, message: str = "Credentials not found"):
        super().__init__(message=message, status_code=401, error_type="USER_TOKEN_NOT_FOUND")


class PermissionDeniedError(AppError):
    def __init__(self, message: str = "Permission denied", details: dict | None = None):
        super().__init__(message=message, status_code=403, error_type="PERMISSION_DENIED_ERROR", details=details)


class AuthorizationError(AppError):
    def __init__(self, message: str = "Unauthorized", details: dict | None = None):
        super().__init__(message=message, status_code=401, error_type="AUTHORIZATION_ERROR", details=details)


class ForbiddenError(AppError):
    def __init__(self, message: str = "Forbidden", details: dict | None = None):
        super().__init__(message=message, status_code=403, error_type="FORBIDDEN", details=details)


class BadRequestError(AppError):
    def __init__(self, message: str = "Bad request", details: dict | None = None):
        super().__init__(message=message, status_code=400, error_type="BAD_REQUEST", details=details)


class NotFoundError(AppError):
    def __init__(self, message: str = "Not found", details: dict | None = None):
        super().__init__(message=message, status_code=404, error_type="NOT_FOUND", details=details)


class MethodNotAllowedError(AppError):
    def __init__(self, message: str = "Method not allowed", details: dict | None = None):
        super().__init__(message=message, status_code=405, error_type="METHOD_NOT_ALLOWED", details=details)


class ConflictError(AppError):
    def __init__(self, message: str = "Conflict", details: dict | None = None):
        super().__init__(message=message, status_code=409, error_type="CONFLICT", details=details)


class UnprocessableEntityError(AppError):
    def __init__(self, message: str = "Unprocessable entity", details: dict | None = None):
        super().__init__(message=message, status_code=422, error_type="UNPROCESSABLE_ENTITY", details=details)


class TooManyRequestsError(AppError):
    def __init__(self, message: str = "Too many requests", details: dict | None = None):
        super().__init__(message=message, status_code=429, error_type="TOO_MANY_REQUESTS", details=details)


class InternalServerError(AppError):
    def __init__(self, message: str = "Internal server error", details: dict | None = None):
        super().__init__(message=message, status_code=500, error_type="INTERNAL_SERVER_ERROR", details=details)


class BadGatewayError(AppError):
    def __init__(self, message: str = "Bad gateway", details: dict | None = None):
        super().__init__(message=message, status_code=502, error_type="BAD_GATEWAY", details=details)


class ServiceUnavailableError(AppError):
    def __init__(self, message: str = "Service unavailable", details: dict | None = None):
        super().__init__(message=message, status_code=503, error_type="SERVICE_UNAVAILABLE", details=details)


class GatewayTimeoutError(AppError):
    def __init__(self, message: str = "Gateway timeout", details: dict | None = None):
        super().__init__(message=message, status_code=504, error_type="GATEWAY_TIMEOUT", details=details)


class UnknownApiError(AppError):
    def __init__(self, message: str = "Unknown API error", status_code: int = 500, details: dict | None = None):
        super().__init__(message=message, status_code=status_code, error_type="UNKNOWN_API_ERROR", details=details)


class TransportError(AppError):
    def __init__(self, message: str = "Transport error", status_code: int = 502, details: dict | None = None):
        super().__init__(message=message, status_code=status_code, error_type="TRANSPORT_ERROR", details=details)
