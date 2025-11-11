"""
Сервис аутентификации
"""

from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import Token


class AuthService:
    """Сервис для работы с аутентификацией"""

    async def authenticate_user(
        self, db: AsyncSession, username: str, password: str
    ) -> User | None:
        """Аутентификация пользователя"""
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        if not user.is_active:
            return None

        return user

    async def create_user(
        self, db: AsyncSession, username: str, email: str, password: str
    ) -> User:
        """Создание нового пользователя"""
        hashed_password = get_password_hash(password)

        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user

    async def get_user_by_username(
        self, db: AsyncSession, username: str
    ) -> User | None:
        """Получение пользователя по username"""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, db: AsyncSession, email: str) -> User | None:
        """Получение пользователя по email"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> User | None:
        """Получение пользователя по ID"""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    def create_tokens(self, user_id: int) -> Token:
        """Создание access и refresh токенов"""
        access_token = create_access_token(subject=user_id)
        refresh_token = create_refresh_token(subject=user_id)

        return Token(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )

    async def refresh_access_token(
        self, db: AsyncSession, refresh_token: str
    ) -> Token | None:
        """Обновление access токена используя refresh токен"""
        try:
            payload = decode_token(refresh_token)

            if payload.get("type") != "refresh":
                return None

            sub = payload.get("sub")
            if sub is None:
                return None

            user_id = int(sub)
            user = await self.get_user_by_id(db, user_id)

            if not user or not user.is_active:
                return None

            return self.create_tokens(user_id)

        except (JWTError, ValueError):
            return None


# Singleton instance
auth_service = AuthService()
