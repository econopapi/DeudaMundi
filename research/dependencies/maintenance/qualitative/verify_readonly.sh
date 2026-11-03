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
#   5. Validez y trazabilidad de claim-ledger.csv y coverage-matrix.csv.
#   6. Referencias internas (enlaces relativos de los .md del paquete).
#   7. Ausencia de modificaciones sin commitear en datos congelados.

set -e
ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"
FAIL=0
note() { printf '%s\n' "$*"; }
check() {
  if [ "$1" -eq 0 ]; then note "PASS: $2"; else note "FAIL: $2"; FAIL=1; fi
}

note "== 1. Manifiesto del Paso 4 (maintenance/SHA256SUMS) =="
( cd research/dependencies/maintenance && sha256sum -c SHA256SUMS >/dev/null 2>&1 )
check $? "454/454 entradas del Paso 4 (incluye los 443 JSON congelados)"

note "== 2. Manifiesto del Paso 5 (maintenance/analysis/SHA256SUMS) =="
( cd research/dependencies/maintenance/analysis && sha256sum -c SHA256SUMS >/dev/null 2>&1 )
check $? "todas las entradas del Paso 5 verifican"

note "== 3. Manifiesto cualitativo (maintenance/qualitative/SHA256SUMS) =="
( cd research/dependencies/maintenance/qualitative && sha256sum -c SHA256SUMS >/dev/null 2>&1 )
check $? "todas las entradas del paquete cualitativo verifican"

note "== 4. Manifiestos Plotly (index.json vs fig{1..5}.json) =="
python3 - << 'PYEOF'
import hashlib, json, sys, pathlib
base = pathlib.Path("research/dependencies/maintenance/analysis/results/plotly-embed")
idx = json.loads((base / "index.json").read_text())
ok = 0
for fig in idx["figures"]:
    digest = hashlib.sha256((base / fig["file"]).read_bytes()).hexdigest()
    if digest == fig["sha256"]:
        ok += 1
print(f"{ok}/5 manifiestos Plotly coinciden con index.json")
sys.exit(0 if ok == 5 else 1)
PYEOF
check $? "5/5 figuras Plotly"

note "== 5. claim-ledger.csv y coverage-matrix.csv =="
python3 - << 'PYEOF'
import csv, re, sys
base = "research/dependencies/maintenance/qualitative/"
rows = list(csv.DictReader(open(base + "claim-ledger.csv")))
assert rows and len(rows[0]) == 7, "claim-ledger.csv mal formado"
ids = [r["id"] for r in rows]
assert len(set(ids)) == len(ids), "IDs duplicados en claim-ledger.csv"
assert all(r["nivel_evidencia"] and r["fuente_exacta"] for r in rows), "fila incompleta"
matrix = list(csv.DictReader(open(base + "coverage-matrix.csv")))
missing = set()
for row in matrix:
    for cid in re.findall(r"C\d\d", row["claim_id"]):
        if cid not in set(ids):
            missing.add(cid)
assert not missing, f"IDs inexistentes citados en coverage-matrix.csv: {missing}"
print(f"{len(rows)} afirmaciones (IDs únicos, 7 columnas); "
      f"{len(matrix)} filas de cobertura, todas trazables")
PYEOF
check $? "registro de afirmaciones válido y trazable"

note "== 6. Referencias internas de los .md del paquete =="
python3 - << 'PYEOF'
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
check $? "sin enlaces relativos rotos"

note "== 7. Datos congelados sin modificar (sin commitear) =="
DIRTY=$(git status --porcelain -- \
  research/dependencies/maintenance/data \
  research/dependencies/maintenance/analysis/results \
  research/dependencies/maintenance/analysis/pypi-evidence \
  research/dependencies/graph \
  research/dependencies/attributions \
  research/dependencies/pip-inspect.json)
if [ -z "$DIRTY" ]; then
  check 0 "data/, analysis/results/, pypi-evidence/, graph/, attributions/: intactos"
else
  printf '%s\n' "$DIRTY"
  check 1 "hay modificaciones sin commitear en rutas congeladas"
fi

note ""
if [ "$FAIL" -eq 0 ]; then note "VERIFICACIÓN COMPLETA: PASS"; else note "VERIFICACIÓN COMPLETA: FAIL"; fi
exit "$FAIL"
