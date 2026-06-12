import os

import pytest
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("RATE_LIMIT", "1000/minute")
os.environ.setdefault("API_KEY", "")

from app.main import app  # noqa: E402


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as http_client:
        yield http_client
