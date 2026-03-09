import json
import logging
from datetime import datetime, timezone


MASK_KEYS = {"authorization", "x-client-secret", "token", "cookie", "set-cookie"}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base = {
            "ts": datetime.now(tz=timezone.utc).isoformat(),
            "level": record.levelname.lower(),
            "msg": record.getMessage(),
        }
        extra = getattr(record, "extra", None)
        if isinstance(extra, dict):
            base.update(_sanitize_dict(extra))
        return json.dumps(base, ensure_ascii=True)


def _sanitize_dict(data: dict) -> dict:
    sanitized = {}
    for key, value in data.items():
        if key.lower() in MASK_KEYS:
            sanitized[key] = "***"
        elif isinstance(value, dict):
            sanitized[key] = _sanitize_dict(value)
        else:
            sanitized[key] = value
    return sanitized


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
