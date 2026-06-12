from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "Unicornio Dev API"
    APP_VERSION: str = "1.1.0"
    DEBUG: bool = False

    DATABASE_URL: str = "sqlite+aiosqlite:///./unicornio.db"
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7

    CLAUDE_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"
    CLAUDE_API_URL: str = "https://api.anthropic.com/v1/messages"
    CLAUDE_MAX_TOKENS: int = 4000
    CLAUDE_TIMEOUT_SECONDS: int = 60

    API_KEY: str = ""
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    RATE_LIMIT: str = "30/minute"


@lru_cache
def get_settings() -> Settings:
    return Settings()
