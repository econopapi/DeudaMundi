#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -f "${SCRIPT_DIR}/.env.api" ]; then
  echo "Missing ${SCRIPT_DIR}/.env.api (copy from .env.api.example)"
  exit 1
fi

cd "${SCRIPT_DIR}"

echo "[deploy] Building and starting DeudaMundi API stack..."
docker compose -f docker-compose.prod.yml up -d --build

echo "[deploy] Current status:"
docker compose -f docker-compose.prod.yml ps

echo "[deploy] Last API logs:"
docker compose -f docker-compose.prod.yml logs api --tail=100
