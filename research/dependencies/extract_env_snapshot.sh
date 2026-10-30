#!/usr/bin/env bash
# Freeze a verifiable snapshot of the Python environment of the DeudaMundi
# backend PRODUCTION image (api/Dockerfile, target "production").
#
# What it does:
#   1. rebuilds the production image exactly as the repository defines it;
#   2. runs `python -m pip inspect` inside that image and saves the raw JSON;
#   3. categorizes the inventory (project package / direct / transitive / tooling)
#      using the pyproject.toml that lives inside the image (/app/pyproject.toml);
#   4. collects build and runtime metadata into manifest.json;
#   5. writes SHA256SUMS for every generated artifact.
#
# Usage (from anywhere):
#   ./research/dependencies/extract_env_snapshot.sh
#
# Environment overrides:
#   SNAPSHOT_TAG  image tag to use  (default deudamundi-api:research-env-snapshot)
#
# Host requirement: Docker only (git recommended; no host Python needed).
# Container files are exchanged with `docker cp` into /tmp (no bind mounts),
# so the script also works under userns-remap / selinux-restricted Docker installs.
#
# Result is an "environment snapshot", not a reproducible lock: see
# research/dependencies/README.md for what would be needed for a true lock.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT_DIR="${REPO_ROOT}/research/dependencies"
API_DIR="api"
BASE_REF="python:3.12-slim"
IMAGE_TAG="${SNAPSHOT_TAG:-deudamundi-api:research-env-snapshot}"
BUILD_CMD="docker build --file ${API_DIR}/Dockerfile --target production --tag ${IMAGE_TAG} ${API_DIR}"

# --- 0. sanity ---------------------------------------------------------------
command -v docker >/dev/null || { echo "ERROR: docker no está disponible" >&2; exit 1; }
mkdir -p "${OUT_DIR}"

# --- 1. build the production image as defined by the repo --------------------
echo "==> ${BUILD_CMD}"
(cd "${REPO_ROOT}" && ${BUILD_CMD})

# --- 2. capture image + base metadata ---------------------------------------
IMAGE_ID="$(docker image inspect "${IMAGE_TAG}" --format '{{.Id}}')"
IMAGE_ARCH="$(docker image inspect "${IMAGE_TAG}" --format '{{.Os}}/{{.Architecture}}')"
DOCKER_VERSION="$(docker version --format '{{.Client.Version}}')"

# Resolve the base image digest. Should the builder's storage not retain the
# base tag, this call is a no-op and the field stays empty (documented).
BASE_REPO_DIGESTS="$(docker image inspect "${BASE_REF}" --format '{{json .RepoDigests}}' 2>/dev/null || true)"
BASE_DIGEST=""
if [ -n "${BASE_REPO_DIGESTS}" ] && [ "${BASE_REPO_DIGESTS}" != "[]" ]; then
  BASE_DIGEST="$(printf '%s' "${BASE_REPO_DIGESTS}" | grep -oE 'sha256:[0-9a-f]{64}' | head -1 || true)"
fi

# --- 3. capture runtime facts (always from the built image) ------------------
echo "==> python -m pip inspect (inside ${IMAGE_TAG})"
docker run --rm --entrypoint python "${IMAGE_TAG}" -m pip inspect \
  > "${OUT_DIR}/pip-inspect.json"

SYSCONF_PLATFORM="$(docker run --rm --entrypoint python "${IMAGE_TAG}" \
  -c 'import sysconfig; print(sysconfig.get_platform())')"

# Smoke check: every declared runtime dependency must be importable here.
echo "==> smoke check: importing declared runtime dependencies"
docker run --rm --entrypoint python "${IMAGE_TAG}" -c \
  "import fastapi, uvicorn, httpx, apscheduler, pydantic_settings, sqlalchemy, alembic, psycopg, redis, slowapi; print('runtime imports OK')"

# --- 4. categorize + manifest (inside the image, where pyproject.toml lives) --
GENERATED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
COMMIT_SHA="$(git -C "${REPO_ROOT}" rev-parse HEAD 2>/dev/null || echo "")"
COMMIT_DATE="$(git -C "${REPO_ROOT}" log -1 --format='%cI' 2>/dev/null || echo "")"
COMMIT_SUBJECT="$(git -C "${REPO_ROOT}" log -1 --format='%s' 2>/dev/null || echo "")"
BRANCH="$(git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")"

echo "==> categorizing inventory and writing manifest"
CID="$(docker create \
  --entrypoint python \
  -e SNAPSHOT_OUT=/tmp \
  -e SNAPSHOT_WRITES_MANIFEST=1 \
  -e SNAPSHOT_GENERATED_AT="${GENERATED_AT}" \
  -e SNAPSHOT_COMMIT_SHA="${COMMIT_SHA}" \
  -e SNAPSHOT_COMMIT_DATE="${COMMIT_DATE}" \
  -e SNAPSHOT_COMMIT_SUBJECT="${COMMIT_SUBJECT}" \
  -e SNAPSHOT_BRANCH="${BRANCH}" \
  -e SNAPSHOT_BUILD_CMD="${BUILD_CMD}   # run from repo root" \
  -e SNAPSHOT_BASE_REF="${BASE_REF}" \
  -e SNAPSHOT_BASE_DIGEST="${BASE_DIGEST}" \
  -e SNAPSHOT_BASE_REPO_DIGESTS="${BASE_REPO_DIGESTS}" \
  -e SNAPSHOT_IMAGE_TAG="${IMAGE_TAG}" \
  -e SNAPSHOT_IMAGE_ID="${IMAGE_ID}" \
  -e SNAPSHOT_IMAGE_PLATFORM="${IMAGE_ARCH}" \
  -e SNAPSHOT_SYSCONF_PLATFORM="${SYSCONF_PLATFORM}" \
  -e SNAPSHOT_DOCKER_VERSION="${DOCKER_VERSION}" \
  "${IMAGE_TAG}" /tmp/categorize_env.py)"
trap 'docker rm -f "${CID}" >/dev/null 2>&1 || true' EXIT

docker cp "${OUT_DIR}/pip-inspect.json" "${CID}:/tmp/pip-inspect.json"
docker cp "${OUT_DIR}/categorize_env.py" "${CID}:/tmp/categorize_env.py"
docker start -a "${CID}"
docker cp "${CID}:/tmp/installed-packages.txt" "${OUT_DIR}/installed-packages.txt"
docker cp "${CID}:/tmp/manifest.json" "${OUT_DIR}/manifest.json"

# --- 5. checksums -------------------------------------------------------------
cd "${OUT_DIR}"
find . -maxdepth 1 -type f ! -name 'SHA256SUMS' | LC_ALL=C sort | xargs sha256sum > SHA256SUMS
echo "==> outputs written to ${OUT_DIR}:"
ls -l SHA256SUMS pip-inspect.json installed-packages.txt manifest.json
echo "Done. Commit these artifacts on the research branch."
