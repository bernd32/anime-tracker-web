# Anime Backlog Tracker

Self-hosted anime backlog tracker with a Next.js frontend, FastAPI backend, PostgreSQL database, CSV import/export, and anime metadata lookup from shikimori.io.

## Overview

This project is split into three main services:

- `frontend`: Next.js 16 app for the UI
- `backend`: FastAPI application with SQLAlchemy, Alembic, and business logic
- `db`: PostgreSQL 17 database

The main deployment path is Docker Compose with prebuilt Docker Hub images for the app services and the official PostgreSQL image for the database. A development overlay is also included for bind-mounted local development and local image builds.

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
- `API_PROXY_TARGET`
- `CORS_ALLOW_ORIGINS`
- `AUTH_OWNER_USERNAME`
- `AUTH_OWNER_PASSWORD`
- `AUTH_SESSION_SECRET`
- `AUTH_LOGIN_MAX_FAILURES`
- `AUTH_LOGIN_WINDOW_SECONDS`
- `AUTH_LOGIN_LOCKOUT_SECONDS`
- published ports 
in `.env`

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

Use `make build && make up` only when you want to build and run the runtime images locally without bind mounts.

Stop it with:

```sh
make dev-down


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
