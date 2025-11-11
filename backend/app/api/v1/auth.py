"""
Endpoints для аутентификации
"""
from fastapi import APIRouter, HTTPException, status

from app.api.deps import DBSession
from app.schemas.auth import LoginRequest, RefreshTokenRequest, RegisterRequest, Token
from app.schemas.user import UserProfile
from app.services.auth_service import auth_service

router = APIRouter()


@router.post(
    "/register", response_model=UserProfile, status_code=status.HTTP_201_CREATED
)
async def register(
    request: RegisterRequest,
    db: DBSession,
):
    """Регистрация нового пользователя"""
    # Проверяем существование пользователя
    existing_user = await auth_service.get_user_by_username(db, request.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует",
        )

    existing_email = await auth_service.get_user_by_email(db, request.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email уже используется"
        )

    # Создаем пользователя
    user = await auth_service.create_user(
        db=db, username=request.username, email=request.email, password=request.password
    )

    return user


@router.post("/login", response_model=Token)
async def login(
    request: LoginRequest,
    db: DBSession,
):
    """Вход в систему"""
    user = await auth_service.authenticate_user(db, request.username, request.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return auth_service.create_tokens(user.id)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: RefreshTokenRequest,
    db: DBSession,
):
    """Обновление access токена"""
    tokens = await auth_service.refresh_access_token(db, request.refresh_token)

    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный refresh токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return tokens
