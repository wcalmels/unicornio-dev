from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.config import get_settings
from app.main import create_app


@pytest.fixture
def authed_app(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-secret-key")
    get_settings.cache_clear()
    yield create_app()
    get_settings.cache_clear()


@pytest.fixture
async def authed_client(authed_app):
    transport = ASGITransport(app=authed_app)
    async with AsyncClient(transport=transport, base_url="http://test") as http_client:
        yield http_client


@pytest.mark.asyncio
async def test_api_key_required(authed_client):
    response = await authed_client.post(
        "/api/v1/refactor/code",
        json={"code": "x = 1"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_invalid_api_key(authed_client):
    response = await authed_client.post(
        "/api/v1/refactor/code",
        json={"code": "x = 1"},
        headers={"Authorization": "Bearer wrong-key"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_valid_api_key(authed_client):
    with patch(
        "app.services.claude.ClaudeService.complete",
        new_callable=AsyncMock,
        return_value="ok",
    ):
        response = await authed_client.post(
            "/api/v1/refactor/code",
            json={"code": "x = 1"},
            headers={"Authorization": "Bearer test-secret-key"},
        )

    assert response.status_code == 200
