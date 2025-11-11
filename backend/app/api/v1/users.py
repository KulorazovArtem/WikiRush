"""
Endpoints для пользователей
"""
from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DBSession
from app.schemas.user import UserProfile, UserPublic, UserStats
from app.services.auth_service import auth_service

router = APIRouter()


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: CurrentUser,
):
    """Получение профиля текущего пользователя"""
    return current_user


@router.get("/{user_id}", response_model=UserPublic)
async def get_user(
    user_id: int,
    db: DBSession,
):
    """Получение публичной информации о пользователе"""
    user = await auth_service.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )

    return user


@router.get("/{user_id}/stats", response_model=UserStats)
async def get_user_stats(
    user_id: int,
    db: DBSession,
):
    """Получение статистики пользователя"""
    user = await auth_service.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )

    win_rate = (
        (user.total_wins / user.total_games * 100) if user.total_games > 0 else 0.0
    )

    return UserStats(
        total_games=user.total_games,
        total_wins=user.total_wins,
        win_rate=round(win_rate, 2),
        best_time=user.best_time,
        best_steps=user.best_steps,
        average_steps=None,  # TODO: calculate from game history
        average_time=None,  # TODO: calculate from game history
    )
