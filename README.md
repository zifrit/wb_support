# WB Wrapper App v1

Fullstack API wrapper around WB endpoints.

## Features
- FastAPI backend with unified external API pipeline.
- Two-token model:
  - static WB secret from `.env` in `X-Client-Secret`.
  - per-user token from external auth service saved in `user_tokens` table and used in `Authorization`.
- Dynamic wrapper routes for `/wb/*`.
- React API Explorer UI (Login, Catalog, Runner, JSON viewer).
- Internal DB SELECT clients for Postgres and ClickHouse (sync + async).
- JSON structured logging.

## Backend Run (uv)
```bash
cd backend
uv run alembic upgrade head
uv run uvicorn backend.app.main:app --app-dir .. --reload --host 0.0.0.0 --port 8000
```

## Frontend Run
```bash
cd frontend
npm install
npm run dev
```

## Docker Compose
```bash
cp .env.example .env
docker compose up --build
```

## Migrations
```bash
cd backend
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "describe change"
```

## Backend API
- `POST /auth/login`
- `GET /auth/verify`
- `GET /meta/endpoints`
- `GET /wb/adverts`
- `GET /wb/fullstats`
- `GET /wb/stop`
- `POST /wb/normquery/stats`
- `POST /wb/normquery/get-minus`
- `GET /wb/orders`
- `POST /wb/search-report/product/search-texts`

## Header rules for WB calls
- `X-Client-Secret: <WB_CLIENT_SECRET from env>`
- `User-Agent: wbas_xway`
- `Authorization: <token selected from DB by username>`

## Admin bypass
- If frontend username is `admin`, login skips token issue/verify requests.
- Backend also bypasses external auth calls for `admin` and uses `ADMIN_AUTHORIZATION_TOKEN` for WB `Authorization` header.

## Debug mode
- Set `DEBUG=true` to disable auth checks across the app.
- In debug mode backend does not require a logged-in user and uses `DEBUG_USERNAME` plus `DEBUG_AUTHORIZATION_TOKEN`.
- Frontend reads debug state from `/meta/endpoints` and unlocks the full UI without login.
