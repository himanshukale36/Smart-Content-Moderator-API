import asyncio

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db import init_db


@pytest.fixture(scope="module")
def client():
    asyncio.run(init_db())
    with TestClient(app) as c:
        yield c


def test_moderate_text(client):
    response = client.post(
        "/api/v1/moderate/text",
        json={"email": "test@example.com", "text": "This is safe"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["classification"] in {"safe", "toxic", "spam", "harassment", "error"}
    assert "request_id" in data
