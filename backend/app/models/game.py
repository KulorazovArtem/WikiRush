"""
Модели для игр
"""
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class GameMode(str, Enum):
    """Режимы игры"""

    SINGLE = "single"  # Одиночная игра
    MULTIPLAYER = "multiplayer"  # Соревнование
    COOPERATIVE = "cooperative"  # Кооператив


class GameStatus(str, Enum):
    """Статусы игры"""

    WAITING = "waiting"  # Ожидание игроков
    IN_PROGRESS = "in_progress"  # Игра идет
    FINISHED = "finished"  # Игра завершена
    CANCELLED = "cancelled"  # Игра отменена


class Game(Base):
    """Модель игры"""

    __tablename__ = "games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Настройки игры
    mode: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default=GameStatus.WAITING.value, nullable=False
    )

    # Статьи
    start_article: Mapped[str] = mapped_column(String(255), nullable=False)
    target_article: Mapped[str] = mapped_column(String(255), nullable=False)

    # Ограничения
    max_steps: Mapped[int] = mapped_column(Integer, nullable=False)
    time_limit: Mapped[int] = mapped_column(Integer, nullable=False)  # В секундах
    max_players: Mapped[int] = mapped_column(Integer, default=10, nullable=False)

    # Создатель
    creator_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Временные метки
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    creator: Mapped["User"] = relationship(
        "User", back_populates="created_games", foreign_keys=[creator_id]
    )

    participants: Mapped[list["GameParticipant"]] = relationship(
        "GameParticipant", back_populates="game", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Game(id={self.id}, mode='{self.mode}', status='{self.status}')>"


class GameParticipant(Base):
    """Модель участника игры"""

    __tablename__ = "game_participants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Связи
    game_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Результаты
    is_finished: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_winner: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    steps_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    time_taken: Mapped[int | None] = mapped_column(Integer, nullable=True)  # В секундах

    # Путь (список посещенных статей)
    path: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    # Прогресс соперника (видимость для других игроков)
    current_article: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Временные метки
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    game: Mapped["Game"] = relationship("Game", back_populates="participants")
    user: Mapped["User"] = relationship("User", back_populates="game_participations")

    def __repr__(self) -> str:
        return f"<GameParticipant(game_id={self.game_id}, user_id={self.user_id})>"
