# Expediente cualitativo — `kludex/starlette` (antes `encode/starlette`)

**Caso 6 de 6** (selección mecánica: «función distinta — capa de servidor»).
**Evidencia congelada:** corte `2026-10-30T00:00:00Z`. **Evidencia web:**
2026-11-02 (SHA de fijación `0f08970e5cce0aec4fc1cea7447c262d741795eb`).

## A. Identificación y relación con DeudaMundi

| Campo | Valor (congelado) | Fuente |
|---|---|---|
| Distribución instalada | `starlette` **0.46.2** | `distribution-map.csv` |
| Categoría | `runtime:transitive` (vía `fastapi`); 2 saltos | `graph/nodes.csv` |
| Rutas desde la raíz | 1 (`deudamundi-api → fastapi → starlette`) | `graph/paths.txt` |
| Requerida por | `fastapi` | `nodes.csv` |
| Repositorio atribuido | `https://github.com/Kludex/starlette` | `source-repos.csv` |
| **Redirección congelada** | `redirect_from = encode/starlette`; la evidencia `attributions/github-evidence/encode__starlette.json` registra: `requested_repo: encode/starlette` → `resolved_full_name: Kludex/starlette` el **2026-10-30T14:16:11Z** | artefactos congelados |

**Redirección posterior (observación del 2026-11-02, E2):** la redirección
**sigue activa**: `https://github.com/encode/starlette` responde `HTTP/2 301`
con `location: https://github.com/Kludex/starlette`. Los metadatos PyPI
congelados de la versión instalada (0.46.2) todavía declaraban
`Source/Homepage: https://github.com/encode/starlette` y
`Funding: https://github.com/sponsors/encode` (E2 congelado), mientras que el
PyPI **actual** (versión 1.10.0) declara `Source: …/Kludex/starlette` y
`Funding: …/sponsors/Kludex`: la evolución de los metadatos queda documentada
en ambos instantes, sin mezclarse.

## B. Organización y gobernanza (C2/C3)

- **Propietario público actual:** cuenta personal `Kludex` (`owner.type: User`,
  E2). La transferencia de la organización `encode` a esa cuenta está
  **documentada públicamente** (C6):
  - Anuncio (Discussion #2997, 2025-09-04, E1): «As some of you may have
    noticed, Uvicorn and Starlette are now under my personal handle (@Kludex)»
    … «After a lot of conversations with @lovelydinosaur, we came to an
    agreement that it was reasonable to move those projects» … «this only
    changes the official administration of the projects.»
  - El origen de la transferencia se expresa también públicamente (comentario
    de `lovelydinosaur`, 2025-09-05, E1): «I'm currently spending most of my
    working time on `httpx`. Marcello has been lead on `starlette` & `uvicorn`
    for some time now.»
  - Debate posterior sobre el modelo de propiedad (Issue #3180, 2026-03-09,
    E1): la cuenta `lovelydinosaur` pidió reconsiderar la propiedad
    («Perhaps there's space for community ownership … under a FastAPI
    organisation, or back under Encode»); la respuesta del titular actual fue
    «There's a written agreement on your behalf on the transfer»; la issue se
    cerró como *not planned* y se bloqueó el mismo día.
  - La **licencia conserva el titular histórico**: «Copyright © 2018, Encode
    OSS Ltd» (E1, `LICENSE.md`). La organización `encode` sigue existiendo
    («Collaboratively funded software development») pero ya no lista starlette
    ni uvicorn entre sus repositorios (E2).
- **Aceptación de cambios (E1):** `docs/contributing.md`: «Contributions should
  generally start out with a discussion»; desarrollo por fork; revisión de
  terceros invitada («Review Pull Requests of others»).
- **Publicación de versiones (E1):** «This section is targeted at Starlette
  maintainers» … «Once the release PR is merged, create a new release … Once
  created this release will be automatically uploaded to PyPI» (workflow
  `publish.yml`).
- **Roles nombrados (E1):** PyPI declara `author: Tom Christie` y
  `maintainer: Marcelo Trylesinski`; `CITATION.cff` nombra como autores a
  Marcelo Trylesinski y Tom Christie; la documentación usa el plural
  «Starlette maintainers» sin lista de nombres. Sin `GOVERNANCE.md` ni
  `SECURITY.md` localizados (E2 de ausencia; E4 para sucesión formal).

## C. Roles observables (C1/C4)

Métricas congeladas (12 m):

| Flujo | Total ventana | Denominador humano | Actor top (cuenta) | Cuota |
|---|---|---|---|---|
| Commits sin merges | 262 (sin merges) | 222 (incl. 1 «no atribuido») | `Kludex` 151 | **0.6802** (H1 conclusivo > 50 %) |
| PR fusionados a rama principal | 260 (40 bots, 220 humanos) | 220 | `Kludex` 149 | 0.6773 |
| Pares únicos revisor–PR | 570 (**376 bots**) | 194 | `Kludex` 117 | 0.6031 |
| Releases de GitHub | 23 | 23 | `Kludex` 23 | 1.0 |

- **H2 no cambia** (0.6802 → 0.6773) y **H4 coincide** (`Kludex` en los tres
  roles): la cuenta principal concentra autoría, integración, revisión y
  publicación en la ventana.
- **Materialización squash (dictamen §4):** este repo es uno de los cuatro
  casos en los que commits sin merges **igualan exactamente** a PR fusionados a
  rama principal (262/260 con 2 diferencias explicadas) y el 100 % se
  materializa vía `web-flow`: autoría de commits y autoría de PR **no son
  medidas independientes** aquí.
- **Revisión con automatización declarada masiva:** 376 de 570 pares son bots
  (variante con bots: el top de revisión pasa a `cubic-dev-ai`); la revisión
  **humana** distribuye tras `Kludex` entre ~49 cuentas con pares en la
  ventana. En 24 m hay 105 PR humanos fusionados a bases distintas de `main`
  (`merged_other_base_nonbot`), detalle que la métrica principal excluye por
  diseño.
- **Publicación:** los 23 releases de la ventana están a nombre de `Kludex`
  (humano); la documentación describe el paso de release PR → release de GitHub
  → subida automática a PyPI.

## D. Incentivos y financiación (C5)

- **Declarado en la documentación del proyecto (E1):** `FUNDING.yml`:
  `github: Kludex`; la web oficial (`starlette.dev`) pide patrocinio con la
  formulación «Help us keep Starlette maintained and sustainable by becoming a
  sponsor» y lista «Current sponsors: FastAPI». El patrocinio vía
  `github.com/sponsors/Kludex` se autodescribe: «I'm Marcelo Trylesinski
  (Kludex) … Core maintainer of this powerful ASGI framework that powers
  FastAPI».
- La página `github.com/sponsors/encode` sigue activa (30 sponsors; tiers
  «Early access» y «Partner Tier») pero **su texto actual no menciona starlette
  ni uvicorn** (E2): la financiación declarada de la organización ya no apunta
  a este proyecto. Los metadatos PyPI congelados (0.46.2) sí la apuntaban
  (`Funding: sponsors/encode`): ambos instantes quedan registrados por
  separado.
- **No** se infieren importes, salarios ni dedicación.

## E. Continuidad y límites (C6)

- **Transferencia de responsabilidad documentada (C6):** del proyecto bajo la
  organización `encode` a la cuenta personal `Kludex` (2025-09), con acuerdo
  público entre las partes (Discussion #2997). Es el caso de los seis con un
  **evento de sucesión/transferencia explícito y fechado**.
- Continuidad observable en la ventana: releases cada 5,97 días de media
  (descriptivo), 12/12 meses con actividad en todos los flujos, último evento
  in-window 2026-10-29.
- **Señal de debate abierto (sensible):** la Issue #3180 (2026-03) documenta
  que la cuestión del modelo de propiedad fue **planteada públicamente** y
  resuelta por el titular actual sin cambios, cerrándose y bloqueándose el hilo.
  Una pregunta relacionada de una tercera cuenta quedó sin respuesta
  registrada (E1/E2, verificada en la API de la Discussion #2997):
  «Does this mean you're the only maintainer right now?» (Jackenmen,
  2026-03-23), que además observaba que sin organización dedicada «there's no
  way to see a list of members». **La ausencia de respuesta no se interpreta
  como confirmación**; estas afirmaciones pasan a revisión factual
  (`../factual-review.md`).
- Sin `GOVERNANCE.md` ni mecanismo de sucesión formal (E4).

## F. Contraste con el análisis cuantitativo

| Confirma | Matiza | Debilita |
|---|---|---|
| H1 0.6802 y H4 coincidente: la documentación declara a la cuenta actual como lead de mantenimiento (E1) y propietaria del repositorio (E2) | La igualdad exacta commits/PR es materialización squash (dictamen §4): no «confirma dos veces» | La lectura unipersonal literal: la documentación nombra dos roles (autor y mantenedor) y prevé revisión comunitaria; ~49 cuentas humanas revisan en la ventana |
| La publicación 100 % de la cuenta principal coincide con el proceso de release documentado (release PR → GitHub release → PyPI) | 66 % de los pares de revisión son bots declarados: la «revisión» agregada solo se entiende separando la automatización (fig5) | La equivalencia entre propiedad del repo y «mantenimiento del ecosistema encode»: la licencia conserva a Encode OSS Ltd y `encode` sigue operando con otros proyectos |
| — | — | Cualquier lectura de «abandono» de la comunidad: hay PR humanos a bases secundarias (105 en 24 m), 32 PR abiertos y una comunidad que debate activamente |

**Contraejemplo/limite de validez:** starlette demuestra que la atribución
paquete→repositorio **no es estable en el tiempo** (redirección, cambio de
propiedad, metadatos que evolucionan): cualquier titular sobre «quién mantiene»
un proyecto debe fechar su afirmación. También es el caso con afirmaciones más
sensibles sobre personas/organizaciones: exige la revisión factual prevista.

## G. Fuentes (selección)

| # | URL | Tipo | Consulta | Fragmento | Nivel |
|---|---|---|---|---|---|
| 1 | `attributions/github-evidence/encode__starlette.json` | Evidencia congelada | 2026-10-30 (congelado) | `requested_repo: encode/starlette` → `resolved_full_name: Kludex/starlette` | E2 |
| 2 | `https://github.com/encode/starlette` | Cabeceras HTTP (redirect) | 2026-11-02 | `HTTP/2 301` · `location: https://github.com/Kludex/starlette` | E2 |
| 3 | `github.com/Kludex/starlette/discussions/2997` | Anuncio de transferencia | 2026-11-02 | «Uvicorn and Starlette are now under my personal handle (@Kludex)» / «this only changes the official administration of the projects.» | E1 |
| 4 | ídem, comentario `lovelydinosaur` (2025-09-05) | Discussion | 2026-11-02 | «Marcello has been lead on `starlette` & `uvicorn` for some time now.» | E1 |
| 5 | `github.com/Kludex/starlette/issues/3180` | Issue (propiedad/nombre) | 2026-11-02 | «Perhaps there's space for community ownership of Starlette & Uvicorn…» / respuesta: «There's a written agreement on your behalf on the transfer.» | E1 |
| 6 | `raw.githubusercontent.com/Kludex/starlette/main/LICENSE.md` | Licencia | 2026-11-02 | «Copyright © 2018, Encode OSS Ltd.» | E1 |
| 7 | `raw…/main/docs/contributing.md` | CONTRIBUTING (docs) | 2026-11-02 | «This section is targeted at Starlette maintainers.» / «Once created this release will be automatically uploaded to PyPI.» | E1 |
| 8 | `raw…/main/CITATION.cff` | Metadatos de citación | 2026-11-02 | `authors: Marcelo Trylesinski … Tom Christie`; `repository-code: …/Kludex/starlette` | E1 |
| 9 | `raw…/main/.github/FUNDING.yml` | Financiación | 2026-11-02 | `github: Kludex` | E1 |
| 10 | `https://starlette.dev/` | Web oficial | 2026-11-02 | «Help us keep Starlette maintained and sustainable by becoming a sponsor»; «Current sponsors: FastAPI» | E1 |
| 11 | `https://pypi.org/pypi/starlette/json` | Metadatos PyPI actuales | 2026-11-02 | `author_email: Tom Christie…`; `maintainer_email: Marcelo Trylesinski…`; `Funding: …/sponsors/Kludex` | E1 |
| 12 | `attributions/pypi-evidence/starlette/0.46.2.json` | Metadatos PyPI congelados | 2026-10-30 (congelado) | `ownership: Owner Kludex`; `Funding: …/sponsors/encode`; `Source: …/encode/starlette` | E2 |
| 13 | `api.github.com/repos/Kludex/starlette` | API repositorio | 2026-11-02 | `owner: {login: Kludex, type: User}`; `created_at: 2018-06-25` (preservado en la transferencia) | E2 |
| 14 | `https://github.com/sponsors/encode` | Patrocinio org | 2026-11-02 | «Encode is dedicated to pushing forward the Python web ecosystem.» — sin mención de starlette | E1/E2 |
| 15 | `analysis/results/repo-metrics.csv`, `actor-shares.csv`, `final-audits/traceability-h1h4.csv` | Métricas congeladas | corte 2026-10-30 | H1 0.6802; H2 no cambia; H4 coincide; revisión 376/570 bots | E2 |
