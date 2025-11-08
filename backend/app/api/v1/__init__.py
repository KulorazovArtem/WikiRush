"""
API v1 router
"""
from fastapi import APIRouter

from app.api.v1 import auth, games, leaderboard, users

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(games.router, prefix="/games", tags=["games"])
api_router.include_router(leaderboard.router, prefix="/leaderboard", tags=["leaderboard"])
