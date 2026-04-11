# syntax=docker/dockerfile:1.7

ARG PYTHON_VERSION=3.14

FROM python:${PYTHON_VERSION}-slim-bookworm AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app

FROM base AS dev
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml alembic.ini ./
COPY alembic ./alembic
COPY app ./app
COPY scripts ./scripts
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -e ".[dev]"
ENV PATH="/opt/venv/bin:$PATH"
RUN groupadd --system --gid 10001 app && useradd --system --uid 10001 --gid 10001 --home /app app \
    && chown -R app:app /app /opt/venv \
    && chmod +x /app/scripts/*.sh
USER app
EXPOSE 43968
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "43968", "--reload"]

FROM base AS builder
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml alembic.ini ./
COPY alembic ./alembic
COPY app ./app
COPY scripts ./scripts
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install .

FROM python:${PYTHON_VERSION}-slim-bookworm AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*
RUN groupadd --system --gid 10001 app && useradd --system --uid 10001 --gid 10001 --home /app app
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app/alembic.ini /app/alembic.ini
COPY --from=builder /app/alembic /app/alembic
COPY --from=builder /app/app /app/app
COPY --from=builder /app/scripts /app/scripts
RUN chown -R app:app /app /opt/venv \
    && chmod +x /app/scripts/*.sh
USER app
EXPOSE 43968
CMD ["/app/scripts/start-api.sh"]
