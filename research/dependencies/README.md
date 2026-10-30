# Congelación del entorno Python del backend de producción — «fotografía del entorno»

> **Paso 1 del protocolo de investigación.** Rama `research/freeze-python-env` (desde `dev`).
>
> El resultado es una **fotografía del entorno** (environment snapshot) verificable,
> **no** un archivo de bloqueo reproducible. Véase
> [Qué falta para un lock](#qué-falta-para-convertir-esto-en-un-lock-reproducible).

## Qué se congeló

La imagen **production** del backend, tal como la define el repositorio:

- `api/Dockerfile`, target `production`: `FROM python:3.12-slim` + `pip install .`
  (tras `pip install --upgrade pip setuptools wheel`).
- Es exactamente el build que define `docker-compose.prod.yml` para el servicio
  `api` (contexto `./api`, target `production`). El `docker compose ... build`
  de producción no necesita `.env.production` porque `env_file` solo se usa al
  ejecutar el contenedor, no al construir la imagen.
- El inventario se extrajo ejecutando **`python -m pip inspect`** dentro de la
  imagen construida, y se clasificó contra el `pyproject.toml` que la propia
  imagen contiene en `/app/pyproject.toml`.

## Archivos

| Archivo | Contenido |
|---|---|
| `extract_env_snapshot.sh` | Script que reconstruye la imagen y reextrae todo el snapshot (idempotente). |
| `categorize_env.py` | Clasificador del inventario; corre dentro de la imagen, con los artefactos intercambiados vía `docker cp` (sin bind mounts). |
| `pip-inspect.json` | Inventario JSON original de `python -m pip inspect` (41 paquetes instalados). |
| `installed-packages.txt` | Lista legible de nombres y versiones agrupados por categoría. |
| `manifest.json` | Metadatos: commit SHA, fecha UTC, plataforma, versiones de Python y pip, comando de construcción, digest de la imagen base, ID de la imagen construida, conteos por categoría. |
| `SHA256SUMS` | Hashes SHA-256 de todos los artefactos de la carpeta (no se incluye a sí mismo). |

## Categorías del inventario

| Categoría | Significado |
|---|---|
| `project:package` | `deudamundi-api`: el paquete del proyecto, instalado por `pip install .`. |
| `runtime:direct` | Las 10 dependencias declaradas en `api/pyproject.toml → [project.dependencies]`. |
| `runtime:transitive` | Resueltas por pip en build-time; la lista indica las dependencias directas que las alcanzan en el grafo activo (extras incluidos: p. ej. `uvicorn[standard]` arrastra `uvloop`, `watchfiles`, `websockets`, `httptools`, `pyyaml`, `python-dotenv`; `psycopg[binary]` arrastra `psycopg-binary`). |
| `build:tooling` | `pip`, `setuptools` y `wheel`, actualizados explícitamente en el `RUN` del `api/Dockerfile` (`pip install --upgrade pip setuptools wheel`). |

El extra `dev` (`pytest`, `pytest-cov`, `ruff`, `locust`) **no se instala** en el
target `production`; el clasificador lo comprueba y lo declara en el archivo
legible (`dev-extra metadata present in installed env: none`).

## Cómo repetir la extracción

Desde la raíz del repositorio, sobre el commit que quieras fotografiar:

```bash
./research/dependencies/extract_env_snapshot.sh
```

Requisito: Docker instalado (>= 20.10) con acceso de red a Docker Hub en el
primer build. Para usar otro tag de imagen local:

    SNAPSHOT_TAG=deudamundi-api:otro-tag ./research/dependencies/extract_env_snapshot.sh

El script: (1) ejecuta `docker build -f api/Dockerfile --target production`;
(2) guarda `python -m pip inspect` como JSON; (3) clasifica el inventario con
`categorize_env.py`; (4) recopila metadatos de build/runtime en `manifest.json`;
(5) recalcula `SHA256SUMS`. Reejecutarlo reemplaza los artefactos con un
snapshot del build (cacheado) disponible en ese momento.

## Qué falta para convertir esto en un lock reproducible

Una fotografía describe **una** construcción en **una** fecha concreta; no
reconstruirá bit-idénticamente. Para eso hacen falta:

1. **Archivo de bloqueo con digests** (`uv lock` / `pip-compile --generate-hashes`
   en `api/`), con nombre+versión+artefacto (SHA-256 de cada wheel/sdist)
   comprometido al repositorio. Codifica la resolución original exacta.
2. **Digest de la imagen base fijado** (`FROM python:3.12-slim@sha256:<digest>`).
   El digest aquí documentado se resolvió del registry al extraer el snapshot,
   pero sin `@sha256` un re-push futuro de `python:3.12-slim` cambia el entorno.
3. **Eliminación de la resolución en build-time**: `pip install .` resuelve
   dependencias en el build; la sustitución por `uv sync` / `pip install
   --no-deps` sobre los artefactos del lock hace indispensable que el lock
   exista y que sea compartido entre desarrollo e imagen.
4. **Verificación de round-trip en CI**: reconstruir la imagen y comparar el
   `pip inspect` resultante (o `pip list`) con este snapshot.

Por ahora se documenta el build concreto; los rangos semver declarados en
`pyproject.toml` siguen intactos y **no hay promesa de reconstrucción
idéntica**: distintas corridas del mismo commit resuelven versiones nuevas
que aparezcan dentro de los rangos declarados, y `pip install .` vuelve a
resolver en cada build sin pin de artefactos.

## Verificación

- El snapshot fue ejecutado sobre `dev` en el commit documentado;
  `manifest.json` conserva commit SHA, digest de la imagen base, ID de la
  imagen construida y fecha UTC.
- Dentro del entorno aislado de la imagen se verificó que las 10 dependencias
  de runtime declaradas importan correctamente (`import fastapi, uvicorn, ...`
  → `runtime imports OK`).
- El clasificador verifica dentro de la propia imagen que las dependencias del
  extra `dev` no están instaladas en el target de producción
  (`dev-extra metadata present in installed env: none`).
- `pip inspect` produjo salida **byte-idéntica en dos ejecuciones separadas**
  contra la misma imagen; `pip list` reporta las mismas 41 distribuciones.
- `sha256sum -c SHA256SUMS` valida los artefactos.

### Matiz sobre el ID de la imagen

El builder (Docker 29 con containerd y attestations de provenance) reexporta
el manifest list del tag local en cada operación, por lo que el `image.id`
registrado en `manifest.json` puede no coincidir con el que reporte un
`docker image inspect` posterior. Las capas y el contenido (`pip inspect`,
versiones instaladas) permanecen idénticos; el ID documentado corresponde al
momento exacto de la extracción.
