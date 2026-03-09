from backend.app.core.exceptions import TransportError


RETRYABLE_STATUS = {429, 500, 502, 503, 504}


def is_retryable_status(code: int) -> bool:
    return code in RETRYABLE_STATUS


def should_retry(attempt: int, max_retries: int, status_code: int | None = None, error: Exception | None = None) -> bool:
    if attempt >= max_retries:
        return False
    if status_code is not None:
        return is_retryable_status(status_code)
    if error is not None:
        return isinstance(error, TransportError)
    return False
