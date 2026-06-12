from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_architect_analyze(client):
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
        )

    assert response.status_code == 200
    data = response.json()
    assert data["project"] == "Mi App"
    assert data["analysis"] == "Análisis de arquitectura"


@pytest.mark.asyncio
async def test_refactor_code(client):
    with patch(
        "app.services.claude.ClaudeService.complete",
        new_callable=AsyncMock,
        return_value="Código refactorizado",
    ):
        response = await client.post(
            "/api/v1/refactor/code",
            json={"code": "def foo(): pass", "language": "python"},
        )

    assert response.status_code == 200
    assert response.json()["result"] == "Código refactorizado"


@pytest.mark.asyncio
async def test_debug_solve(client):
    with patch(
        "app.services.claude.ClaudeService.complete",
        new_callable=AsyncMock,
        return_value="Solución al error",
    ):
        response = await client.post(
            "/api/v1/debug/solve",
            json={"error": "KeyError: 'id'", "context": "al leer usuario"},
        )

    assert response.status_code == 200
    assert response.json()["solution"] == "Solución al error"


@pytest.mark.asyncio
async def test_security_audit(client):
    with patch(
        "app.services.claude.ClaudeService.complete",
        new_callable=AsyncMock,
        return_value="Sin vulnerabilidades críticas",
    ):
        response = await client.post(
            "/api/v1/security/audit",
            json={"code": "eval(user_input)", "language": "python"},
        )

    assert response.status_code == 200
    assert "audit" in response.json()


@pytest.mark.asyncio
async def test_performance_analyze(client):
    with patch(
        "app.services.claude.ClaudeService.complete",
        new_callable=AsyncMock,
        return_value="O(n²) detectado",
    ):
        response = await client.post(
            "/api/v1/performance/analyze",
            json={"code": "for i in range(n):\n  for j in range(n): pass"},
        )

    assert response.status_code == 200
    assert response.json()["analysis"] == "O(n²) detectado"


@pytest.mark.asyncio
async def test_validation_rejects_empty_code(client):
    response = await client.post(
        "/api/v1/refactor/code",
        json={"code": "", "language": "python"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_claude_not_configured(client, monkeypatch):
    monkeypatch.setenv("CLAUDE_API_KEY", "")
    from app.config import get_settings

    get_settings.cache_clear()
    response = await client.post(
        "/api/v1/refactor/code",
        json={"code": "x = 1"},
    )
    assert response.status_code == 503
    get_settings.cache_clear()
