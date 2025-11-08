"""
Схемы для пользователей
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    """Базовая схема пользователя"""
    username: str
    email: EmailStr


class UserCreate(UserBase):
    """Схема создания пользователя"""
    password: str


class UserUpdate(BaseModel):
    """Схема обновления пользователя"""
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None


class UserInDB(UserBase):
    """Схема пользователя в БД"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime


class UserPublic(BaseModel):
    """Публичная схема пользователя (для других игроков)"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    total_games: int
    total_wins: int
    best_time: int | None
    best_steps: int | None


class UserProfile(UserPublic):
    """Профиль пользователя (расширенная информация)"""
    model_config = ConfigDict(from_attributes=True)
    
    email: EmailStr
    created_at: datetime


class UserStats(BaseModel):
    """Статистика пользователя"""
    model_config = ConfigDict(from_attributes=True)
    
    total_games: int
    total_wins: int
    win_rate: float
    best_time: int | None
    best_steps: int | None
    average_steps: float | None
    average_time: float | None
