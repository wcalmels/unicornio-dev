from fastapi import APIRouter

from app.config import get_settings
from app.schemas.responses import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        claude_configured=bool(settings.CLAUDE_API_KEY),
    )
