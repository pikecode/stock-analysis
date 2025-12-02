"""Application configuration."""
from __future__ import annotations

from functools import lru_cache
from typing import List, Optional

from pydantic import field_validator, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    model_config = ConfigDict(
        extra='ignore',
        env_file='.env',
        case_sensitive=True
    )

    # App
    APP_NAME: str = "Stock Analysis API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/stock_analysis"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS - comma separated string (stored internally)
    _cors_origins_str: str = "http://localhost:3000,http://localhost:5173"
    ALLOWED_HOSTS: str = "*"

    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Get CORS origins as a list."""
        origins = getattr(self, '_cors_origins_str', "http://localhost:3000,http://localhost:5173")
        # If it comes from env with name CORS_ORIGINS, try to parse it
        if hasattr(self, '__dict__') and 'CORS_ORIGINS' in self.__dict__:
            origins = self.__dict__['CORS_ORIGINS']
        return [o.strip() for o in origins.split(",") if o.strip()]

    def __init__(self, **data):
        # Handle CORS_ORIGINS from env
        if 'CORS_ORIGINS' in data:
            data['_cors_origins_str'] = data.pop('CORS_ORIGINS')
        super().__init__(**data)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
