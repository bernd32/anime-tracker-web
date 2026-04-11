#!/bin/sh
set -eu

mkdir -p backups
STAMP="$(date +%Y%m%d-%H%M%S)"
OUT="backups/postgres-${STAMP}.sql.gz"

docker compose exec -T db sh -lc \
  'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-owner --no-privileges' \
  | gzip -9 > "$OUT"

echo "Backup written to $OUT"