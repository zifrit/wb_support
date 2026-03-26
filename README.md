# WB Wrapper App

Fullstack wrapper around selected Wildberries endpoints with a FastAPI backend and React-based API Explorer frontend.

## Что есть в проекте
- `backend/`: FastAPI API, unified error handling, proxy to WB endpoints, external auth integration, `user_tokens` storage.
- `frontend/`: Vite + React explorer with login page, catalog of endpoints, request runner and JSON viewer.
- `infra/token-validator-mock/`: локальный mock auth-сервиса для docker compose.
- `docker-compose.yml`: локальный dev-стек с live reload для backend и frontend.

## Текущий auth flow
Логин разделен на 2 шага:

1. `POST /auth/login`
   - фронт отправляет `username` в формате телефона без `+` и скобок;
   - backend просит внешний auth-сервис отправить код.
2. `POST /auth/verify`
   - фронт отправляет `username + code`;
   - backend получает токен от внешнего auth-сервиса и сохраняет `username + token` в таблицу `user_tokens`.

Дополнительно:
- `POST /auth/check` проверяет сохраненный токен пользователя из `user_tokens`.
- frontend вызывает `/auth/check` перед каждым вызовом любой `/wb/*` ручки.
- если `/auth/check` не проходит, фронт очищает локальную сессию и возвращает пользователя на `/login`.

Важно:
- `/auth/check` проверяет пользовательскую auth-сессию.
- сами `/wb/*` продолжают использовать текущую shop-token логику через `shop_id` и `adv_shop`.

## Backend API

### Auth
- `POST /auth/login`
- `POST /auth/verify`
- `POST /auth/check`

### Meta
- `GET /meta/config`
- `GET /meta/endpoints`

### WB proxy
- `POST /wb/adverts`
- `POST /wb/fullstats`
- `POST /wb/normquery/stats`
- `POST /wb/normquery/get-minus`
- `POST /wb/orders`
- `POST /wb/search-report/product/search-texts`

## Header rules for WB calls
WB proxy отправляет во внешний WB API:
- `X-Client-Secret: <WB_CLIENT_SECRET>`
- `User-Agent: your_user_agent`
- `Authorization: <shop token resolved by shop_id>`

Для вызова backend `/wb/*` фронт передает:
- `X-Username: <username>`

## Frontend behavior
- страница входа отделена от страницы со списком ручек;
- в обычном режиме доступ к каталогу возможен только после успешного логина;
- в `DEBUG=true` логин пропускается и приложение сразу открывает `/endpoints`;
- фронтовая сессия живет 3 дня;
- состояние runner по каждой ручке хранится 1 час в `localStorage`;
- список ручек загружается только после авторизации или debug-bypass.

## Локальный запуск без Docker

### Backend
```bash
cd backend
uv run alembic upgrade head
uv run uvicorn backend.app.main:app --app-dir .. --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Docker Compose
Все основные переменные читаются из `.env`.

### Подготовка
```bash
cp .env.example .env
```

### Запуск
```bash
docker compose up --build
```

После запуска:
- backend доступен на `http://localhost:8000`
- frontend доступен на `http://localhost:3000`
- auth mock доступен на `http://localhost:9000`
- Postgres проброшен на `localhost:5444`

## Переменные окружения
Основные переменные описаны в [.env.example](/Applications/python%20projects/adv-support/.env.example).

Ключевые из них:
- `VITE_API_BASE_URL`: базовый URL backend для frontend.
- `AUTH_BASE_URL`: базовый URL внешнего auth-сервиса.
- `AUTH_SEND_CODE`, `AUTH_VERIFY_CODE`, `AUTH_VERIFY_TOKEN`: пути auth API.
- `DB_*`: основная БД backend.
- `TEST_DATABASE_URL_ASYNC`, `TEST_DATABASE_URL_SYNC`: SQLite URLs для тестового режима.
- `DEBUG`, `DEBUG_USERNAME`, `DEBUG_AUTHORIZATION_TOKEN`: debug-режим.
- `TESTING`: отдельный тестовый режим для SQLite без debug-bypass.

## Миграции
```bash
cd backend
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "describe change"
```

## Тесты
В тестах проект использует SQLite через `TESTING=true`, а не боевой Postgres.

Запуск всех backend-тестов:
```bash
uv run --project backend pytest backend/tests
```

На текущий момент проверено:
- `backend/tests/integration/test_auth_routes.py`
- `backend/tests/integration/test_wb_routes.py`
- `backend/tests/unit/test_auth_service.py`
- `backend/tests/unit/test_sql_guard.py`
- `backend/tests/unit/test_wb_mapper_and_resolver.py`

## Debug mode
- `DEBUG=true` отключает обычный login-flow.
- backend начинает использовать `DEBUG_USERNAME` и `DEBUG_AUTHORIZATION_TOKEN`.
- frontend читает debug-состояние из `GET /meta/config` и сразу открывает приложение.

## Testing mode
- `TESTING=true` переводит backend migrations и DB session на SQLite.
- `TESTING` не включает debug-bypass.
- этот режим нужен именно для pytest и локальной тестовой БД.
