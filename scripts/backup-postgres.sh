#!/bin/sh
set -eu

mkdir -p backups
STAMP="$(date +%Y%m%d-%H%M%S)"
OUT="backups/postgres-${STAMP}.sql.gz"

# In case we use kubernetes 
if [ "${1:-}" = "k8s" ]; then
  kubectl exec deploy/anime-backlog-db -n anime-backlog -- sh -lc \
  'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-owner --no-privileges' \
  | gzip -9 > "$OUT"
else
# In case we use just docker
  docker compose exec -T db sh -lc \
    'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-owner --no-privileges' \
    | gzip -9 > "$OUT"
fi

echo "Backup written to $OUT"