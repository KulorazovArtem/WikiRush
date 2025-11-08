"""
Схемы для достижений
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AchievementBase(BaseModel):
    """Базовая схема достижения"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    code: str
    name: str
    description: str
    icon: str | None


class AchievementPublic(AchievementBase):
    """Публичная схема достижения"""
    pass


class UserAchievementPublic(BaseModel):
    """Схема достижения пользователя"""
    model_config = ConfigDict(from_attributes=True)
    
    achievement: AchievementPublic
    unlocked_at: datetime
