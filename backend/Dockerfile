FROM python:3.12-slim

WORKDIR /app

COPY . /app/backend
RUN pip install --no-cache-dir -U pip setuptools wheel && pip install --no-cache-dir /app/backend

CMD ["sh", "-c", "cd /app/backend && alembic upgrade head && uvicorn backend.app.main:app --app-dir /app --host 0.0.0.0 --port 8000"]
