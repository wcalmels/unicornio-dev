from fastapi import Header, HTTPException

from app.config import get_settings


async def verify_api_key(authorization: str | None = Header(default=None)) -> None:
    settings = get_settings()
    if not settings.API_KEY:
        return

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token de autenticación requerido")

    token = authorization.removeprefix("Bearer ").strip()
    if token != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Token de autenticación inválido")
