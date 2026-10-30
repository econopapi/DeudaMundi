# Atribución de repositorios fuente de las 37 dependencias de ejecución — paso 3

> **Paso 3 del protocolo de investigación.** Rama `research/deudamundi-dependencies`.
>
> Universo fijo: **`../graph/nodes.csv`** + **`../pip-inspect.json`**
> (foto congelada del paso 1 y grafo del paso 2). Se mantiene `deudamundi-api`
> como **raíz** (no es dependencia) y `pip`, `setuptools`, `wheel` como
> **tooling** de build, fuera del denominador de 37. No se reconstruyó la
> imagen, no se actualizaron paquetes, no se modificó el grafo.

## Objetivo y alcance

Identificar el **repositorio fuente** de cada una de las 37 dependencias de
ejecución (10 directas + 27 transitivas). Este paso distingue explícitamente
cuatro conceptos y solo concluye sobre los dos primeros:

| Concepto | aquí | fuera de alcance |
|---|---|---|
| **Distribución** | nombre PEP 503 + versión congelada (`nodes.csv`, `pip-inspect.json`) | |
| **Repositorio** | URL canónica resuelta (`source-repos.csv:repo_url`) | |
| **Propietario del repositorio** | organización/usuario GitHub vigente (`repo_owner`), con `redirect_from` cuando hubo migración | |
| **Personas que mantienen** | — | paso(s) posteriores: NO se concluye quién mantiene efectivamente cada proyecto |
| Métricas de actividad | — | NO se calculan |

No se dedica nada a métricas; ni editorialización: el resultado es una tabla
trazable de distribución → repositorio con evidencia fechada.

## Métodos y fuentes (evidencia con fecha)

1. **Metadatos congelados del wheel** — campo `Project-URL` de cada paquete
   instalado en el snapshot (`pip-inspect.json → installed[].metadata`), el
   registro binario de lo que pip instaló en la imagen de producción.
2. **PyPI JSON API para la versión exacta**
   `https://pypi.org/pypi/<nombre>/<versión>/json` — datos vivos; cada
   respuesta se guarda íntegra en `pypi-evidence/<nombre>/<versión>.json` con
   su instante UTC de consulta (`requested_at_utc`), para que las decisiones
   puedan volver a consultarse sin depender del estado futuro de PyPI.
3. **GitHub REST API vía `gh`** solo para *resolver* el repositorio
   candidato (nombre final tras redirects, `fork`, `archived`) — guardado
   íntegro en `github-evidence/<owner>__<repo>.json` con su instante.

## Reglas de decisión (sin adivinar por el nombre)

| confidence | significado | resultado en este snapshot |
|---|---|---|
| `verified` | la URL del repositorio declarada por los **metadatos del wheel congelado** y los **metadatos actuales de PyPI (misma distribución/versión) son la misma** y el repositorio resuelve en GitHub. Esto demuestra concordancia de metadatos publicados por el proyecto y existencia del repositorio: **no** son dos confirmaciones independientes de que el paquete se produjo allí (esa auditoría más profunda queda como trabajo futuro) | 37 |
| `single-source` | solo una de las dos fuentes da la URL (no corroborada; se lista en `ambiguous.md`) | 0 |
| `pending` | fuentes en conflicto, repositorio no resoluble o falta de URL de código (razón registrada, nunca inventada) | 0 |

Las URLs se normalizan (solo hosts de código, raíz `owner/repo`, sin `.git` ni
subrutas); un proyecto que vive en un monorepo, o cuyo homepage es el propio
repositorio, se resuelve con nota explícita. Inicialmente 6 casos quedaron
`pending` (falta de URL con las etiquetas explícitas de repositorio) y solo
pasaron a `verified` al localizar la URL real en los metadatos; cero
adivinaciones.

## Archivos

| Archivo | Contenido |
|---|---|
| `identify_source_repos.py` | Extractor con las reglas de decisión y cache de evidencia (stdlib + `gh`; sin instalar nada). |
| `build_source_attribution.sh` | Orquestador: válida inputs por hash, doble corrida (estabilidad), cobertura, publicación condicionada, checksums. |
| `source-repos.csv` | Tabla legible: nombre canonizado, display, versión congelada, categoría (direct/transitive), `repo_url` final, `repo_owner`, `repo_name`, `redirect_from`, `supporting_urls` (URLs concretas que respaldan), `method`, `confidence`, `consulted_at_utc`, `shared_repository`, `notes`. |
| `attributions.json` | Misma información en JSON: candidatos por fuente (frozen vs PyPI), URLs observadas en cada fuente y resolución de GitHub con `full_name`, fecha de consulta y notas; reutilizable programáticamente. |
| `coverage-check.txt` | Verificación de cobertura: 37/37, sin faltantes, sin duplicados por nombre, versiones congeladas coherentes con `nodes.csv`; lista shared y redirects. |
| `ambiguous.md` | Casos a marcar e interpretaciones que exige transparencia (repos compartidos, redirect de owner, URLs sacadas de etiquetas secundárias, pendientes). |
| `pypi-evidence/` | Respuesta compleja de PyPI por (nombre, versión) fija + instante de consulta (37 ficheros). |
| `github-evidence/` | Respuesta de `gh api repos/…` por repositorio candidato + instante (35 ficheros: 37 - 2 repos compartidos doble-conteados). |
| `verification.txt` | Certificación del orquestador (inputs, evidencia cacheada, nodes-vs-foto, cobertura, estabilidad); solo se publica si todas las puertas pasaron. |
| `SHA256SUMS` | Hashes de TODOS los ficheros de la carpeta con **excepciones ninguna**: tablas/código/README **y los 72 JSON de evidencia** (`pypi-evidence/`, `github-evidence/`) queda dentro del manifiesto. La puerta 1 del orquestador los valida bit a bit *antes* de extraer, de modo que una caché modificada o no commitida detiene la corrida en lugar de sobrescribirse a sí misma con evidencia adulterada. |

## Cómo regenerar

```bash
./research/dependencies/attributions/build_source_attribution.sh
```

Requisitos en el host: Docker no; `gh` autenticada; `python3` (stdlib puro)
y `sha256sum`. Con las carpetas de evidencia presentes, **todas las consultas
usan la caché** y la salida es byte-idéntica (el orquestador lo exige con su
doble corrida): las consultas externas solo ocurren para URLs nuevas o
ficheras de evidencia desaparecidas. Estabilidad demostrada con la doble
corrida y con `sha256sum -c SHA256SUMS` verde.

Gates del orquestador ahora mismo:

- Puerta 1 (**antes de extraer**): valida el `SHA256SUMS` completo, que cubre
  tablas/código **y los 72 JSON de evidencia**; detecta una caché modificada
  o una evidencia no commitida y detiene sin regenerar nada sobre ella.
- Puerta 2: doble extracción byte-idéntica (inestabilidad ⇒ exit 1 y no
  publica nada, como en el paso 2).
- Puerta 3 (en el extractor): cada fila de `nodes.csv` debe tener la misma
  versión que la foto del paso 1 (`pip-inspect.json`) — la comparación es
  contra **ambas** entradas, no solo consigo misma — y la identidad completa
  de las 41 distribuciones congeladas es coherente con el entorno de
  ejecución.
- Publicación: `verification.txt`, tablas y manifiesto se publican solo si
  todas las puertas pasaron.

Puerta negativa documentada:

```bash
COVERAGE_TEST=drop ./research/dependencies/attributions/build_source_attribution.sh
# exit 2: el universe pierde una ruta → coverage FAIL y NO se publica nada
```

## Números y verificación (2026-10-30)

- Universo: **37** (10 directas + 27 transitivas). Raíz `deudamundi-api`
  excluido; tooling `pip`/`setuptools`/`wheel` excluido.
- Atribuciones: **37 de 37 `verified`** (0 `single-source`, 0 `pending`).
- Repositorios únicos: **35** (37 − 2 compartidos: `psycopg/psycopg` con
  `psycopg`+`psycopg-binary`; `pydantic/pydantic` con `pydantic`+`pydantic-core`).
- Redirect de owner resuelto y documentado: `starlette`
  (`encode/starlette` → `kludex/starlette`).
- Cobertura: `missing==[]`, `duplicated==[]`, `unexpected==[]`;
  versiones congeladas ⇔ `nodes.csv`: coherentes.
- Verificación post-corrida-verde de 2026-10-30: hash de `nodes.csv` y
  `pip-inspect.json` confirmados contra los `SHA256SUMS` publicados de los
  pasos 1 y 2 (instante exacto en `verification.txt`).

## Limitaciones

1. **URLs escritas por los propios mantenedores:** una URL "Repository"
   errónea se replica tal cual aquí. La regla `verified` demuestra la
   **concordancia de los metadatos publicados por el proyecto** (wheel
   congelado + PyPI actual) y que el repositorio existe; **no** son dos
   confirmaciones independientes de que el paquete se produjo en ese
   repositorio. Auditar la producción a fondo exigiría cruces adicionales
   (p. ej. hash del wheel contra el release del repositorio): trabajo
   futuro, no un supuesto de este paso.
2. **Volatilidad temporal:** PyPI y GitHub son servicios vivos (por ejemplo,
   el redirect de `starlette` cambió de owner después de congelar los
   metadatos). El estudio fija las consultas con fecha; re-ejecuciones
   posteriores pueden divergir, y eso no autoriza a actualizar los CSV sin
   reprocesar la evidencia completa.
3. **Distribuciones sin URL declarada** quedarían `pending` por diseño; no
   hay ninguna en el snapshot actual (ambas fuentes concordaron en las 37).
4. **Distribución ≠ repositorio ≠ maintainer:** el atributo de repositorio
   responde "dónde vive el código fuente", no "quién lo cuida".
