"""
Pydantic schemas
"""
from app.schemas.achievement import (
    AchievementBase,
    AchievementPublic,
    UserAchievementPublic,
)
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    Token,
    TokenPayload,
)
from app.schemas.game import (
    GameCreate,
    GameDetail,
    GameJoinResponse,
    GameListResponse,
    GameMoveRequest,
    GameMoveResponse,
    GameParticipantDetail,
    GameParticipantPublic,
    GamePublic,
    GameUpdate,
)
from app.schemas.user import (
    UserCreate,
    UserInDB,
    UserProfile,
    UserPublic,
    UserStats,
    UserUpdate,
)

__all__ = [
    # Auth
    "Token",
    "TokenPayload",
    "LoginRequest",
    "RegisterRequest",
    "RefreshTokenRequest",
    # User
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "UserPublic",
    "UserProfile",
    "UserStats",
    # Game
    "GameCreate",
    "GameUpdate",
    "GamePublic",
    "GameDetail",
    "GameParticipantPublic",
    "GameParticipantDetail",
    "GameJoinResponse",
    "GameMoveRequest",
    "GameMoveResponse",
    "GameListResponse",
    # Achievement
    "AchievementBase",
    "AchievementPublic",
    "UserAchievementPublic",
]
