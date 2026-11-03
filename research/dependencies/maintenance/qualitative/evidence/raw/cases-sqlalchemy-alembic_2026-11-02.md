# Evidencia documental web — `sqlalchemy/sqlalchemy` y `sqlalchemy/alembic`

- **Fecha de consulta:** 2026-11-02 (TODAS las fuentes son **posteriores al corte de datos congelados 2026-10-30**; registrar como "consulta post-corte").
- **Ámbito:** recopilación de fuentes verificables para el estudio de caso «DeudaMundi» (mantenimiento de software Open Source). Este documento **no contiene conclusiones**; solo fuentes, fragmentos textuales y clasificación de evidencia.
- **Niveles de evidencia:**
  - **E1** = documental directa (política/documentación oficial del proyecto, roles declarados en su documentación).
  - **E2** = observación técnica (registro público observable: metadatos de API, historial de commits, etiquetas de rol de la plataforma).
  - **E3** = inferencia contextual (interpretación; se marca explícitamente como tal).
  - **E4** = no verificable / no recuperado.
- **Advertencias de método (obligatorias):**
  - No se identifica una cuenta de GitHub con una persona. Donde la documentación nombra "Mike Bayer"/"Michael Bayer" y una cuenta (`zzzeek`, `CaselIT`, …) muestra un rol, ambos hechos se registran por separado.
  - No se infieren salarios, dedicación, empleo ni causalidad. La única mención a remuneración (libraries.io/Tidelift) se cita como texto de un tercero, sin validar.
  - Los SHAs de commit permiten fijar versiones de los archivos raw de GitHub. HEAD observados el 2026-11-02: `sqlalchemy/sqlalchemy@57ddc05ffafeec2ea81237dcdf51a0ac02fb589b` (fecha de commit 2026-11-02, posterior al corte) y `sqlalchemy/alembic@1bcba93ea0473c69b48e704f842ca96e9e5348f5` (2026-10-27).

---

## REPOSITORIO 1 — `sqlalchemy/sqlalchemy`

### 1. Gobernanza

**1.1 Propietario público.** La organización GitHub `sqlalchemy` (tipo `Organization`, "The Database Toolkit and Object Relational Mapper", `is_verified: true`) es la propietaria del repositorio. Fuente: API GitHub `GET /orgs/sqlalchemy` y `GET /repos/sqlalchemy/sqlalchemy` (E2).

**1.2 Política de contribución y aceptación de cambios (PR obligatorio con etiqueta previa; nada de push directo desde contribuidores externos).**
- `.github/CONTRIBUTING.md` (SHA-pinned, E1):
  > "**We accept pull requests only for issues that a maintainer has marked with the `open for pull requests` label.** A pull request that doesn't reference such an issue is closed automatically, by a bot, as soon as it's opened."
  > "This applies to documentation and typo fixes too."
  > Tabla de etiquetas: `open for pull requests`, `code review in progress`, `NO pull requests please`.
- `https://www.sqlalchemy.org/develop.html` (E1):
  > "The SQLAlchemy project and its related projects Alembic, Mako, dogpile.cache accept PRs only on a **limited, pre-approved basis**."
  > "Once accepted for review … code review occurs within our Gerrit system at https://gerrit.sqlalchemy.org … The pull request will be closed with a link to the review in Gerrit. **Pull requests for code changes are never merged directly.**"

**1.3 Autoridad de merge.** Revisión en Gerrit propio del proyecto. `.gitreview` (SHA-pinned, E1):
> "[gerrit]\nhost=ssh.gerrit.sqlalchemy.org\nproject=sqlalchemy/sqlalchemy\ndefaultbranch=main"

E2 complementario (observable): los commits de `main` tienen como committer "Gerrit Code Review" (p. ej. `57ddc05ffa`, `24c2817c05`, 2026-11-02) o cuentas del proyecto; en hilos públicos de PR se observan votaciones Gerrit del estilo "Code-Review+2 Workflow+2" por la cuenta `zzzeek` (hilo del PR #5480). No se localizó documento que designe por escrito quién posee derechos de merge (E4 sobre "designación formal").

**1.4 CLA.** No se localizó CLA ni DCO documentado en el árbol del repositorio (README, CONTRIBUTING, `.github/`, `doc/`) ni en la Community Guide (E4: no localizado). Sí existe política explícita sobre IA/bots en CONTRIBUTING.md (E1):
> "we must ask that **AI/LLM generated content is not spammed onto SQLAlchemy discussions, issues, or PRs** … **users who post content that appears to be trolling for karma / upvotes / vanity commits … will be banned**."

**1.5 Política de seguridad.** `.github/SECURITY.md` (SHA-pinned, E1):
> "SQLAlchemy participates in the Tidelift security infrastructure for reporting potential vulnerabilities reponsibly. Please follow the guidelines at: https://tidelift.com/docs/security … we would ask that you please do not file CVEs without emailing us first, so that proper disclosure steps may be taken."

`participate.html` añade (E1): "there have only been three CVEs reported in a fourteen year period".

**1.6 Publicación de versiones (proceso de release).**
- Política de versionado documentada en `https://www.sqlalchemy.org/download.html` (E1): "All projects within the SQLAlchemy Organization use the same version numbering scheme … a modified 'semantic versioning' scheme"; tabla "Release Status" con categorías Development/Beta/Current Release/Maintenance/EOL; "The 2.0 series is the current 'Maintenance' series".
- Firma de releases (E1): "SQLAlchemy 2.1.6 is signed using Michael Bayer's PGP key id **C4DAFEE1**".
- Mecánica de publicación descrita públicamente por cuenta con etiqueta "Maintainer" (`CaselIT`) en Discussion #13324 (E2 — declaración observable en el repositorio oficial):
  > "mike pushes the tar.gz to pypi and makes the GitHub release that starts the pipeline - the pure python wheel will start and upload in a couple of minutes … the per-platform wheels then come a couple of hours later"
- Observación (E2): todas las GitHub Releases recientes figuran publicadas por la cuenta `sqla-tester` (p. ej. `rel_2_1_6`, 2026-10-21T16:25:11Z; assets subidos por `github-actions[bot]`).
- No se localizó un "RELEASING.md" o runbook de release en el árbol del repositorio (E4: proceso no documentado en archivo dedicado; la descripción está en la Discussion #13324 y en `download.html`).

**1.7 Mecanismos de sucesión / relevo.** No se localizó ningún documento de sucesión, relevo o continuidad (GOVERNANCE, succession plan, etc.) (E4). Únicos indicios documentales:
- CODE_OF_CONDUCT (web + `.github/CODE_OF_CONDUCT.md`, E1): "Project maintainers who do not follow or enforce the Code of Conduct in good faith may face temporary or permanent repercussions as determined by **other members of the project's leadership**." (menciona un "leadership" sin definir composición).
- Statement público de la cuenta `zzzeek` en Discussion #11553 (E2, cita textual; sin atribución de identidad):
  > "noting, I've been in this community since 2005. I have seen lots of very big, very major projects go dormant, seen some of them come back, others not. **nothing is forever**, but having a large legacy/dormant project on your hands is a major inconvenience."

### 2. Roles nombrados

- `AUTHORS` (SHA-pinned, E1): "SQLAlchemy was created by **Michael Bayer**. Major contributing authors include:" [lista de 26 nombres, entre ellos "Mike Bayer", "Federico Caselli", "Gord Thompson", "Jonathan Vanasco", …].
- `pyproject.toml` (SHA-pinned, E1): `authors = [{name = "Mike Bayer", email = "mike_mp@zzzcomputing.com"}]`. No hay campo `maintainers`.
- PyPI (página renderizada de SQLAlchemy 2.1.6, E2): panel "SQLAlchemy **2 maintainers** … CaselIT zzzeek" y "Credits Author: **Mike Bayer**" ("Data sourced directly from PyPI's database").
- Miembros públicos de la organización GitHub (`GET /orgs/sqlalchemy/public_members`, E2): `bourke`, `CaselIT`, `gordthompson`, `jvanasco`, `zzzeek`.
- Etiqueta de rol de plataforma (E2): en Discussions del repo, las cuentas `zzzeek` y `CaselIT` aparecen con la etiqueta **"Maintainer"** (ver Discussion #11553 y #13324).
- Declaración de roles en hilo oficial (Discussion #11553, 2024-07-01, E2 — declaración de una cuenta, no verificación de identidad):
  > "myself and [@CaselIT] are the maintainers of every project under the 'sqlalchemy' organization and all of them are basically my own projects."
  > "it's more analogous to pallets - a collection of projects that originated with the same developer. this is only because as mentioned, me and @CaselIT are mostly it for now and **sqlalchemy org itself / infra I do most of that personally**."

### 3. Financiación declarada

- `.github/FUNDING.yml` (SHA-pinned, E1):
  > "github: sqlalchemy\npatreon: zzzeek\ntidelift: \"pypi/SQLAlchemy\""
- Web oficial, barra lateral "Sponsor SQLAlchemy!" (todas las páginas de sqlalchemy.org, E1): "Donate to SQLAlchemy through **PayPal**" y "Sponsor SQLAlchemy through the **Tidelift Subscription**" (enlace a `tidelift.com/subscription/pkg/pypi-sqlalchemy`).
- GitHub Sponsors para la organización: `https://github.com/sponsors/sqlalchemy` devuelve perfil de sponsors activo (E2: `og:title` = "Sponsor @sqlalchemy on GitHub Sponsors"; botón de patrocinio presente). `https://github.com/sponsors/alembic` y `https://github.com/sponsors/zzzeek` resuelven a páginas de perfil **sin** botón de Sponsors observado (E2: FUNDING.yml los declara, pero no se observó perfil de Sponsors activo para esas cuentas).
- Participación en Tidelift (E1, SECURITY.md y develop.html, ya citados).
- Tercero (E2 — texto observable en biblioteca de tercero, **no** declaración del proyecto; sin validar): `https://libraries.io/pypi/SQLAlchemy` muestra el texto estándar de paquetes gestionados por Tidelift:
  > "The maintainers of this project get paid by Tidelift to make sure it meets pre-defined standards around security, maintenance and licensing."
- **No se localizó** ninguna declaración del propio proyecto sobre empresas que empleen a mantenedores. Única mención genérica a empleadores, CONTRIBUTING.md (E1): "Some of us here use large language models (LLM) to help us with our work, and **some of us are even employer mandated to do so**." (no nombra empresas ni personas).
- No recuperado (E4): el contenido de la página `https://tidelift.com/subscription/pkg/pypi-sqlalchemy` no se verificó — la petición devuelve contenido con la marca "Sonar" (adquisición/ transición Tidelift→Sonar anunciada en libraries.io: "Sonar has entered a definitive agreement to acquire Tidelift!"), sin el texto del paquete.

### 4. Continuidad

Historial de releases GitHub (API `/releases`, E2; publicadas por cuenta `sqla-tester`): 2.1.6 (2026-10-21), 2.1.5 (2026-10-16), 2.0.55 (2026-10-16), 2.1.4 (2026-10-07), 2.1.3 (2026-10-02), 2.1.2 (2026-10-02), 2.1.1 (2026-09-25), 2.1.0 (2026-09-24), 2.0.54 (2026-09-15), 2.0.53 (2026-09-14), 2.1.0rc2 (2026-09-08), 2.1.0rc1 (2026-08-31), 2.0.52 (2026-08-11), 2.1.0b3 (2026-06-27). Fragmento de release notes 2.1.6 (E2): "Released: October 21, 2026 … **[orm] [bug]** Fixed issue where a `Session` flush that replaced an expired object in the identity map …".

Actividad de commits posterior al corte (E2, observación directa): cuatro merge commits en `main` vía Gerrit con fecha 2026-11-02 (entre ellos `57ddc05ffa` "Merge \"raise for differing of_type() targets on same relationship\" into main"), autor `zzzeek`, committer "Gerrit Code Review".

Cambios organizacionales/proceso observados en 2026 (Discussion #13324, mayo-junio 2026, E2): debate público sobre Trusted Publishing/PyPI attestations que modifica el flujo de publicación (pipeline `create-wheels.yaml`, atestaciones `pypi-attestations`); PR #13331 vinculado. Fragmento (`zzzeek`, "Maintainer"): "our source build is uploaded via twine from shell scripts I run locally. Looking, it looks like I have a .pypirc with a token as well for the local twine."

Transferencias de responsabilidad documentadas: **ninguna localizada** (E4).

### 5. CONTRAEVIDENCIA

**Debilitan la lectura de «un solo mantenedor»:**
- Dos cuentas con rol "Maintainer" activas y declaradas (`zzzeek`, `CaselIT`) en la documentación de discusión oficial (E1/E2, citadas arriba).
- Cinco miembros públicos de la organización (E2).
- Procesos formales extensos: CONTRIBUTING.md con política de PR, CODE_OF_CONDUCT.md, SECURITY.md, `.gitreview` + revisión en Gerrit con votos (Code-Review/Workflow), CI, `pre-commit`, `noxfile.py`, política de versionado/EOL documentada en `download.html`, etiquetas de triage (E1/E2).
- Comunidad de contribución observable: en commits desde 2026-08-01 (muestra de 100, API GitHub, E2) aparecen 15 cuentas autoras distintas (`zzzeek` 80, `CaselIT` 7, y 13 cuentas con 1 commit cada una) y committers variados ("Gerrit Code Review" 34, `zzzeek` 54, `CaselIT` 3, `sqla-tester` 2, `web-flow` 7).
- Métricas de terceros (E3 — inferencia de terceros, no verificada por este estudio): GitStats "Bus Factor 1 … Michael Bayer is primary owner of 793 of 927 files"; inspect.software "Bus factor — 1 contributor(s) cover half of all commits … top contributor authored 84% of commits … 99 contributors"; Linux Foundation Insights afirma "11 active maintainers with merge rights" (esta última cifra **contradice** las demás fuentes; E4 para su verificación).

**Refuerzan la lectura de concentración (no trivial):**
- La misma declaración que nombra dos mantenedores añade "sqlalchemy org itself / infra I do most of that personally" y "me and @CaselIT are mostly it for now" (E2, Discussion #11553).
- Distribución de autoría reciente: 80/100 commits desde 2026-08-01 con autor `zzzeek` (E2).
- Firma de releases con una única llave PGP declarada ("Michael Bayer's PGP key id C4DAFEE1", E1) y subida de sdist "via twine from shell scripts I run locally" según declaración de la cuenta `zzzeek` (E2, #13324).
- Campo `authors` singular en `pyproject.toml` y "Alembic/SQLAlchemy was created by …" en AUTHORS/README (E1).

---

## REPOSITORIO 2 — `sqlalchemy/alembic`

### 1. Gobernanza

**1.1 Propietario público.** Misma organización `sqlalchemy`. Documentado en docs oficiales, `front.html` (E1):
> "Alembic is hosted on GitHub at [sqlalchemy/alembic](https://github.com/sqlalchemy/alembic) **under the SQLAlchemy organization**."

**1.2 Contribución / aceptación de cambios.** Los documentos de gobernanza son **idénticos** a los de sqlalchemy (mismos blob SHA en GitHub: `CONTRIBUTING.md` = `9ee6682edc33ef307fe629b3523279e6d36ba7a2`; `CODE_OF_CONDUCT.md` = `27395431b19bbb56bd1c2b4a2f93a5b1e477a1cf` en ambos repos — E2). El texto de CONTRIBUTING.md comienza incluso "# Contributing to SQLAlchemy" y enlaza a `https://www.sqlalchemy.org/develop.html` (E1). La Community Guide aclara su ámbito (E1):
> "While these sections may be written to address developers of the core SQLAlchemy project, the various guidelines, especially the Code of Conduct, **apply to all projects hosted under the SQLAlchemy organization's repository**."

**1.3 Autoridad de merge.** `.gitreview` (SHA-pinned, E1):
> "[gerrit]\nhost=ssh.gerrit.sqlalchemy.org\nproject=sqlalchemy/alembic\ndefaultbranch=main\nport=29418"

Observación (E2): commits recientes con committer "Gerrit Code Review" (p. ej. `a914c9dc34`, 2026-10-21) y commits con pie `Change-Id:`; PRs externos se integran vía Gerrit con trailers verificables (ejemplo en el commit de cierre del issue #1683, visible en el hilo público: "Pull-request: sqlalchemy/alembic#1683 / Pull-request-sha: 46d03fb… / Change-Id: I4071e069…"; mensaje del bot "Gerrit review … has been merged"). El README de alembic además se describe a sí mismo (E1): "Alembic is a database migrations tool **written by the author of `SQLAlchemy`**."

**1.4 CLA.** No localizado (E4), misma situación que sqlalchemy.

**1.5 Seguridad.** `.github/SECURITY.md` (SHA-pinned, E1):
> "SQLAlchemy participates in the Tidelift security infrastructure for reporting potential vulnerabilities reponsibly. Please follow the guidelines at: https://tidelift.com/docs/security in order to report a security issue."

(versión más corta que la de sqlalchemy: sin tabla de versiones soportadas ni mención de CVEs).

**1.6 Publicación de versiones.** `front.html` (E1): "Releases and project status are available on Pypi at https://pypi.python.org/pypi/alembic". Esquema de versionado documentado (E1): "it **does not use SemVer** … the middle digit is considered to be a 'Significant Minor Release'". Observación (E2): releases publicadas por la cuenta `sqla-tester` (rel_1_20_1, 2026-10-22T03:24:42Z) y commits de preparación de release por la cuenta `zzzeek` ("- 1.20.1" 2026-10-22; "Version 1.20.2 placeholder" 2026-10-22).

**1.7 Sucesión / relevo.** Ningún mecanismo documentado localizado (E4). `front.html` declara autoría individual (E1): "**Alembic is developed by [Mike Bayer], and is part of the [SQLAlchemy] project.**"

### 2. Roles nombrados

- `pyproject.toml` (SHA-pinned, E1): `authors = [{name = "Mike Bayer", email = "mike_mp@zzzcomputing.com"}]`; sin campo `maintainers`.
- Docs oficiales, pie de página (E1): "By Mike Bayer — © Copyright 2010-2026, Mike Bayer."
- README.rst (SHA-pinned, E1): "written by the author of SQLAlchemy".
- Etiquetas de rol de plataforma (E2): en issues/PRs del repo `sqlalchemy/alembic`, las cuentas `zzzeek` y `CaselIT` aparecen con etiqueta "Maintainer" (p. ej. issue #1683, 2025-06); la cuenta `sqla-tester` actúa como "Collaborator" puente hacia Gerrit.
- No hay archivo AUTHORS en alembic (E2: listado de raíz del repo).

### 3. Financiación declarada

- `.github/FUNDING.yml` (SHA-pinned, E1):
  > "github: alembic\npatreon: zzzeek\ntidelift: \"pypi/SQLAlchemy\""
- El Tidelift referenciado es el mismo paquete `pypi/SQLAlchemy` (E1). No hay página de sponsors propia de alembic; `https://github.com/sponsors/alembic` resuelve a perfil de organización sin botón de Sponsors observado (E2).
- No se localizó declaración de empresas empleadoras (E4).

### 4. Continuidad

Historial de releases GitHub (API, E2): 1.20.1 (publicada 2026-10-22; "Released: October 21, 2026"), 1.20.0 (2026-09-11), 1.19.2 (2026-09-04), 1.19.1 (2026-08-08), 1.19.0 (2026-08-04), 1.18.5 (2026-06-25), 1.18.4 (2026-02-10), 1.18.3 (2026-01-29), 1.18.2 (2026-01-28), 1.18.1 (2026-01-14), 1.18.0 (2026-01-09). Fragmento release 1.20.1 (E2):
> "Fixed issue where a table or column comment set to an empty string would cause autogenerate to detect a comment change on every run … Pull request courtesy vineoy."

Actividad (E2): último commit en `main` = `1bcba93ea0` (2026-10-27, autor/committer `zzzeek`, con `Change-Id:`); **sin commits entre 2026-10-27 y la consulta 2026-11-02**. El commit "Version 1.20.2 placeholder" (2026-10-22) indica preparación declarativa de la siguiente versión.

Transferencias de responsabilidad documentadas: **ninguna localizada** (E4).

### 5. CONTRAEVIDENCIA

**Debilitan «un solo mantenedor»:** gobernanza compartida y formal con sqlalchemy (mismos blobs de CONTRIBUTING/CODE_OF_CONDUCT — E2); dos cuentas con rol "Maintainer" activas en 2025-2026 (`zzzeek`, `CaselIT`); contribuciones externas aceptadas y acreditadas en el changelog ("Pull request courtesy vineoy", release 1.20.1; commits de `cycsmail`, `vineoy`, `bjorkbjork` — E2); revisión Gerrit con CI.

**Refuerzan concentración:** autoría del README y de la documentación en singular ("written by the author of SQLAlchemy"; "Alembic is developed by [Mike Bayer]" — E1); de 48 commits desde 2026-08-01, 38 con autor `zzzeek` y 38 con committer `zzzeek` (E2); campo `authors` singular en `pyproject.toml`; releases y "version placeholder" emitidos por la cuenta `zzzeek`, publicados por la cuenta `sqla-tester` (E2).

---

## Tabla final de fuentes

| # | URL | Tipo | Fecha consulta | Fragmento textual (corta) | Nivel E |
|---|-----|------|----------------|---------------------------|---------|
| 1 | https://raw.githubusercontent.com/sqlalchemy/sqlalchemy/57ddc05ffafeec2ea81237dcdf51a0ac02fb589b/.github/CONTRIBUTING.md | CONTRIBUTING (SHA-pinned) | 2026-11-02 | "We accept pull requests only for issues that a maintainer has marked with the `open for pull requests` label." | E1 |
| 2 | https://raw.githubusercontent.com/sqlalchemy/sqlalchemy/57ddc05ffafeec2ea81237dcdf51a0ac02fb589b/.github/SECURITY.md | SECURITY policy (SHA-pinned) | 2026-11-02 | "SQLAlchemy participates in the Tidelift security infrastructure for reporting potential vulnerabilities reponsibly." | E1 |
| 3 | https://raw.githubusercontent.com/sqlalchemy/sqlalchemy/57ddc05ffafeec2ea81237dcdf51a0ac02fb589b/.github/FUNDING.yml | Financiación (SHA-pinned) | 2026-11-02 | "github: sqlalchemy / patreon: zzzeek / tidelift: \"pypi/SQLAlchemy\"" | E1 |
| 4 | https://raw.githubusercontent.com/sqlalchemy/sqlalchemy/57ddc05ffafeec2ea81237dcdf51a0ac02fb589b/.gitreview | Config de revisión Gerrit (SHA-pinned) | 2026-11-02 | "host=ssh.gerrit.sqlalchemy.org … project=sqlalchemy/sqlalchemy … defaultbranch=main" | E1 |
| 5 | https://raw.githubusercontent.com/sqlalchemy/sqlalchemy/57ddc05ffafeec2ea81237dcdf51a0ac02fb589b/AUTHORS | AUTHORS (SHA-pinned) | 2026-11-02 | "SQLAlchemy was created by Michael Bayer. Major contributing authors include:" | E1 |
| 6 | https://raw.githubusercontent.com/sqlalchemy/sqlalchemy/57ddc05ffafeec2ea81237dcdf51a0ac02fb589b/pyproject.toml | Metadatos de paquete (SHA-pinned) | 2026-11-02 | `authors = [{name = "Mike Bayer", email = "mike_mp@zzzcomputing.com"}]` | E1 |
| 7 | https://raw.githubusercontent.com/sqlalchemy/sqlalchemy/57ddc05ffafeec2ea81237dcdf51a0ac02fb589b/README.rst | README (SHA-pinned) | 2026-11-02 | "The Python SQL Toolkit and Object Relational Mapper" | E1 |
| 8 | https://www.sqlalchemy.org/develop.html | Guía de desarrollo oficial | 2026-11-02 | "Pull requests for code changes are never merged directly." / "accept PRs only on a limited, pre-approved basis" | E1 |
| 9 | https://www.sqlalchemy.org/participate.html | Guía comunitaria | 2026-11-02 | "there have only been three CVEs reported in a fourteen year period" | E1 |
| 10 | https://www.sqlalchemy.org/download.html | Política de versiones/releases | 2026-11-02 | "SQLAlchemy 2.1.6 is signed using Michael Bayer's PGP key id C4DAFEE1" / tabla "Release Status" | E1 |
| 11 | https://www.sqlalchemy.org/codeofconduct.html | CODE_OF_CONDUCT | 2026-11-02 | "…may face temporary or permanent repercussions as determined by other members of the project's leadership." | E1 |
| 12 | https://github.com/sqlalchemy/sqlalchemy/discussions/11553 | Discussion oficial (roles) | 2026-11-02 | "myself and @CaselIT are the maintainers of every project under the \"sqlalchemy\" organization" (cuenta `zzzeek`, rol "Maintainer") | E2 |
| 13 | https://github.com/sqlalchemy/sqlalchemy/discussions/13324 | Discussion oficial (release/CI) | 2026-11-02 | "mike pushes the tar.gz to pypi and makes the GitHub release that starts the pipeline" (cuenta `CaselIT`, rol "Maintainer") | E2 |
| 14 | https://api.github.com/orgs/sqlalchemy/public_members | API GitHub (roles públicos) | 2026-11-02 | `bourke`, `CaselIT`, `gordthompson`, `jvanasco`, `zzzeek` | E2 |
| 15 | https://api.github.com/repos/sqlalchemy/sqlalchemy/releases | API GitHub (releases) | 2026-11-02 | `rel_2_1_6` publicada 2026-10-21T16:25:11Z por cuenta `sqla-tester` | E2 |
| 16 | https://api.github.com/repos/sqlalchemy/sqlalchemy/commits?since=2026-08-01 | API GitHub (actividad) | 2026-11-02 | merges vía "Gerrit Code Review" con fecha 2026-11-02; 80/100 commits con autor `zzzeek` (muestra) | E2 |
| 17 | https://pypi.org/project/SQLAlchemy/ | PyPI (metadatos renderizados) | 2026-11-02 | "SQLAlchemy 2 maintainers … CaselIT zzzeek / Credits Author: Mike Bayer" | E2 |
| 18 | https://github.com/sponsors/sqlalchemy | GitHub Sponsors (organización) | 2026-11-02 | og:title "Sponsor @sqlalchemy on GitHub Sponsors" (perfil de sponsors observado) | E2 |
| 19 | https://github.com/sponsors/alembic · https://github.com/sponsors/zzzeek | GitHub Sponsors (cuentas) | 2026-11-02 | Resuelven a perfiles sin botón de Sponsors observado pese a constar en FUNDING.yml | E2 |
| 20 | https://libraries.io/pypi/SQLAlchemy | Tercero (libraries.io) | 2026-11-02 | "The maintainers of this project get paid by Tidelift to make sure it meets pre-defined standards around security, maintenance and licensing." (texto de tercero, sin validar) | E2 (afirmación de tercero) |
| 21 | https://raw.githubusercontent.com/sqlalchemy/alembic/1bcba93ea0473c69b48e704f842ca96e9e5348f5/README.rst | README alembic (SHA-pinned) | 2026-11-02 | "Alembic is a database migrations tool written by the author of `SQLAlchemy`." | E1 |
| 22 | https://raw.githubusercontent.com/sqlalchemy/alembic/1bcba93ea0473c69b48e704f842ca96e9e5348f5/pyproject.toml | Metadatos alembic (SHA-pinned) | 2026-11-02 | `authors = [{name = "Mike Bayer", email = "mike_mp@zzzcomputing.com"}]` | E1 |
| 23 | https://raw.githubusercontent.com/sqlalchemy/alembic/1bcba93ea0473c69b48e704f842ca96e9e5348f5/.github/SECURITY.md | SECURITY alembic (SHA-pinned) | 2026-11-02 | "SQLAlchemy participates in the Tidelift security infrastructure…" | E1 |
| 24 | https://raw.githubusercontent.com/sqlalchemy/alembic/1bcba93ea0473c69b48e704f842ca96e9e5348f5/.github/FUNDING.yml | Financiación alembic (SHA-pinned) | 2026-11-02 | "github: alembic / patreon: zzzeek / tidelift: \"pypi/SQLAlchemy\"" | E1 |
| 25 | https://raw.githubusercontent.com/sqlalchemy/alembic/1bcba93ea0473c69b48e704f842ca96e9e5348f5/.gitreview | Gerrit alembic (SHA-pinned) | 2026-11-02 | "project=sqlalchemy/alembic … defaultbranch=main … port=29418" | E1 |
| 26 | https://raw.githubusercontent.com/sqlalchemy/alembic/1bcba93ea0473c69b48e704f842ca96e9e5348f5/.github/CONTRIBUTING.md | CONTRIBUTING alembic (SHA-pinned) | 2026-11-02 | Idéntico al de sqlalchemy (mismo blob SHA `9ee6682…`) | E1 |
| 27 | https://alembic.sqlalchemy.org/en/latest/front.html | Docs oficiales alembic | 2026-11-02 | "Alembic is developed by [Mike Bayer], and is part of the [SQLAlchemy] project." / "under the SQLAlchemy organization" | E1 |
| 28 | https://api.github.com/repos/sqlalchemy/alembic/releases | API GitHub (releases alembic) | 2026-11-02 | `rel_1_20_1` publicada 2026-10-22T03:24:42Z por `sqla-tester`; "Pull request courtesy vineoy." | E2 |
| 29 | https://api.github.com/repos/sqlalchemy/alembic/commits?since=2026-08-01 | API GitHub (actividad alembic) | 2026-11-02 | 38/48 commits con autor `zzzeek`; último commit 2026-10-27; commits con `Change-Id:` | E2 |
| 30 | https://github.com/sqlalchemy/sqlalchemy/pull/5480 (hilo) | PR/registro público Gerrit | 2026-11-02 | "mike bayer (zzzeek) wrote: Code-Review+2 Workflow+2 … merge at will" | E2 |
| 31 | https://shenxianpeng.dev/gitstats/gallery/sqlalchemy/ownership.html | Tercero (GitStats) | 2026-11-02 | "Bus Factor 1 — Michael Bayer is primary owner of 793 of 927 files" | E3 (inferencia de tercero) |
| 32 | https://inspect.software/software/sqlalchemy/sqlalchemy | Tercero (inspect.software) | 2026-11-02 | "Bus factor — 1 contributor(s) cover half of all commits … top contributor authored 84%" | E3 (inferencia de tercero) |
| 33 | https://insights.linuxfoundation.org/project/sqlalchemy | Tercero (LF Insights) | 2026-11-02 | "11 active maintainers with merge rights" (contradice fuentes 12/14/17; no verificada) | E3/E4 |
| 34 | https://tidelift.com/subscription/pkg/pypi-sqlalchemy | Página de patrocinio Tidelift | 2026-11-02 | **No recuperada**: el contenido servido corresponde a la marca "Sonar" (transición Tidelift→Sonar); sin texto del paquete | E4 (no recuperada) |
| 35 | https://pypi.org/project/alembic/ | PyPI alembic | 2026-11-02 | Página recuperada; panel de "maintainers" no localizado en el contenido extraído | E4 (parcial) |
| 36 | (búsqueda en árbol de ambos repos + Community Guide) | GOVERNANCE / CLA / succession plan | 2026-11-02 | No se localizó GOVERNANCE.md, CLA/DCO ni documento de sucesión en `sqlalchemy/sqlalchemy` ni `sqlalchemy/alembic` | E4 (no localizado) |

---

## Notas de integridad

- SHAs de fijación: `sqlalchemy/sqlalchemy@57ddc05ffafeec2ea81237dcdf51a0ac02fb589b` (HEAD observado 2026-11-02; el propio commit es posterior al corte 2026-10-30) y `sqlalchemy/alembic@1bcba93ea0473c69b48e704f842ca96e9e5348f5` (HEAD observado 2026-11-02; commit de 2026-10-27).
- Los datos de releases/actividad se recuperaron el 2026-11-02 vía API de GitHub y por tanto son **registros de consulta post-corte**, aunque muchos eventos sean anteriores al corte.
- No se realiza ninguna afirmación de causalidad, riesgo, abandono o remuneración; las menciones de terceros a pagos (libraries.io/Tidelift) y a "bus factor" (GitStats, inspect.software, LF Insights) se registran como texto o métrica de terceros, sin adoptarlas como hechos del estudio.
