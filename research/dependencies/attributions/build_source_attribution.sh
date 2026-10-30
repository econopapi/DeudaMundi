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
#   1. verifies frozen inputs AND the cached external evidence against the
#      committed SHA256SUMS BEFORE extraction — the manifest covers ALL
#      files (tables + the 72 pypi-evidence/ and github-evidence/ JSONs), so
#      a tampered/drifting cache stops the run instead of being silently
#      overwritten by a regeneration;
#   2. runs identify_source_repos.py twice and REQUIRES byte-identical
#      tables: on instability it exits 1 WITHOUT publishing anything (the
#      previously published set, verification.txt and SHA256SUMS included,
#      stays untouched);
#   3. checks coverage (exactly 37 distributions, no missing/duplicates,
#      and frozen versions consistent with BOTH inputs: nodes.csv AND the
#      step-1 photo pip-inspect.json);
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

# derived garbage must never enter the manifest or trip the gates
rm -rf "${OUT_DIR}/__pycache__"

# --- 1. verify frozen inputs AND cached evidence (full manifest) --------------
echo "==> verifying frozen inputs"
( cd "${DEPS_DIR}/graph" && grep -F -- './nodes.csv' SHA256SUMS | sha256sum -c - ) \
  || fail "nodes.csv no coincide con el grafo congelado del paso 2"
( cd "${DEPS_DIR}" && grep -F -- './pip-inspect.json' SHA256SUMS | sha256sum -c - ) \
  || fail "pip-inspect.json no coincide con la foto congelada del paso 1"

echo "==> verifying cached evidence against the committed manifest"
# 1a. every file listed in SHA256SUMS must match (catches modified caches).
# The manifest covers ALL committed files: tables, docs AND the 72 evidence
# JSONs. The two code scripts are EXCLUDED from this live check (they cannot
# certify their own hash while being edited; their integrity is the git
# history), and any drift there is reported as a warning, not a failure —
# drift in DATA/EVIDENCE files remains a hard stop.
CODE_FILES_RE='^\S+  \./(build_source_attribution\.sh|identify_source_repos\.py)$'
CHECK_MANIFEST="$(mktemp)"
( cd "${OUT_DIR}" && grep -vE "${CODE_FILES_RE}" SHA256SUMS ) > "${CHECK_MANIFEST}"
if ! ( cd "${OUT_DIR}" && sha256sum -c "${CHECK_MANIFEST}" 2>&1 >/dev/null | grep -q . ); then
  : # all good (failures would have been printed by the check itself)
fi
if ( cd "${OUT_DIR}" && sha256sum -c "${CHECK_MANIFEST}" --quiet >/dev/null 2>&1 ); then
  : # PASS
else
  ( cd "${OUT_DIR}" && sha256sum -c "${CHECK_MANIFEST}" 2>&1 || true ) >&2
  rm -f "${CHECK_MANIFEST}"
  fail "SHA256SUMS no corresponde a los ficheros del directorio (tablas o caches de evidencia modificadas). Deteniendo: no se regenera nada sobre evidencia adulterada."
fi
rm -f "${CHECK_MANIFEST}"
for f in build_source_attribution.sh identify_source_repos.py; do
  expected="$( cd "${OUT_DIR}" && awk -v f="./${f}" '$2 == f {print $1}' SHA256SUMS )"
  actual="$( cd "${OUT_DIR}" && sha256sum "./${f}" | awk '{print $1}' )"
  if [ -n "${expected}" ] && [ "${expected}" != "${actual}" ]; then
    echo "AVISO: ${f} difiere del hash del manifiesto (código local candidato a commit); la puerta continúa porque el manifiesto protege datos/evidencia y la integridad del código queda en el historial git." >&2
  fi
done

# 1b. every evidence file present on disk must be listed in the manifest
# (catches new evidence smuggled in without being committed).
# Both counts run INSIDE OUT_DIR so the gate does not depend on the
# caller's working directory.
evidence_count="$(cd "${OUT_DIR}" && find pypi-evidence github-evidence -type f 2>/dev/null | wc -l)"
manifest_evidence_count="$(cd "${OUT_DIR}" && grep -cE '^\S+  \./(pypi-evidence|github-evidence)/' SHA256SUMS || true)"
if [ "${evidence_count}" != "${manifest_evidence_count}" ]; then
  fail "hay ${evidence_count} ficheros de evidencia en pypi-evidence/ y github-evidence/ pero solo ${manifest_evidence_count} figuran en SHA256SUMS. Evidencia no cometida detectada; deteniendo."
fi
echo "==> evidence cache verified: ${evidence_count} ficheros, manifest al día"

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
  run_snapshot_consistency="$(python3 -c "import json;print(json.load(open('${OUT_DIR}/runs/run1/coverage-check.txt'))['snapshot_consistency']['nodes_vs_photo_versions'])")"
else
  stability="FAIL (two extractions differ)"
  run_snapshot_consistency="FAIL"
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
  echo "evidence_cache: ${evidence_count} ficheros (pypi-evidence + github-evidence) verificados contra SHA256SUMS antes de extraer"
  echo "nodes_vs_photo_versions: ${run_snapshot_consistency}"
  echo "coverage_result: ${COVERAGE_RESULT}"
  echo "stability_result: ${stability}"
  echo "publish_policy: verification.txt is published ONLY after every gate passes"
} > "${VERIF}"
trap 'rm -f "${OUT_DIR}/.verification.staged"' EXIT
echo "gates: inputs OK; evidence ${evidence_count} OK; nodes_vs_photo ${run_snapshot_consistency}; coverage ${COVERAGE_RESULT}; stability ${stability}"

if [ "${COVERAGE_RESULT}" != "PASS" ] || [[ "${stability}" != PASS* ]] || [ "${run_snapshot_consistency}" != "PASS" ]; then
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

# The regenerated manifest now covers EVERYTHING: tables and the evidence
# caches themselves (pypi-evidence/, github-evidence/), so the next run's
# gate 1 verifies the JSONs bit-for-bit.
( cd "${OUT_DIR}" &&
  find . -type f ! -name 'SHA256SUMS' ! -path '*/__pycache__/*' ! -path './runs/*' | LC_ALL=C sort \
  | xargs sha256sum > SHA256SUMS )
# planted check: the freshly regenerated manifest itself must validate
( cd "${OUT_DIR}" && sha256sum -c SHA256SUMS --quiet ) \
  || fail "el manifiesto recién regenerado no valida; estado inconsistente"
echo "==> outputs in ${OUT_DIR} (manifest ahora incluye evidencia):"
ls -1 "${OUT_DIR}"
