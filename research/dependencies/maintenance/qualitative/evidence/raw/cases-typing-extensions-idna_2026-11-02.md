# Evidencia documental web — Repositorios `python/typing_extensions` y `kjd/idna`

**Fecha de consulta de todas las fuentes: 2026-11-02.** La fecha de corte de los datos congelados del estudio es **2026-10-30**; todas las fuentes de este informe se consultan **con posterioridad al corte** y así se registran. Los SHAs citados fijan el estado del repositorio al momento de la consulta.

Convenciones:
- **E1** = documental directa (texto literal de un documento oficial del proyecto o metadato público del repositorio).
- **E2** = observación técnica (listados de API, presencia/ausencia de archivos, respuestas HTTP).
- **E3** = inferencia contextual — **marcada explícitamente como interpretación**.
- **E4** = no verificable / no recuperada.
- Los nombres de cuentas y campos de autoría se citan como **metadatos públicos del proyecto**. No se asimila cuenta = persona. No se infieren salarios, dedicación, riesgo ni causalidad.

---

## 1. `python/typing_extensions`

SHA de `main` fijado a la consulta: `cfde842014f0e05e2a09bf58fd9e2e4a20a9fdff` (commit de 2026-10-23, «Update uv to 0.13.5 (#812)», API de commits de GitHub).

### 1.1 Gobernanza

- **Propietario público**: el repositorio vive bajo la organización GitHub `python`. El perfil de la organización declara: «Repositories related to the Python Programming language» y su blog apunta a `https://www.python.org/` (E1, `https://api.github.com/orgs/python`).
- **Estatus PSF**: el `pyproject.toml` declara `license = "PSF-2.0"` y `CONTRIBUTING.md` exige: «contributors need to sign the PSF Contributor Agreement» (E1). La documentación usa voz institucional plural: «`typing_extensions` is among the most widely used packages in the Python ecosystem. Therefore, we take security seriously» (E1, `doc/index.rst`).
- **Relación con PEPs / typing team**: la documentación oficial fija el criterio de admisión de funcionalidad: «New features may be added to `typing_extensions` as soon as they are specified in a PEP that has been added to the `python/peps` repository» y «Bugfixes and new typing features that don't require a PEP may be added to `typing_extensions` once they are merged into CPython's main branch» (E1, `doc/index.rst`). El README enlaza como canal de Q&A a `https://github.com/python/typing/discussions` (E1).
- **VERIFICACIÓN SOBRE PEP 576 (contraste con la hipótesis de guion)**: se recuperó `https://peps.python.org/pep-0576/`. Su título es «PEP 576 – Rationalize Built-in function classes», autor Mark Shannon, estado «Status: Withdrawn». **El PEP 576 no trata sobre `typing_extensions` ni sobre su gobernanza** (E1, hallazgo negativo verificable). Cualquier vínculo «typing_extensions ↔ PEP 576» quedaría como E4 refutado por esta fuente.
- **Proceso de contribución**: `CONTRIBUTING.md` detalla estilo («Code in this repository should follow CPython's style guidelines»), pruebas, linting y documentación (E1).
- **Proceso de release documentado**: sección «Workflow for PyPI releases» de `CONTRIBUTING.md`: crear release de GitHub con tag = versión, «Release automation will finish the release. You'll have to manually approve the last step before upload.» (E1). La política de versionado está en `doc/index.rst`: «Feature releases, with version numbers of the form 4.N.0, are made at irregular intervals when enough new features accumulate. Before a feature release, at least one release candidate … should be released… After at least a week of testing, the new feature version may then be released.» (E1).
- **Publicación automatizada**: `.github/workflows/publish.yml` publica en PyPI solo en eventos `release`, con Trusted Publishing: `permissions: id-token: write # IMPORTANT: mandatory for trusted publishing` (E1/E2, YAML de CI).
- **Mecanismos de sucesión**: no se localizó `GOVERNANCE.md`, `CODEOWNERS` ni política de sucesión en el árbol del repositorio al SHA fijado (E2, listado de API de contenidos). **Proceso de sucesión documentado: no verificado (E4).**

### 1.2 Roles nombrados (solo lo que dice la documentación)

- Metadatos del paquete (`pyproject.toml`, campo `[[project.authors]]`): `name = "Guido van Rossum, Jukka Lehtosalo, Łukasz Langa, Michael Lee"`, `email = "levkivskyi@gmail.com"` (E1). Es el campo de autoría del proyecto; no se interpreta como lista de mantenedores actuales.
- El `CHANGELOG.md` atribuye cambios a múltiples firmas: «Patch by Brian Schubert», «Patch by Jelle Zijlstra», «Patch by [Victorien Plot]», «Patch by Daraan», «Patch by [Semyon Moroz]», entre muchos otros (E1).
- Los metadatos de releases de GitHub registran como `author` de la release 4.16.0 la cuenta `AlexWaygood` y de la release 4.15.0 la cuenta `JelleZijlstra` (E1, API de releases; hecho a nivel de cuenta).

### 1.3 Financiación declarada

- **Ausencia de mecanismo de patrocinio en el repo**: `https://raw.githubusercontent.com/python/typing_extensions/cfde842014f0e05e2a09bf58fd9e2e4a20a9fdff/.github/FUNDING.yml` → HTTP 404 (E4 «no recuperada»; corroborada como ausencia por el listado de `.github/`, que solo contiene `codecov.yml`, `renovate.json5` y `workflows/`, E2).
- **GitHub Sponsors de la organización `python`** (recuperado, E1): `https://github.com/sponsors/python`. Fragmento: «The capacity of the Python Software Foundation to support the development of CPython … hasn't kept pace with the growth in popularity of the programming language» y «The goal is to hire to address backlog, and afterwards, hire to address new projects.» La página destaca repositorios («Featured work»: `python/cpython`, `python/mypy`, `python/pythondotorg`, `python/asyncio`, `python/pymanager`, `python/psf-salt`) — **`typing_extensions` no figura entre ellos** (E2).
  - *E3 — INTERPRETACIÓN*: la página de patrocinio es de la organización/PSF y no declara de forma explícita que los fondos se destinen a `typing_extensions`. Toda vinculación financiera concreta con este repositorio queda como **inferencia no documentada** y no debe presentarse como hecho.
- No se localizaron en el repositorio declaraciones de empleadores, Tidelift ni otros flujos de financiación atribuidos al proyecto (E2 sobre el árbol de archivos; E4 para cualquier financiación específica no declarada).

### 1.4 Continuidad

- **Transferencia documentada de ubicación/propiedad**: el README de `python/typing` declara: «Historically, this repository also hosted: The `typing_extensions` package, which now lives in the [typing_extensions](https://github.com/python/typing_extensions) repo. It used to be in the `typing_extensions` directory.» (E1).
- **Historial de releases reciente** (E1, CHANGELOG y API de releases): 4.12.0rc1 (2024-05-16, «Releases are now made using Trusted Publishers improving the security of the release process»), 4.13.x (2025-03/04), 4.14.x (2025-05/06), 4.15.0 (2025-08-25), 4.16.0rc1 (2026-06-24), 4.16.0rc2 (2026-06-25), **4.16.0 (2026-07-02, última release publicada a la consulta)**. El `pyproject.toml` al SHA fijado muestra `version = "4.16.1.dev0"` (E1/E2), indicador documental de ciclo de desarrollo en curso tras la última release.
- **Actividad de commits**: commit más reciente en `main` al SHA fijado: 2026-10-23, PR #812 (E1/E2, API de commits).

### 1.5 Contraevidencia (hechos que matizan la lectura «un solo mantenedor»)

1. **Múltiples cuentas publican releases**: releases creadas por las cuentas `AlexWaygood` (4.16.0, 4.16.0rc1/rc2) y `JelleZijlstra` (4.15.0, 4.15.0rc1) (E1, API de releases).
2. **Proceso formal de release documentado** con candidaturas, semana de pruebas y aprobación manual final (E1, `CONTRIBUTING.md` + `doc/index.rst`) — un proceso explícito, no ad hoc.
3. **Requisito institucional de contribución**: firma del PSF Contributor Agreement (E1).
4. **Protecciones de publicación automatizadas** (Trusted Publishers, aprobación manual del último paso) (E1/E2, `publish.yml` + CHANGELOG 4.12.0rc1).
5. **Pluralidad de contribuciones atribuidas** en CHANGELOG (docenas de «Patch by …» distintos a lo largo de 2021-2026) (E1).
6. **Alineación con CPython/PEPs**: las features se admiten tras especificación en PEP o fusión en `main` de CPython; hay CI que testea contra ~10 proyectos de terceros (mypy, sqlalchemy, pydantic, etc., `third_party.yml`) (E1/E2).
7. En sentido contrario, para registro: el campo `authors` del paquete lista una única entrada de metadatos con cuatro nombres históricos (E1); no existe `CODEOWNERS` ni `GOVERNANCE.md` (E2).

---

## 2. `kjd/idna`

SHA de `master` fijado a la consulta: `d357725082245ff90f5cf8800a3fc297b1f2319a` (merge de PR #278, 2026-10-31, **posterior al corte 2026-10-30**). Metadatos de API: creado 2013-05-27, licencia BSD-3-Clause, `default_branch: master`, descripción: «Internationalized Domain Names for Python (IDNA 2008 and UTS #46)» (E1/E2).

### 2.1 Gobernanza

- **Propietario**: cuenta personal `kjd`; el repositorio no está bajo organización alguna (E1/E2, API de repositorio: `"owner":{"login":"kjd" ...}`, `"fork":false`).
- **Relación con estándares (declarada en docs)**: el README declara: «Support for [Internationalized Domain Names in Applications (IDNA)](https://tools.ietf.org/html/rfc5891) and [Unicode IDNA Compatibility Processing](https://unicode.org/reports/tr46/)» (E1). `tools/README.md` declara: «`idna-data make-table`. Generate a table of the IDNA disposition (e.g. PVALID, CONTEXTJ, CONTEXTO) in the format found in Appendix B.1 of RFC 5892 and the pre-computed tables published by [IANA](https://www.iana.org/).» (E1). El README también menciona explícitamente a la IAB: «Internet Architecture Board (IAB) issued statement recommending against the use of Unicode 7.0.0…» (E1, `HISTORY.md` 1.1).
- **Políticas de contribución**: **no existe `CONTRIBUTING.md`** en la raíz del repositorio al SHA fijado (E2, listado de API de contenidos: solo `.github/`, `.gitignore`, `HISTORY.md`, `LICENSE.md`, `README.md`, `SECURITY.md`, `idna/`, `pyproject.toml`, `tests/`, `tools/`). No se localizó `GOVERNANCE.md` ni `CODEOWNERS` (E2). **Política de contribución escrita: no verificada (E4).**
- **Proceso de release**: no hay documento prose que lo describa, pero el workflow `.github/workflows/deploy.yml` lo implementa (E1/E2): publicación en PyPI solo en tags `v*` con Trusted Publishing (`id-token: write # IMPORTANT: mandatory for trusted publishing`), validación de que el tag coincide con `__version__`, firma Sigstore («Sign with Sigstore») y creación automática de la GitHub Release extrayendo notas de `HISTORY.md`, con la regla explícita: «A release without a HISTORY entry is an error.»
- **Mecanismos de sucesión**: no documentados (E4).

### 2.2 Roles nombrados (solo lo que dice la documentación)

- Metadatos del paquete (`pyproject.toml`): `authors = [ {name = "Kim Davies", email = "kim+pypi@gumleaf.org"} ]` (E1) — única entrada de autoría declarada por el proyecto.
- `SECURITY.md` declara en plural: «be mindful that this project is maintained by a team of volunteers who work on a best effort basis.» (E1). Nótese la tensión documental entre esta autodescripción («team of volunteers») y el campo de autores con una sola entrada; ambos hechos se registran sin resolver la tensión.
- `HISTORY.md` agradece contribuciones nombradas: «Thanks to stefan6419846, LouieLuNZ, and Salvatore Corvaglia for contributions to this release.» (3.19); «Thanks to Felix Yan, Stan Ulbrych, and metsw24-max» (3.15); «Thanks to Guido Vranken for reporting the issue» (3.7); «Thanks to Rodrigo Nogueira» (3.12) (E1).
- La cuenta `kjd` declara públicamente en su perfil de GitHub afiliación a «@icann @iana-org» (E1, `https://github.com/sponsors/kjd` redirige al perfil; dato de la cuenta, declarado públicamente por ella misma).

### 2.3 Financiación declarada

- `https://raw.githubusercontent.com/kjd/idna/d357725082245ff90f5cf8800a3fc297b1f2319a/.github/FUNDING.yml` → HTTP 404 (E4 «no recuperada»; ausencia corroborada por el listado de `.github/`: solo `dependabot.yml`, `requirements/`, `workflows/`, E2).
- `https://github.com/sponsors/kjd` redirige al perfil de la cuenta, donde **no se recuperó un programa de GitHub Sponsors activo ni niveles de patrocinio** (E4 para financiación vía GitHub Sponsors; la página de perfil sí recupera la afiliación declarada citada arriba, E1).
- No se localizaron en README/HISTORY/pyproject declaraciones de financiación, patrocinio ni fundaciones (E2; E4 para financiación específica no declarada).

### 2.4 Continuidad

- **Releases recientes** (E1, `HISTORY.md` y API de releases): 3.16 (2026-05-22), 3.17 (2026-05-28), 3.18 (2026-06-02), 3.19 (2026-08-18), **3.20 (2026-09-17, última publicada)**. En desarrollo al SHA fijado: «## 3.21 (2026-XX-XX) — Raise the minimum supported Python version to 3.10» (E1).
- **Publicación automatizada y firmada**: las releases v3.16–v3.20 figuran publicadas por `github-actions[bot]` con artefactos `*.sigstore.json` (E1/E2, API de releases) — infraestructura de release independiente de intervención manual en el paso de subida.
- **Actividad reciente (posterior al corte)**: merges el 2026-10-31 (PR #278, de un fork externo `Pitchfork-and-Torch`), 2026-10-29 (PR #287 rama `kjd/ascii-label-fast-path`), 2026-10-22 (PR #283 y #284, de `zydo`) (E1/E2, API de commits).
- **Ciclo de seguridad documentado**: CVE-2024-3651 (3.7) y CVE-2026-45409 (3.14, «Reference CVE-2026-45409 for the 3.14 advisory in place of the initial GHSA identifier») con avisos publicados (E1, `HISTORY.md`). *E3 — INTERPRETACIÓN*: la existencia de un canal de advisories y de respuestas CVE documenta un procedimiento de respuesta, sin que ello permita concluir nada sobre capacidad futura ni asignación de responsables.

### 2.5 Contraevidencia (hechos relevantes en ambos sentidos)

**Debilitan la lectura «un solo mantenedor»:**
1. `SECURITY.md`: «this project is maintained by a **team of volunteers** who work on a best effort basis.» (E1).
2. Integración activa de contribuciones externas: PRs #278 (`Pitchfork-and-Torch`), #283/#284 (`zydo`) fusionados en octubre de 2026 (E1/E2).
3. Créditos de contribución nombrados en HISTORY en múltiples releases (3.3, 3.4, 3.8, 3.9, 3.12, 3.15, 3.19) (E1).
4. Proceso de release formalizado en CI: validación de metadatos, tests contra la wheel instalada, Trusted Publishing, firma Sigstore, notas de release obligatorias (E1/E2, `deploy.yml`).
5. Infraestructura de calidad amplia: `scorecard.yml` (OpenSSF Scorecard), `unicode-check.yml` (verificación de tablas contra el generador), dependabot, tests property-based y fuzzing («Add property-based tests, extended fuzzing targets, coverage measurement…», HISTORY 3.19) (E1/E2).

**Refuerzan de forma no trivial la lectura de concentración de responsabilidad (hechos documentados, sin inferir personas):**
1. El campo `authors` del paquete declara una sola entrada (E1, `pyproject.toml`).
2. Los merges en `master` del período octubre 2026 fueron ejecutados desde la cuenta `kjd` (E1/E2, API de commits — hecho a nivel de cuenta, sin asimilar cuenta a persona).
3. La propiedad del repositorio es una cuenta individual y no una organización (E1/E2, API de repositorio).
4. No hay `CONTRIBUTING.md`, `GOVERNANCE.md`, `CODEOWNERS` ni proceso de sucesión documentado (E2/E4).

---

## 3. Registro de URLs no recuperadas (E4)

| URL intentada | Resultado | Registro |
|---|---|---|
| `https://raw.githubusercontent.com/python/typing_extensions/cfde842014f0e05e2a09bf58fd9e2e4a20a9fdff/.github/FUNDING.yml` | HTTP 404 | E4 «no recuperada»; ausencia de FUNDING.yml corroborada por listado de API (E2) |
| `https://raw.githubusercontent.com/kjd/idna/d357725082245ff90f5cf8800a3fc297b1f2319a/.github/FUNDING.yml` | HTTP 404 | E4 «no recuperada»; ausencia corroborada por listado de API (E2) |
| `https://github.com/sponsors/kjd` | Redirige al perfil sin programa de Sponsors recuperable | E4 para financiación vía Sponsors |
| GOVERNANCE.md / proceso de sucesión (`typing_extensions`) | No existe en el árbol al SHA fijado | E4 (ausencia E2) |
| CONTRIBUTING.md / GOVERNANCE.md / sucesión (`kjd/idna`) | No existen en el árbol al SHA fijado | E4 (ausencia E2) |
| Financiación específica declarada para `typing_extensions` | Sin declaración explícita localizada | E4 (la página de sponsors de la org `python` es E1 de la org, no del proyecto) |

---

## 4. Tabla final de fuentes

| # | URL | Tipo | Fecha consulta | Fragmento textual verificable | Nivel E |
|---|---|---|---|---|---|
| 1 | `https://raw.githubusercontent.com/python/typing_extensions/cfde842014f0e05e2a09bf58fd9e2e4a20a9fdff/README.md` | README (raw @SHA) | 2026-11-02 | «See [CONTRIBUTING.md](…) for how to contribute to `typing_extensions`.» | E1 |
| 2 | `https://raw.githubusercontent.com/python/typing_extensions/cfde842014f0e05e2a09bf58fd9e2e4a20a9fdff/CONTRIBUTING.md` | CONTRIBUTING (raw @SHA) | 2026-11-02 | «contributors need to sign the PSF Contributor Agreement» / «Release automation will finish the release. You'll have to manually approve the last step before upload.» | E1 |
| 3 | `https://raw.githubusercontent.com/python/typing_extensions/cfde842014f0e05e2a09bf58fd9e2e4a20a9fdff/pyproject.toml` | Metadatos de proyecto (raw @SHA) | 2026-11-02 | `[[project.authors]] name = "Guido van Rossum, Jukka Lehtosalo, Łukasz Langa, Michael Lee"`; `license = "PSF-2.0"`; `version = "4.16.1.dev0"` | E1 |
| 4 | `https://raw.githubusercontent.com/python/typing_extensions/cfde842014f0e05e2a09bf58fd9e2e4a20a9fdff/SECURITY.md` | SECURITY (raw @SHA) | 2026-11-02 | «Only the latest release is supported.» / «We commit to respond to any issue within 14 days» | E1 |
| 5 | `https://raw.githubusercontent.com/python/typing_extensions/cfde842014f0e05e2a09bf58fd9e2e4a20a9fdff/doc/index.rst` | Docs oficiales (raw @SHA) | 2026-11-02 | «New features may be added to `typing_extensions` as soon as they are specified in a PEP that has been added to the `python/peps` repository.» / «Feature releases … are made at irregular intervals when enough new features accumulate.» | E1 |
| 6 | `https://raw.githubusercontent.com/python/typing_extensions/cfde842014f0e05e2a09bf58fd9e2e4a20a9fdff/CHANGELOG.md` | Changelog (raw @SHA) | 2026-11-02 | «# Release 4.16.0 (July 2, 2026) — No user-facing changes since 4.16.0rc2.»; «Patch by Brian Schubert.» | E1 |
| 7 | `https://api.github.com/repos/python/typing_extensions/releases?per_page=5` | API: releases (quién publica) | 2026-11-02 | 4.16.0 `published_at: 2026-07-02`, `author.login: "AlexWaygood"`; 4.15.0 `author.login: "JelleZijlstra"` | E1 |
| 8 | `https://raw.githubusercontent.com/python/typing_extensions/cfde842014f0e05e2a09bf58fd9e2e4a20a9fdff/.github/workflows/publish.yml` | Workflow de release (raw @SHA) | 2026-11-02 | `if: github.event_name == 'release'`; `id-token: write # IMPORTANT: mandatory for trusted publishing` | E1/E2 |
| 9 | `https://api.github.com/repos/python/typing_extensions/contents/?ref=cfde842014f0e05e2a09bf58fd9e2e4a20a9fdff` | API: listado de contenidos | 2026-11-02 | Árbol sin GOVERNANCE.md ni FUNDING.yml; con README, CONTRIBUTING, SECURITY, CHANGELOG, LICENSE, pyproject | E2 |
| 10 | `https://api.github.com/repos/python/typing_extensions/commits/main` | API: commit HEAD | 2026-11-02 | `"message":"Update uv to 0.13.5 (#812)"`, fecha 2026-10-23 | E1/E2 |
| 11 | `https://api.github.com/orgs/python` | API: metadatos de organización | 2026-11-02 | `"description":"Repositories related to the Python Programming language"` | E1 |
| 12 | `https://github.com/sponsors/python` | Página de patrocinio GitHub Sponsors (org `python`) | 2026-11-02 | «The capacity of the Python Software Foundation to support the development of CPython … hasn't kept pace with the growth…» / «The goal is to hire to address backlog…» | E1 (contenido de la página de la org) |
| 13 | `https://raw.githubusercontent.com/python/typing/main/README.md` | README de `python/typing` (transferencia documentada) | 2026-11-02 | «The `typing_extensions` package, which now lives in the typing_extensions repo. It used to be in the `typing_extensions` directory.» | E1 |
| 14 | `https://peps.python.org/pep-0576/` | PEP (verificación de hipótesis) | 2026-11-02 | «PEP 576 – Rationalize Built-in function classes … Status: Withdrawn» | E1 (hallazgo negativo: el PEP 576 no trata de typing_extensions) |
| 15 | `https://raw.githubusercontent.com/python/typing_extensions/cfde842014f0e05e2a09bf58fd9e2e4a20a9fdff/.github/FUNDING.yml` | Financiación (intento) | 2026-11-02 | — | E4 «no recuperada» (HTTP 404) |
| 16 | `https://raw.githubusercontent.com/kjd/idna/d357725082245ff90f5cf8800a3fc297b1f2319a/README.md` | README (raw @SHA) | 2026-11-02 | «Support for [Internationalized Domain Names in Applications (IDNA)](https://tools.ietf.org/html/rfc5891) and [Unicode IDNA Compatibility Processing](https://unicode.org/reports/tr46/).» | E1 |
| 17 | `https://raw.githubusercontent.com/kjd/idna/d357725082245ff90f5cf8800a3fc297b1f2319a/pyproject.toml` | Metadatos de proyecto (raw @SHA) | 2026-11-02 | `authors = [ {name = "Kim Davies", email = "kim+pypi@gumleaf.org"} ]` | E1 |
| 18 | `https://raw.githubusercontent.com/kjd/idna/d357725082245ff90f5cf8800a3fc297b1f2319a/SECURITY.md` | SECURITY (raw @SHA) | 2026-11-02 | «this project is maintained by a team of volunteers who work on a best effort basis.» | E1 |
| 19 | `https://raw.githubusercontent.com/kjd/idna/d357725082245ff90f5cf8800a3fc297b1f2319a/HISTORY.md` | Changelog (raw @SHA) | 2026-11-02 | «## 3.20 (2026-09-17)» / «## 3.21 (2026-XX-XX) — Raise the minimum supported Python version to 3.10» / «Thanks to stefan6419846, LouieLuNZ, and Salvatore Corvaglia for contributions to this release.» | E1 |
| 20 | `https://raw.githubusercontent.com/kjd/idna/d357725082245ff90f5cf8800a3fc297b1f2319a/tools/README.md` | Docs de herramientas (raw @SHA) | 2026-11-02 | «Generate a table of the IDNA disposition … in the format found in Appendix B.1 of RFC 5892 and the pre-computed tables published by [IANA](https://www.iana.org/).» | E1 |
| 21 | `https://raw.githubusercontent.com/kjd/idna/d357725082245ff90f5cf8800a3fc297b1f2319a/.github/workflows/deploy.yml` | Workflow de release (raw @SHA) | 2026-11-02 | «A release without a HISTORY entry is an error.» / `id-token: write # IMPORTANT: mandatory for trusted publishing` / «Sign with Sigstore» | E1/E2 |
| 22 | `https://api.github.com/repos/kjd/idna/releases?per_page=5` | API: releases (quién publica) | 2026-11-02 | v3.20 `published_at: 2026-09-17`, `author.login: "github-actions[bot]"`, artefactos `*.sigstore.json` | E1/E2 |
| 23 | `https://api.github.com/repos/kjd/idna/commits?per_page=10` | API: historial de commits | 2026-11-02 | «Merge pull request #278 from Pitchfork-and-Torch/…» (2026-10-31); «Merge pull request #283 from zydo/sweep/generator-help» (2026-10-22) | E1/E2 |
| 24 | `https://api.github.com/repos/kjd/idna` | API: metadatos de repositorio | 2026-11-02 | `"owner":{"login":"kjd"}`; `"description":"Internationalized Domain Names for Python (IDNA 2008 and UTS #46)"`; `"license":{"spdx_id":"BSD-3-Clause"}` | E1/E2 |
| 25 | `https://api.github.com/repos/kjd/idna/contents/?ref=d357725082245ff90f5cf8800a3fc297b1f2319a` | API: listado de contenidos | 2026-11-02 | Árbol sin CONTRIBUTING.md, GOVERNANCE.md ni FUNDING.yml | E2 |
| 26 | `https://github.com/sponsors/kjd` | Perfil de cuenta (afiliación declarada) | 2026-11-02 | «@icann @iana-org» (afiliación declarada en el perfil de la cuenta) | E1 (declaración de la cuenta); E4 para programa de Sponsors |
| 27 | `https://raw.githubusercontent.com/kjd/idna/d357725082245ff90f5cf8800a3fc297b1f2319a/.github/FUNDING.yml` | Financiación (intento) | 2026-11-02 | — | E4 «no recuperada» (HTTP 404) |

---

## 5. Notas metodológicas

1. **Posterioridad al corte**: todas las consultas son de 2026-11-02 > corte 2026-10-30. En particular, el HEAD de `kjd/idna` fijado (`d357725…`, 2026-10-31) es posterior al corte; los fragmentos de HISTORY/README/pyproject citados existían antes del corte salvo las entradas en desarrollo (3.21 «2026-XX-XX»), que se registran como estado al 2026-11-02.
2. **Cuentas ≠ personas**: los campos `author` de la API de GitHub, los firmantes de commits y los campos `authors` de los paquetes se citan como metadatos públicos. No se afirma equivalencia entre cuenta y persona física.
3. **Lecturas E3**: las únicas interpretaciones están rotuladas «E3 — INTERPRETACIÓN» en §1.3 y §2.4; el resto del informe es registro documental (E1/E2) o ausencia documentada (E4).
4. **Prohibiciones respetadas**: no se infiere causalidad, riesgo, abandono, remuneración ni dedicación; los hechos de §1.5 y §2.5 se presentan como registros que matizan o refuerzan descriptivamente una lectura, no como juicios sobre continuidad futura.
