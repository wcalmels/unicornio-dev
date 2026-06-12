from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas.auth import LoginReq, RegisterReq, TokenResponse, UserResponse
from app.services.auth import authenticate_user, create_access_token, create_user, get_user_by_email

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(req: RegisterReq, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    existing = await get_user_by_email(db, req.email)
    if existing:
        raise HTTPException(status_code=409, detail="El email ya está registrado")

    user = await create_user(db, req.email, req.name, req.password)
    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginReq, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    user = await authenticate_user(db, req.email, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        plan=current_user.plan,
        created_at=current_user.created_at,
    )
