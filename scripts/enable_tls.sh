#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  enable_tls.sh — activate TLS 1.3 HTTPS
#
#  Prerequisites:
#    1. Obtain a certificate pair (Let's Encrypt, self-signed, etc.)
#    2. Place in ./nginx/certs/:
#         fullchain.pem   (certificate + intermediate chain)
#         privkey.pem     (private key, mode 600)
#    3. Run this script once
#    4. docker compose restart nginx
#
#  To revert to HTTP:  ./scripts/disable_tls.sh
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail
cd "$(dirname "$0")/.."

CERT_DIR="./nginx/certs"
HTTP_CONF="./nginx/conf.d/app.conf"
TLS_CONF="./nginx/conf.d/app_tls.conf.disabled"
HTTP_BAK="./nginx/conf.d/app.conf.http_backup"
TLS_ACTIVE="./nginx/conf.d/app.conf"

# Validate certs
for cert_file in fullchain.pem privkey.pem; do
  if [ ! -f "${CERT_DIR}/${cert_file}" ]; then
    echo "[ERROR] Missing: ${CERT_DIR}/${cert_file}"
    exit 1
  fi
done

echo "[INFO] Certificate files found."

# Check private key permissions
chmod 600 "${CERT_DIR}/privkey.pem"
echo "[INFO] Private key permissions set to 600."

# Swap configs
if [ ! -f "$TLS_CONF" ]; then
  echo "[ERROR] TLS config not found: $TLS_CONF"
  exit 1
fi

cp "$HTTP_CONF" "$HTTP_BAK"
cp "$TLS_CONF"  "$TLS_ACTIVE"

# Update .env
if [ -f .env ]; then
  sed -i 's/^TLS_ENABLED=.*/TLS_ENABLED=true/' .env
  echo "[INFO] TLS_ENABLED=true set in .env"
fi

echo ""
echo "[INFO] TLS configuration activated."
echo "[INFO] Now run: docker compose restart nginx"
echo "[INFO] Your site will be available at: https://your-domain"
