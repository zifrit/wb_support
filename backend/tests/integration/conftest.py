import asyncio

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.db.session import init_db


@pytest.fixture
def test_client():
    asyncio.run(init_db())
    with TestClient(app) as client:
        yield client
