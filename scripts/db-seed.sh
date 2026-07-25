#!/bin/bash

# Bash script that seeds the anime-backlog database on the deployed server
set -euo pipefail

BASE=http://192.168.88.80:43968/api/v1
COOKIES=$(mktemp)
CSV_FILE=backlog.csv
USERNAME=owner
PASSWORD='REPLACE_WITH_A_LONG_RANDOM_PASSWORD'

trap 'rm -f "$COOKIES"' EXIT

if [ ! -f "$CSV_FILE" ]; then
  echo "File $CSV_FILE not found" >&2
  exit 1
fi

LOGIN_HTTP_CODE=$(curl -s -o /tmp/login-response.json -w '%{http_code}' \
  -c "$COOKIES" -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg u "$USERNAME" --arg p "$PASSWORD" '{username:$u,password:$p}')")

if [ "$LOGIN_HTTP_CODE" != "200" ]; then
  echo "Логин не удался (HTTP $LOGIN_HTTP_CODE):" >&2
  cat /tmp/login-response.json >&2
  exit 1
fi

CSRF=$(grep anime_tracker_csrf "$COOKIES" | awk '{print $7}')
if [ -z "$CSRF" ]; then
  echo "Cannot get CSRF token" >&2
  exit 1
fi

echo "----- DRY RUN -----"
DRY_RUN_RESPONSE=$(curl -s -b "$COOKIES" -X POST "$BASE/import/csv?dry_run=true" \
  -H "X-CSRF-Token: $CSRF" \
  -F "file=@${CSV_FILE}")
echo "$DRY_RUN_RESPONSE" | jq .

INVALID_ROWS=$(echo "$DRY_RUN_RESPONSE" | jq '.summary.invalid_rows')
if [ "$INVALID_ROWS" != "0" ]; then
  echo "There are invalid rows in the csv file: ($INVALID_ROWS) — importing aborted" >&2
  exit 1
fi

read -p "Dry-run was successful. Do you want to import entries from the csv file? [y/N] " CONFIRM
if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
  echo "Canceled by the user"
  exit 0
fi

echo "----- IMPORT -----"
curl -s -b "$COOKIES" -X POST "$BASE/import/csv" \
  -H "X-CSRF-Token: $CSRF" \
  -F "file=@${CSV_FILE}" | jq .