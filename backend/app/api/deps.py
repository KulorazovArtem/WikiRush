"""
API dependencies
"""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.services.auth_service import auth_service

security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Получение текущего аутентифицированного пользователя"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = decode_token(token)

        if payload.get("type") != "access":
            raise credentials_exception

        sub = payload.get("sub")
        if sub is None:
            raise credentials_exception

        user_id: int = int(sub)

    except (JWTError, ValueError):
        raise credentials_exception

    user = await auth_service.get_user_by_id(db, user_id)

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Неактивный пользователь"
        )

    return user


async def get_current_active_superuser(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Проверка что текущий пользователь - суперпользователь"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав"
        )
    return current_user


# Type aliases for convenience
CurrentUser = Annotated[User, Depends(get_current_user)]
DBSession = Annotated[AsyncSession, Depends(get_db)]
