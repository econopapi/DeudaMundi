# Fase 0 — control de integridad y matriz de estado

**Fecha de verificación:** 2 de noviembre de 2026 UTC. **Rama:**
`research/deudamundi-dependencies`. **HEAD verificado:** `761a947` = commit de
referencia del encargo (`761a9470a2d5a71c68319b8bd0593947d881899d`); la rama no
avanzó antes de este trabajo. **Árbol de trabajo:** limpio al inicio de la
ejecución (sin cambios ajenos que preservar).

## Verificaciones ejecutadas (solo lectura)

| Comando | Resultado |
|---|---|
| `git status` / `git rev-parse HEAD` | Limpio; HEAD = `761a9470a2d5a71c68319b8bd0593947d881899d` |
| `python research/dependencies/maintenance/verify_activity.py` | PASS 35/35; 144/183/45 páginas; 2 ventanas (regenera `coverage-descriptive.csv` de forma determinista: el árbol siguió limpio, es decir, byte-idéntico) |
| `sha256sum -c maintenance/SHA256SUMS` | **454/454 OK** tras la corrección autorizada de la entrada `README.md` (hallazgo H-01, 2026-11-03). Antes de la corrección: 453/454, única desviación `README.md` (documentación, no datos) |
| `sha256sum -c maintenance/analysis/SHA256SUMS` | **Todos OK** (incluye `results/`, `figures/`, `plotly-embed/`, scripts) |
| `index.json` de `plotly-embed/` vs `fig{1..5}.json` | **PASS 5/5**; los mismos hashes constan además en `analysis/SHA256SUMS` |
| Reconstrucción de resultados | No se re-ejecutó `analyze_activity.py` para no tocar derivados; la verificación del Paso 5 (byte-idéntica en checkout limpio) consta en `../analysis/final-audits/dictamen.md` |
| Búsqueda de trabajo cualitativo previo | **No existe** ningún directorio, archivo ni commit posterior al HEAD de referencia con trabajo cualitativo (`git log --all`, búsqueda de rutas `*qualitative*`/`*cualit*`): no hay riesgo de duplicarlo |

## Hallazgo H-01 — manifiesto del Paso 4 desalineado en `README.md` (**corregido y documentado el 2026-11-03**)

- `maintenance/SHA256SUMS` declaraba para `README.md` el hash
  `8188c66599b8f20e…`, pero el archivo versionado actual (y el del checkout
  `e02ad67` auditado por el dictamen) tiene `81e9affe5f242729…`.
- Causa (confirmada con Git): `maintenance/README.md` se editó en `eaee185`
  («align README wording with final WP integration path») sin refrescar la
  entrada del manifiesto, que data de `1363af8`.
- **Impacto:** nulo sobre datos científicos (es un documento de navegación, no
  evidencia). Afectaba a la afirmación del dictamen «454/454 OK» para este
  manifiesto: con el árbol anterior la comprobación real era 453/454.
- **Acción tomada (excepción controlada del encargo de auditoría):** se
  actualizó **únicamente** la entrada de `README.md` en `maintenance/SHA256SUMS`
  — hash anterior `8188c66599b8f20e8ee1a1065de19b122bb34768e8ab3851ad4616ead1f6f1fa`;
  hash nuevo `81e9affe5f2427299f19c27c185115605dd54fcc64fb55446338ea10166265b6`;
  fecha 2026-11-03; motivo: alinear el manifiesto con un documento ya
  versionado y verificado —, con el diff de una sola línea conservado en el
  commit y la trazabilidad completa en `corrective-audit.md`. **No** se tocó
  ninguna otra entrada: los 453 hashes restantes (incluidos los 443 JSON de
  actividad) permanecen idénticos y verifican.
- **Verificación posterior:** `sha256sum -c maintenance/SHA256SUMS` →
  **454/454 OK**. El hallazgo queda registrado como anomalía documental
  detectada y corregida, no ocultada.

## Qué está confirmado como canónico

- Resultados H1–H4 y sensibilidad: `../analysis/results/hypotheses.json`,
  `h3-test.csv`, `repo-metrics.csv`, `actor-shares.csv`, `continuity.csv`,
  `../analysis/final-audits/traceability-h1h4.csv`.
- Valores de referencia obligatorios (dictamen/README del Paso 5): H1 12m = 22
  evaluables, 15 cuotas numéricas > 50 %, 1 inconcluso (fastapi), 14
  conclusivos; H2 12m = 6 cambios de categoría de 18 evaluables (autoría de
  commits vs autoría de PR fusionados, no integración; 13/18 mayor cuota por
  commits, 2/18 por PR, 3/18 iguales); H3 = 4 casos
  (psycopg, certifi, httpx, tzlocal); H4 12m = 18 repos incluidos, 16 con
  revisión evaluable, **6 divergencias** (5 parciales: dos cuentas coinciden;
  1 con las tres distintas, sqlalchemy) **y 10 coincidencias** de los tres
  roles (24m: 25/24/6/18 con la misma estructura) — recontado de
  `hypotheses.json` en la auditoría correctiva 2026-11-03.
- Figuras v2: `../analysis/results/plotly-embed/fig{1..5}.json` + `index.json`
  (manifiestos Econopapi Plotly v1). Los `post-2735-fig*.json` son archivo
  histórico y **no** son fuente de la nueva integración.
- Selección mecánica de los seis casos: `../analysis/plan.md`, Aclaración 3.

## Matriz de estado — completado / pendiente / requiere decisión editorial

| Componente | Estado | Evidencia exacta |
|---|---|---|
| Pasos 1–4 (foto, grafo, atribución, actividad congelada) | **Completado** | `verify_activity.py` PASS 35/35; manifiestos (salvo H-01); 443 JSON íntegros |
| Paso 5 — análisis descriptivo H1–H4 | **Completado (APROBADO CON LIMITACIONES)** | `../analysis/final-audits/dictamen.md` (30-10-2026) |
| Limitaciones persistentes del dictamen (rama por fecha, ventana `updatedAt`, tags sin release, cobertura ≠ completitud, alias, compartimiento de datos) | **Completado (declaradas)** | `dictamen.md` §Limitaciones; se heredan sin resolver |
| Figuras v2 + payloads `plotly-embed` | **Completado** | hashes verificados 5/5 + `index.json` |
| Protocolo cualitativo y código de clasificación | **Completado (este paso)** | `protocol.md` (posterior al análisis cuantitativo; sin presentarse como preregistro) |
| Seis expedientes cualitativos | **Completado (este paso)** | `cases/*.md` con evidencia trazable E1–E4 |
| Triangulación H1–H4 | **Completado (este paso)** | `synthesis.md` (sin recalcular resultados) |
| Marco económico y literatura | **Completado (este paso)** | `literature.md` |
| Claim ledger | **Completado (este paso)** | `claim-ledger.csv` |
| Limitaciones cualitativas | **Completado (este paso)** | `limitations.md` |
| Propuesta editorial + especificación de figuras | **Completado (este paso, como propuesta)** | `editorial-handoff.md` |
| Consulta del contenido del artículo 2735 | **Completado (lectura autorizada por el autor con contraseña; sin edición)** | contenido leído por la API REST de WordPress el 02-11-2026; esquema de 74 bloques en `editorial-handoff.md` |
| Revisión factual con actores externos | **Requiere decisión editorial (recomendada; no condición universal de publicación)** | mensajes propuestos en `factual-review.md`; **no enviados** |
| Publicación del artículo y desbloqueo | **Requiere decisión editorial** | solo el autor puede autorizar; ver bloqueos en `editorial-handoff.md` |
| Integración de figuras en WordPress | **Pendiente (ejecución del agente del tema)** | especificación lista; **ningún cambio realizado en WordPress** |
| Cohorte comparativa (FastAPI/Flask/Django) | **Requiere decisión editorial (recomendación: diferir)** | `deferred-comparative-cohort.md` |
| Corrección de H-01 en `maintenance/SHA256SUMS` | **Completado (2026-11-03)** | entrada `README.md` refrescada con diff de una línea; 454/454 OK; trazabilidad en `corrective-audit.md` |
| Auditoría correctiva de cierre (Fase 6.1 del encargo) | **Completado (2026-11-03)** | `corrective-audit.md`; H4/C39 corregidos; grados de conocimiento A–D; sucesión vs transferencia; alcance y financiación; literatura auditada |
| Matriz de cobertura artículo 2735 ↔ claim-ledger | **Completado (2026-11-03, Opción A)** | `coverage-matrix.csv` (31 filas; texto íntegro del artículo leído por API REST con contraseña del post, solo lectura) |

## Nota de alcance

El cierre técnico del Paso 5 **no** equivale a la finalización del estudio:
quedaban la lectura cualitativa de los seis casos, la triangulación, la
revisión factual y la edición final. Este Paso 6 ejecuta las tres primeras y
prepara la cuarta; la publicación sigue bloqueada por decisiones que solo el
autor puede tomar.
