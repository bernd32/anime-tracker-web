SHELL := /bin/sh
COMPOSE := docker compose

.PHONY: help build up down logs ps restart dev dev-down pull backup restore db-shell api-shell front-shell test-backend test-frontend ci

help:
	@printf "%s\n" \
	"make build      - build production-like images" \
	"make up         - start production-like stack" \
	"make down       - stop stack" \
	"make logs       - follow logs" \
	"make ps         - show container status" \
	"make restart    - restart stack" \
	"make dev        - start development stack with bind mounts" \
	"make dev-down   - stop development stack" \
	"make backup     - create a PostgreSQL backup in ./backups" \
	"make restore FILE=./backups/file.sql.gz - restore a PostgreSQL backup" \
	"make db-shell   - open psql shell in db container" \
	"make api-shell  - open shell in api container" \
	"make front-shell - open shell in frontend container" \
	"make test-backend - run backend tests locally (requires backend deps)" \
	"make test-frontend - run frontend tests locally" \
	"make ci         - run the local quality gate set"

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f --tail=200

ps:
	$(COMPOSE) ps

restart:
	$(COMPOSE) down
	$(COMPOSE) up -d

dev:
	$(COMPOSE) -f compose.yaml -f compose.dev.yaml up --build

dev-down:
	$(COMPOSE) -f compose.yaml -f compose.dev.yaml down

pull:
	$(COMPOSE) pull

backup:
	./scripts/backup-postgres.sh

restore:
	test -n "$(FILE)" || (echo "Usage: make restore FILE=./backups/backup.sql.gz" && exit 1)
	./scripts/restore-postgres.sh "$(FILE)"

db-shell:
	$(COMPOSE) exec db psql -U $$POSTGRES_USER -d $$POSTGRES_DB

api-shell:
	$(COMPOSE) exec api sh

front-shell:
	$(COMPOSE) exec frontend sh

test-backend:
	cd backend && \
	python3 -m venv venv && \
	. venv/bin/activate && \
	python3 -m pytest -q

test-frontend:
	cd frontend && npm test

ci:
	cd backend && pytest -q
	cd frontend && npm test
