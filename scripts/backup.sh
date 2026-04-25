#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  backup.sh — dump MySQL data to a timestamped .sql.gz file
#  Usage:  ./scripts/backup.sh [output_dir]
#  Default output dir: ./backups/
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail
cd "$(dirname "$0")/.."

BACKUP_DIR="${1:-./backups}"
mkdir -p "$BACKUP_DIR"

# Load env
if [ -f .env ]; then
  set -a; source .env; set +a
fi

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTFILE="${BACKUP_DIR}/kyber_${TIMESTAMP}.sql.gz"

echo "[INFO] Backing up database '${MYSQL_DATABASE}' to ${OUTFILE} ..."

docker compose exec -T mysql \
  mysqldump \
    --no-tablespaces \
    --single-transaction \
    --quick \
    -u "${MYSQL_USER}" \
    -p"${MYSQL_PASSWORD}" \
    "${MYSQL_DATABASE}" \
  | gzip > "$OUTFILE"

SIZE=$(du -sh "$OUTFILE" | cut -f1)
echo "[INFO] Backup complete: ${OUTFILE} (${SIZE})"
