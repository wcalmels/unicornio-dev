import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.config import get_settings
from app.database import init_db
from app.routers import api_router
from app.routers.ai_v2 import router as api_v2_router
from app.schemas.responses import ErrorResponse

logger = logging.getLogger("unicornio")


def create_app() -> FastAPI:
    settings = get_settings()
    logging.basicConfig(
        level=logging.DEBUG if settings.DEBUG else logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        force=True,
    )

    limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT])

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        await init_db()
        logger.info("Iniciando %s v%s", settings.APP_NAME, settings.APP_VERSION)
        yield
        logger.info("Apagando %s", settings.APP_NAME)

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="API de asistente de desarrollo potenciada por Claude AI.",
        lifespan=lifespan,
        responses={422: {"model": ErrorResponse}},
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"detail": "Datos de entrada inválidos", "errors": exc.errors()},
        )

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        response = await call_next(request)
        logger.info("%s %s -> %s", request.method, request.url.path, response.status_code)
        return response

    app.include_router(api_router)
    app.include_router(api_v2_router)
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=get_settings().DEBUG,
    )
