"""
Схемы для игр
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.game import GameMode, GameStatus
from app.schemas.user import UserPublic


class GameCreate(BaseModel):
    """Схема создания игры"""
    mode: GameMode
    start_article: str
    target_article: str
    max_steps: int = Field(default=100, ge=1, le=1000)
    time_limit: int = Field(default=300, ge=30, le=3600)  # От 30 секунд до 1 часа
    max_players: int = Field(default=10, ge=1, le=50)


class GameUpdate(BaseModel):
    """Схема обновления игры"""
    status: GameStatus | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None


class GameParticipantBase(BaseModel):
    """Базовая схема участника"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    is_finished: bool
    is_winner: bool
    steps_count: int
    time_taken: int | None
    current_article: str | None
    joined_at: datetime


class GameParticipantPublic(GameParticipantBase):
    """Публичная информация об участнике"""
    user: UserPublic


class GameParticipantDetail(GameParticipantPublic):
    """Детальная информация об участнике (включая путь)"""
    path: list[str]
    finished_at: datetime | None


class GameBase(BaseModel):
    """Базовая схема игры"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    mode: str
    status: str
    start_article: str
    target_article: str
    max_steps: int
    time_limit: int
    max_players: int
    created_at: datetime


class GamePublic(GameBase):
    """Публичная информация об игре"""
    creator: UserPublic
    participants_count: int = 0


class GameDetail(GameBase):
    """Детальная информация об игре"""
    creator: UserPublic
    participants: list[GameParticipantPublic]
    started_at: datetime | None
    finished_at: datetime | None


class GameJoinResponse(BaseModel):
    """Ответ при присоединении к игре"""
    game_id: int
    participant_id: int
    message: str


class GameMoveRequest(BaseModel):
    """Запрос на ход в игре"""
    article: str


class GameMoveResponse(BaseModel):
    """Ответ на ход в игре"""
    success: bool
    current_article: str
    steps_count: int
    is_target_reached: bool
    message: str | None = None


class GameListResponse(BaseModel):
    """Список игр"""
    games: list[GamePublic]
    total: int
    page: int
    page_size: int
