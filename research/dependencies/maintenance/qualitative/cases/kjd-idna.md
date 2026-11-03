# Expediente cualitativo — `kjd/idna`

**Caso 4 de 6** (selección mecánica: «transitivo con más rutas»: 4 rutas).
**Evidencia congelada:** corte `2026-10-30T00:00:00Z`. **Evidencia web:**
2026-11-02 (SHA de fijación `d357725082245ff90f5cf8800a3fc297b1f2319a`,
**posterior al corte**: merge del 2026-10-31; los archivos citados existían
antes del corte salvo indicación).

## A. Identificación y relación con DeudaMundi

| Campo | Valor (congelado) | Fuente |
|---|---|---|
| Distribución instalada | `idna` **3.20** | `distribution-map.csv` |
| Categoría | `runtime:transitive`; 2 saltos | `graph/nodes.csv` |
| Rutas desde la raíz | 4 | `graph/paths.txt` |
| Reclamada por | `deudamundi-api; fastapi; httpx; uvicorn` | `nodes.csv` |
| Requerida por | `anyio; httpx` | `nodes.csv` |
| Repositorio atribuido | `https://github.com/kjd/idna` | `source-repos.csv` (verificado 2026-10-30T14:16:11Z) |

idna entra por las cuatro esquinas de la pila web (cada dependente lo arrastra
por separado): `anyio` e `httpx` lo requieren explícitamente.

## B. Organización y gobernanza (C2/C3)

- **Propietario público:** cuenta individual `kjd` (API de repositorio:
  `owner.login: kjd`, `type: User`, `fork: false`; E2). Creado en 2013.
- **Relación con estándares (E1, declarada por el proyecto):** el README
  documenta soporte para IDNA (RFC 5891) y Unicode IDNA Compatibility
  Processing (UTS #46); `tools/README.md` documenta la generación de tablas
  «in the format found in Appendix B.1 of RFC 5892 and the pre-computed tables
  published by [IANA]»; `HISTORY.md` cita declaraciones de la IAB. La cuenta
  declara en su perfil afiliación pública «@icann @iana-org» (E1, declaración
  de la cuenta; **no** se interpreta como financiación ni dedicación).
- **Políticas de contribución:** **sin** `CONTRIBUTING.md`, `GOVERNANCE.md` ni
  `CODEOWNERS` (E2 de ausencia sobre el árbol; E4 para política escrita).
- **Publicación de versiones (E1/E2):** no hay documento prose, pero el
  workflow `deploy.yml` implementa un proceso formal: release en tags `v*`
  con **Trusted Publishing**, validación tag↔`__version__`, firma **Sigstore**
  y creación automática de la GitHub Release con notas extraídas de
  `HISTORY.md`, con la regla explícita: «A release without a HISTORY entry is
  an error.»
- **Mantenedores nombrados:** el `pyproject.toml` declara una única entrada de
  autoría («Kim Davies», E1). `SECURITY.md` se autodescribe en plural:
  «this project is maintained by a **team of volunteers** who work on a best
  effort basis» (E1). **Tensión documental registrada sin resolver:** autors
  singular vs. «team of volunteers»; ambos hechos son E1.
- **Sucesión y continuidad (clasificación de la auditoría 2026-11-03):**
  cuenta individual propietaria; **mecanismo formal documentado** en el
  workflow de publicación (validación tag↔versión, Trusted Publishing, firma
  Sigstore, exigencia de entrada en `HISTORY.md`) — categoría 2 parcial —;
  **relevo o sucesión futura no localizada** (categorías 4/5). La ausencia de
  `GOVERNANCE.md`/`CONTRIBUTING.md` **no** equivale a ausencia de procesos: el
  workflow de release es un procedimiento escrito ejecutable.

## C. Roles observables (C1/C4)

Métricas congeladas (12 m):

| Flujo | Total ventana | Denominador humano | Actor top (cuenta) | Cuota |
|---|---|---|---|---|
| Commits sin merges | 122 (185 con merges) | 119 (incl. 2 «no atribuido») | `kjd` 109 | **0.916** (H1 conclusivo > 50 %) |
| PR fusionados a rama principal | 55 (3 bots, 52 humanos) | 52 | `kjd` 43 | 0.8269 |
| Pares únicos revisor–PR | 11 (1 bot) | 10 | `kjd` 6 | 0.60 |
| Releases de GitHub | 9 | 0 humanos (**9 bots**) | `github-actions[bot]` | — |

- **H4 coincide** (cmt = int = rev = `kjd`): los tres roles observables
  convergen en la misma cuenta, y la cuota de PR (0.8269) acompaña a la de
  commits (0.916) — **H2 no cambia de categoría** (0.916 → 0.8269, ambas
  > 75 %).
- **Publicación automatizada declarada:** los 9 releases de GitHub de la
  ventana (y los 10 de 24 m) están publicados por `github-actions[bot]` con
  artefactos `*.sigstore.json` (E1/E2 coherente con `deploy.yml`). La métrica
  de «quién publica» observa aquí un **bot declarado**, no a una cuenta humana:
  exactamente la situación que H3 enseñó a leer en la dirección opuesta (release
  ausente ≠ mantenimiento ausente).
- **Automatización no declarada:** no se observa en este caso; los patrones
  documentados (`claude`, `sqla-tester`, `invalid-email-address`) pertenecen a
  otros repositorios.

## D. Incentivos y financiación (C5)

- Sin `FUNDING.yml` (E2 de ausencia) y sin programa de GitHub Sponsors activo
  recuperable para la cuenta (E4: la URL `github.com/sponsors/kjd` redirige al
  perfil sin tiers).
- Sin declaraciones de financiación del proyecto en README/HISTORY/pyproject
  (E2). La única declaración de vinculación es la afiliación del perfil de la
  cuenta («@icann @iana-org», E1): es una declaración pública de la cuenta,
  **no** una financiación del proyecto ni evidencia de dedicación remunerada.

## E. Continuidad y límites (C6)

- Releases: 3.16 (2026-05-22) … **3.20 (2026-09-17)**, última publicada;
  en desarrollo al SHA fijado: «3.21 (2026-XX-XX) — Raise the minimum supported
  Python version to 3.10» (E1). Cadencia congelada: `rel_cadence_days` 30,37
  (descriptivo). Coherente con la ventana: 8 meses con commits en 12 m, último
  commit in-window 2026-10-29.
- Ciclo de seguridad documentado (E1): CVE-2024-3651 y CVE-2026-45409 con
  advisories publicados. *E3 — interpretación:* documenta un procedimiento de
  respuesta a seguridad, sin que permita concluir sobre capacidad futura.
- **Actividad post-corte (observada 2026-11-02, fuera de las ventanas):**
  merges de PR externos (#278 del fork `Pitchfork-and-Torch` el 2026-10-31;
  #283/#284 de `zydo` el 2026-10-22). Se registra como contexto actual y
  **no** se mezcla con los eventos congelados.
- Sin relevo o sucesión futura documentada (E4, búsqueda registrada); sí
  proceso de publicación formalizado (categoría 2 parcial).

## F. Contraste con el análisis cuantitativo

| Confirma | Matiza | Debilita |
|---|---|---|
| H1 0.916: la cuenta `kjd` concentra autoría, integración y revisión — la documentación declara una autoría singular (E1) y la propiedad es una cuenta individual (E2) | La «ausencia de releases humanos» no es ausencia de publicación: la publicación está **automatizada y firmada** (E1/E2) | La lectura unipersonal estricta: `SECURITY.md` declara «a team of volunteers» (E1) y los changelog agradecen contribuciones nombradas en múltiples releases (E1) |
| H2 no cambia (ambas cuotas > 75 %): autoría e integración coinciden en la misma cuenta | Los pares de revisión humanos son escasos (10 en 12 m) pero incluyen cuentas distintas de `kjd` | — |
| — | — | La inferencia «poca actividad externa = abandono»: hay PR externos fusionados en octubre de 2026 y una release en desarrollo (3.21) |

**Contraejemplo/limite de validez:** idna es el caso en que más se alinean
métricas y documentación sobre concentración de roles, y aun así la
autodescripción del proyecto («team of volunteers») **no coincide literalmente**
con el dato de una sola cuenta de autoría: ninguna de las dos lecturas puede
presentarse como «el hecho completo».

## G. Fuentes (selección)

| # | URL | Tipo | Consulta | Fragmento | Nivel |
|---|---|---|---|---|---|
| 1 | `raw.githubusercontent.com/kjd/idna/d357725…/README.md` | README (SHA fijado) | 2026-11-02 | `Support for [IDNA](…rfc5891) and [Unicode IDNA Compatibility Processing](…tr46)` | E1 |
| 2 | `raw…/d357725…/pyproject.toml` | Metadatos (SHA fijado) | 2026-11-02 | `authors = [ {name = "Kim Davies", email = "kim+pypi@gumleaf.org"} ]` | E1 |
| 3 | `raw…/d357725…/SECURITY.md` | SECURITY (SHA fijado) | 2026-11-02 | «this project is maintained by a team of volunteers who work on a best effort basis.» | E1 |
| 4 | `raw…/d357725…/HISTORY.md` | Changelog (SHA fijado) | 2026-11-02 | «## 3.20 (2026-09-17)» / «3.21 (2026-XX-XX)» / «Thanks to stefan6419846, LouieLuNZ, and Salvatore Corvaglia…» | E1 |
| 5 | `raw…/d357725…/.github/workflows/deploy.yml` | Workflow de release | 2026-11-02 | «A release without a HISTORY entry is an error.» / «Sign with Sigstore» | E1/E2 |
| 6 | `api.github.com/repos/kjd/idna/releases?per_page=5` | API releases | 2026-11-02 | v3.20 `author.login: github-actions[bot]`, artefactos `*.sigstore.json` | E1/E2 |
| 7 | `api.github.com/repos/kjd/idna` | API repositorio | 2026-11-02 | `owner.login: kjd`, `type: User` | E2 |
| 8 | `api.github.com/repos/kjd/idna/contents/?ref=d357725…` | API contenidos | 2026-11-02 | Árbol sin CONTRIBUTING/GOVERNANCE/FUNDING | E2 (ausencia) |
| 9 | `github.com/sponsors/kjd` (perfil) | Perfil de cuenta | 2026-11-02 | «@icann @iana-org» (afiliación declarada) | E1 (declaración de cuenta) |
| 10 | `attributions/pypi-evidence/idna/3.20.json` | Metadatos PyPI congelados | 2026-10-30 (congelado) | `ownership: Owner kjd`; author_email Kim Davies | E2 |
| 11 | `analysis/results/repo-metrics.csv`, `h3-test.csv`, `actor-shares.csv` | Métricas congeladas | corte 2026-10-30 | H1 0.916; releases 9/9 bots; H3 no califica (releases > 0) | E2 |
