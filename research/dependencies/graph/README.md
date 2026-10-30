# Grafo de dependencias Python del backend de producción — paso 2

> **Paso 2 del protocolo de investigación.** Rama `research/deudamundi-dependencies`
> (antes `research/freeze-python-env`, del paso 1).
>
> Fuente única de verdad: **`../pip-inspect.json`** (la fotografía congelada
> del paso 1) + **`pyproject-frozen.toml`** (copia congelada de
> `api/pyproject.toml`, verificada byte a byte contra el checkout actual y
> contra `/app/pyproject.toml` de la imagen del paso 1 antes de extraer).
> NO se reconstruyó la imagen ni se actualizaron paquetes.

## Qué es

Grafo dirigido de ejecución `deudamundi-api → dependencias`, derivado
exclusivamente de los metadatos ya instalados en la foto (Requires-Dist de
cada distribución), con nombres canonizados PEP 503, todos los requisitos
evaluados con `packaging` (el mismo motor de pip; se ejecuta dentro de la
imagen del paso 1) y los extras propagados al punto fijo:

- **semilla** desde `pyproject.toml`: `uvicorn[standard]`, `psycopg[binary]`;
- **propagación**: un requisito activo `foo[bar]` activa los requisitos
  `extra == "bar"` dentro de los metadatos de `foo` (ninguno extra aquí);
- **marcadores** evaluados contra el entorno registrado en la foto
  (`implementation_name=cpython`, `platform=`linux/x86_64, etc.), con
  `extra` sustituido por cada extra pedido del paquete requeredor.

## Archivos

| Archivo | Contenido |
|---|---|
| `extract_dependency_graph.py` | Extractor (corre dentro de la imagen; solo Docker + Python 3.11+ con `pip._vendor.packaging`). Verifica además la **identidad completa** (nombre+versión) de las distribuciones instaladas entre la foto y su entorno, y aborta sin escribir salidas si no coincide. |
| `build_dependency_graph.sh` | Orquestador en host: verificación de la foto, binding del pyproject (checkout e imagen), doble corrida **con puerta de publicación** (inestabilidad ⇒ exit 1 y no publica nada), checksums. |
| `pyproject-frozen.toml` | Copia congelada de `api/pyproject.toml` en el momento de la foto; define dependencias directas y extras pedidos. |
| `nodes.csv` | Tabla de nodos: nombre canonizado, display, versión, categoría (`project:package` / `runtime:direct` / `runtime:transitive` / `build:tooling`), extras pedidos, `paths_from_root`, `hops_from_root`, ancestros reclamados, requerido por. |
| `edges.csv` | Aristas activas (55 del grafo de ejecución + 1 de `wheel→packaging` fuera del grafo, por ser tooling). |
| `edges-inactive.csv` | 233 requisitos evaluados pero inactivos, con razón: `extra-not-requested` (**199**), `marker-unmet-for-all-requested-extras` (**25**), `marker-not-satisfied` (**9**). Total 233 = 199 + 25 + 9. |
| `paths.txt` | Rutas más cortas y conteo de rutas simples `deudamundi-api → cada transitiva`. |
| `graph-diagram.mmd` | Visualización Mermaid (renderiza en GitHub). |
| `checks.json` | Datos de verificación: extras activos/inactivos, marcadores Python/plataforma, dependencias compartidas, aislamiento del tooling, no-explicados. |
| `step1-vs-step2.txt` | Comparación semántica contra las flechas del paso 1 (no se usan como fuente de verdad). |
| `verification.txt` | Certificación del orquestador: hash de la foto, entorno de imagen vs foto, binding del pyproject, resultado de la puerta de estabilidad. **Se escribe a un fichero temporal y solo se publica tras pasar todas las puertas**; en un fallo no se toca (queda el de la última corrida verde). |
| `SHA256SUMS` | Hashes de todos los archivos de la carpeta. |

## Cómo regenerar

```bash
./research/dependencies/graph/build_dependency_graph.sh
```

Requisitos en el host: Docker + `sha256sum` + la imagen de producción del
paso 1 presente localmente (por defecto
`deudamundi-api:research-env-snapshot`; se usa tal cual, **no se reconstruye**).
El orquestador: (1) valida `pip-inspect.json` contra `SHA256SUMS` del paso 1;
(2) comprueba que la imagen existe — si falta, se detiene con mensaje claro
que explica **cómo recuperar la imagen original** (`docker save`/`docker
load` desde la máquina donde se construyó el paso 1) y **sin sugerir
reconstruirla**: reconstruir reescribiría `pip-inspect.json` y cancelaría la
foto congelada; (3) vincula la definición de directas/extras a la foto:
`pyproject-frozen.toml` debe ser idéntico al checkout actual **y** a
`/app/pyproject.toml` dentro de la imagen — el volcado se hace con el ID
devuelto por `docker create` (la creación debe funcionar; sin nombres fijos
de contenedor, por si un contenedor viejo aporta el archivo equivocado); (4)
verifica pip/Python de la imagen contra los de la foto; (5) el extractor
comprueba identidad completa (nombre canónico + versión) de las 41
distribuciones entre la foto y el entorno donde corre, con `exit 2` en
desacuerdo; (6) extrae dos veces y exige salida byte-idéntica — si difieren,
**exit 1 sin publicar nada**: los artefactos publicados, incluidos
`verification.txt` y `SHA256SUMS`, quedan intactos (de la última corrida
verde) y solo se conservan `runs/run1` y `runs/run2` para depurar; (7)
publica run1, publica `verification.txt` — que se genera en un fichero
temporal y solo se publica tras pasar **todas** las puertas — y recalcula
`SHA256SUMS`.

Demostración del comportamiento de fallo por inestabilidad:

```bash
STABILITY_TEST=mismatch ./research/dependencies/graph/build_dependency_graph.sh
# exit 1 + "Not published": muta la segunda corrida (ficheros publicados intactos)
```

## Números comprobados (snapshot 2026-10-30, pip 26.2.2 / CPython 3.12.16)

| Métrica | Valor |
|---|---|
| Distribuciones instaladas | 41 |
| Nodos alcanzables | 38 = **1 raíz (`deudamundi-api`)** + 37 dependencias |
| — dependencias directas (`[project.dependencies]`) | 10 |
| — dependencias transitivas | 27 |
| Paquete del proyecto (raíz, fuera del grafo de ejecución) | 1 (`deudamundi-api`) |
| Tooling de build (fuera del grafo) | 3 (`pip`, `setuptools`, `wheel`) |
| Aristas activas totales | 56 (55 de ejecución; `wheel→packaging` queda fuera) |
| Requisitos inactivos evaluados | 233 |
| Paquetes sin ruta activa desde la raíz | **0** |
| Extras activos tras punto fijo | `uvicorn: [standard]`, `psycopg: [binary]` |
| Grafo acíclico (DAG) | sí |
| Estabilidad de salida | byte-idéntica en dos corridas |

Rutas compartidas destacadas: `typing-extensions` se alcanza por 9 caminos
desde otros tantos ancestros (17 rutas simples totales); `anyio` por 4
ancestros (3 rutas); `idna` por 4 ancestros (4 rutas); `pydantic` y
`pydantic-core` por `fastapi` y `pydantic-settings` (2 rutas cada uno).

## Comparación con el paso 1 (diferencias documentadas)

26 de 27 paquetes transitivos atribuyen exactamente a los mismos ancestros.
**Única divergencia: `typing-extensions`.**

- El paso 1 reclamaba también a **`redis`** como ancestro.
- La cadena `deudamundi-api → redis → PyJWT → typing_extensions` tenía su
  último salto con el marcador `python_version < "3.11"` — falso en
  CPython 3.12.16. El paso 1 trataba cualquier marcador no-`extra` como
  activo (falso positivo); el paso 2 lo evalúa y descarta la arista
  (`redis → PyJWT` activa; `PyJWT → typing_extensions` inactiva,
  `marker-not-satisfied`).
- Conclusión: la cobertura se mantiene; el paso 1 sobre-atribuía 1 de 27.
  El caso documenta la debilidad definida por diseño del simplificador
  del paso 1 (exactamente este hueco).
- 4 «diferencias» adicionales del primer borrador del extractor eran sólo
  de ortografía (`pydantic_core` vs `pydantic-core`); se resolvieron
  canonizando los nombres en la comparación.

## Verificación realizada

Puertas del orquestador (todas ejecutadas en la corrida verde, además de sus
demostraciones negativas):

0. **Hash de la foto:** `pip-inspect.json` validado contra los `SHA256SUMS`
   del paso 1 antes de empezar.
0b. **Imagen con la que se extrae:** si la imagen del paso 1 no existe, el
   orquestador termina con mensaje claro y no reconstruye ni resuelve
   dependencias (demostrado con `SNAPSHOT_TAG=inexistente:tag` → exit 1).
1. **Binding del pyproject a la foto:** `pyproject-frozen.toml` idéntico
   byte-a-byte al checkout actual y a `/app/pyproject.toml` de la imagen
   (demostrado el rechazo con un pyproject divergente en un sandbox → exit 1).
2. **Entorno de imagen vs foto:** pip 26.2.2 y CPython 3.12.16 iguales.
3. **Identidad de las distribuciones (nombres + versiones), no solo
   Python/pip:** las 41 de la foto vs `importlib.metadata` del entorno de
   ejecución — 41/41 idénticas (`checks.json → identity_check`).
   Demostrado el rechazo con una foto mutada en copia temporal
   (`redis 9.9.9`) → exit 2 sin escribir salidas.
4. **Estabilidad con puerta de publicación:** dos extracciones byte-idénticas;
   en divergencia, exit 1 y nada publicado, incluidos
   `verification.txt` y `SHA256SUMS` (que se generan en fichero temporal y
   solo se publican tras pasar todas las puertas); demostrado con
   `STABILITY_TEST=mismatch` → exit 1 y SHA de `verification.txt`,
   `nodes.csv` y `SHA256SUMS` intactos tras el intento.

Verificaciones de gramática del grafo (sin cambiar tras las correcciones):

5. **Extras activos vs inactivos:** `uvicorn[standard]` y
   `psycopg[binary]` activos (aristas etiquetadas en el diagrama);
   inactivos confirmados: `apscheduler[doc]`, `fastapi[standard]/[all]`
   (extras del propio fastapi) y `deudamundi-api[dev]`
   (pytest/pytest-cov/ruff/locust, no instalados).
6. **Marcadores Python/Linux activos:** `typing_extensions>=4.16.0;
   python_version < "3.15"` (anyio), `typing-extensions>=4.6;
   python_version < "3.13"` (psycopg[binary]), y el largo marcador de
   `uvloop` (`sys_platform != 'win32' and … and extra == 'standard'`,
   uvicorn) — evaluados por `packaging` contra la foto, no asumidos.
7. **Inactivos verificados:** `tomli` y `exceptiongroup`
   (`python_version < "3.11"` → falso en 3.12), `tzdata`
   (`extra == "tz"` no pedido), `trio` (`extra == "trio"`, anyio),
   `async-timeout` (redis, `python_full_version < "3.11.3"`).
8. **Compartidas por varias rutas:** 27 paquetes en `shared_paths` con
   conteos de ancestros y de rutas simples.
9. **Aislamiento:** ninguna arista de ejecución alcanza a
   `pip`/`setuptools`/`wheel`; el tooling sólo aporta
   `wheel → packaging` (documentado fuera del grafo).
10. **No explicados:** lista vacía (`[]` en `checks.json` y `paths.txt`).

## Ambigüedades pendientes

- Exactamente **una** divergencia semántica entre el simplificador del
  paso 1 y el evaluador exacto del paso 2 (`typing-extensions`; sin
  impacto en la foto, sí en la atribución de ancestros).
- 25 requisitos quedan como `marker-unmet-for-all-requested-extras`
  (p. ej. `uvicorn[standard]` referenciado dentro de extras propios de
  fastapi, que no fueron pedidos). Se documentan en `edges-inactive.csv`;
  no hay ambigüedad semántica: pip no los instaló y así se clasifican.
- El tooling de build aporta una arista hacia el grafo
  (`wheel → packaging`); si versiones futuras del tooling introdujeran
  otros requerimientos cruzados, habría que documentarlos como caso
  aparte (no afecta a la ejecución runtime).
