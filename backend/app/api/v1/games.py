"""
Endpoints для игр
"""
from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
    status,
)

from app.api.deps import CurrentUser, DBSession
from app.models.game import GameMode, GameStatus
from app.schemas.game import (
    GameCreate,
    GameDetail,
    GameJoinResponse,
    GameListResponse,
    GameMoveRequest,
    GameMoveResponse,
    GamePublic,
)
from app.services.game_service import game_service
from app.services.websocket_service import websocket_manager
from app.services.wikipedia_service import wikipedia_service

router = APIRouter()


@router.post("", response_model=GameDetail, status_code=status.HTTP_201_CREATED)
async def create_game(
    game_data: GameCreate,
    current_user: CurrentUser,
    db: DBSession,
):
    """Создание новой игры"""
    try:
        game = await game_service.create_game(
            db=db,
            creator_id=current_user.id,
            mode=game_data.mode,
            start_article=game_data.start_article,
            target_article=game_data.target_article,
            max_steps=game_data.max_steps,
            time_limit=game_data.time_limit,
            max_players=game_data.max_players,
        )

        return game

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=GameListResponse)
async def list_games(
    db: DBSession,
    status_filter: GameStatus | None = Query(None, alias="status"),
    mode: GameMode | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """Получение списка игр"""
    skip = (page - 1) * page_size

    games, total = await game_service.list_games(
        db=db,
        status=status_filter,
        mode=mode,
        skip=skip,
        limit=page_size,
    )

    games_public = [
        GamePublic(**game.__dict__, participants_count=len(game.participants))
        for game in games
    ]

    return GameListResponse(
        games=games_public,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/random-articles")
async def get_random_articles():
    """Получить случайные начальную и целевую статьи с гарантированным путём между ними"""
    import random

    start_article = await wikipedia_service.get_random_article()

    if not start_article:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось получить случайную начальную статью",
        )

    # Генерируем целевую статью, достижимую за 2-3 перехода
    depth = random.randint(2, 3)
    target_article = None
    max_attempts = 3

    for _ in range(max_attempts):
        target_article = await wikipedia_service.get_reachable_article_at_depth(
            start_article, depth
        )
        if target_article and target_article != start_article:
            break

    if not target_article or target_article == start_article:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось найти достижимую целевую статью",
        )

    return {
        "start_article": start_article,
        "target_article": target_article,
        "min_steps": depth,  # Минимальное количество шагов до цели
    }


@router.get("/{game_id}", response_model=GameDetail)
async def get_game(
    game_id: int,
    db: DBSession,
):
    """Получение информации об игре"""
    game = await game_service.get_game(db, game_id)

    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Игра не найдена"
        )

    return game


@router.get("/{game_id}/available-links")
async def get_available_links(
    game_id: int,
    current_user: CurrentUser,
    db: DBSession,
):
    """Получить доступные ссылки из текущей статьи игрока"""
    # Получаем игру
    game = await game_service.get_game(db, game_id)

    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Игра не найдена"
        )

    # Находим участника
    from sqlalchemy import select
    from app.models.game import GameParticipant

    result = await db.execute(
        select(GameParticipant).where(
            GameParticipant.game_id == game_id,
            GameParticipant.user_id == current_user.id,
        )
    )
    participant = result.scalar_one_or_none()

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы не участвуете в этой игре",
        )

    # Получаем текущую статью
    current_article = participant.current_article or game.start_article

    # Получаем доступные ссылки
    links = await wikipedia_service.get_article_links(current_article, limit=100)

    return {
        "current_article": current_article,
        "target_article": game.target_article,
        "available_links": links,
        "total_links": len(links),
    }


@router.post("/{game_id}/join", response_model=GameJoinResponse)
async def join_game(
    game_id: int,
    current_user: CurrentUser,
    db: DBSession,
):
    """Присоединение к игре"""
    try:
        participant = await game_service.join_game(db, game_id, current_user.id)

        # Уведомляем других игроков
        await websocket_manager.notify_player_joined(game_id, current_user.username)

        return GameJoinResponse(
            game_id=game_id,
            participant_id=participant.id,
            message="Вы успешно присоединились к игре",
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{game_id}/start")
async def start_game(
    game_id: int,
    current_user: CurrentUser,
    db: DBSession,
):
    """Запуск игры (только создатель)"""
    game = await game_service.get_game(db, game_id)

    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Игра не найдена"
        )

    if game.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только создатель может запустить игру",
        )

    try:
        game = await game_service.start_game(db, game_id)

        # Уведомляем всех игроков
        await websocket_manager.notify_game_started(game_id)

        return {"message": "Игра началась", "game_id": game_id}

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{game_id}/move", response_model=GameMoveResponse)
async def make_move(
    game_id: int,
    move_data: GameMoveRequest,
    current_user: CurrentUser,
    db: DBSession,
):
    """Совершить ход (перейти на статью)"""
    try:
        participant, is_winner = await game_service.make_move(
            db=db,
            game_id=game_id,
            user_id=current_user.id,
            article=move_data.article,
        )

        # Уведомляем других игроков о ходе
        await websocket_manager.notify_player_move(
            game_id=game_id,
            username=current_user.username,
            article=move_data.article,
            steps=participant.steps_count,
        )

        # Если победа - уведомляем
        if is_winner:
            await websocket_manager.notify_player_won(
                game_id=game_id,
                username=current_user.username,
                time=participant.time_taken or 0,
                steps=participant.steps_count,
            )

        return GameMoveResponse(
            success=True,
            current_article=participant.current_article or "",
            steps_count=participant.steps_count,
            is_target_reached=is_winner,
            message="Победа! Вы достигли цели!" if is_winner else None,
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.websocket("/{game_id}/ws")
async def game_websocket(
    websocket: WebSocket,
    game_id: int,
    db: DBSession,
):
    """WebSocket для real-time обновлений игры"""
    # Проверяем существование игры
    game = await game_service.get_game(db, game_id)

    if not game:
        await websocket.close(code=1008, reason="Game not found")
        return

    # Подключаемся
    await websocket_manager.connect(websocket, game_id)

    try:
        while True:
            # Просто держим соединение открытым
            # Все сообщения отправляются через websocket_manager
            _ = await websocket.receive_text()

            # Можно обрабатывать входящие сообщения от клиента
            # Например, ping/pong для keep-alive

    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, game_id)
