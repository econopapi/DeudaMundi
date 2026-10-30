#!/usr/bin/env bash
# Build the Python dependency graph of the DeudaMundi production backend
# (research step 2), using research/dependencies/pip-inspect.json as the
# FROZEN PHOTO (step 1). It does NOT rebuild the image and does NOT
# reinstall/upgrade anything.
#
# What this does:
#   1. verifies the frozen photo against research/dependencies/SHA256SUMS;
#   2. reuses the local snapshot image (docker create + docker cp; no bind
#      mounts, no rebuild) to run extract_dependency_graph.py with the same
#      interpreter (pip vendored `packaging`) that built the photo;
#   3. cross-checks the snapshot image against the environment recorded in
#      the photo (pip + Python versions);
#   4. writes the step-2 outputs into research/dependencies/graph/;
#   5. performs a second extraction and verifies byte-level stability;
#   6. writes SHA256SUMS and verification.txt.
#
# Usage (from anywhere):
#   ./research/dependencies/graph/build_dependency_graph.sh
#
# Environment overrides:
#   SNAPSHOT_TAG   image tag with the frozen environment
#                  (default deudamundi-api:research-env-snapshot)
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
DEPS_DIR="${REPO_ROOT}/research/dependencies"
OUT_DIR="${DEPS_DIR}/graph"
IMAGE_TAG="${SNAPSHOT_TAG:-deudamundi-api:research-env-snapshot}"

command -v docker >/dev/null || { echo "ERROR: docker no disponible" >&2; exit 1; }
command -v sha256sum >/dev/null || { echo "ERROR: sha256sum no disponible" >&2; exit 1; }

mkdir -p "${OUT_DIR}"

# --- 1. verify the frozen photo ----------------------------------------------
echo "==> verifying frozen photo (pip-inspect.json vs step-1 SHA256SUMS)"
( cd "${DEPS_DIR}" && grep -F -- './pip-inspect.json' SHA256SUMS | sha256sum -c - ) \
  || { echo "ERROR: pip-inspect.json no coincide con la foto congelada del paso 1" >&2; exit 1; }

# --- 2. reuse the snapshot image (no rebuild) ----------------------------------
if ! docker image inspect "${IMAGE_TAG}" >/dev/null 2>&1; then
  echo "ERROR: la imagen ${IMAGE_TAG} no existe localmente." >&2
  echo "Reconstruyela UNA VEZ con ./research/dependencies/extract_env_snapshot.sh" >&2
  echo "(o ejecuta este script en una maquina que tenga la imagen del paso 1)." >&2
  exit 1
fi

# --- 3. interpreter/environment cross-check against the photo -----------------
IMG_PIP_VERSION="$(docker run --rm --entrypoint python "${IMAGE_TAG}" -m pip --version \
  | awk '{print $2}')"
IMG_PYTHON_VERSION="$(docker run --rm --entrypoint python "${IMAGE_TAG}" \
  -c 'import sys;print(".".join(map(str,sys.version_info[:3])))')"
PHOTO_PIP_VERSION="$(grep -o '"pip_version": *"[^"]*"' "${DEPS_DIR}/pip-inspect.json" \
  | head -1 | cut -d'"' -f4)"
PHOTO_PYTHON_VERSION="$(grep -o '"python_full_version": *"[^"]*"' "${DEPS_DIR}/pip-inspect.json" \
  | head -1 | cut -d'"' -f4)"

VERIF="${OUT_DIR}/verification.txt"
{
  echo "# verification.txt - step 2 extraction checks"
  echo "generated_at_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "image_tag: ${IMAGE_TAG}"
  echo "photo_pip_version: ${PHOTO_PIP_VERSION}"
  echo "image_pip_version: ${IMG_PIP_VERSION}"
  echo "photo_python_version: ${PHOTO_PYTHON_VERSION}"
  echo "image_python_version: ${IMG_PYTHON_VERSION}"
} > "${VERIF}"

if [ "${IMG_PIP_VERSION}" = "${PHOTO_PIP_VERSION}" ] \
   && [ "${IMG_PYTHON_VERSION}" = "${PHOTO_PYTHON_VERSION}" ]; then
  echo "environment_match: OK" >> "${VERIF}"
else
  echo "environment_match: MISMATCH (results not trustworthy)" >> "${VERIF}"
  echo "ERROR: el entorno de la imagen no coincide con la foto." >&2
  exit 1
fi

# --- 4. extract (twice for stability) ------------------------------------------
run_extraction() {
  local dest="$1"
  local tmp="$2" cid
  mkdir -p "$(dirname "${dest}")"
  rm -rf "${dest}" "${tmp}"
  mkdir -p "${tmp}"
  cid="$(docker create \
    --entrypoint python \
    -e GRAPH_OUT=/tmp/graph \
    -e GRAPH_SNAPSHOT=/tmp/pip-inspect.json \
    -e GRAPH_PYPROJECT=/tmp/pyproject.toml \
    -e GRAPH_STEP1_TXT=/tmp/installed-packages.txt \
    "${IMAGE_TAG}" /tmp/extract_dependency_graph.py)"
  trap 'docker rm -f "${cid}" >/dev/null 2>&1 || true' RETURN
  docker cp "${DEPS_DIR}/pip-inspect.json"        "${cid}:/tmp/pip-inspect.json"
  docker cp "${REPO_ROOT}/api/pyproject.toml"     "${cid}:/tmp/pyproject.toml"
  docker cp "${DEPS_DIR}/installed-packages.txt"  "${cid}:/tmp/installed-packages.txt"
  docker cp "${OUT_DIR}/extract_dependency_graph.py" "${cid}:/tmp/extract_dependency_graph.py"
  docker start -a "${cid}" >&2
  for f in nodes.csv edges.csv edges-inactive.csv paths.txt \
           graph-diagram.mmd checks.json step1-vs-step2.txt; do
    docker cp "${cid}:/tmp/graph/${f}" "${tmp}/${f}"
  done
  mv "${tmp}" "${dest}"
}

echo "==> extraction run 1/2"
run_extraction "${OUT_DIR}/runs/run1" "${OUT_DIR}/.tmp1"
echo "==> extraction run 2/2 (stability)"
run_extraction "${OUT_DIR}/runs/run2" "${OUT_DIR}/.tmp2"

if diff -r "${OUT_DIR}/runs/run1" "${OUT_DIR}/runs/run2" >/dev/null 2>&1; then
  echo "stability: PASS (byte-identical outputs across two runs)" >> "${VERIF}"
  diff_result="stable"
else
  {
    echo "stability: FAIL"
    diff -r "${OUT_DIR}/runs/run1" "${OUT_DIR}/runs/run2" || true
  } >> "${VERIF}"
  diff_result="unstable"
fi

# publish run1 as the artifact set; drop the stability helper copy
cp "${OUT_DIR}/runs/run1/"*.csv \
   "${OUT_DIR}/runs/run1/"*.txt \
   "${OUT_DIR}/runs/run1/"*.mmd \
   "${OUT_DIR}/runs/run1/"checks.json \
   "${OUT_DIR}/"
echo "stability_detail: outputs published from run1; run2 discarded after diff" >> "${VERIF}"
echo "stability_result: ${diff_result}" >> "${VERIF}"
rm -rf "${OUT_DIR}/runs" "${OUT_DIR}/.tmp1" "${OUT_DIR}/.tmp2"

# --- 5. checksums ---------------------------------------------------------------
( cd "${OUT_DIR}" &&
  find . -maxdepth 1 -type f ! -name 'SHA256SUMS' | LC_ALL=C sort \
  | xargs sha256sum > SHA256SUMS )
echo "==> outputs in ${OUT_DIR}:"
ls -1 "${OUT_DIR}"
