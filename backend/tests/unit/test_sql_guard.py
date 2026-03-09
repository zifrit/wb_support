import pytest

from backend.app.core.exceptions import BadRequestError
from backend.app.internal_db.sql_guard import ensure_safe_select


def test_allow_simple_select_and_auto_limit():
    sql = ensure_safe_select("select 1")
    assert "LIMIT 10000" in sql


def test_reject_non_select():
    with pytest.raises(BadRequestError):
        ensure_safe_select("update users set a=1")


def test_reject_multiple_statements():
    with pytest.raises(BadRequestError):
        ensure_safe_select("select 1; select 2")


def test_reject_large_limit():
    with pytest.raises(BadRequestError):
        ensure_safe_select("select * from x limit 50000")
