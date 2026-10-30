#!/usr/bin/env bash
# Build the Python dependency graph of the DeudaMundi production backend
# (research step 2), using research/dependencies/pip-inspect.json as the
# FROZEN PHOTO (step 1). It does NOT rebuild the image and does NOT
# reinstall/upgrade anything.
#
# What this does:
#   1. verifies the frozen photo against research/dependencies/SHA256SUMS;
#   2. binds the direct-dependency definition to the photo: compares the
#      frozen pyproject-frozen.toml (committed in this folder) with BOTH the
#      current checkout api/pyproject.toml AND /app/pyproject.toml inside the
#      step-1 image — any drift stops the extraction;
#   3. reuses the local snapshot image (docker create + docker cp; no bind
#      mounts, no rebuild) to run extract_dependency_graph.py with the same
#      interpreter (pip vendored `packaging`) that built the photo;
#   4. the extractor verifies the full identity of the installed
#      distributions (canonical name + version) between the photo and its
#      runtime, and hard-fails on mismatch;
#   5. performs a second extraction and REQUIRES byte-level stability: on
#      instability the orchestrator exits 1 WITHOUT publishing anything;
#   6. publishes outputs, then writes SHA256SUMS and verification.txt.
#
# Usage (from anywhere):
#   ./research/dependencies/graph/build_dependency_graph.sh
#
# Environment:
#   SNAPSHOT_TAG     image tag with the frozen environment
#                    (default deudamundi-api:research-env-snapshot)
#   STABILITY_TEST   'mismatch' mutates the second extraction's nodes.csv
#                    before the diff, to DEMONSTRATE the fail-fast publish
#                    guard; leave unset for normal operation.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
DEPS_DIR="${REPO_ROOT}/research/dependencies"
OUT_DIR="${DEPS_DIR}/graph"
API_PYPROJECT="${REPO_ROOT}/api/pyproject.toml"
FROZEN_PYPROJECT="${OUT_DIR}/pyproject-frozen.toml"
IMAGE_TAG="${SNAPSHOT_TAG:-deudamundi-api:research-env-snapshot}"
STABILITY_TEST="${STABILITY_TEST:-}"

command -v docker >/dev/null || { echo "ERROR: docker no disponible" >&2; exit 1; }
command -v sha256sum >/dev/null || { echo "ERROR: sha256sum no disponible" >&2; exit 1; }

mkdir -p "${OUT_DIR}"

fail() { echo "ERROR: $*" >&2; exit 1; }

# --- 1. verify the frozen photo ----------------------------------------------
echo "==> verifying frozen photo (pip-inspect.json vs step-1 SHA256SUMS)"
( cd "${DEPS_DIR}" && grep -F -- './pip-inspect.json' SHA256SUMS | sha256sum -c - ) \
  || fail "pip-inspect.json no coincide con la foto congelada del paso 1"

# --- 2. reuse the snapshot image (no rebuild) ----------------------------------
echo "==> reusing snapshot image ${IMAGE_TAG} (no rebuild, no installs)"
docker image inspect "${IMAGE_TAG}" >/dev/null 2>&1 \
  || fail "la imagen ${IMAGE_TAG} no existe localmente. Obténla ejecutando UNA VEZ ./research/dependencies/extract_env_snapshot.sh en una máquina que tenga el paso 1; este script no reconstruye ni resuelve dependencias."

# --- 3. bind direct deps/extras to the photo -----------------------------------
# 3a. the committed frozen copy must equal the CURRENT checkout of
#     api/pyproject.toml (otherwise the repo drifted since the photo)
[ -f "${FROZEN_PYPROJECT}" ] || fail "falta ${FROZEN_PYPROJECT} (copia congelada de api/pyproject.toml)"
if ! cmp -s "${API_PYPROJECT}" "${FROZEN_PYPROJECT}"; then
  fail "api/pyproject.toml del checkout actual difiere de la copia congelada pyproject-frozen.toml: el repositorio cambió desde la foto; deteniendo (no se resuelve ni re-instala dependencias)."
fi
echo "==> pyproject-frozen.toml == api/pyproject.toml (checkout): OK"

# 3b. the frozen copy must equal /app/pyproject.toml INSIDE the image
IMG_PYPROJECT="$(mktemp /tmp/img-pyproject-XXXXXX)"
docker create --name tmp-fg-dump "${IMAGE_TAG}" >/dev/null 2>&1 || true
docker cp "tmp-fg-dump:/app/pyproject.toml" "${IMG_PYPROJECT}" \
  || { docker rm -f tmp-fg-dump >/dev/null 2>&1 || true; fail "no se pudo leer /app/pyproject.toml de la imagen; no se puede vincular la definición de dependencias a la foto."; }
docker rm -f tmp-fg-dump >/dev/null 2>&1 || true
cmp -s "${IMG_PYPROJECT}" "${FROZEN_PYPROJECT}" \
  || fail "/app/pyproject.toml de la imagen difiere de pyproject-frozen.toml: la imagen ya no es la de la foto. Deteniendo."
rm -f "${IMG_PYPROJECT}"
echo "==> pyproject-frozen.toml == /app/pyproject.toml (imagen): OK"

# version cross-check against the photo
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
  [ "${IMG_PIP_VERSION}" = "${PHOTO_PIP_VERSION}" ] \
    && [ "${IMG_PYTHON_VERSION}" = "${PHOTO_PYTHON_VERSION}" ] \
    && echo "environment_match: OK"
  echo "pyproject_binding: frozen==checkout AND frozen==image(/app/pyproject.toml): OK"
} > "${VERIF}"
[ "${IMG_PIP_VERSION}" = "${PHOTO_PIP_VERSION}" ] \
  && [ "${IMG_PYTHON_VERSION}" = "${PHOTO_PYTHON_VERSION}" ] \
  || fail "el entorno (pip/Python) de la imagen no coincide con la foto. Deteniendo."

# --- 4. extract (twice: one blind run for stability) ----------------------------
STABLE_FILENAMES="nodes.csv edges.csv edges-inactive.csv paths.txt graph-diagram.mmd checks.json step1-vs-step2.txt"
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
  docker cp "${DEPS_DIR}/pip-inspect.json"       "${cid}:/tmp/pip-inspect.json"
  docker cp "${FROZEN_PYPROJECT}"                "${cid}:/tmp/pyproject.toml"
  docker cp "${DEPS_DIR}/installed-packages.txt" "${cid}:/tmp/installed-packages.txt"
  docker cp "${OUT_DIR}/extract_dependency_graph.py" "${cid}:/tmp/extract_dependency_graph.py"
  docker start -a "${cid}" >&2
  for f in ${STABLE_FILENAMES}; do
    docker cp "${cid}:/tmp/graph/${f}" "${tmp}/${f}"
  done
  mv "${tmp}" "${dest}"
}

echo "==> extraction run 1/2"
run_extraction "${OUT_DIR}/runs/run1" "${OUT_DIR}/.tmp1"
echo "==> extraction run 2/2 (stability)"
run_extraction "${OUT_DIR}/runs/run2" "${OUT_DIR}/.tmp2"

# --- 5. stability gate: differences must fail hard, publishing nothing ----------
if [ "${STABILITY_TEST}" = "mismatch" ]; then
  printf '\n# injected instability for the fail-fast demo\n' \
    >> "${OUT_DIR}/runs/run2/nodes.csv"
fi

if diff -r "${OUT_DIR}/runs/run1" "${OUT_DIR}/runs/run2" >/dev/null 2>&1; then
  echo "stability: PASS (byte-identical outputs across two runs)" >> "${VERIF}"
  echo "stability_detail: outputs published from run1; run2 discarded after diff" >> "${VERIF}"
  echo "stability_result: stable" >> "${VERIF}"
else
  {
    echo "stability: FAIL (two extractions differ)"
    echo "stability_result: unstable"
    echo "NOT PUBLISHED: no output from this orchestrator run is valid; publish nothing."
  } >> "${VERIF}"
  echo "ERROR: las dos extracciones difieren. No se publica NADA." >&2
  echo "       Runs para depuración conservados en ${OUT_DIR}/runs/ (run1, run2)." >&2
  echo "       Bórralos (rm -rf ${OUT_DIR}/runs) tras investigar." >&2
  exit 1
fi

# publish run1 as the artifact set; drop the stability helper copy
for f in ${STABLE_FILENAMES}; do
  cp "${OUT_DIR}/runs/run1/${f}" "${OUT_DIR}/${f}"
done
rm -rf "${OUT_DIR}/runs" "${OUT_DIR}/.tmp1" "${OUT_DIR}/.tmp2"

# --- 6. checksums ---------------------------------------------------------------
( cd "${OUT_DIR}" &&
  find . -maxdepth 1 -type f ! -name 'SHA256SUMS' | LC_ALL=C sort \
  | xargs sha256sum > SHA256SUMS )
echo "==> outputs in ${OUT_DIR}:"
ls -1 "${OUT_DIR}"
