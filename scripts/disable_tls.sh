#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
HTTP_BAK="./nginx/conf.d/app.conf.http_backup"
TLS_ACTIVE="./nginx/conf.d/app.conf"
if [ -f "$HTTP_BAK" ]; then
  cp "$HTTP_BAK" "$TLS_ACTIVE"
  echo "[INFO] Reverted to HTTP configuration."
fi
if [ -f .env ]; then
  sed -i 's/^TLS_ENABLED=.*/TLS_ENABLED=false/' .env
fi
echo "[INFO] Run: docker compose restart nginx"
