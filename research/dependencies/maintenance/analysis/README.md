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
| `make_figures.py` + `figures/` | Cinco figuras interactivas autocontenidas (Plotly 2.35.2 desde CDN con `no-integrity` documentado), identidad Econopapi con el manual oficial (`/home/econopapi/Projects/econopapi-video-studio/docs/brand/ECONOPAPI_BRAND_KIT_LIGHT_DARK_v04/`), fuente Montserrat/Source Sans Pro embebidas, claro/oscuro por `prefers-color-scheme` y toggle manual, tabla accesible por figura y texto alternativo; los datos exactos de cada gráfico viajan en `figN-data.json`. Subconjuntos de fuentes con pyftsubset 4.68.0 y licencias SIL OFL 1.1 (`FONTS-NOTICE.txt`). |
| `wp-snippets/` | Fragmentos HTML autocontenidos (descartados como vía principal tras la revisión editorial: no respetan la higiene de bloques). La vía definitiva es el plugin de bloque dinámico: `wp-block-plugin/econopapi-plotly/` con el bloque nativo `econopapi/plotly-figure` (el post guarda solo `{"figure":"figN"}`; el servidor imprime kicker/título/subtítulo/tabla accesible; contenedores con ID única; Plotly/fonts/datos encolados una vez). `README.txt` documenta el método verificado y la evaluación del antiguo plugin wp-plotly. Integración pendiente de la instalación del plugin y aprobación editorial. |
| `SHA256SUMS` / `verification.txt` | Manifest del directorio y bitácora de verificación. |

## Reproducción (una sola persona, sin red)

```sh
cd research/dependencies/maintenance
sha256sum -c SHA256SUMS                          # resultados y fragmentos del análisis
../graph  # jump — not needed here
```

Desde la raíz del repositorio:

```sh
python research/dependencies/maintenance/verify_activity.py       # puerta del paso 4
sha256sum -c research/dependencies/maintenance/SHA256SUMS         # calle de datos
python research/dependencies/maintenance/analysis/analyze_activity.py
python research/dependencies/maintenance/analysis/make_figures.py
```

El script de análisis imprime PASS solo si su recomputo coincide con `coverage-descriptive.csv` (que a su vez lo produce el verificador del paso 4). No invoca a GitHub.

## Resultados en una línea (todo está en `audits.md` y `results/`)

- **H1 (12m):** 14 de 22 repos evaluables tienen cuota top-1 de commits no-fusión no-bot superior al 50 % — `sqlalchemy/mako` (1,000), `wrapt` (0,964), `websockets` (0,947), `idna` (0,916), `limits` (0,900)…
- **H2 (12m):** 6 de 18 repos evaluables cambian de categoría entre cuota por commits y por PR fusionados a rama principal (24m: 10 de 25).
- **H3:** 4 repos califican (psycopg, certifi, httpx, tzlocal): PyPI publica, GitHub Releases no, con actividad humana observable.
- **H4 (12m):** 6 repos con divergencia de roles en commits frente a integración/revisión; la cuenta `sqla-tester` contamina la lectura de revisión en sqlalchemy (automatización no declarada como bot).
- **Participación de bots declarados (12m):** 24,6 % commits, 21,7 % PR, 28,6 % revisiones, 55,7 % releases — y Cuadro: en certifi/controllers automático; en fastapi el actor top con bots incluidos es `github-actions[bot]`.

Los totales de cobertura del paso 4 (7,014 commits, 3,981 PR, 10,543 revisiones y 356 releases en 12m) se reproducen aquí con cero discrepancias.

## Lo que esto NO permite afirmar

Quiénes son formalmente los mantenedores; horas trabajadas, coordinación privada, pagos y gobernanza; «bus factor» ni riesgo operativo de DeudaMundi; nada sobre el ecosistema Python en general (la cohorte complementaria de otros backends es un módulo aparte con sus propios denominadores). La lectura profunda de los casos elegidos (selección en `plan.md`) sigue pendiente como paso posterior.

## Verificación (resumen)

- `analyze_activity.py`: PASS + 0 mismatch vs `coverage-descriptive.csv` en ambas ventanas.
- Auditoría manual: 24 repos × 2 ventanas, cero discrepancias; dos errores internos detectados y corregidos (ambos en la tooling de auditoría o de proceso, no en los resultados publicados) documentados en `audits.md`.
- Contrast meter H1/H2/H3/H4 recalculados exactamente cuando se corrigió el error del denominador por commits (los bots contaban en el denominador); solo el resultado final ha sido revalidado en su totalidad.
- Figuras: renderizadas y capturadas en Chrome headless (claro y oscuro, formato móvil 390px); sin errores JS.
- Fuentes tipográficas embebidas como subconjuntos; origen y licencias registrados en `figures/FONTS-NOTICE.txt`.
