"""
Настройка базы данных и сессий
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """Базовый класс для моделей"""

    pass


# Создание async engine
engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=True,
    future=True,
    pool_pre_ping=True,
)

# Создание фабрики сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency для получения сессии БД"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Инициализация базы данных"""
    async with engine.begin() as conn:
        # Импортируем все модели чтобы Base.metadata был заполнен
        from app.models import user, game, achievement  # noqa

        # Создаем таблицы
        await conn.run_sync(Base.metadata.create_all)
