#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPOSITORY_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

if [ ! -f "${REPOSITORY_DIR}/.env.production" ]; then
  echo "Missing ${REPOSITORY_DIR}/.env.production (run 'make prod-init' and configure it)"
  exit 1
fi

cd "${REPOSITORY_DIR}"

echo "[deploy] Building and starting the complete DeudaMundi stack..."
make prod-up

echo "[deploy] Current status:"
make prod-ps

echo "[deploy] Last logs:"
docker compose --env-file .env.production -f docker-compose.prod.yml logs --tail=100
