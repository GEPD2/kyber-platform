#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
echo "[INFO] Stopping services..."
docker compose down
echo "[INFO] Done. Data volumes preserved."
echo "       To also remove data: docker compose down -v"
