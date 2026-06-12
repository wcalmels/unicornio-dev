from fastapi import APIRouter

from app.routers import ai, auth, health, projects, queries

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(projects.router)
api_router.include_router(queries.router)
api_router.include_router(ai.router)
