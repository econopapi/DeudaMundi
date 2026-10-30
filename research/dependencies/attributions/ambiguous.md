# Casos ambiguos e interpretaciones — atribución de repositorios (paso 3)

Estado: **0 de 37 dependencias quedan `pending`**. Todas las atribuciones
actuales pasaron la regla `verified`: los metadatos congelados del wheel y los
metadatos vivos de PyPI (para la versión exacta) concuerdan en el mismo
repositorio canónico, y el repositorio resuelve en GitHub. Las observaciones
siguientes no son fallos de cobertura: son los casos cuya interpretación
merece transparencia para la auditoría.

## 1. Repositorios compartidos (multipaquete)

| Propietario/Repositorio | Distribuciones | Justificación |
|---|---|---|
| `psycopg/psycopg` | `psycopg`, `psycopg-binary` | `psycopg-binary` no tiene repositorio propio: sus metadatos (congelados y de PyPI) apuntan al mismo proyecto `psycopg/psycopg`; la URL secundaria `…/issues` confirma la misma raíz. |
| `pydantic/pydantic` | `pydantic`, `pydantic-core` | Los metadatos de `pydantic-core 2.50.2` declaran `Repository: https://github.com/pydantic/pydantic`, y una segunda URL sirve de prueba de que el paquete se produce dentro del árbol de ese repositorio: `…/tree/main/pydantic-core`. |

Ambos casos comparten repositorio porque es lo que declaran los propios
proyectos. Cada distribución es un paquete; el repositorio es uno compartido.
La distinción **distribución vs repositorio** queda marcada en las columnas
`shared_repository` y `notes` de `source-repos.csv`.

## 2. Redirecciones resueltas (propietario del repositorio)

| Distribución | URL declarada (frozen + PyPI) | Resultado de `gh api repos/…` |
|---|---|---|
| `starlette` | `https://github.com/encode/starlette` | `kludex/starlette` (movimiento del owner posterior a la generación de los metadatos del wheel) |

La atribución registra el **propietario vigente** (`kludex`) según la API de
GitHub en el día de la consulta, y conserva `redirect_from = encode/starlette`.
Los renames que solo cambian la capitalización (por ejemplo `Kludex/uvicorn`
frente a `kludex/uvicorn`) no cuentan como redirect, porque la identidad
normalizada es la misma. **Advertencia de volatilidad:** un renombre futuro
cambiaría `repo_owner`; la carpeta `github-evidence/` registra exactamente lo
que se vio y en qué instante.

## 3. Nombres de distribución vs display

- `APScheduler`, `Deprecated` y `typing_extensions` llevan mayúsculas o
  subrayado en su display; el eje de la tabla es el nombre canonizado PEP 503
  (`apscheduler`, `deprecated`, `typing-extensions`). Ninguna distribución se
  duplica por diferencias de nombre (verificado en `coverage-check.txt` con
  `duplicated_names: []`).
- `pyjwt` se atribuye a `jpadilla/pyjwt`: la homepage del wheel y la de PyPI
  coinciden, y GitHub responde con ese repositorio sin redirect.

## 4. URLs de repositorio tomadas de etiquetas secundarias

En 5 distribuciones la *homepage* del proyecto es directamente el
repositorio (`h11`, `httptools`, `pyjwt`, `websockets`, `wrapt`); en `mako` la
URL de GitHub aparece bajo la etiqueta `Issue Tracker` (la homepage es el
sitio web del proyecto). El extractor lo marca con la nota
`repo URL taken from metadata label '…'` y conserva la etiqueta y la URL
exactas tanto en `source-repos.csv` como en los ficheros de evidencia.
Ningún URL fue deducido ni supuesto a partir del nombre del paquete.

## 5. Qué este paso NO concluye

- **No** identifica a las personas que mantienen efectivamente cada
  repositorio; el mantenimiento cambia con el tiempo, y el caso `starlette`
  ya ilustra esa evolución. Este paso pide repositorios, no personas.
- **No** calcula métricas de actividad.
- Los 6 casos que inicialmente salieron `pending` (`h11`, `httptools`,
  `mako`, `pyjwt`, `websockets`, `wrapt`) pasaron a `verified` únicamente
  cuando las dos fuentes coincidieron; nada se adivinó para cerrar en verde.
- Reconstruir la imagen o actualizar dependencias para "contrastar" el
  upstream quedó fuera de alcance: los datos vienen de los metadatos
  congelados y de APIs de solo lectura.

## 6. Datos externos que pueden cambiar con el tiempo

- Los metadatos de PyPI y la API de GitHub (redirecciones, `fork`,
  `archived`) son volátiles. Las carpetas `pypi-evidence/` y
  `github-evidence/` guardan la respuesta completa y su instante UTC de
  consulta (2026-10-30): si el upstream cambia después, esos ficheros
  documentan lo que se vio.
- Un nivel de atribución más duro (por ejemplo, hash del sdist contra tag del
  repositorio) queda como trabajo explícito de un paso posterior, no como
  conclusión de este entregable.
