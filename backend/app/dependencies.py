from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models import User
from app.services.auth import decode_access_token


async def get_current_user(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token de autenticación requerido")

    token = authorization.removeprefix("Bearer ").strip()
    settings = get_settings()

    if settings.API_KEY and token == settings.API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Usa un token JWT de usuario. Inicia sesión en /api/v1/auth/login",
        )

    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    return user
