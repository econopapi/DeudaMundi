#!/usr/bin/env bash
set -euo pipefail

# Usage (defaults shown):
# APP_DIR=/home/admin/apps/deudamundi \
# SERVICE_NAME=deudamundi-api \
# SERVICE_USER=admin \
# SERVICE_GROUP=admin \
# SERVICE_PORT=8000 \
# UVICORN_WORKERS=2 \
# ./deploy/vps/systemd/deploy_systemd.sh

APP_DIR="${APP_DIR:-/home/admin/apps/deudamundi}"
SERVICE_NAME="${SERVICE_NAME:-deudamundi-api}"
SERVICE_USER="${SERVICE_USER:-admin}"
SERVICE_GROUP="${SERVICE_GROUP:-admin}"
SERVICE_PORT="${SERVICE_PORT:-8000}"
UVICORN_WORKERS="${UVICORN_WORKERS:-2}"

if [ -n "${PYTHON_BIN:-}" ]; then
  SELECTED_PYTHON_BIN="${PYTHON_BIN}"
else
  SELECTED_PYTHON_BIN=""
  for candidate in python3.13 python3.12 python3; do
    if command -v "${candidate}" >/dev/null 2>&1; then
      CANDIDATE_OK="$(${candidate} -c 'import sys; print(int(sys.version_info >= (3, 12)))' 2>/dev/null || echo 0)"
      if [ "${CANDIDATE_OK}" = "1" ]; then
        SELECTED_PYTHON_BIN="${candidate}"
        break
      fi
    fi
  done
fi

TEMPLATE_PATH="${APP_DIR}/deploy/vps/systemd/deudamundi-api.service.template"
RENDERED_PATH="/tmp/${SERVICE_NAME}.service"
UNIT_PATH="/etc/systemd/system/${SERVICE_NAME}.service"

if [ ! -f "${TEMPLATE_PATH}" ]; then
  echo "Template not found: ${TEMPLATE_PATH}"
  exit 1
fi

if [ ! -d "${APP_DIR}/api" ]; then
  echo "API directory not found: ${APP_DIR}/api"
  exit 1
fi

if [ -z "${SELECTED_PYTHON_BIN}" ]; then
  echo "No compatible Python interpreter found (requires >=3.12)."
  echo "Tip: install Python >= 3.12 and rerun with PYTHON_BIN=<path-or-binary>"
  exit 1
fi

PY_OK="$(${SELECTED_PYTHON_BIN} -c 'import sys; print(int(sys.version_info >= (3, 12)))')"
if [ "${PY_OK}" != "1" ]; then
  echo "${SELECTED_PYTHON_BIN} must be Python >= 3.12"
  "${SELECTED_PYTHON_BIN}" -V || true
  exit 1
fi

echo "[deploy-systemd] Using Python interpreter: ${SELECTED_PYTHON_BIN}"

echo "[deploy-systemd] Ensuring Python venv and dependencies..."
cd "${APP_DIR}/api"
if [ -d ".venv" ]; then
  VENV_OK="$(.venv/bin/python -c 'import sys; print(int(sys.version_info >= (3, 12)))' 2>/dev/null || echo 0)"
  if [ "${VENV_OK}" != "1" ]; then
    echo "[deploy-systemd] Existing .venv uses Python < 3.12. Recreating..."
    rm -rf .venv
  fi
fi

if [ ! -d ".venv" ]; then
  "${SELECTED_PYTHON_BIN}" -m venv .venv
fi

.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e .

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "[deploy-systemd] Created api/.env from .env.example (please review values)"
fi

cd "${APP_DIR}"

echo "[deploy-systemd] Rendering unit file..."
sed \
  -e "s|__APP_DIR__|${APP_DIR}|g" \
  -e "s|__SERVICE_USER__|${SERVICE_USER}|g" \
  -e "s|__SERVICE_GROUP__|${SERVICE_GROUP}|g" \
  -e "s|__SERVICE_PORT__|${SERVICE_PORT}|g" \
  -e "s|__UVICORN_WORKERS__|${UVICORN_WORKERS}|g" \
  "${TEMPLATE_PATH}" > "${RENDERED_PATH}"

sudo mv "${RENDERED_PATH}" "${UNIT_PATH}"

sudo systemctl daemon-reload
sudo systemctl enable "${SERVICE_NAME}"
sudo systemctl restart "${SERVICE_NAME}"

echo "[deploy-systemd] Service status:"
sudo systemctl status "${SERVICE_NAME}" --no-pager

echo "[deploy-systemd] Done."
