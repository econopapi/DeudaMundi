#!/usr/bin/env bash
# Step 3 of the research protocol: attribute each of the 37 runtime
# dependencies of the frozen DeudaMundi graph to its source repository.
#
# It does NOT rebuild the image, install or upgrade anything; it only reads
# the frozen universe (research/dependencies/graph/nodes.csv + research/
# dependencies/pip-inspect.json) and consults read-only external APIs, with
# every response cached verbatim (pypi-evidence/, github-evidence/) so the
# decisions are auditable and reproducible offline.
#
# What this does:
#   1. verifies the frozen inputs against the step-1/step-2 SHA256SUMS;
#   2. runs identify_source_repos.py twice and REQUIRES byte-identical
#      tables: on instability it exits 1 WITHOUT publishing anything (the
#      previously published set, verification.txt and SHA256SUMS included,
#      stays untouched);
#   3. checks coverage (exactly 37 distributions, no missing/duplicates,
#      frozen versions consistent with nodes.csv);
#   4. publishes outputs, verification.txt and SHA256SUMS only after every
#      gate passes (see step-2 orchestrator for the pattern).
#
# Usage:
#   ./research/dependencies/attributions/build_source_attribution.sh
#
# Environment:
#   COVERAGE_TEST  'drop' strips one distribution from the universe to
#                  DEMONSTRATE the coverage check failing hard; leave unset
#                  for normal operation.
#                  'no-universe' fabricates an empty universe for the demo.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${HERE}/../../.." && pwd)"
DEPS_DIR="${REPO_ROOT}/research/dependencies"
OUT_DIR="${HERE}"
COVERAGE_TEST="${COVERAGE_TEST:-}"

command -v gh >/dev/null || { echo "ERROR: gh CLI no disponible" >&2; exit 1; }
command -v python3 >/dev/null || { echo "ERROR: python3 no disponible" >&2; exit 1; }
command -v sha256sum >/dev/null || { echo "ERROR: sha256sum no disponible" >&2; exit 1; }

fail() { echo "ERROR: $*" >&2; exit 1; }

# --- 1. verify the frozen inputs ---------------------------------------------
echo "==> verifying frozen inputs"
( cd "${DEPS_DIR}/graph" && grep -F -- './nodes.csv' SHA256SUMS | sha256sum -c - ) \
  || fail "nodes.csv no coincide con el grafo congelado del paso 2"
( cd "${DEPS_DIR}" && grep -F -- './pip-inspect.json' SHA256SUMS | sha256sum -c - ) \
  || fail "pip-inspect.json no coincide con la foto congelada del paso 1"

# --- 2. extract twice and require byte-identical outputs ----------------------
TABLE_FILES="source-repos.csv attributions.json coverage-check.txt"

run_extraction() {
  local dest="$1"
  rm -rf "${dest}"
  mkdir -p "${dest}"
  ATTR_OUT="${dest}" "${OUT_DIR}/identify_source_repos.py"
}

echo "==> extraction run 1/2"
run_extraction "${OUT_DIR}/runs/run1"
echo "==> extraction run 2/2 (stability)"
run_extraction "${OUT_DIR}/runs/run2"

if diff -r "${OUT_DIR}/runs/run1" "${OUT_DIR}/runs/run2" >/dev/null 2>&1; then
  stability="PASS (byte-identical outputs across two runs)"
else
  stability="FAIL (two extractions differ)"
fi

# --- 3. coverage verification -------------------------------------------------
COVERAGE_RESULT="FAIL"
if [ -f "${OUT_DIR}/runs/run1/coverage-check.txt" ]; then \
  COVERAGE_RESULT="$(python3 -c "import json;print(json.load(open('${OUT_DIR}/runs/run1/coverage-check.txt'))['result'])")"
fi

VERIF="${OUT_DIR}/.verification.staged"
VERIF_PUBLISHED="${OUT_DIR}/verification.txt"
rm -f "${VERIF}"
{
  echo "# verification.txt - step 3 attribution checks"
  echo "generated_at_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "inputs_source: graph/nodes.csv (step 2) + pip-inspect.json (step 1), hash-verified"
  echo "coverage_result: ${COVERAGE_RESULT}"
  echo "stability_result: ${stability}"
  echo "publish_policy: verification.txt is published ONLY after every gate passes"
} > "${VERIF}"
trap 'rm -f "${OUT_DIR}/.verification.staged"' EXIT
echo "gates: inputs OK; coverage ${COVERAGE_RESULT}; stability ${stability}"

if [ "${COVERAGE_RESULT}" != "PASS" ] || [[ "${stability}" != PASS* ]]; then
  echo "ERROR: una puerta no pasó." >&2
  echo "       Runs para depuración conservados en ${OUT_DIR}/runs/ (run1, run2)." >&2
  echo "       Los artefactos publicados (verification.txt, SHA256SUMS, tablas)" >&2
  echo "       no se tocaron: siguen siendo los de la última corrida verde." >&2
  exit 1
fi

# --- 4. publish only after every gate passed ----------------------------------
for f in ${TABLE_FILES}; do
  cp "${OUT_DIR}/runs/run1/${f}" "${OUT_DIR}/${f}"
done
rm -rf "${OUT_DIR}/runs"
mv "${VERIF}" "${VERIF_PUBLISHED}"

( cd "${OUT_DIR}" &&
  find . -maxdepth 1 -type f ! -name 'SHA256SUMS' | LC_ALL=C sort \
  | xargs sha256sum > SHA256SUMS )
echo "==> outputs in ${OUT_DIR}:"
ls -1 "${OUT_DIR}"
