from fastapi import APIRouter

from app.routers import ai, health

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(ai.router)
