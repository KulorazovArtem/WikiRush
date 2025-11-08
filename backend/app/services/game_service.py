"""
Сервис для работы с играми
"""
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.game import Game, GameMode, GameParticipant, GameStatus
from app.models.user import User
from app.services.wikipedia_service import wikipedia_service


class GameService:
    """Сервис для работы с играми"""
    
    async def create_game(
        self,
        db: AsyncSession,
        creator_id: int,
        mode: GameMode,
        start_article: str,
        target_article: str,
        max_steps: int,
        time_limit: int,
        max_players: int
    ) -> Game:
        """Создание новой игры"""
        # Проверяем существование статей
        start_exists = await wikipedia_service.validate_article_exists(start_article)
        target_exists = await wikipedia_service.validate_article_exists(target_article)
        
        if not start_exists:
            raise ValueError(f"Статья '{start_article}' не найдена")
        
        if not target_exists:
            raise ValueError(f"Статья '{target_article}' не найдена")
        
        if start_article == target_article:
            raise ValueError("Начальная и целевая статьи не могут быть одинаковыми")
        
        game = Game(
            mode=mode.value,
            status=GameStatus.WAITING.value,
            start_article=start_article,
            target_article=target_article,
            max_steps=max_steps,
            time_limit=time_limit,
            max_players=max_players,
            creator_id=creator_id,
        )
        
        db.add(game)
        await db.commit()
        await db.refresh(game)
        
        # Автоматически присоединяем создателя
        await self.join_game(db, game.id, creator_id)
        
        return game
    
    async def get_game(self, db: AsyncSession, game_id: int) -> Game | None:
        """Получение игры по ID"""
        result = await db.execute(
            select(Game)
            .options(
                selectinload(Game.creator),
                selectinload(Game.participants).selectinload(GameParticipant.user)
            )
            .where(Game.id == game_id)
        )
        return result.scalar_one_or_none()
    
    async def list_games(
        self,
        db: AsyncSession,
        status: GameStatus | None = None,
        mode: GameMode | None = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[list[Game], int]:
        """Получение списка игр"""
        query = select(Game).options(
            selectinload(Game.creator),
            selectinload(Game.participants)
        )
        
        if status:
            query = query.where(Game.status == status.value)
        
        if mode:
            query = query.where(Game.mode == mode.value)
        
        query = query.order_by(Game.created_at.desc())
        
        # Получаем общее количество
        count_query = select(func.count()).select_from(Game)
        if status:
            count_query = count_query.where(Game.status == status.value)
        if mode:
            count_query = count_query.where(Game.mode == mode.value)
        
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Получаем игры с пагинацией
        result = await db.execute(query.offset(skip).limit(limit))
        games = list(result.scalars().all())
        
        return games, total
    
    async def join_game(
        self,
        db: AsyncSession,
        game_id: int,
        user_id: int
    ) -> GameParticipant:
        """Присоединение к игре"""
        game = await self.get_game(db, game_id)
        
        if not game:
            raise ValueError("Игра не найдена")
        
        if game.status != GameStatus.WAITING.value:
            raise ValueError("Нельзя присоединиться к начатой или завершенной игре")
        
        # Проверяем, не присоединился ли уже
        existing = await db.execute(
            select(GameParticipant).where(
                GameParticipant.game_id == game_id,
                GameParticipant.user_id == user_id
            )
        )
        
        if existing.scalar_one_or_none():
            raise ValueError("Вы уже присоединились к этой игре")
        
        # Проверяем лимит игроков
        participants_count = len(game.participants)
        if participants_count >= game.max_players:
            raise ValueError("Игра заполнена")
        
        participant = GameParticipant(
            game_id=game_id,
            user_id=user_id,
            path=[game.start_article],
            current_article=game.start_article,
        )
        
        db.add(participant)
        await db.commit()
        await db.refresh(participant)
        
        return participant
    
    async def start_game(self, db: AsyncSession, game_id: int) -> Game:
        """Запуск игры"""
        game = await self.get_game(db, game_id)
        
        if not game:
            raise ValueError("Игра не найдена")
        
        if game.status != GameStatus.WAITING.value:
            raise ValueError("Игра уже начата или завершена")
        
        if len(game.participants) < 1:
            raise ValueError("В игре должен быть хотя бы один участник")
        
        game.status = GameStatus.IN_PROGRESS.value
        game.started_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(game)
        
        return game
    
    async def make_move(
        self,
        db: AsyncSession,
        game_id: int,
        user_id: int,
        article: str
    ) -> tuple[GameParticipant, bool]:
        """
        Совершить ход (перейти на статью)
        Возвращает (participant, is_winner)
        """
        game = await self.get_game(db, game_id)
        
        if not game:
            raise ValueError("Игра не найдена")
        
        if game.status != GameStatus.IN_PROGRESS.value:
            raise ValueError("Игра не активна")
        
        # Находим участника
        participant = await db.execute(
            select(GameParticipant).where(
                GameParticipant.game_id == game_id,
                GameParticipant.user_id == user_id
            )
        )
        participant = participant.scalar_one_or_none()
        
        if not participant:
            raise ValueError("Вы не участвуете в этой игре")
        
        if participant.is_finished:
            raise ValueError("Вы уже завершили игру")
        
        # Проверяем лимит шагов
        if participant.steps_count >= game.max_steps:
            raise ValueError("Превышен лимит шагов")
        
        # Проверяем лимит времени
        time_elapsed = (datetime.utcnow() - game.started_at).total_seconds()
        if time_elapsed > game.time_limit:
            raise ValueError("Время вышло")
        
        # Проверяем что ссылка существует
        current = participant.current_article or game.start_article
        is_valid_link = await wikipedia_service.is_link_valid(current, article)
        
        if not is_valid_link:
            raise ValueError(f"Нет ссылки из '{current}' в '{article}'")
        
        # Совершаем ход
        participant.path.append(article)
        participant.current_article = article
        participant.steps_count += 1
        
        # Проверяем достижение цели
        is_winner = False
        if article == game.target_article:
            participant.is_finished = True
            participant.is_winner = True
            participant.finished_at = datetime.utcnow()
            participant.time_taken = int(time_elapsed)
            is_winner = True
            
            # Обновляем статистику пользователя
            user = await db.get(User, user_id)
            if user:
                user.total_wins += 1
                if not user.best_time or participant.time_taken < user.best_time:
                    user.best_time = participant.time_taken
                if not user.best_steps or participant.steps_count < user.best_steps:
                    user.best_steps = participant.steps_count
        
        await db.commit()
        await db.refresh(participant)
        
        return participant, is_winner
    
    async def finish_game(self, db: AsyncSession, game_id: int) -> Game:
        """Завершение игры"""
        game = await self.get_game(db, game_id)
        
        if not game:
            raise ValueError("Игра не найдена")
        
        game.status = GameStatus.FINISHED.value
        game.finished_at = datetime.utcnow()
        
        # Обновляем статистику всех участников
        for participant in game.participants:
            user = await db.get(User, participant.user_id)
            if user:
                user.total_games += 1
        
        await db.commit()
        await db.refresh(game)
        
        return game
    
    async def get_leaderboard(
        self,
        db: AsyncSession,
        limit: int = 100
    ) -> list[User]:
        """Получение таблицы лидеров"""
        result = await db.execute(
            select(User)
            .where(User.total_games > 0)
            .order_by(User.total_wins.desc(), User.best_time.asc())
            .limit(limit)
        )
        return list(result.scalars().all())


# Singleton instance
game_service = GameService()
