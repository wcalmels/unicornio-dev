import os
class Settings:
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")
    DEBUG = os.getenv("DEBUG", "True") == "True"
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./unicornio.db")
settings = Settings()
