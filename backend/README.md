# WikiRush Backend

FastAPI backend для игры WikiRush - гонки по Википедии.

## Особенности

- ✅ FastAPI с async/await
- ✅ SQLAlchemy 2.0 с async поддержкой
- ✅ JWT аутентификация
- ✅ WebSocket для real-time обновлений
- ✅ Integration с Wikipedia API
- ✅ Полное покрытие типами (mypy)
- ✅ Линтеры и форматтеры (ruff, black)
- ✅ Pre-commit hooks
- ✅ Pytest с async тестами

## Установка

### Требования

- Python 3.11+
- PostgreSQL 15+ (или SQLite для разработки)
- Redis (опционально)

### Шаги установки

1. Клонируйте репозиторий:
```bash
git clone https://github.com/YOUR_USERNAME/wikirush.git
cd wikirush/backend
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Скопируйте `.env.example` в `.env` и настройте переменные:
```bash
cp .env.example .env
# Отредактируйте .env
```

5. Инициализируйте базу данных:
```bash
# База будет создана автоматически при первом запуске
```

6. Установите pre-commit hooks:
```bash
pre-commit install
```

## Запуск

### Для разработки

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Или через Python:
```bash
python -m app.main
```

### С помощью Docker

```bash
cd ..  # В корень проекта
docker-compose up
```

## API Документация

После запуска доступна по адресу:
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## Структура проекта

```
backend/
├── app/
│   ├── api/           # API endpoints
│   ├── core/          # Конфигурация, БД, безопасность
│   ├── models/        # SQLAlchemy модели
│   ├── schemas/       # Pydantic схемы
│   ├── services/      # Бизнес-логика
│   └── main.py        # Точка входа
├── tests/             # Тесты
├── requirements.txt   # Зависимости
└── README.md
```

## Основные эндпоинты

### Аутентификация
- `POST /api/v1/auth/register` - Регистрация
- `POST /api/v1/auth/login` - Вход
- `POST /api/v1/auth/refresh` - Обновление токена

### Пользователи
- `GET /api/v1/users/me` - Текущий пользователь
- `GET /api/v1/users/{id}` - Информация о пользователе
- `GET /api/v1/users/{id}/stats` - Статистика пользователя

### Игры
- `POST /api/v1/games` - Создать игру
- `GET /api/v1/games` - Список игр
- `GET /api/v1/games/{id}` - Информация об игре
- `POST /api/v1/games/{id}/join` - Присоединиться
- `POST /api/v1/games/{id}/start` - Запустить игру
- `POST /api/v1/games/{id}/move` - Сделать ход
- `WS /api/v1/games/{id}/ws` - WebSocket для обновлений

### Лидерборд
- `GET /api/v1/leaderboard` - Таблица лидеров

## Тестирование

Запуск всех тестов:
```bash
pytest
```

С покрытием:
```bash
pytest --cov=app --cov-report=html
```

## Линтинг и форматирование

```bash
# Форматирование
black .

# Линтинг
ruff check .

# Проверка типов
mypy app/

# Все проверки сразу (через pre-commit)
pre-commit run --all-files
```

## Разработка

### Добавление новых зависимостей

```bash
pip install package_name
pip freeze > requirements.txt
```

### Миграции базы данных (с Alembic)

```bash
# Создать миграцию
alembic revision --autogenerate -m "description"

# Применить миграции
alembic upgrade head

# Откатить
alembic downgrade -1
```

## Примеры использования API

### Регистрация и вход

```python
import httpx

# Регистрация
response = httpx.post(
    "http://localhost:8000/api/v1/auth/register",
    json={
        "username": "player1",
        "email": "player1@example.com",
        "password": "secure_password"
    }
)

# Вход
response = httpx.post(
    "http://localhost:8000/api/v1/auth/login",
    json={
        "username": "player1",
        "password": "secure_password"
    }
)
token = response.json()["access_token"]

# Использование токена
headers = {"Authorization": f"Bearer {token}"}
```

### Создание игры

```python
response = httpx.post(
    "http://localhost:8000/api/v1/games",
    headers=headers,
    json={
        "mode": "single",
        "start_article": "Python_(programming_language)",
        "target_article": "Computer_science",
        "max_steps": 50,
        "time_limit": 300,
        "max_players": 1
    }
)
```

## Troubleshooting

### База данных не подключается

Проверьте настройки в `.env`:
```bash
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

### Wikipedia API не отвечает

Проверьте доступ к интернету и URL:
```bash
WIKIPEDIA_API_URL=https://ru.wikipedia.org/w/api.php
```

## Лицензия

MIT
