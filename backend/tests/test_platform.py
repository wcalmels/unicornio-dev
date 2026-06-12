import pytest


@pytest.mark.asyncio
async def test_create_and_list_projects(client, auth_headers):
    create = await client.post(
        "/api/v1/projects",
        json={"name": "Mi API", "description": "Backend FastAPI"},
        headers=auth_headers,
    )
    assert create.status_code == 201
    project = create.json()
    assert project["name"] == "Mi API"

    listing = await client.get("/api/v1/projects", headers=auth_headers)
    assert listing.status_code == 200
    assert len(listing.json()) == 1


@pytest.mark.asyncio
async def test_projects_require_auth(client):
    response = await client.get("/api/v1/projects")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_history_isolated_per_user(client):
    user_a = await client.post(
        "/api/v1/auth/register",
        json={"email": "a@test.com", "name": "A", "password": "password123"},
    )
    user_b = await client.post(
        "/api/v1/auth/register",
        json={"email": "b@test.com", "name": "B", "password": "password123"},
    )
    headers_a = {"Authorization": f"Bearer {user_a.json()['access_token']}"}
    headers_b = {"Authorization": f"Bearer {user_b.json()['access_token']}"}

    from unittest.mock import AsyncMock, patch

    with patch(
        "app.services.claude.ClaudeService.complete",
        new_callable=AsyncMock,
        return_value="solo para A",
    ):
        await client.post(
            "/api/v1/refactor/code",
            json={"code": "a=1"},
            headers=headers_a,
        )

    history_b = await client.get("/api/v1/queries/history", headers=headers_b)
    assert history_b.json() == []

    history_a = await client.get("/api/v1/queries/history", headers=headers_a)
    assert len(history_a.json()) == 1
