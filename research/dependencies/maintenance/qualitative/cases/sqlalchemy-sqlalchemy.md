# Expediente cualitativo — `sqlalchemy/sqlalchemy`

**Caso 1 de 6** (selección mecánica: `../analysis/plan.md`, Aclaración 3 —
«directo central» con 2 rutas desde la raíz). **Evidencia congelada:** corte
exclusivo `2026-10-30T00:00:00Z`. **Evidencia documental web:** consultada
2026-11-02 (posterior al corte; SHA de fijación
`57ddc05ffafeec2ea81237dcdf51a0ac02fb589b`). Fuentes completas en §G y en
`../evidence/raw/cases-sqlalchemy-alembic_2026-11-02.md`.

## A. Identificación y relación con DeudaMundi

| Campo | Valor (artefactos congelados) | Fuente |
|---|---|---|
| Distribución instalada | `sqlalchemy` **2.1.6** | `analysis/results/distribution-map.csv`; `pip-inspect.json` |
| Categoría | `runtime:direct` (declarada en `api/pyproject.toml`) | `graph/nodes.csv` |
| Rutas desde la raíz | **2** (`deudamundi-api → sqlalchemy`; `deudamundi-api → alembic → sqlalchemy`); 1 salto en la ruta directa | `graph/paths.txt`, `nodes.csv` |
| Reclamada por | `alembic; deudamundi-api` | `nodes.csv` |
| Repositorio atribuido | `https://github.com/sqlalchemy/sqlalchemy` | `attributions/source-repos.csv` |
| Alcance de la atribución | `verified`: metadatos de la versión congelada y PyPI coinciden y el repositorio resolvía en GitHub el 2026-10-30T14:16:11Z. No demuestra que el wheel instalado se compilara de ese repo ni identifica personas | `attributions/source-repos.csv`, `attributions/README.md` |
| Repositorio compartido | No (a diferencia de `psycopg/psycopg-binary` y `pydantic/pydantic-core`) | `distribution-map.csv` |

SQLAlchemy es el único caso seleccionado que llega por **dos rutas distintas**
(directa y a través de alembic), lo que explica su peso en el grafo sin que
ello implique nada sobre su mantenimiento.

## B. Organización y gobernanza (C2/C3)

- **Propietario público:** organización GitHub `sqlalchemy` (E2). Miembros
  públicos de la organización observados el 2026-11-02: `bourke`, `CaselIT`,
  `gordthompson`, `jvanasco`, `zzzeek` (E2, API de miembros públicos).
- **Cómo se aceptan cambios (E1):** el `CONTRIBUTING.md` del repo fija:
  «We accept pull requests only for issues that a maintainer has marked with
  the `open for pull requests` label. A pull request that doesn't reference
  such an issue is closed automatically, by a bot». La guía oficial de
  desarrollo (`sqlalchemy.org/develop.html`) añade que los PR de código «are
  never merged directly» y que la revisión ocurre en una instancia **Gerrit**
  propia (`.gitreview`: `host=ssh.gerrit.sqlalchemy.org`).
- **Seguridad (E1):** `SECURITY.md` canaliza la seguridad vía la
  infraestructura de Tidelift («SQLAlchemy participates in the Tidelift
  security infrastructure») y pide no abrir CVEs sin contactar antes.
- **Publicación de versiones (E1/E2):** política de versionado y fin de vida
  (`Current / Maintenance / EOL`) en `download.html`; releases **firmadas**
  («signed using Michael Bayer's PGP key id C4DAFEE1»). La release observada
  `rel_2_1_6` (2026-10-21) fue publicada por la cuenta `sqla-tester` (E2); la
  mecánica se describe públicamente en la Discussion #13324: «mike pushes the
  tar.gz to pypi and makes the GitHub release that starts the pipeline».
- **Mantenedores nombrados (E1/E2):** PyPI muestra «2 maintainers … CaselIT
  zzzeek»; la propia cuenta `zzzeek` declara en la Discussion #11553: «myself
  and @CaselIT are the maintainers of every project under the "sqlalchemy"
  organization». Los metadatos PyPI **congelados** del Paso 3 registran
  `ownership.organization = sqlalchemy` con roles Owner: `CaselIT` y `zzzeek`
  (E2 congelado, 2026-10-30).
- **Sucesión y continuidad (clasificación de la auditoría 2026-11-03):**
  **roles y responsabilidades formales documentados** —dos mantenedores
  declarados, revisión y aceptación por Gerrit con reglas escritas
  (categoría 2)—; **procedimiento de relevo o sucesión futura no localizado**
  (categorías 4/5: búsqueda registrada en el árbol del repo). No se localizó
  `GOVERNANCE.md` (E2 de ausencia sobre el árbol; E4 para cualquier sucesión
  no documentada), pero su ausencia **no** equivale a ausencia de gobernanza:
  la gobernanza observable vive en `CONTRIBUTING.md`, la guía de desarrollo y
  la Community Guide. El CODE_OF_CONDUCT menciona «other members of the
  project's leadership» sin nombrar composición (E1).

## C. Roles observables (C1/C4) — contraste con métricas congeladas

Datos de `analysis/results/repo-metrics.csv` y `actor-shares.csv` (12 m;
denominadores del plan; bots fuera de las cuotas):

| Flujo | Total ventana | Denominador humano | Actor top (cuenta) | Cuota |
|---|---|---|---|---|
| Commits sin merges | 484 (673 con merges) | 473 (incl. 4 «no atribuido») | `zzzeek` 300 | **0.6342** (H1 conclusivo > 50 %) |
| PR fusionados a rama principal | 41 (11 bots, 30 humanos) | 30 | `leogallot` 4 | 0.1333 |
| Pares únicos revisor–PR | 256 (4 bots) | 252 | `sqla-tester` 96 | 0.381 — **patrón de automatización no declarada** |
| Releases de GitHub | 23 | 23 | `sqla-tester` 23 | 1.0 |

Lecturas (C4), sin convertir rankings en responsabilidad:

- **Autoría:** `zzzeek` concentra 300 de 473 commits no-fusión no-bot; `CaselIT`
  es segundo (53). 189 commits de fusión en la ventana (integración observada
  aparte, según la regla del plan).
- **Integración:** el top de `merged_by` es `CaselIT` (base del contraste H4):
  H4 **diverge** (cmt=`zzzeek`; int=`CaselIT`; rev=`sqla-tester`).
- **Revisión:** la cuenta top es `sqla-tester`, registrada en
  `../analysis/audits.md` como «la cuenta automatizada que reporta ejecuciones
  de CI de SQLAlchemy», **no declarada bot** en los datos congelados. La cuota
  literal de «quién revisa» **no** debe leerse como personas. Tras `sqla-tester`
  aparecen `CaselIT` (58) y `zzzeek` (51) — revisión humana observable y
  distribuida en tres cuentas.
- **Publicación:** los 23 releases de la ventana están registrados a nombre de
  `sqla-tester` (la cuenta que materializa el pipeline), no de autorías
  humanas: la métrica de «quién publica» identifica un **mecanismo**.
- **Canal de entrada (contexto cualitativo, E3 sobre E1):** solo 41 PR
  fusionados frente a 484 commits sin merges es coherente con el flujo Gerrit
  documentado («never merged directly»): el canal principal de entrada de
  cambios **no es el PR de GitHub**. Esto **matiza H2** para este repo: la
  caída de 0.6342 (commits) a 0.1333 (PR) no describe «autoría de PR repartida»
  sino un repositorio cuya integración real ocurre fuera del flujo de PR que
  la métrica observa (inferencia E3; el hecho E1 es la política documentada).

## D. Incentivos y financiación (C5)

- `FUNDING.yml` (E1): `github: sqlalchemy` / `patreon: zzzeek` /
  `tidelift: "pypi/SQLAlchemy"`. Web oficial: vía PayPal y «Sponsor SQLAlchemy
  through the Tidelift Subscription».
- GitHub Sponsors de la organización activo el 2026-11-02 (E2). Sin botón de
  Sponsors observable para `zzzeek`/`alembic` como cuentas individuales (E2).
- Una fuente de terceros (libraries.io) afirma que los mantenedores «get paid
  by Tidelift» (afirmación de tercero, **no verificada**, E3/E4): se registra
  como tal y **no** se adopta. La página de Tidelift no se recuperó (E4).
- **No** se infieren salarios, dedicación ni presupuestos. La existencia de
  canales de patrocinio declarados (E1) es el hecho; su volumen y destino
  concreto son E4.

## E. Continuidad y límites (C6)

- Cadencia observable congelada: releases cada 4,81 días de media en 12 m
  (`rel_cadence_days`, descriptivo, **no** es «salud»); último release
  in-window 2026-10-21; actividad de commits hasta 2026-10-29 (ventana).
- Releases recientes documentadas: 2.1.6 (2026-10-21), 2.1.5/2.0.55
  (2026-10-16), 2.1.0 GA (2026-09-24) — post-corte observadas el 2026-11-02.
- Debate público 2026 (#13324) sobre modernizar el flujo de publicación
  (Trusted Publishing/attestations): señal de revisión de procesos (E1/E2),
  sin concluir sobre su resultado.
- **Sin procedimiento de relevo o sucesión futura documentado (E4, búsqueda
  registrada).** Lo que sí está documentado (categoría 2) son roles,
  responsabilidades y procesos: revisión/aceptación Gerrit, mantenedores
  declarados y pipeline de releases. La concentración documental
  de la autoridad (una llave PGP nombrada; «sqlalchemy org itself / infra I do
  most of that personally», Discussion #11553) es un hecho E1/E2 de la cuenta;
  **no** se traduce a predicción de continuidad ni a riesgo.

## F. Contraste con el análisis cuantitativo

| Lo que confirma | Lo que matiza | Lo que contradice / debilita |
|---|---|---|
| H1: cuota top-1 de autoría alta y concluyente (0.6342) coincide con el rol documentado de creador y principal mantenedor (E1) y con el segundo lugar de `CaselIT` en commits | H2: el salto commits→PR se explica en parte por el canal Gerrit (E1/E3), no solo por «reparto de PR» | La lectura «un solo mantenedor»: hay **dos** mantenedores declarados (PyPI + Discussion #11553), **cinco** miembros públicos de organización, procesos formales extensos (votos Code-Review/Workflow en Gerrit, etiquetas de triage, CI) y contribuciones externas acreditadas |
| H4: la divergencia de roles es real (autoría `zzzeek`, integración `CaselIT`) y la documentación nombra a ambas cuentas como mantenedoras | La cuota de revisión está contaminada por `sqla-tester` (automatización no declarada): el «top revisor» identifica un bot de CI, no a una persona | Terceros afirman «Bus Factor 1» o «11 active maintainers» (métricas de tercero **incompatibles entre sí**, E3/E4): **no se adoptan**; este estudio no calcula bus factor |
| La publicación por `sqla-tester` explica por qué el rol «release» aparece como automatizado aunque el proceso sea manual aguas arriba (#13324) | 41 PR/484 commits: la métrica de PR observa un canal secundario aquí | — |

**Contraejemplo/limite de validez:** este repo desaconseja titular con
«concentración = abandono latente»: la evidencia documental muestra un proyecto
con dos mantenedores declarados, relevo de tareas visible (integración en
`CaselIT`) y procesos formales, pese a cuotas top-1 elevadas.

## G. Fuentes (selección; tabla completa en el anexo crudo)

| # | URL | Tipo | Consulta | Fragmento | Nivel |
|---|---|---|---|---|---|
| 1 | `raw.githubusercontent.com/sqlalchemy/sqlalchemy/57ddc05…/.github/CONTRIBUTING.md` | CONTRIBUTING (SHA fijado) | 2026-11-02 | «We accept pull requests only for issues that a maintainer has marked with the `open for pull requests` label.» | E1 |
| 2 | `https://www.sqlalchemy.org/develop.html` | Guía de desarrollo | 2026-11-02 | «Pull requests for code changes are never merged directly.» | E1 |
| 3 | `raw…/57ddc05…/.github/SECURITY.md` | SECURITY (SHA fijado) | 2026-11-02 | «SQLAlchemy participates in the Tidelift security infrastructure…» | E1 |
| 4 | `raw…/57ddc05…/.github/FUNDING.yml` | Financiación (SHA fijado) | 2026-11-02 | `github: sqlalchemy / patreon: zzzeek / tidelift: "pypi/SQLAlchemy"` | E1 |
| 5 | `raw…/57ddc05…/.gitreview` | Configuración Gerrit (SHA fijado) | 2026-11-02 | `host=ssh.gerrit.sqlalchemy.org … project=sqlalchemy/sqlalchemy` | E1 |
| 6 | `https://www.sqlalchemy.org/download.html` | Política de releases | 2026-11-02 | «signed using Michael Bayer's PGP key id C4DAFEE1» | E1 |
| 7 | `github.com/sqlalchemy/sqlalchemy/discussions/11553` | Discussion (roles) | 2026-11-02 | «myself and @CaselIT are the maintainers of every project under the "sqlalchemy" organization» | E2 |
| 8 | `github.com/sqlalchemy/sqlalchemy/discussions/13324` | Discussion (releases) | 2026-11-02 | «mike pushes the tar.gz to pypi and makes the GitHub release that starts the pipeline» | E2 |
| 9 | `api.github.com/orgs/sqlalchemy/public_members` | API organización | 2026-11-02 | miembros: `bourke, CaselIT, gordthompson, jvanasco, zzzeek` | E2 |
| 10 | `api.github.com/repos/sqlalchemy/sqlalchemy/releases` | API releases | 2026-11-02 | `rel_2_1_6` publicada 2026-10-21 por `sqla-tester` | E2 |
| 11 | `attributions/pypi-evidence/sqlalchemy/2.1.6.json` | Metadatos PyPI congelados | 2026-10-30 (congelado) | `ownership: organization sqlalchemy; Owner CaselIT, Owner zzzeek` | E2 |
| 12 | `analysis/results/repo-metrics.csv`, `actor-shares.csv` | Métricas congeladas | corte 2026-10-30 | cuotas y denominadores de §C | E2 |
| 13 | `libraries.io/pypi/SQLAlchemy` | Tercero (no verificado) | 2026-11-02 | «The maintainers of this project get paid by Tidelift…» | E3/E4 (no adoptada) |
