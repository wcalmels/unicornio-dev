from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_analyze_v2_refactor(client, auth_headers):
    with patch(
        "app.services.claude.ClaudeService.complete",
        new_callable=AsyncMock,
        return_value="Código mejorado v2",
    ):
        response = await client.post(
            "/api/v2/analyze",
            headers=auth_headers,
            json={
                "module": "refactor",
                "files": [{"path": "main.py", "content": "x=1"}],
                "context": {"language": "python"},
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["module"] == "refactor"
    assert data["result"] == "Código mejorado v2"
    assert data["files_analyzed"] == ["main.py"]


@pytest.mark.asyncio
async def test_analyze_v2_architect(client, auth_headers):
    with patch(
        "app.services.claude.ClaudeService.complete",
        new_callable=AsyncMock,
        return_value="Arquitectura propuesta",
    ):
        response = await client.post(
            "/api/v2/analyze",
            headers=auth_headers,
            json={
                "module": "architect",
                "files": [],
                "context": {
                    "project_name": "SaaS",
                    "description": "Plataforma de tareas",
                },
            },
        )

    assert response.status_code == 200
    assert response.json()["result"] == "Arquitectura propuesta"


@pytest.mark.asyncio
async def test_analyze_v2_requires_files_for_refactor(client, auth_headers):
    response = await client.post(
        "/api/v2/analyze",
        headers=auth_headers,
        json={"module": "refactor", "files": [], "context": {}},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_analyze_v2_requires_auth(client):
    response = await client.post(
        "/api/v2/analyze",
        json={
            "module": "refactor",
            "files": [{"path": "a.py", "content": "x=1"}],
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_analyze_v2_saves_history(client, auth_headers):
    with patch(
        "app.services.claude.ClaudeService.complete",
        new_callable=AsyncMock,
        return_value="audit v2",
    ):
        await client.post(
            "/api/v2/analyze",
            headers=auth_headers,
            json={
                "module": "security",
                "files": [{"path": "app.py", "content": "eval(x)"}],
                "context": {"language": "python"},
            },
        )

    history = await client.get("/api/v1/queries/history", headers=auth_headers)
    assert history.json()[0]["module"] == "security"


@pytest.mark.asyncio
async def test_analyze_stream_v2(client, auth_headers):
    async def fake_stream(self, prompt):
        yield "Hola "
        yield "mundo"

    with patch("app.services.claude.ClaudeService.stream_complete", fake_stream):
        response = await client.post(
            "/api/v2/analyze/stream",
            headers=auth_headers,
            json={
                "module": "refactor",
                "files": [{"path": "a.py", "content": "x=1"}],
                "context": {"language": "python"},
            },
        )

    assert response.status_code == 200
    body = response.text
    assert "Hola " in body
    assert '"done": true' in body or '"done":true' in body
