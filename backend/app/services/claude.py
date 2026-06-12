import json
from collections.abc import AsyncGenerator

import httpx
from fastapi import HTTPException

from app.config import get_settings


class ClaudeService:
    def _headers(self, settings) -> dict[str, str]:
        return {
            "x-api-key": settings.CLAUDE_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

    def _ensure_configured(self) -> None:
        if not get_settings().CLAUDE_API_KEY:
            raise HTTPException(
                status_code=503,
                detail="CLAUDE_API_KEY no configurada en .env",
            )

    async def complete(self, prompt: str) -> str:
        settings = get_settings()
        self._ensure_configured()

        try:
            async with httpx.AsyncClient(timeout=settings.CLAUDE_TIMEOUT_SECONDS) as client:
                response = await client.post(
                    settings.CLAUDE_API_URL,
                    headers=self._headers(settings),
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

    async def stream_complete(self, prompt: str) -> AsyncGenerator[str, None]:
        settings = get_settings()
        self._ensure_configured()

        try:
            async with httpx.AsyncClient(timeout=settings.CLAUDE_TIMEOUT_SECONDS) as client:
                async with client.stream(
                    "POST",
                    settings.CLAUDE_API_URL,
                    headers=self._headers(settings),
                    json={
                        "model": settings.CLAUDE_MODEL,
                        "max_tokens": settings.CLAUDE_MAX_TOKENS,
                        "stream": True,
                        "messages": [{"role": "user", "content": prompt}],
                    },
                ) as response:
                    if response.status_code != 200:
                        body = await response.aread()
                        raise HTTPException(
                            status_code=502,
                            detail=f"Claude API respondió con error ({response.status_code}): "
                            f"{body.decode(errors='replace')[:200]}",
                        )

                    async for line in response.aiter_lines():
                        if not line.startswith("data:"):
                            continue
                        payload = line.removeprefix("data:").strip()
                        if not payload or payload == "[DONE]":
                            continue
                        try:
                            event = json.loads(payload)
                        except json.JSONDecodeError:
                            continue
                        if event.get("type") != "content_block_delta":
                            continue
                        delta = event.get("delta", {})
                        if delta.get("type") == "text_delta":
                            text = delta.get("text", "")
                            if text:
                                yield text
        except HTTPException:
            raise
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=502,
                detail="No se pudo conectar con la API de Claude",
            ) from exc


def get_claude_service() -> ClaudeService:
    return ClaudeService()
