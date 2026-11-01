# Paso 5: análisis descriptivo de la actividad de mantenimiento

**Estado:** análisis de los datos del paso 4 ejecutado bajo `plan.md` (preregistrado antes de calcular). No identifica por sí solo a las personas mantenedoras ni mide riesgo, esfuerzo o remuneración. Rama `research/deudamundi-dependencies`.

## Qué contiene

| Ruta | Contenido |
|---|---|
| `plan.md` | Plan preregistrado (hipótesis H1–H4, denominadores, umbrales de evaluabilidad, reglas de bots/merges/no atribuidos, sensibilidad 12/24, aclaraciones fechadas). |
| `analyze_activity.py` | Rehora los conteos desde `../data/` (los 443 JSON congelados), sin red, y contrasta **cada** total contra `../coverage-descriptive.csv` antes de emitir resultados. Produce todo `results/`. |
| `results/` | `repo-metrics.csv` (70 filas = 35 repos × 2 ventanas), `actor-shares.csv`, `overview-totals.json`, `hypotheses.json` (H1/H2/H4 con sensibilidad), `h3-test.csv`, `continuity.csv`, `distribution-map.csv`, `low-activity.csv`, `audit-packs.json`. |
| `collect_pypi.py` + `pypi-evidence/` | Historial de versiones de PyPI para las 37 distribuciones (H3), con recibos URL/UTC/estado/hash SHA-256 por distribución; se ejecutó **después** del plan y antes del contraste, como quedó registrado. |
| `audit_manual.py` | Segunda implementación independiente para la auditoría manual: 24 repos × 2 ventanas disparadores de hipótesis + muestra aleatoria seed 42 + máxima exposición. Cero discrepancias contra el script principal en todos los campos comparados. |
| `audits.md` | Bitácora de auditoría manual, con las correcciones de proceso destapadas (todas fechadas y explicadas) y los patrones de automatización no declarada observados (`sqla-tester`, `claude`, `invalid-email-address`). |
| `make_figures.py` + `figures/` | Cinco figuras interactivas autocontenidas (Plotly 2.35.2 desde CDN con `no-integrity` documentado), identidad Econopapi con el manual oficial (`/home/econopapi/Projects/econopapi-video-studio/docs/brand/ECONOPAPI_BRAND_KIT_LIGHT_DARK_v04/`), fuente Montserrat/Source Sans Pro embebidas, claro/oscuro por `prefers-color-scheme` y toggle manual, tabla accesible por figura y texto alternativo; los datos exactos de cada gráfico viajan en `figN-data.json`. Subconjuntos de fuentes con pyftsubset 4.68.0 y licencias SIL OFL 1.1 (`FONTS-NOTICE.txt`). Son las figuras originales del paso 5: el scatter de `fig3-concentracion-commits-vs-pr.html` permanece como **suplemento técnico** del dictamen externo (01-11-2026). |
| `wp-snippets/` | (Eliminado 2026-10-31 por decisión del autor: los fragmentos wp:html y el plugin-puente quedaron fuera de la rama. El historial Git los conserva auditables.) |
| `export_payloads.py` | Exporta los **manifiestos Econopapi Plotly v1, figuras v2 del dictamen externo (01-11-2026, §5)**: `results/plotly-embed/fig{1..5}.json` + `index.json`. Derivados de presentación construidos únicamente desde `results/*.json|csv` y `figures/fig*-data.json` congelados (solo lectura; ya no consume `results/figure-meta.json`): fig1 totales por flujo con no aditividad, fig2 ranking apilado por commits no automatizados con conmutador 12/24 y recorte fijo top-15, fig3 barras divergentes de Δpp con H2 por categorías, fig4 dumbbell 12/24 con estados e inconclusos, fig5 100 % por flujo con pares únicos separados de crudas. Cada exportación reejecuta 9 contrastes contra los datos congelados y las cifras del dictamen y **aborta** ante cualquier discrepancia. No fija tipografía, fondos ni colorway (eso es del tema); solo la paleta funcional de actores/conectores/inconcluso, necesaria para leyendas coherentes al conmutar ventanas. |
| `SHA256SUMS` / `verification.txt` | Manifest del directorio y bitácora de verificación. |
| `final-audits/` | **Auditoría metodológica y científica de cierre (§2–§8)**: matriz de cobertura y procedencia por repositorio (`coverage-provenance.{py,csv,md}`), cronología metodológica con clasificación de cada cambio (`method_timeline.{py,csv,md}`), trazabilidad H1–H4 por repo y ventana (`traceability-h1h4.csv`), correspondencia PyPI↔GitHub (`pypi-github-map.csv`), muestra estratificada de eventos recontada de forma independiente (`manual_sample_audit.py` + `manual-sample-audits.json`), matriz de validez de constructo (`construct-validity.md`) y dictamen final por dimensión (`dictamen.md`). |

## Dictamen de cierre del análisis (resumen)

**El Paso 5 queda cerrado metodológicamente (APROBADO CON LIMITACIONES)**: la
reproducción es byte-idéntica desde checkout limpio sin red; los contrastes
reconcilian fila a fila con una tercera implementación; la cronología del
preregistro es demostrable frente a los resultados versionados (con la
advertencia honesta de que no prueba ausencia de impresiones previas de
terminal); los límites están declarados y no afectan denominadores publicados.
El detalle, la matriz de cobertura y el dictamen completo están en
`final-audits/dictamen.md`.

## Reproducción

Análisis **sin red** (solo los 443 JSON congelados), desde la raíz del repositorio, rama `research/deudamundi-dependencies`:

```sh
python research/dependencies/maintenance/verify_activity.py        # puerta del paso 4 (35/35)
python research/dependencies/maintenance/analysis/analyze_activity.py   # re-cómpilación + contraste vs coverage-descriptive.csv
python research/dependencies/maintenance/analysis/verify_contrasts.py   # contrastes corregidos (variante bots, H4, H1)
cd research/dependencies/maintenance && sha256sum -c SHA256SUMS    # manifiesto del directorio del paso 4
```

Visualización **requiere red** (Plotly 2.35.2 desde cdn.plot.ly; los datos de cada gráfico viven impregnados en el HTML/payload, no en el CDN):

```sh
cd research/dependencies/maintenance && sha256sum -c SHA256SUMS    # manifiesto de ESTE directorio (analysis/)
python research/dependencies/maintenance/analysis/make_figures.py       # tablas + figuras standalone + datos (suplemento original)
python research/dependencies/maintenance/analysis/export_payloads.py      # manifiestos Econopapi Plotly v1, figuras v2 (dictamen §5)
```

El exportador lee directamente los resultados congelados (`results/` y `figures/fig*-data.json`), así que **no requiere ejecutar `make_figures.py` antes**; sus contrastes se vuelven a comprobar en cada corrida.

Para publicar, sube `results/plotly-embed/fig1.json` a `fig5.json` en **Fuente de la figura**, un archivo por cada bloque `econopapi/plotly-figure`. No subas el HTML autocontenido ni `index.json`: este último solo cataloga los cinco manifiestos y sus hashes. El exportador toma `meta.analysis.commit` del `HEAD` del checkout y no necesita red, pandas ni Plotly para escribir los JSON. Los `post-2735-fig{1..5}.json` del mismo directorio son archivo histórico (lo subido al borrador 2735 el 01-11-2026, idéntico a los canónicos salvo el kicker); no se resuben.

El orden importa: `analyze_activity.py` verifica cada total contra `../coverage-descriptive.csv` (que el verificador del paso 4 también reconstruye) antes de emitir `results/`. Las figuras y el plugin se generan DESDE `results/`; el manifiesto `SHA256SUMS` de `analysis/`/YYYY:MM:DD cubre todos los artefactos publicados de este directorio. La banana del visor (plugin y zip) viene del post; no es dependencia del análisis.

## Resultados en una línea (todo está en `audits.md` y `results/`)

- **H1 (12m), sin ambigüedad:** 22 repos evaluables (≥30 commits no-bot sin fusiones); **15** con cuota numérica >50 %; **1 inconcluso** por la regla preregistrada (`fastapi/fastapi`, bots ≥50 % de sus commits); **14 conclusivos >50 %**: `sqlalchemy/mako` (1,000), `wrapt` (0,964), `websockets` (0,947), `idna` (0,916), `limits` (0,900)… Sensibilidad 24m: 28 evaluables, 19 >50 %, 0 inconclusos.
- **H2 (12m):** 6 de 18 repos evaluables cambian de categoría entre cuota por commits y por PR fusionados a rama principal (24m: 10 de 25). Contraejemplo útil: `fastapi/fastapi` NO cambia (0.722 vs 0.694, ambas en 50–75 %).
- **H3:** 4 repos califican (psycopg, certifi, httpx, tzlocal): publican el paquete en PyPI dentro de la ventana, mantienen cero GitHub Releases en la misma y muestran actividad observable (commits no-bot, PR fusionados no-bot o pares de revisión no-bot). «Sin GitHub Release» no significa «sin mantenimiento» ni «sin publicación»: H3 existe para rebatir ese atajo y NO convierte la ausencia en prueba de abandono.
- **H4 (12m):** 6 repos con divergencia de roles (cuenta top de commits ≠ cuenta top de integración/revisión): fastapi, pyjwt, click, typing_extensions, sqlalchemy (integrador CaselIT; el rol de revisión está contaminado por `sqla-tester`, automatización no declarada), python-dotenv. Evaluabilidad del rol de revisión por **pares no-bot totales del repo ≥5** (plan.md, Aclaración 1); tras corregirla, wrapt/typing-inspection/watchfiles pasan a evaluables en 24m — en los tres el actor top coincide en commits y revisión, así que los 6 divergentes de cada ventana se mantienen.
- **Participación de bots declarados (12m, con campo congelado `bot`, denominía explícita):** commits **1,495/7,014 = 21.3 %**; PR fusionados **670/3,981 = 16.8 %**; revisiones **crudas** **2,610/10,543 = 24.8 %** (por **pares únicos revisor-PR: 1,638/5,756 = 28.5 %**); releases de GitHub **140/356 = 39.3 %**. Estos porcentajes no se suman entre flujos ni se atribuyen los bots a los cambios del denominador.
- Las cuentas marcadas `type=User` en GitHub no son por definición «personas». Las métricas identifican cuentas y eventos observables, no mantenedores formales; las advertencias sobre `claude`, `sqla-tester` y `invalid-email-address` permanecen en `audits.md`.

Los totales de cobertura del paso 4 (7,014 commits, 3,981 PR, 10,543 revisiones y 356 releases en 12m) se reproducen aquí con cero discrepancias.

## Lo que esto NO permite afirmar

Quiénes son formalmente los mantenedores; horas trabajadas, coordinación privada, pagos y gobernanza; «bus factor» ni riesgo operativo de DeudaMundi; nada sobre el ecosistema Python en general (la cohorte complementaria de otros backends es un módulo aparte con sus propios denominadores). La lectura profunda de los casos elegidos (selección en `plan.md`) sigue pendiente como paso posterior.

## Verificación (resumen)

- `analyze_activity.py`: PASS + 0 mismatch vs `coverage-descriptive.csv` en ambas ventanas.
- Auditoría manual: 24 repos × 2 ventanas, cero discrepancias; dos errores internos detectados y corregidos (ambos en la tooling de auditoría o de proceso, no en los resultados publicados) documentados en `audits.md`.
- Contrast meter H1/H2/H3/H4 recalculados exactamente cuando se corrigió el error del denominador por commits (los bots contaban en el denominador); solo el resultado final ha sido revalidado en su totalidad.
- Figuras: renderizadas y capturadas en Chrome headless (claro y oscuro, formato móvil 390px); sin errores JS.
- Fuentes tipográficas embebidas como subconjuntos; origen y licencias registrados en `figures/FONTS-NOTICE.txt`.
