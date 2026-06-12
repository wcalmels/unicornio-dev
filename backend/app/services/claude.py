import httpx
from fastapi import HTTPException

from app.config import get_settings


class ClaudeService:
    async def complete(self, prompt: str) -> str:
        settings = get_settings()
        if not settings.CLAUDE_API_KEY:
            raise HTTPException(
                status_code=503,
                detail="CLAUDE_API_KEY no configurada en .env",
            )

        try:
            async with httpx.AsyncClient(timeout=settings.CLAUDE_TIMEOUT_SECONDS) as client:
                response = await client.post(
                    settings.CLAUDE_API_URL,
                    headers={
                        "x-api-key": settings.CLAUDE_API_KEY,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": settings.CLAUDE_MODEL,
                        "max_tokens": settings.CLAUDE_MAX_TOKENS,
                        "messages": [{"role": "user", "content": prompt}],
                    },
                )
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=502,
                detail="No se pudo conectar con la API de Claude",
            ) from exc

        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Claude API respondió con error ({response.status_code})",
            )

        try:
            return response.json()["content"][0]["text"]
        except (KeyError, IndexError, ValueError) as exc:
            raise HTTPException(
                status_code=502,
                detail="Respuesta inesperada de la API de Claude",
            ) from exc


def get_claude_service() -> ClaudeService:
    return ClaudeService()
