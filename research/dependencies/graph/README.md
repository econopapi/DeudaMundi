# Grafo de dependencias Python del backend de producción — paso 2

> **Paso 2 del protocolo de investigación.** Rama `research/deudamundi-dependencies`
> (antes `research/freeze-python-env`, del paso 1).
>
> Fuente única de verdad: **`../pip-inspect.json`** (la fotografía congelada del
> paso 1) + **`api/pyproject.toml`** (dependencias directas y extras pedidos).
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
| `extract_dependency_graph.py` | Extractor (corre dentro de la imagen; solo Docker + Python 3.11+ con `pip._vendor.packaging`). |
| `build_dependency_graph.sh` | Orquestador en host: verificación de la foto, doble corrida para estabilidad, checksums. |
| `nodes.csv` | Tabla de nodos: nombre canonizado, display, versión, categoría (`project:package` / `runtime:direct` / `runtime:transitive` / `build:tooling`), extras pedidos, `paths_from_root`, `hops_from_root`, ancestros reclamados, requerido por. |
| `edges.csv` | Aristas activas (55 del grafo de ejecución + 1 de `wheel→packaging` fuera del grafo, por ser tooling). |
| `edges-inactive.csv` | 233 requisitos evaluados pero inactivos, con razón: `extra-not-requested` (174), `marker-unmet-for-all-requested-extras` (25), `marker-not-satisfied` (9). |
| `paths.txt` | Rutas más cortas y conteo de rutas simples `deudamundi-api → cada transitiva`. |
| `graph-diagram.mmd` | Visualización Mermaid (renderiza en GitHub). |
| `checks.json` | Datos de verificación: extras activos/inactivos, marcadores Python/plataforma, dependencias compartidas, aislamiento del tooling, no-explicados. |
| `step1-vs-step2.txt` | Comparación semántica contra las flechas del paso 1 (no se usan como fuente de verdad). |
| `verification.txt` | Certificación del orquestador: hash de la foto, entorno de imagen vs foto, estabilidad byte-a-byte. |
| `SHA256SUMS` | Hashes de todos los archivos de la carpeta. |

## Cómo regenerar

```bash
./research/dependencies/graph/build_dependency_graph.sh
```

Requisitos en el host: Docker + `sha256sum` + la imagen de producción del
paso 1 presente localmente (por defecto
`deudamundi-api:research-env-snapshot`; se usa tal cual, **no se reconstruye**).
El orquestador: (1) valida `pip-inspect.json` contra `SHA256SUMS` del paso 1;
(2) verifica pip/Python de la imagen contra los de la foto; (3) extrae dos
veces y exige salida byte-idéntica; (4) recalcula `SHA256SUMS`.

## Números comprobados (snapshot 2026-10-30, pip 26.2.2 / CPython 3.12.16)

| Métrica | Valor |
|---|---|
| Distribuciones instaladas | 41 |
| Nodos del grafo de ejecución (runtime) | 38 |
| Paquete del proyecto (raíz, fuera del grafo) | 1 (`deudamundi-api`) |
| Tooling de build (fuera del grafo) | 3 (`pip`, `setuptools`, `wheel`) |
| Dependencias directas (`[project.dependencies]`) | 10 |
| Dependencias transitivas | 27 |
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

27/28 paquetes transitivos atribuyen exactamente a los mismos ancestros.
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

1. **Extras activos vs inactivos:** `uvicorn[standard]` y
   `psycopg[binary]` activos (aristas etiquetadas en el diagrama);
   inactivos confirmados: `apscheduler[doc]`, `fastapi[standard]/[all]`
   (extras del propio fastapi) y `deudamundi-api[dev]`
   (pytest/pytest-cov/ruff/locust, no instalados).
2. **Marcadores Python/Linux activos:** `typing_extensions>=4.16.0;
   python_version < "3.15"` (anyio), `typing-extensions>=4.6;
   python_version < "3.13"` (psycopg[binary]), y el largo marcador de
   `uvloop` (`sys_platform != 'win32' and … and extra == 'standard'`,
   uvicorn) — evaluados por `packaging` contra la foto, no asumidos.
3. **Inactivos verificados:** `tomli` y `exceptiongroup`
   (`python_version < "3.11"` → falso en 3.12), `tzdata`
   (`extra == "tz"` no pedido), `trio` (`extra == "trio"`, anyio),
   `async-timeout` (redis, `python_full_version < "3.11.3"`).
4. **Compartidas por varias rutas:** 27 paquetes en `shared_paths` con
   conteos de ancestros y de rutas simples.
5. **Aislamiento:** ninguna arista de ejecución alcanza a
   `pip`/`setuptools`/`wheel`; el tooling sólo aporta
   `wheel → packaging` (documentado fuera del grafo).
6. **No explicados:** lista vacía (`[]` en `checks.json` y `paths.txt`).
7. **Estabilidad:** dos corridas con salida byte-idéntica (diff limpio).

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
