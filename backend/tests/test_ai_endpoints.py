from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_architect_analyze(client, auth_headers):
    with patch(
        "app.services.claude.ClaudeService.complete",
        new_callable=AsyncMock,
        return_value="Análisis de arquitectura",
    ):
        response = await client.post(
            "/api/v1/architect/analyze",
            json={
                "project_name": "Mi App",
                "description": "API REST para gestión de tareas",
            },
            headers=auth_headers,
        )

    assert response.status_code == 200
    data = response.json()
    assert data["project"] == "Mi App"
    assert data["analysis"] == "Análisis de arquitectura"


@pytest.mark.asyncio
async def test_refactor_code(client, auth_headers):
    with patch(
        "app.services.claude.ClaudeService.complete",
        new_callable=AsyncMock,
        return_value="Código refactorizado",
    ):
        response = await client.post(
            "/api/v1/refactor/code",
            json={"code": "def foo(): pass", "language": "python"},
            headers=auth_headers,
        )

    assert response.status_code == 200
    assert response.json()["result"] == "Código refactorizado"


@pytest.mark.asyncio
async def test_debug_solve(client, auth_headers):
    with patch(
        "app.services.claude.ClaudeService.complete",
        new_callable=AsyncMock,
        return_value="Solución al error",
    ):
        response = await client.post(
            "/api/v1/debug/solve",
            json={"error": "KeyError: 'id'", "context": "al leer usuario"},
            headers=auth_headers,
        )

    assert response.status_code == 200
    assert response.json()["solution"] == "Solución al error"


@pytest.mark.asyncio
async def test_security_audit(client, auth_headers):
    with patch(
        "app.services.claude.ClaudeService.complete",
        new_callable=AsyncMock,
        return_value="Sin vulnerabilidades críticas",
    ):
        response = await client.post(
            "/api/v1/security/audit",
            json={"code": "eval(user_input)", "language": "python"},
            headers=auth_headers,
        )

    assert response.status_code == 200
    assert "audit" in response.json()


@pytest.mark.asyncio
async def test_performance_analyze(client, auth_headers):
    with patch(
        "app.services.claude.ClaudeService.complete",
        new_callable=AsyncMock,
        return_value="O(n²) detectado",
    ):
        response = await client.post(
            "/api/v1/performance/analyze",
            json={"code": "for i in range(n):\n  for j in range(n): pass"},
            headers=auth_headers,
        )

    assert response.status_code == 200
    assert response.json()["analysis"] == "O(n²) detectado"


@pytest.mark.asyncio
async def test_validation_rejects_empty_code(client, auth_headers):
    response = await client.post(
        "/api/v1/refactor/code",
        json={"code": "", "language": "python"},
        headers=auth_headers,
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_claude_not_configured(client, auth_headers, monkeypatch):
    monkeypatch.setenv("CLAUDE_API_KEY", "")
    get_settings = __import__("app.config", fromlist=["get_settings"]).get_settings
    get_settings.cache_clear()

    response = await client.post(
        "/api/v1/refactor/code",
        json={"code": "x = 1"},
        headers=auth_headers,
    )
    assert response.status_code == 503
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_query_saved_to_history(client, auth_headers):
    with patch(
        "app.services.claude.ClaudeService.complete",
        new_callable=AsyncMock,
        return_value="resultado guardado",
    ):
        await client.post(
            "/api/v1/refactor/code",
            json={"code": "x=1", "language": "python"},
            headers=auth_headers,
        )

    history = await client.get("/api/v1/queries/history", headers=auth_headers)
    assert history.status_code == 200
    items = history.json()
    assert len(items) == 1
    assert items[0]["module"] == "refactor"
    assert items[0]["output_text"] == "resultado guardado"
