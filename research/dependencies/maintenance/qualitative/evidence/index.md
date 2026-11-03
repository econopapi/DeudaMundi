# Índice de fuentes y procedencia (Paso 6)

**Regla de procedencia:** cada fuente de este índice indica su tipo, su fecha
de consulta y su nivel de evidencia (E1–E4, definidos en `../protocol.md`).
Todas las fuentes **web** se consultaron el **2 de noviembre de 2026** salvo
indicación: son **posteriores al corte exclusivo `2026-10-30T00:00:00Z`** y no
se presentan como representativas del estado histórico del corte. Los
artefactos congelados del estudio se citan con su fecha de congelación.

## 1. Fuentes internas (artefactos congelados; solo lectura)

| Conjunto | Ruta | Fecha del hecho | Uso en este paso |
|---|---|---|---|
| Inventario de entorno | `../../pip-inspect.json`, `installed-packages.txt`, `manifest.json` | 2026-10-30 (snapshot) | §A de los expedientes |
| Grafo de dependencias | `../../graph/nodes.csv`, `paths.txt` | Paso 2 | §A (rutas, exposición) |
| Atribuciones | `../../attributions/source-repos.csv`, `github-evidence/`, `ambiguous.md` | 2026-10-30T14:16:11Z | §A (incluye redirección starlette) |
| Metadatos PyPI congelados | `../../attributions/pypi-evidence/<dist>/<ver>.json` | 2026-10-30T14:16:11Z | §B/§D (ownership, funding, autores) |
| Actividad de mantenimiento | `../data/` (443 JSON) | 2026-10-30T15:50–16:15Z | §C vía resultados derivados |
| Resultados del Paso 5 | `../analysis/results/` (`repo-metrics.csv`, `actor-shares.csv`, `hypotheses.json`, `h3-test.csv`, `continuity.csv`, `overview-totals.json`) | corte 2026-10-30 | §C y triangulación |
| Auditorías | `../analysis/audits.md`, `../analysis/final-audits/` (`traceability-h1h4.csv`, `manual-sample-audits.json`, `dictamen.md`) | 2026-10-30 / 01-11-2026 | patrones de automatización, valores de referencia |
| Figuras v2 | `../analysis/results/plotly-embed/fig{1..5}.json` + `index.json` | 2026-11-01 (generación) | especificación editorial |

## 2. Anexos crudos de recogida web (este paso)

| Archivo | Contenido | Agente/fecha |
|---|---|---|
| `raw/cases-sqlalchemy-alembic_2026-11-02.md` | 36 fuentes de `sqlalchemy/sqlalchemy` y `sqlalchemy/alembic` (SHAs fijados `57ddc05…` / `1bcba93e…`) | recogida web 2026-11-02 |
| `raw/cases-typing-extensions-idna_2026-11-02.md` | 27 fuentes de `python/typing_extensions` y `kjd/idna` (SHAs `cfde842…` / `d357725…`), incluye la verificación negativa del PEP 576 | recogida web 2026-11-02 |

Las fuentes de `psycopg/psycopg` y `kludex/starlette` están integradas en §G
de sus expedientes (`../cases/psycopg-psycopg.md`, `../cases/kludex-starlette.md`)
con URL exacta, tipo, fecha, fragmento y nivel E. Las fuentes bibliográficas
están en `../literature.md` §referencias.

## 3. Resumen de fuentes por nivel de evidencia

| Nivel | Volumen aproximado | Ejemplos representativos |
|---|---|---|
| E1 (documental directa) | ~70 fragmentos | CONTRIBUTING/SECURITY/FUNDING/docs de release de los seis proyectos; anuncio de transferencia de starlette; roles nombrados de psycopg; declaración «team of volunteers» de idna |
| E2 (observación técnica) | ~50 registros | APIs de GitHub (releases, miembros, contenidos, redirects); metadatos PyPI congelados; métricas congeladas |
| E3 (inferencia contextual) | ~15, siempre rotuladas | lectura del canal Gerrit como explicación de H2 en sqlalchemy; vinculación de fondos PSF↔typing_extensions (rechazada como hecho); métricas de terceros (no adoptadas) |
| E4 (desconocido) | ~10, con búsqueda registrada | Procedimiento de relevo/sucesión **futura** no localizado en 6 de 6 casos (una transferencia administrativa **histórica** documentada en starlette; ver C49); `GOVERNANCE.md` no localizado en 6 de 6 (sin que ello implique ausencia de gobernanza); financiación específica no declarada de idna; página Tidelift (no recuperada); protocolo Notion (requiere autenticación) |

## 4. Fuentes externas de terceros (no adoptadas como evidencia del caso)

Se registran para transparencia y **no** sostienen ninguna afirmación del
artículo: GitStats («Bus Factor 1»), inspect.software («top contributor 84%»),
LF Insights («11 active maintainers» — contradice al resto), libraries.io
(«get paid by Tidelift»), Simon Willison (corrobora redirección), deps.dev,
Hacker News. Todas quedan como E3/E4: métricas ajenas con metodologías no
auditadas por este estudio.

## 5. Lectura del artículo 2735 (fuente editorial)

- **Mecanismo:** API REST de WordPress
  `https://econopapi.com/wp-json/wp/v2/posts/2735` **con contraseña del post
  facilitada por el autor** el 2026-11-02 (lectura; **ninguna escritura**).
- **Estado registrado:** `status: publish`, `protected: true`,
  `modified: 2026-11-01T06:40:31`, 22 revisiones en el historial, contenido
  renderizado 43.458 caracteres HTML (74 bloques: notas, párrafos, 5 avisos de
  figura pendientes, 2 figuras fijas existentes).
- **Procedencia:** copia de trabajo extraída a esquema numerado (§ bloques) en
  `../editorial-handoff.md`; el contenido crudo **no** se versiona en este
  repositorio para no duplicar el post protegido.
- **Segunda lectura (2026-11-03, auditoría correctiva):** el texto íntegro se
  recuperó de nuevo vía la misma API, con la contraseña del post facilitada por
  el autor, **solo lectura**, para ejecutar la matriz de cobertura
  (`../coverage-matrix.csv`, Fase 6/Opción A). El carácter renderizado (43.458
  caracteres) coincide con el registro del 02-11-2026: mismo estado del post.
  El contenido sigue sin versionarse aquí.

## 6. Búsquedas fallidas registradas (E4 reproducible)

| Búsqueda | Resultado |
|---|---|
| `GOVERNANCE.md` / procedimiento de relevo o sucesión futura en sqlalchemy, alembic, typing_extensions, idna, starlette, psycopg | No localizados (listados de API de contenidos). **No** equivale a ausencia de gobernanza: roles, procesos y una transferencia histórica sí están documentados (C49) |
| `CONTRIBUTING.md` en idna y psycopg | No existen en la raíz |
| `.github/FUNDING.yml` en typing_extensions e idna | HTTP 404 (ausencia corroborada) |
| Programa GitHub Sponsors activo de `kjd` | Sin tiers recuperables |
| Página Tidelift `pypi-sqlalchemy` | No recuperada (contenido de marca «Sonar») |
| Protocolo de Notion (`app.notion.com/p/409…`) | Requiere autenticación; sin contenido recuperable |
