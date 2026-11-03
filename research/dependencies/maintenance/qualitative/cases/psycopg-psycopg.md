# Expediente cualitativo — `psycopg/psycopg`

**Caso 5 de 6** (selección mecánica: «función distinta — capa de datos»).
**Evidencia congelada:** corte `2026-10-30T00:00:00Z`. **Evidencia web:**
2026-11-02/03 (SHA de fijación `4daf632fae52ad7493c76fdea11d3a65856df114`).

## A. Identificación y relación con DeudaMundi

| Campo | Valor (congelado) | Fuente |
|---|---|---|
| Distribuciones instaladas | `psycopg` **3.3.6** (directa, extra `binary`) y `psycopg-binary` **3.3.6** (transitiva) | `distribution-map.csv` |
| Categoría | 1 directa + 1 transitiva; 1 salto cada una | `graph/nodes.csv` |
| Rutas desde la raíz | 1 por distribución; `psycopg → psycopg-binary` (extra `binary`) | `graph/paths.txt` |
| Repositorio atribuido | **compartido**: `https://github.com/psycopg/psycopg` para las dos distribuciones (`shared_repository = yes`) | `source-repos.csv` |
| Unidad de conteo | El repositorio se contó **una sola vez** en los 35 (regla del Paso 4) | `maintenance/protocol.md` |

**Alcance real de la atribución:** la actividad observable de este repositorio
puede incluir trabajo de otros paquetes del monorepo (`psycopg_pool`, que el
README declara con «a different release cycle»), no solo de las dos
distribuciones instaladas — límite ya declarado para repos compartidos.

## B. Organización y gobernanza (C2/C3)

- **Propietario público:** organización `psycopg` (API: `owner.type:
  Organization`; E2). Identidad colectiva declarada: «© The Psycopg Team» y
  «We at the Psycopg team are able to maintain this thanks to the generosity
  of the companies and individuals listed below» (E1, web oficial).
- **Roles nombrados (E1, web oficial `#maintainers`):** Daniele Varrazzo —
  «Technical Lead» («creator and primary maintainer of Psycopg 2 and Psycopg
  3»); Hannah Maher — «Operations Lead» («project coordination, release
  support, issue triage, documentation oversight, and contributor
  communication»). Es el caso de los seis con **roles operativos nombrados y
  diferenciados** en documentación oficial.
- **Aceptación de cambios (E1):** `README.rst` («Hacking»): «Please follow the
  conventional commits specification»; hooks `pre-commit` obligatorios;
  estructura modular (`psycopg_pool` como paquete separado con ciclo propio).
- **Publicación de versiones (E1):** `docs/release.rst` («How to make a
  psycopg release»): `tools/bump_version.py`, CI, workflows de empaquetado
  (`packages-src/bin/pool.yml`), `git push --tags`, subida a PyPI con twine.
  **GitHub Releases no se usa** (API `/releases` vacía, E2): el versionado se
  documenta con tags + PyPI. Sin GOVERNANCE/SECURITY/CONTRIBUTING en raíz ni
  `.github/` (E2 de ausencia; E4 para procedimiento de sucesión).
- **Propiedad del paquete:** los metadatos PyPI **congelados** registran
  `ownership` con un único rol Owner: `piro` (E2 congelado, 2026-10-30) para
  `psycopg` y `psycopg-binary`, mientras que el campo `author_email` nombra a
  Daniele Varrazzo. **No se identifican cuentas entre sí**: se registra que la
  propiedad registrada del paquete y las autorías declaradas son campos
  distintos con valores distintos.
- **Sucesión y continuidad (clasificación de la auditoría 2026-11-03):**
  **roles y responsabilidades formales documentados** (Technical Lead y
  Operations Lead con funciones escritas; proceso de release documentado) —
  categoría 2 —; **relevo o sucesión futura no localizado** (categorías 4/5).
  Sin `GOVERNANCE`/`SECURITY`/`CONTRIBUTING` en raíz ni `.github/` (E2 de
  ausencia; E4 para procedimiento de sucesión), lo que **no** contradice la
  gobernanza observable en la web oficial y en `docs/release.rst`.

## C. Roles observables (C1/C4)

Métricas congeladas (12 m):

| Flujo | Total ventana | Denominador humano | Actor top (cuenta) | Cuota |
|---|---|---|---|---|
| Commits sin merges | 241 (289 con merges) | 231 (incl. 1 «no atribuido») | `dvarrazzo` 152 | **0.658** (H1 conclusivo > 50 %) |
| PR fusionados a rama principal | 91 (10 bots, 81 humanos) | 81 | `dvarrazzo` 34 | 0.4198 |
| Pares únicos revisor–PR | 73 (**0 bots**) | 73 | `dvarrazzo` 36 | 0.4932 |
| Releases de GitHub | **0** | — | — | (H3) |

- **H2 cambia de categoría** (0.658 → 0.4198): la autoría se concentra más que
  la integración; el PR más autorizado de la ventana es de `DylanYoung` (31
  commits, 7 PR, 11 pares de revisión) — una segunda cuenta activa en los tres
  flujos humanos (E2).
- **H4 coincide** (cmt = int = rev = `dvarrazzo`), pero la cuota de revisión
  (0.49) está **justo en el límite**: 36 de 73 pares; el resto se reparte entre
  23 cuentas revisoras humanas — revisión plural observable.
- **H3 — caso más claro:** 0 releases de GitHub + publicación en PyPI de
  `psycopg` y `psycopg-binary` dentro de la ventana (evidencia congelada
  `analysis/pypi-evidence/`: subidas 2026-09-18) + actividad observable (230
  commits no-fusión no-bot, 81 PR, 73 pares). La documentación **explica** el
  dato: el proceso de release usa tags + PyPI y no crea objetos GitHub Release
  (E1/E2) — la «ausencia» es un rasgo del proceso, no un vacío de mantenimiento.
- **Automatización:** 10 commits bot y 10 PR bot en 12 m (bots declarados);
  ninguna revisión bot: la revisión es 100 % humana en los pares de la ventana.

## D. Incentivos y financiación (C5)

- **Patrocinio declarado por la cuenta:** `github.com/sponsors/dvarrazzo`
  (enlazada en los metadatos PyPI como `Funding`, E1/E2 congelado y actual):
  «Your sponsorship goes directly towards the development and tie [sic]
  maintenance of Psycopg 3 and Psycopg 2»; la página declara además actividad
  de consultoría propia («I am currently working as a consultant with my
  personal company, Codice Lieve, and my paying customers make the activity
  viable»). `FUNDING.yml`: `github: dvarrazzo` + `custom: paypal.me/dvarrazzo`.
- **Patrocinio a nivel de proyecto/organización (E1):** `github.com/sponsors/psycopg`
  activo; página `psycopg.org/sponsors/` con tiers declarados (Platinum: AWS;
  Gold: Command Prompt; Silver: Postgres Pro; Bronze: G-Research Open Source,
  Materialize, Sentry, YouGov, Dalibo, y otras entidades) y «Backers»
  individuales; registro versionado `BACKERS.yaml` en el repo.
- **No** se infieren importes por entidad, salarios, dedicación ni
  presupuestos: los tiers son declaraciones públicas del proyecto.

## E. Continuidad y límites (C6)

- Cadencia congelada: **0 releases de GitHub en 24 m** (toda la ventana de
  sensibilidad), pero PyPI registra subidas periódicas (3.3.0 2025-12-01 →
  3.3.6 2026-09-18). Actividad continua: 13 meses con commits en 12 m; último
  evento in-window 2026-10-29.
- **Post-corte (contexto, no ventana):** release `3.3.7` subida a PyPI el
  2026-11-03T03:51Z y commit «bump psycopg package version to 3.3.7»
  (2026-11-03) — observados durante esta consulta; **no** se mezclan con los
  eventos congelados.
- Estructura con dos cargos nombrados (Technical/Operations Lead) y un
  «Psycopg Team» autodeclarado: señal documental de distribución de tareas
  operativas (triage, coordinación, docs) **que los commits no capturan** (C8).
- Sin procedimiento de relevo o sucesión futura escrito localizable (E4,
  búsqueda registrada); sí roles nombrados y proceso de release documentados
  (categoría 2).

## F. Contraste con el análisis cuantitativo

| Confirma | Matiza | Debilita |
|---|---|---|
| H3: la documentación confirma que el proyecto publica en PyPI sin objetos GitHub Release por diseño (E1/E2): la «ausencia» medida es un hecho de proceso | H2 (cambio de categoría 0.658→0.4198) coincide con una base de contribución plural (35 cuentas con PR humanos, 23 revisoras) y con roles nombrados de coordinación que no aparecen en los commits | La lectura unipersonal: la web declara dos cargos y un equipo; `DylanYoung` concentra actividad en los tres flujos humanos (E2) |
| H1 0.658 coincide con la autodescripción «creator and primary maintainer» (E1) del Technical Lead | La propiedad registrada del paquete (`piro`, E2 congelado) **no** coincide con la cuenta top de eventos (`dvarrazzo`): «quién puede publicar» y «quién escribe» son campos distintos | La lectura de que 0 releases = poco mantenimiento: queda refutada en su caso más claro |
| — | — | El «riesgo por dependencia de una persona»: **no evaluable**; la financiación declarada (patrocinio personal + corporativo) existe, pero nada de ello permite estimar dedicación ni continuidad futura |

**Contraejemplo/limite de validez:** psycopg muestra que los distintos planos
pueden tener **respuestas distintas** a «quién mantiene»: los tres planos que
contrasta H4 (autoría: `dvarrazzo`; integración: más repartida; revisión:
plural y sin bots — aquí H4 coincide) y, **separado de H4**, el plano de
publicación (PyPI/tags, sin GitHub Releases; H4 no incorpora la publicación).
La documentación añade aún otro plano (operaciones/coordinación) que ningún
flujo observa.

## G. Fuentes (selección)

| # | URL | Tipo | Consulta | Fragmento | Nivel |
|---|---|---|---|---|---|
| 1 | `https://www.psycopg.org/` (`#maintainers`) | Web oficial (roles) | 2026-11-02 | «Daniele Varrazzo — Technical Lead — …creator and primary maintainer of Psycopg 2 and Psycopg 3»; «Hannah Maher — Operations Lead»; «© The Psycopg Team» | E1 |
| 2 | `raw.githubusercontent.com/psycopg/psycopg/master/docs/release.rst` | Proceso de release (SHA fijado) | 2026-11-02 | «If the package is stable, omit `-r testpypi`: `$ twine upload *`» | E1 |
| 3 | `raw…/4daf632…/README.rst` | README (SHA fijado) | 2026-11-02 | «Please follow the conventional commits specification for your commit messages.» | E1 |
| 4 | `raw…/4daf632…/.github/FUNDING.yml` | Financiación (SHA fijado) | 2026-11-02 | `github: dvarrazzo` · `custom: "https://www.paypal.me/dvarrazzo"` | E1 |
| 5 | `raw…/4daf632…/BACKERS.yaml` | Registro de mecenas (SHA fijado) | 2026-11-02 | «You can find our sponsors at https://www.psycopg.org/sponsors/» | E1 |
| 6 | `https://www.psycopg.org/sponsors/` | Patrocinio del proyecto | 2026-11-02 | «We at the Psycopg team are able to maintain this thanks to the generosity of…»; Platinum: AWS | E1 |
| 7 | `https://github.com/sponsors/dvarrazzo` | Patrocinio de cuenta | 2026-11-02 | «Your sponsorship goes directly towards the development and tie maintenance of Psycopg 3 and Psycopg 2» | E1 |
| 8 | `api.github.com/repos/psycopg/psycopg/releases?per_page=5` | API releases | 2026-11-02 | lista vacía: sin GitHub Releases | E2 |
| 9 | `api.github.com/repos/psycopg/psycopg/contents/` | API contenidos | 2026-11-02 | Sin GOVERNANCE/SECURITY/CONTRIBUTING; sí `BACKERS.yaml`, `docs/release.rst` | E2 (ausencia) |
| 10 | `attributions/pypi-evidence/psycopg/3.3.6.json` (+`psycopg-binary`) | Metadatos PyPI congelados | 2026-10-30 (congelado) | `ownership: Owner piro`; `Funding: sponsors/dvarrazzo`; subidas 2026-09-18 | E2 |
| 11 | `analysis/results/h3-test.csv`, `repo-metrics.csv`, `actor-shares.csv` | Métricas congeladas | corte 2026-10-30 | H3 califica; H1 0.658; H2 cambia; H4 coincide | E2 |
