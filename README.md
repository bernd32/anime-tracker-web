# Anime Backlog Tracker

Self-hosted anime backlog tracker with a Next.js frontend, FastAPI backend, PostgreSQL database, CSV import/export, and Shikimori metadata lookup.

## Overview

This project is split into three main services:

- `frontend`: Next.js 16 app for the UI
- `backend`: FastAPI application with SQLAlchemy, Alembic, and business logic
- `db`: PostgreSQL 17 database

The main deployment path is Docker Compose with prebuilt Docker Hub images. A development overlay is also included for bind-mounted local development and local image builds.

## Features

- Track anime by year and season
- Separate pre-2010 and per-year library views
- Status tracking: `unwatched`, `watching`, `completed`
- Downloaded flag
- Search by anime name
- Random pick within the current scope
- CSV import and export
- Cached Shikimori metadata lookup
- Preferences for theme, density, and remembered scope
- Docker-based deployment and local development flow

## Architecture

### Frontend

- Framework: Next.js 16
- Language: TypeScript
- State/query layer: TanStack Query
- Forms: React Hook Form + Zod
- UI primitives: Radix UI

Key directories:

- `frontend/app`: app router pages
- `frontend/components`: shared layout and UI components
- `frontend/features`: feature-specific client code
- `frontend/lib`: API client, validation, utility code
- `frontend/tests`: Vitest tests

### Backend

- Framework: FastAPI
- ORM: SQLAlchemy 2
- Migrations: Alembic
- Settings: Pydantic Settings
- Driver: Psycopg 3

### Runtime

- `compose.yaml`: production-like stack
- `compose.dev.yaml`: local development overrides
- `Makefile`: common operational shortcuts
- `scripts/`: backup, restore, rsync deploy helpers

## Quick Start

### 1. Configure environment

Copy the example env files:

```sh
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Review at minimum:

- `POSTGRES_PASSWORD`
- `NEXT_PUBLIC_API_BASE_URL`
- `CORS_ALLOW_ORIGINS`
- `AUTH_OWNER_USERNAME`
- `AUTH_OWNER_PASSWORD`
- `AUTH_SESSION_SECRET`
- `AUTH_LOGIN_MAX_FAILURES`
- `AUTH_LOGIN_WINDOW_SECONDS`
- `AUTH_LOGIN_LOCKOUT_SECONDS`
- published ports in `.env`

Default ports:

- frontend: `20773`
- backend API: `43968`
- PostgreSQL: `5432`

### 2. Pull and run

```sh
docker compose pull
docker compose up -d
```

Open:

- frontend: `http://localhost:20773`
- backend healthcheck: `http://localhost:43968/api/v1/healthz`

## Development

### Start dev stack

This uses bind mounts and local builds:

```sh
docker compose -f compose.yaml -f compose.dev.yaml up --build
```

Or with `make`:

```sh
make dev
```

Stop it with:

```sh
make dev-down
```

### Local backend

```sh
cd backend
python -m pip install -e ".[dev]"
uvicorn app.main:app --host 0.0.0.0 --port 43968 --reload
```

Notes:

- Set `DATABASE_URL` before running outside Compose
- Run migrations before starting the app:

```sh
cd backend
alembic upgrade head
```

### Local frontend

```sh
cd frontend
npm ci
npm run dev -- --hostname 0.0.0.0 --port 20773
```

If you run frontend locally against Docker backend, make sure `NEXT_PUBLIC_API_BASE_URL` points to the correct host/API URL.

## Testing

### Frontend

```sh
cd frontend
npm test
```

### Backend

```sh
cd backend
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -e ".[dev]"
python3 -m pytest -q
```

### Project shortcuts

```sh
make test-frontend
make test-backend
make ci
```

## CI

GitHub Actions workflow:

- `.github/workflows/ci.yml`

Current CI gates:

- backend dependency install
- backend pytest
- frontend dependency install
- frontend Vitest suite
- frontend production build

## Deployment

Production deployment is image-first. The intended flow is:

1. publish updated images to Docker Hub
2. pull those images on the target machine
3. recreate the stack with Docker Compose

Default image references in `compose.yaml`:

- `skeirs/anime-backlog-db-1`
- `skeirs/anime-backlog-api`
- `skeirs/anime-backlog-frontend`

For VPS deployment, use the root `compose.yaml` directly and follow [DEPLOY_VPS.md](/home/bernd/Documents/programs/python/anime-tracker-web/DEPLOY_VPS.md).

## Configuration

Top-level `.env` controls the Docker Compose stack.

Important variables:

- `COMPOSE_PROJECT_NAME`
- `DB_IMAGE`
- `API_IMAGE`
- `FRONTEND_IMAGE`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_PORT`
- `API_PORT`
- `FRONTEND_PORT`
- `NEXT_PUBLIC_API_BASE_URL`
- `APP_ENV`
- `APP_DEBUG`
- `LOG_LEVEL`
- `UVICORN_WORKERS`
- `CORS_ALLOW_ORIGINS`
- `AUTH_OWNER_USERNAME`
- `AUTH_OWNER_PASSWORD`
- `AUTH_SESSION_SECRET`
- `AUTH_SESSION_MAX_AGE_SECONDS`
- `AUTH_LOGIN_MAX_FAILURES`
- `AUTH_LOGIN_WINDOW_SECONDS`
- `AUTH_LOGIN_LOCKOUT_SECONDS`
- `SHIKIMORI_GRAPHQL_URL`
- `SHIKIMORI_REQUEST_TIMEOUT_SECONDS`
- `SHIKIMORI_CACHE_TTL_SECONDS`
- `SHIKIMORI_USER_AGENT`
- `SHIKIMORI_HTTPS_PROXY_URL`
- `SHIKIMORI_SOCKS5_PROXY_URL`

The application uses a single owner login:

- everyone can read the backlog
- only the signed-in owner can create, edit, delete, import, or change preferences
- production startup is blocked if `AUTH_OWNER_USERNAME`, `AUTH_OWNER_PASSWORD`, or `AUTH_SESSION_SECRET` are left on insecure defaults
- repeated failed owner logins are throttled using the `AUTH_LOGIN_*` settings

`CORS_ALLOW_ORIGINS` is a JSON array string, for example:

```dotenv
CORS_ALLOW_ORIGINS=["http://localhost:20773","http://192.168.88.40:20773"]
```

### Shikimori proxy configuration

You can route Shikimori requests through exactly one proxy type:

- `SHIKIMORI_HTTPS_PROXY_URL`
- `SHIKIMORI_SOCKS5_PROXY_URL`

Examples:

```dotenv
SHIKIMORI_HTTPS_PROXY_URL=https://proxy.example:8443
```

```dotenv
SHIKIMORI_SOCKS5_PROXY_URL=socks5://127.0.0.1:1080
```

Notes:

- set only one of the two variables
- HTTPS proxy values must start with `http://` or `https://`
- SOCKS5 proxy values must start with `socks5://` or `socks5h://`
- when the backend runs in Docker and the proxy runs on the host machine, use `host.docker.internal` instead of `127.0.0.1`

Example for Docker on the same host:

```dotenv
SHIKIMORI_SOCKS5_PROXY_URL=socks5://host.docker.internal:10808
```

Quick setup steps:

1. Set the proxy URL in `.env`
2. If you also run the backend outside Docker, mirror it in `backend/.env`
3. Recreate the stack so the containers pick up the new environment:

```sh
docker compose up -d
```

## Database and Migrations

The backend startup script:

- waits for the database
- runs `alembic upgrade head`
- starts Uvicorn

Entry point:

- `backend/scripts/start-api.sh`

If you need to run migrations manually:

```sh
cd backend
alembic upgrade head
```

## Backup and Restore

### Backup

```sh
make backup
```

This creates a compressed SQL dump under `./backups`.

### Restore

```sh
make restore FILE=./backups/postgres-YYYYMMDD-HHMMSS.sql.gz
```

Be careful: restore writes into the current configured database.

## Useful Commands

```sh
make help
make build
make pull
make up
make down
make restart
make logs
make ps
make db-shell
make api-shell
make front-shell
```
