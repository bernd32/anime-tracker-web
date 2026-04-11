#!/bin/sh
set -eu

FILE="${1:-}"
if [ -z "$FILE" ]; then
  echo "Usage: $0 ./backups/postgres-YYYYMMDD-HHMMSS.sql.gz"
  exit 1
fi

if [ ! -f "$FILE" ]; then
  echo "File not found: $FILE"
  exit 1
fi

echo "Restoring $FILE into current PostgreSQL database..."
gunzip -c "$FILE" | docker compose exec -T db sh -lc \
  'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'

echo "Restore finished"