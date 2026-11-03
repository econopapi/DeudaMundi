#!/bin/sh
# verify_readonly.sh — verificación de solo lectura del paquete DeudaMundi
# (Pasos 1–6). No escribe nada: solo comprueba hashes, CSV y referencias.
#
# Uso, desde la raíz del repositorio:
#   sh research/dependencies/maintenance/qualitative/verify_readonly.sh
#
# Comprueba:
#   1. Manifiesto del Paso 4  (maintenance/SHA256SUMS) — 454 entradas.
#   2. Manifiesto del Paso 5  (maintenance/analysis/SHA256SUMS).
#   3. Manifiesto cualitativo (maintenance/qualitative/SHA256SUMS).
#   4. Los cinco manifiestos Plotly (plotly-embed/index.json vs fig{1..5}.json).
#   5. Validez e integridad referencial de claim-ledger.csv y
#      coverage-matrix.csv.
#   6. Referencias internas (enlaces relativos de los .md del paquete).
#   7. Ausencia de modificaciones sin commitear en datos congelados.
#
# ALCANCE DE LA VALIDACIÓN (importante): los pasos 5 y 6 comprueban
# **integridad referencial** (CSV válido, IDs existentes, enlaces resueltos).
# NO demuestran cobertura semántica exhaustiva del artículo: esa cobertura es
# una revisión manual documentada en coverage-matrix.csv (claim C45). Un PASS
# de este script no sustituye esa revisión.
#
# Manejo de errores: sin `set -e`; cada paso captura su estado, imprime PASS o
# FAIL con diagnóstico explícito y la ejecución continúa hasta el resumen
# final (exit != 0 si algo falló).

ROOT=$(git rev-parse --show-toplevel) || { echo "FAIL: no es un checkout de Git"; exit 2; }
cd "$ROOT" || { echo "FAIL: no se pudo acceder a la raíz $ROOT"; exit 2; }
FAIL=0

pass() { printf 'PASS: %s\n' "$1"; }
fail() { printf 'FAIL: %s\n' "$1"; FAIL=1; }

check_manifest() {
  dir="$1"; label="$2"
  out=$( cd "$dir" && sha256sum -c SHA256SUMS 2>&1 )
  rc=$?
  if [ "$rc" -eq 0 ]; then
    pass "$label ($(printf '%s\n' "$out" | grep -c ': OK$') entradas OK)"
  else
    fail "$label — sha256sum -c devolvió $rc; entradas con error:"
    printf '%s\n' "$out" | grep -v ': OK$' | sed 's/^/     /'
  fi
}

echo "== 1. Manifiesto del Paso 4 (maintenance/SHA256SUMS) =="
check_manifest research/dependencies/maintenance \
  "Paso 4 (incluye los 443 JSON congelados)"

echo "== 2. Manifiesto del Paso 5 (maintenance/analysis/SHA256SUMS) =="
check_manifest research/dependencies/maintenance/analysis \
  "Paso 5 (resultados, figuras, scripts)"

echo "== 3. Manifiesto cualitativo (maintenance/qualitative/SHA256SUMS) =="
check_manifest research/dependencies/maintenance/qualitative \
  "paquete cualitativo (Paso 6)"

echo "== 4. Manifiestos Plotly (index.json vs fig{1..5}.json) =="
out=$(python3 - << 'PYEOF'
import hashlib, json, sys, pathlib
base = pathlib.Path("research/dependencies/maintenance/analysis/results/plotly-embed")
idx = json.loads((base / "index.json").read_text())
ok = 0
for fig in idx["figures"]:
    digest = hashlib.sha256((base / fig["file"]).read_bytes()).hexdigest()
    if digest == fig["sha256"]:
        ok += 1
    else:
        print(f"descuadre: {fig['file']} (index.json dice {fig['sha256'][:16]}…)")
print(f"{ok}/5 manifiestos Plotly coinciden con index.json")
sys.exit(0 if ok == 5 else 1)
PYEOF
)
rc=$?
if [ "$rc" -eq 0 ]; then pass "5/5 figuras Plotly"; else
  fail "manifiestos Plotly (python devolvió $rc):"; printf '%s\n' "$out" | sed 's/^/     /'
fi

echo "== 5. claim-ledger.csv y coverage-matrix.csv (integridad referencial) =="
out=$(python3 - << 'PYEOF'
import csv, re, sys
base = "research/dependencies/maintenance/qualitative/"
rows = list(csv.DictReader(open(base + "claim-ledger.csv")))
assert rows and len(rows[0]) == 7, "claim-ledger.csv mal formado (se esperaban 7 columnas)"
ids = [r["id"] for r in rows]
assert len(set(ids)) == len(ids), "IDs duplicados en claim-ledger.csv"
assert all(r["nivel_evidencia"] and r["fuente_exacta"] for r in rows), "fila incompleta en claim-ledger.csv"
matrix = list(csv.DictReader(open(base + "coverage-matrix.csv")))
missing = set()
for row in matrix:
    for cid in re.findall(r"C\d\d", row["claim_id"]):
        if cid not in set(ids):
            missing.add(cid)
assert not missing, f"IDs inexistentes citados en coverage-matrix.csv: {missing}"
print(f"{len(rows)} afirmaciones (IDs únicos, 7 columnas); "
      f"{len(matrix)} filas de cobertura con IDs referencialmente válidos")
print("alcance: integridad referencial únicamente; la cobertura semántica "
      "exhaustiva es una revisión manual documentada (C45)")
PYEOF
)
rc=$?
if [ "$rc" -eq 0 ]; then
  pass "registro de afirmaciones válido (integridad referencial)"
  printf '%s\n' "$out" | sed 's/^/     nota: /'
else
  fail "claim-ledger/coverage-matrix (python devolvió $rc):"
  printf '%s\n' "$out" | sed 's/^/     /'
fi

echo "== 6. Referencias internas de los .md del paquete =="
out=$(python3 - << 'PYEOF'
import pathlib, re, sys
base = pathlib.Path("research/dependencies/maintenance/qualitative")
broken = []
for md in list(base.rglob("*.md")):
    for target in re.findall(r"\]\(([^)]+)\)", md.read_text()):
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        if "…" in target:  # URLs elididas dentro de fragmentos citados
            continue
        path = target.split("#")[0]
        if path and not (md.parent / path).exists():
            broken.append(f"{md.name} -> {path}")
for b in broken:
    print("rota:", b)
sys.exit(1 if broken else 0)
PYEOF
)
rc=$?
if [ "$rc" -eq 0 ]; then pass "sin enlaces relativos rotos"; else
  fail "referencias internas (python devolvió $rc):"; printf '%s\n' "$out" | sed 's/^/     /'
fi

echo "== 7. Datos congelados sin modificar (sin commitear) =="
DIRTY=$(git status --porcelain -- \
  research/dependencies/maintenance/data \
  research/dependencies/maintenance/analysis/results \
  research/dependencies/maintenance/analysis/pypi-evidence \
  research/dependencies/graph \
  research/dependencies/attributions \
  research/dependencies/pip-inspect.json)
if [ -z "$DIRTY" ]; then
  pass "data/, analysis/results/, pypi-evidence/, graph/, attributions/: intactos"
else
  fail "hay modificaciones sin commitear en rutas congeladas:"
  printf '%s\n' "$DIRTY" | sed 's/^/     /'
fi

echo ""
if [ "$FAIL" -eq 0 ]; then
  echo "VERIFICACIÓN COMPLETA: PASS"
  echo "(alcance: integridad de hashes, CSV y referencias; no es una prueba de cobertura semántica del artículo)"
else
  echo "VERIFICACIÓN COMPLETA: FAIL (ver diagnóstico por paso arriba)"
fi
exit "$FAIL"
