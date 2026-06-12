from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_register_and_login(client):
    register = await client.post(
        "/api/v1/auth/register",
        json={"email": "user@test.com", "name": "Test", "password": "password123"},
    )
    assert register.status_code == 201
    assert "access_token" in register.json()

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "user@test.com", "password": "password123"},
    )
    assert login.status_code == 200
    assert "access_token" in login.json()


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    payload = {"email": "dup@test.com", "name": "A", "password": "password123"}
    await client.post("/api/v1/auth/register", json=payload)
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "user@test.com", "name": "Test", "password": "password123"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "user@test.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_requires_auth(client):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_returns_user(client, auth_headers):
    response = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "dev@example.com"
    assert data["name"] == "Dev User"
    assert data["plan"] == "free"


@pytest.mark.asyncio
async def test_ai_requires_auth(client):
    response = await client.post(
        "/api/v1/refactor/code",
        json={"code": "x = 1"},
    )
    assert response.status_code == 401
