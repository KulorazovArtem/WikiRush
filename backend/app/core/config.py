"""
Конфигурация приложения
"""
from typing import Any
from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    # Основные настройки
    PROJECT_NAME: str = "WikiRush"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Безопасность
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # База данных
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "wikirush"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: PostgresDsn | None = None
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None, info: Any) -> str:
        if isinstance(v, str):
            return v
        
        data = info.data
        return str(PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=data.get("POSTGRES_USER"),
            password=data.get("POSTGRES_PASSWORD"),
            host=data.get("POSTGRES_SERVER"),
            port=data.get("POSTGRES_PORT"),
            path=f"{data.get('POSTGRES_DB') or ''}",
        ))
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Wikipedia API
    WIKIPEDIA_API_URL: str = "https://ru.wikipedia.org/w/api.php"
    WIKIPEDIA_RATE_LIMIT: int = 100  # requests per minute
    
    # Game settings
    MAX_STEPS: int = 100  # Максимальное количество переходов в игре
    GAME_TIME_LIMIT: int = 300  # Время на игру в секундах (5 минут)


settings = Settings()
