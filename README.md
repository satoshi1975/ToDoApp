# To Do App Backend

## Описание

Это серверная часть приложения для управления задачами (To Do), реализованная на FastAPI с асинхронной работой через SQLAlchemy и PostgreSQL. Приложение предоставляет REST API для регистрации пользователей, аутентификации (JWT), а также создания, просмотра, обновления и удаления задач. 

## Основной функционал
- Регистрация и аутентификация пользователей (JWT)
- Создание, просмотр, обновление и удаление задач
- Валидация данных (Pydantic)
- Логирование запросов и ошибок
- Асинхронная работа с БД (PostgreSQL через asyncpg)
- Документация OpenAPI/Swagger по адресу `/docs`

## Стек технологий
- Python 3.10+
- FastAPI
- SQLAlchemy (asyncio)
- PostgreSQL
- Docker, Docker Compose
- Pytest (тесты)

## Структура проекта
```
app/
  main.py           # Точка входа FastAPI
  api/              # Роутеры API (auth, tasks)
  services/         # Бизнес-логика
  schemas/          # Pydantic-схемы (Task, User, Token)
  db/               # Модели и сессии БД
  core/             # Конфигурация и утилиты
```

## Быстрый старт (Docker)
1. Убедитесь, что установлены Docker и Docker Compose.
2. В корне проекта выполните:
   ```bash
   docker-compose up --build
   ```
3. Приложение будет доступно на http://localhost:8000
4. Swagger UI: http://localhost:8000/docs

## Локальный запуск (без Docker)
1. Установите Python 3.10+ и PostgreSQL.
2. Создайте и активируйте виртуальное окружение:
   ```bash
   python -m venv venv
   source venv/bin/activate  # или venv\Scripts\activate для Windows
   ```
3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
4. Установите переменную окружения `DATABASE_URL`, например:
   ```bash
   export DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/todo_db
   ```
5. Запустите приложение:
   ```bash
   uvicorn app.main:app --reload
   ```

## Описание API
### Аутентификация
- `POST /auth/register` — регистрация пользователя
- `POST /auth/token` — получение JWT токена (логин)
- `POST /auth/refresh` — обновление access токена

### Задачи
- `POST /tasks/create` — создать задачу
- `GET /tasks/` — получить список задач пользователя
- `GET /tasks/{task_id}` — получить задачу по ID
- `PUT /tasks/{task_id}` — обновить задачу
- `DELETE /tasks/{task_id}` — удалить задачу

Все методы с задачами требуют авторизации (JWT Bearer).

## Модели данных (Pydantic)
### User
- `username`: str
- `email`: str
- `password`: str (только при создании)

### Task
- `id`: int
- `datetime_to_do`: datetime (ISO)
- `task_info`: str
- `created_at`: datetime
- `updated_at`: datetime
- `user_id`: int
- `is_completed`: bool

### Token
- `access_token`: str
- `refresh_token`: str
- `token_type`: str

## Тестирование
Для запуска тестов:
```bash
pytest
```
Покрытие: тесты API и бизнес-логики задач, фикстуры для пользователей и задач, изолированная тестовая БД (SQLite in-memory).

## Логи
Все запросы и ошибки логируются в файл `app.log`.
