import re

from backend.app.core.exceptions import BadRequestError

MAX_LIMIT = 10_000
SELECT_RE = re.compile(r"^\s*(with\s+.+\s+select|select)\b", re.IGNORECASE | re.DOTALL)
LIMIT_RE = re.compile(r"\blimit\s+(\d+)\b", re.IGNORECASE)


BLOCKED_KEYWORDS = {
    "insert",
    "update",
    "delete",
    "drop",
    "truncate",
    "alter",
    "create",
    "grant",
    "revoke",
    "merge",
}


def ensure_safe_select(sql: str) -> str:
    normalized = sql.strip()
    if not normalized:
        raise BadRequestError(message="SQL query is empty")

    if ";" in normalized:
        raise BadRequestError(message="Multiple SQL statements are forbidden")

    if not SELECT_RE.match(normalized):
        raise BadRequestError(message="Only SELECT queries are allowed")

    lowered = normalized.lower()
    if any(keyword in lowered for keyword in BLOCKED_KEYWORDS):
        raise BadRequestError(message="DDL/DML statements are forbidden")

    match = LIMIT_RE.search(lowered)
    if match and int(match.group(1)) > MAX_LIMIT:
        raise BadRequestError(message=f"LIMIT exceeds allowed maximum of {MAX_LIMIT}")

    if not match:
        normalized = f"{normalized} LIMIT {MAX_LIMIT}"

    return normalized
