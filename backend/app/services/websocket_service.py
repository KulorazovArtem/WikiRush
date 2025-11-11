"""
WebSocket сервис для real-time обновлений игры
"""
import json
from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    """Менеджер WebSocket соединений"""

    def __init__(self):
        # game_id -> list of websockets
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, game_id: int):
        """Подключение к игре"""
        await websocket.accept()

        if game_id not in self.active_connections:
            self.active_connections[game_id] = []

        self.active_connections[game_id].append(websocket)

    def disconnect(self, websocket: WebSocket, game_id: int):
        """Отключение от игры"""
        if game_id in self.active_connections:
            self.active_connections[game_id].remove(websocket)

            # Удаляем пустой список
            if not self.active_connections[game_id]:
                del self.active_connections[game_id]

    async def send_personal_message(
        self, message: dict[str, Any], websocket: WebSocket
    ):
        """Отправка личного сообщения"""
        await websocket.send_text(json.dumps(message))

    async def broadcast_to_game(self, message: dict[str, Any], game_id: int):
        """Отправка сообщения всем участникам игры"""
        if game_id in self.active_connections:
            disconnected = []

            for connection in self.active_connections[game_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception:
                    disconnected.append(connection)

            # Удаляем отключенные соединения
            for conn in disconnected:
                self.active_connections[game_id].remove(conn)

    async def notify_player_joined(self, game_id: int, username: str):
        """Уведомление о присоединении игрока"""
        await self.broadcast_to_game(
            {
                "type": "player_joined",
                "username": username,
                "message": f"{username} присоединился к игре",
            },
            game_id,
        )

    async def notify_game_started(self, game_id: int):
        """Уведомление о начале игры"""
        await self.broadcast_to_game(
            {"type": "game_started", "message": "Игра началась!"}, game_id
        )

    async def notify_player_move(
        self, game_id: int, username: str, article: str, steps: int
    ):
        """Уведомление о ходе игрока"""
        await self.broadcast_to_game(
            {
                "type": "player_move",
                "username": username,
                "article": article,
                "steps": steps,
            },
            game_id,
        )

    async def notify_player_won(
        self, game_id: int, username: str, time: int, steps: int
    ):
        """Уведомление о победе игрока"""
        await self.broadcast_to_game(
            {
                "type": "player_won",
                "username": username,
                "time": time,
                "steps": steps,
                "message": f"{username} выиграл! Время: {time}с, Шагов: {steps}",
            },
            game_id,
        )

    async def notify_game_finished(self, game_id: int):
        """Уведомление о завершении игры"""
        await self.broadcast_to_game(
            {"type": "game_finished", "message": "Игра завершена"}, game_id
        )


# Singleton instance
websocket_manager = ConnectionManager()
