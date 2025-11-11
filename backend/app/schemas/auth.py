"""
Схемы для аутентификации
"""
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """Схема токена"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Схема payload токена"""

    sub: int
    exp: int
    type: str


class LoginRequest(BaseModel):
    """Схема запроса на вход"""

    username: str
    password: str


class RegisterRequest(BaseModel):
    """Схема запроса на регистрацию"""

    username: str
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Схема запроса на обновление токена"""

    refresh_token: str
