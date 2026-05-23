"""Application configuration from environment variables."""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/sentinel"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SENTRY_DSN: str = ""
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    class Config:
        env_file = ".env"

settings = Settings()
