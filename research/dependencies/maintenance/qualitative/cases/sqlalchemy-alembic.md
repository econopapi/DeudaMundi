# Expediente cualitativo — `sqlalchemy/alembic`

**Caso 2 de 6** (selección mecánica: «directo central», 1 ruta, desempate
alfabético entre los directos con 1 ruta). **Evidencia congelada:** corte
`2026-10-30T00:00:00Z`. **Evidencia web:** 2026-11-02 (SHA de fijación
`1bcba93ea0473c69b48e704f842ca96e9e5348f5`).

## A. Identificación y relación con DeudaMundi

| Campo | Valor (congelado) | Fuente |
|---|---|---|
| Distribución instalada | `alembic` **1.20.1** | `distribution-map.csv` |
| Categoría | `runtime:direct` | `graph/nodes.csv` |
| Rutas desde la raíz | 1 (`deudamundi-api → alembic`); 1 salto | `graph/paths.txt` |
| Reclamada por | `deudamundi-api` | `nodes.csv` |
| Repositorio atribuido | `https://github.com/sqlalchemy/alembic` | `source-repos.csv` (verificado 2026-10-30T14:16:11Z) |
| Nota de atribución | «repo URL taken from metadata label 'issue tracker'» aplica a `mako`, no a este caso; alembic concuerda en dos fuentes independientes | `source-repos.csv` |

Alembic es además «padre» de `mako` y `markupsafe` en el grafo, pero esos son
repositorios atribuidos distintos (`sqlalchemy/mako`, `pallets/markupsafe`).

## B. Organización y gobernanza (C2/C3)

- **Propiedad y continuidad institucional:** repositorio bajo la organización
  `sqlalchemy` (E2). Las **mismas políticas** que `sqlalchemy/sqlalchemy`: los
  `CONTRIBUTING.md` y `CODE_OF_CONDUCT.md` de ambos repositorios son el mismo
  blob (idéntico SHA, E2) y la Community Guide declara que se aplica «to all
  projects hosted under the SQLAlchemy organization's repository» (E1).
- **Aceptación de cambios:** PR de GitHub solo como remoto de entrada a la
  revisión **Gerrit** propia (`.gitreview`: `project=sqlalchemy/alembic`,
  puerto 29418); los PR externos se integran con trailers `Pull-request:` /
  `Change-Id:` y materialización por la cuenta `sqla-tester` (E2).
- **Seguridad (E1):** `SECURITY.md` vía Tidelift (versión más corta que la de
  sqlalchemy).
- **Publicación de versiones (E1/E2):** PyPI + GitHub Release materializadas
  por `sqla-tester` (release `rel_1_20_1` el 2026-10-22); el proyecto declara
  que su versionado «does not use SemVer» (E1).
- **Mantenedores nombrados (E1):** las docs declaran «Alembic is developed by
  [Mike Bayer], and is part of the [SQLAlchemy] project»; el README: «written
  by the author of `SQLAlchemy`»; el pie de docs: «© Copyright 2010-2026, Mike
  Bayer». El `pyproject.toml` declara una entrada `authors` singular. Los
  metadatos PyPI congelados registran Owners `CaselIT` y `zzzeek` para la
  organización `sqlalchemy` (E2 congelado), es decir, la propiedad del paquete
  es organizativa aunque la autoría declarada sea singular.
- **Sucesión:** sin `GOVERNANCE.md` ni procedimiento localizable (E2 de
  ausencia; E4).

## C. Roles observables (C1/C4)

Métricas congeladas (12 m; `repo-metrics.csv`, `actor-shares.csv`):

| Flujo | Total ventana | Denominador humano | Actor top (cuenta) | Cuota |
|---|---|---|---|---|
| Commits sin merges | 108 (121 con merges) | 105 | `zzzeek` 79 | **0.7524** (H1 conclusivo > 50 %) |
| PR fusionados a rama principal | 6 (3 bots, 3 humanos) | 3 | empate 3×1 | **no evaluable** (umbral ≥ 10) |
| Pares únicos revisor–PR | 54 (1 bot) | 53 | `sqla-tester` 19 | 0.3585 — automatización no declarada |
| Releases de GitHub | 12 | 12 | `sqla-tester` 12 | 1.0 |

- **Autoría:** `zzzeek` 79/105 (0.7524) y `CaselIT` segundo con 7; la muestra
  recontada del 2026-08-01 al 2026-11-02 da 38/48 commits con autor `zzzeek`
  (E2 post-corte, coherente con la ventana congelada).
- **Revisión:** top `sqla-tester` (patrón documentado en
  `../analysis/audits.md`: 19 pares en 12 m), seguido de `CaselIT` (10) y
  `zzzeek` (9); contribuyentes externos con pares de revisión observables
  (`MohammedAlkindi`, 8).
- **Integración y publicación:** con solo 3 PR humanos fusionados a rama
  principal, el flujo de PR **no** es informativo aquí (regla preregistrada:
  H2 y H4 **no evaluables** para este repo). Los 12 releases están
  materializados por `sqla-tester`; el changelog acredita autorías externas
  («Pull request courtesy vineoy», 1.20.1).
- **Automatización:** además de `sqla-tester`, `dependabot` aporta PR (con
  bots incluidos, el top de PR es `dependabot`).

## D. Incentivos y financiación (C5)

- `FUNDING.yml` (E1): `github: alembic` / `patreon: zzzeek` /
  `tidelift: "pypi/SQLAlchemy"` — la financiación declarada apunta al conjunto
  SQLAlchemy (Tidelift `pypi/SQLAlchemy`), no a alembic aisladamente.
- Sin botón de Sponsors observable para la cuenta `alembic` (E2). Sin
  declaraciones de empleadores (E4). No se infiere remuneración.

## E. Continuidad y límites (C6)

- Releases in-window: 12 en 12 m (cadencia media 40,34 días, descriptiva);
  última 2026-10-22; commit más reciente in-window 2026-10-27; se observa un
  commit «Version 1.20.2 placeholder» (2026-10-22, E2), señal documental de
  ciclo en curso.
- PR: la ventana registra solo 5 meses con algún PR (`pr_months_all=5`,
  `pr_months_nobot=3`) frente a 12 meses con commits: la actividad se observa
  casi exclusivamente por commits directos — consistente con el flujo Gerrit.
- Sin transferencias de responsabilidad documentadas ni sucesión escrita (E4).

## F. Contraste con el análisis cuantitativo

| Confirma | Matiza | Debilita |
|---|---|---|
| H1 conclusivo alto (0.7524) concuerda con la autoría declarada («developed by Mike Bayer», E1) | La no-evaluabilidad por PR (H2/H4) es un **hecho de flujo de trabajo** (Gerrit), no ausencia de gobernanza | La lectura unipersonal: `CaselIT` es el segundo autor, el segundo revisor y copropietario del paquete en PyPI (E2 congelado); la política comunitaria es la de toda la organización |
| La publicación 100 % `sqla-tester` coincide con el pipeline documentado de la organización | La cuota de revisión por cuenta literal queda contaminada por `sqla-tester` | — |

**Contraejemplo/limite de validez:** alembic muestra que los umbrales de
evaluabilidad (≥ 30 commits, ≥ 10 PR) dejan fuera de H2/H4 a repositorios con
flujo no-PR **totalmente activos**; ningún titular puede leer «no evaluable»
como «sin actividad» o «sin coordinación».

## G. Fuentes (selección)

| # | URL | Tipo | Consulta | Fragmento | Nivel |
|---|---|---|---|---|---|
| 1 | `raw.githubusercontent.com/sqlalchemy/alembic/1bcba93e…/README.rst` | README (SHA fijado) | 2026-11-02 | «written by the author of `SQLAlchemy`» | E1 |
| 2 | `alembic.sqlalchemy.org/en/latest/front.html` | Docs oficiales | 2026-11-02 | «Alembic is developed by [Mike Bayer], and is part of the [SQLAlchemy] project.» | E1 |
| 3 | `raw…/1bcba93e…/.github/FUNDING.yml` | Financiación (SHA fijado) | 2026-11-02 | `github: alembic / patreon: zzzeek / tidelift: "pypi/SQLAlchemy"` | E1 |
| 4 | `raw…/1bcba93e…/.gitreview` | Gerrit (SHA fijado) | 2026-11-02 | `project=sqlalchemy/alembic … port=29418` | E1 |
| 5 | `raw…/1bcba93e…/.github/CONTRIBUTING.md` | CONTRIBUTING (SHA fijado) | 2026-11-02 | blob idéntico al de `sqlalchemy/sqlalchemy` (mismo SHA) | E1/E2 |
| 6 | `api.github.com/repos/sqlalchemy/alembic/releases` | API releases | 2026-11-02 | `rel_1_20_1` (2026-10-22) publicada por `sqla-tester` | E2 |
| 7 | `attributions/pypi-evidence/alembic/1.20.1.json` | Metadatos PyPI congelados | 2026-10-30 (congelado) | `ownership: organization sqlalchemy; Owner CaselIT, Owner zzzeek` | E2 |
| 8 | `analysis/results/repo-metrics.csv`, `actor-shares.csv` | Métricas congeladas | corte 2026-10-30 | cuotas y denominadores de §C | E2 |
