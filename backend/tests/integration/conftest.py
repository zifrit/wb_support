import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client
