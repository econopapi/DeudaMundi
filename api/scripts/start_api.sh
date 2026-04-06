#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH="/app:${PYTHONPATH:-}"

if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
  echo "[deudamundi-api] Running Alembic migrations..."
  alembic upgrade head
fi

PORT_VALUE="${PORT:-8000}"
echo "[deudamundi-api] Starting API on port ${PORT_VALUE}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT_VALUE}"
