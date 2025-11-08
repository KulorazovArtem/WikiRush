"""
Endpoints для таблицы лидеров
"""
from fastapi import APIRouter, Query

from app.api.deps import DBSession
from app.schemas.user import UserPublic
from app.services.game_service import game_service

router = APIRouter()


@router.get("", response_model=list[UserPublic])
async def get_leaderboard(
    db: DBSession,
    limit: int = Query(100, ge=1, le=1000),
):
    """Получение таблицы лидеров"""
    users = await game_service.get_leaderboard(db, limit)
    return users
