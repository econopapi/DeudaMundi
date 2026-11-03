# Expediente cualitativo — `python/typing_extensions`

**Caso 3 de 6** (selección mecánica: «transitivo con más rutas»: **17 rutas**
desde la raíz — la mayor exposición del grafo congelado). **Evidencia
congelada:** corte `2026-10-30T00:00:00Z`. **Evidencia web:** 2026-11-02 (SHA
de fijación `cfde842014f0e05e2a09bf58fd9e2e4a20a9fdff`).

## A. Identificación y relación con DeudaMundi

| Campo | Valor (congelado) | Fuente |
|---|---|---|
| Distribución instalada | `typing-extensions` **4.16.0** | `distribution-map.csv` |
| Categoría | `runtime:transitive`; 2 saltos | `graph/nodes.csv` |
| Rutas desde la raíz | **17** (mayor `paths_from_root` del grafo) | `graph/paths.txt` |
| Reclamada por | `alembic; deudamundi-api; fastapi; httpx; psycopg; pydantic-settings; slowapi; sqlalchemy; uvicorn` (9 progenitores) | `nodes.csv` |
| Requerida por | `alembic; anyio; fastapi; limits; psycopg; pydantic; pydantic-core; pydantic-settings; sqlalchemy; typing-inspection` (10 requirientes) | `nodes.csv` |
| Repositorio atribuido | `https://github.com/python/typing_extensions` | `source-repos.csv` (verificado 2026-10-30T14:16:11Z) |

Es la dependencia **más transversal** del caso: no está declarada por
DeudaMundi pero se cuela por casi todas las ramas. Una sola distribución
instalada, un solo repositorio.

## B. Organización y gobernanza (C2/C3)

- **Propietario público:** organización GitHub `python` («Repositories related
  to the Python Programming language», E1/E2). Licencia `PSF-2.0` (E1).
- **Marco institucional de contribución (E1):** `CONTRIBUTING.md` exige
  «contributors need to sign the PSF Contributor Agreement». La documentación
  fija el criterio de admisión de funcionalidad: «New features may be added to
  `typing_extensions` as soon as they are specified in a PEP that has been
  added to the `python/peps` repository» y «Bugfixes and new typing features
  that don't require a PEP may be added … once they are merged into CPython's
  main branch» (E1, `doc/index.rst`). Canal de Q&A: discusiones de
  `python/typing` (E1).
- **Verificación negativa registrada:** el **PEP 576 NO trata de
  typing_extensions** (es «Rationalize Built-in function classes», estado
  *Withdrawn*; E1, verificación explícita). Cualquier vínculo entre ambos sería
  E4 refutado.
- **Publicación de versiones (E1):** proceso documentado («Workflow for PyPI
  releases»): release de GitHub con tag = versión, «Release automation will
  finish the release. You'll have to manually approve the last step before
  upload»; política de versionado con release candidates y «at least a week of
  testing»; publicación con **Trusted Publishing**
  (`publish.yml`: `id-token: write`).
- **Mantenedores nombrados:** los metadatos PyPI **congelados** registran
  Owners: `JelleZijlstra`, `guido`, `jukkal`; Maintainers: `hauntsaninja`,
  `ilevkivskyi`, `srittau` (E2 congelado, 2026-10-30) — seis cuentas con roles
  de publicación sobre el paquete. El campo `[[project.authors]]` del
  `pyproject.toml` nombra cuatro autores históricos (E1). El CHANGELOG atribuye
  cambios a docenas de firmas («Patch by …», E1).
- **Seguridad (E1):** `SECURITY.md` en voz institucional («we take security
  seriously»; «Only the latest release is supported»; «We commit to respond to
  any issue within 14 days»).
- **Sucesión y continuidad (clasificación de la auditoría 2026-11-03):**
  **roles y responsabilidades formales documentados** —seis cuentas con roles
  Owner/Maintainer en los metadatos PyPI congelados, proceso de release con
  aprobación manual, acuerdo de contribución PSF (categoría 2)—;
  **procedimiento de relevo o sucesión futura no localizado** (categorías 4/5:
  sin `GOVERNANCE.md` ni `CODEOWNERS`, E2 de ausencia; E4 como procedimiento).
  La **migración documentada de repositorio** —el README de `python/typing`
  declara que el paquete «now lives in the typing_extensions repo. It used to
  be in the `typing_extensions` directory» (E1)— es un cambio de repositorio
  **dentro de la misma organización**, no una transferencia de administración
  ni un procedimiento de sucesión; registra continuidad institucional.

## C. Roles observables (C1/C4)

Métricas congeladas (12 m):

| Flujo | Total ventana | Denominador humano | Actor top (cuenta) | Cuota |
|---|---|---|---|---|
| Commits sin merges | 55 (sin merges) | 46 | `AlexWaygood` 21 | 0.4565 (**≤ 50 %**: H1 no supera umbral) |
| PR fusionados a rama principal | 55 (9 bots, 46 humanos) | 46 | `AlexWaygood` 21 | 0.4565 |
| Pares únicos revisor–PR | 76 (1 bot) | 75 | `JelleZijlstra` 28 | 0.3733 |
| Releases de GitHub | 3 | 3 | `AlexWaygood` 3 | 1.0 |

- **H4 diverge en 12 m** (cmt/int = `AlexWaygood`; rev = `JelleZijlstra`) y
  **coincide en 24 m** (los tres roles `JelleZijlstra`): el caso documenta que
  el «actor principal» **depende de la ventana** (así se declaró ya en
  `../analysis/audits.md`).
- **Mecánica squash-mirror (verificación fechada del dictamen §4):** en 12 m y
  24 m el conteo de commits sin merges **iguala exactamente** al de PR
  fusionados a rama principal y el 100 % se materializa vía `web-flow`: los
  dos flujos **no son medidas independientes** de este trabajo.
- **Revisión distribuida:** `JelleZijlstra` 28, `srittau` 22, `AlexWaygood` 16
  pares humanos — tres cuentas con revisión intensiva; ninguno supera el 40 %.
- **Publicación:** 3 releases humanos en 12 m (toda la publicación observable
  de la ventana a una cuenta); en 24 m, 12 releases con tops repartidos
  (`JelleZijlstra` 8, etc.).

## D. Incentivos y financiación (C5)

- **Sin `FUNDING.yml`** en el repositorio (E2 de ausencia verificada sobre el
  árbol al SHA fijado).
- La página de GitHub Sponsors de la organización `python` (E1) destaca
  proyectos (CPython, mypy, pythondotorg, asyncio, pymanager, psf-salt) y
  **no incluye `typing_extensions`** (E2). *E3 — interpretación:* no hay
  declaración pública de financiación **del proyecto**; la vinculación de
  fondos de la PSF con este repositorio es inferencia no documentada y no debe
  presentarse como hecho.
- Sin declaraciones de empleadores atribuidas al proyecto (E2/E4). El nombre
  «Python Software Foundation» aparece como contexto institucional (licencia,
  acuerdo de contribución), **no** como financiación declarada del paquete.

## E. Continuidad y límites (C6)

- Releases documentadas: 4.15.0 (2025-08-25) → 4.16.0rc1/rc2 (junio 2026) →
  **4.16.0 (2026-07-02)**, última publicada; `pyproject.toml` con
  `version = "4.16.1.dev0"` al SHA fijado (E1/E2): ciclo en curso tras la
  última release — concordante con la ventana congelada (último evento de
  commits 2026-10-23; `rel_cadence_days` 6,71).
- Publicación endurecida (Trusted Publishers desde 4.12.0rc1) con aprobación
  manual del último paso: procedimiento de continuidad **documentado** (E1).
- Múltiples cuentas publican releases (`AlexWaygood` y `JelleZijlstra`, E1/E2):
  la función de publicación no depende de una única cuenta en lo observable.
- Sin mecanismo de relevo o sucesión futura escrito localizado (E4, búsqueda
  registrada); sí proceso de publicación documentado y roles de paquete
  repartidos entre seis cuentas (categoría 2).

## F. Contraste con el análisis cuantitativo

| Confirma | Matiza | Debilita |
|---|---|---|
| H1 **no** supera el umbral (0.4565 en 12 m; 0.2252 en 24 m): la documentación describe un proyecto con roles repartidos entre ~6 cuentas con permisos de paquete — coherente con baja concentración de autoría | La igualdad exacta commits/PR es artefacto de materialización squash (dictamen §4): **no** es «confirmación doble» de la cuota | Cualquier lectura de «un solo mantenedor» para este caso: está refutada tanto por métricas como por documentación (E1/E2) |
| H4 12 m: la divergencia de roles es coherente con la documentación (varias cuentas con roles de Owner/Maintainer en PyPI) | La sensibilidad 24 m cambia las identidades top: las narrativas sobre «quién mantiene» dependen de la ventana | — |
| — | — | La hipótesis de guion «typing_extensions ↔ PEP 576»: **refutada por verificación directa (E1)** |

**Contraejemplo/limite de validez:** sirve como contraejemplo interno de los
titulares de concentración: el repositorio más dependido del caso (17 rutas)
es el menos concentrado en autoría. La exposición en el grafo y la
concentración de mantenimiento son **dimensiones distintas**.

## G. Fuentes (selección)

| # | URL | Tipo | Consulta | Fragmento | Nivel |
|---|---|---|---|---|---|
| 1 | `raw.githubusercontent.com/python/typing_extensions/cfde842…/CONTRIBUTING.md` | CONTRIBUTING (SHA fijado) | 2026-11-02 | «contributors need to sign the PSF Contributor Agreement» / «Release automation will finish the release. You'll have to manually approve the last step before upload.» | E1 |
| 2 | `raw…/cfde842…/doc/index.rst` | Docs oficiales (SHA fijado) | 2026-11-02 | «New features may be added … as soon as they are specified in a PEP that has been added to the `python/peps` repository.» | E1 |
| 3 | `raw…/cfde842…/pyproject.toml` | Metadatos (SHA fijado) | 2026-11-02 | `[[project.authors]] name = "Guido van Rossum, Jukka Lehtosalo, Łukasz Langa, Michael Lee"`; `license = "PSF-2.0"` | E1 |
| 4 | `raw…/cfde842…/SECURITY.md` | SECURITY (SHA fijado) | 2026-11-02 | «We commit to respond to any issue within 14 days» | E1 |
| 5 | `raw…/cfde842…/.github/workflows/publish.yml` | Workflow de release | 2026-11-02 | `id-token: write # IMPORTANT: mandatory for trusted publishing` | E1/E2 |
| 6 | `api.github.com/repos/python/typing_extensions/releases?per_page=5` | API releases | 2026-11-02 | 4.16.0 `author.login: AlexWaygood`; 4.15.0 `author.login: JelleZijlstra` | E1/E2 |
| 7 | `attributions/pypi-evidence/typing-extensions/4.16.0.json` | Metadatos PyPI congelados | 2026-10-30 (congelado) | Owners `JelleZijlstra`, `guido`, `jukkal`; Maintainers `hauntsaninja`, `ilevkivskyi`, `srittau` | E2 |
| 8 | `raw.githubusercontent.com/python/typing/main/README.md` | README de `python/typing` | 2026-11-02 | «The `typing_extensions` package, which now lives in the typing_extensions repo.» | E1 |
| 9 | `https://peps.python.org/pep-0576/` | PEP (verificación) | 2026-11-02 | «PEP 576 – Rationalize Built-in function classes … Status: Withdrawn» | E1 (hallazgo negativo) |
| 10 | `https://github.com/sponsors/python` | Patrocinio org | 2026-11-02 | «Featured work» sin `typing_extensions` | E1 (página)/E2 (ausencia) |
| 11 | `analysis/results/repo-metrics.csv`, `actor-shares.csv`, `final-audits/traceability-h1h4.csv` | Métricas congeladas | corte 2026-10-30 | cuotas, H1 ≤ 50 %, H4 divergente 12 m / coincidente 24 m | E2 |
