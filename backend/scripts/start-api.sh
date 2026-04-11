#!/bin/sh
set -eu

DB_MAX_TRIES="${DB_MAX_TRIES:-30}"
DB_WAIT_SECONDS="${DB_WAIT_SECONDS:-2}"
PORT="${PORT:-43968}"
UVICORN_WORKERS="${UVICORN_WORKERS:-1}"

if [ -n "${DATABASE_URL:-}" ]; then
  i=1
  until python - <<'PY'
import os
from sqlalchemy import create_engine, text

url = os.environ["DATABASE_URL"]
engine = create_engine(url, pool_pre_ping=True)
with engine.connect() as conn:
    conn.execute(text("SELECT 1"))
PY
  do
    if [ "$i" -ge "$DB_MAX_TRIES" ]; then
      echo "Database did not become ready in time"
      exit 1
    fi
    echo "Waiting for database... ($i/$DB_MAX_TRIES)"
    i=$((i + 1))
    sleep "$DB_WAIT_SECONDS"
  done
fi

alembic upgrade head

exec uvicorn app.main:app \
  --host 0.0.0.0 \
  --port "$PORT" \
  --workers "$UVICORN_WORKERS" \
  --proxy-headers \
  --forwarded-allow-ips='*'
