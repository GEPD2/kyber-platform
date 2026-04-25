#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  start.sh — build and start all services
#  Usage:  ./scripts/start.sh          (first run: builds images)
#          ./scripts/start.sh --build  (force image rebuild)
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# ── Pre-flight checks ─────────────────────────────────────────────────────────
if [ ! -f .env ]; then
  echo "[ERROR] .env not found."
  echo "        Run: cp .env.example .env  then fill in the secret values."
  exit 1
fi

# Warn if secrets are still placeholders
for key in SECRET_KEY JWT_SECRET MYSQL_ROOT_PASSWORD MYSQL_PASSWORD REDIS_PASSWORD; do
  val=$(grep "^${key}=" .env | cut -d= -f2-)
  if [[ "$val" == *"CHANGE_ME"* ]]; then
    echo "[WARN] ${key} still has placeholder value — replace it in .env"
  fi
done

# ── Build and start ───────────────────────────────────────────────────────────
BUILD_FLAG=""
if [[ "${1:-}" == "--build" ]]; then
  BUILD_FLAG="--build"
fi

echo "[INFO] Starting CRYSTALS-Kyber Training Platform..."
docker compose up -d $BUILD_FLAG

echo ""
echo "[INFO] Services started:"
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo "[INFO] Application: http://localhost"
echo "[INFO] Logs:        docker compose logs -f"
echo "[INFO] Stop:        ./scripts/stop.sh"
