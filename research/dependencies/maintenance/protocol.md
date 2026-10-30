# Paso 4 — registro previo de actividad pública de mantenimiento

Estado: reglas fijadas antes de consultar eventos de los repositorios. Este paso recolecta evidencia; las cuotas de concentración, HHI, interpretación y selección editorial se calculan después.

## Universo y fecha

- Fuente de identidad: `../attributions/source-repos.csv` en el commit `c129e4edd21db956ba6cb68f918d104d5aeac9cc`; SHA-256 `f1d2884a5907652236848be559f168a535eb898e4ef2db14e57e352472fea12c`.
- Unidad de extracción: los 35 repositorios GitHub únicos atribuidos a las 37 distribuciones de ejecución. `psycopg/psycopg` y `pydantic/pydantic` se consultan una vez cada uno y conservan su relación con dos distribuciones. `deudamundi-api` y las tres herramientas de build quedan fuera.
- Corte UTC exclusivo: `2026-10-30T00:00:00Z`. Ventana principal: `[2025-10-30T00:00:00Z, 2026-10-30T00:00:00Z)`. Sensibilidad: `[2024-10-30T00:00:00Z, 2026-10-30T00:00:00Z)`. Se recolectan 24 meses; el análisis de 12 meses usa un subconjunto. No mover el corte después de ver los eventos sin versionar una enmienda.
- Resolver cada URL al identificador numérico de repositorio y registrar nombre final, rama principal, `archived`, `fork` y fecha de consulta. Si el repositorio se trasladó o no está disponible, registrar el hecho y no sustituirlo por otro por semejanza del nombre.

## Eventos observables y denominadores futuros

| Evento | Inclusión en la ventana | Actor principal observable | Separaciones obligatorias |
| --- | --- | --- | --- |
| Commit de rama principal | SHA alcanzable desde la rama principal consultada y `commit.committer.date` dentro de la ventana | `author.login` cuando GitHub lo vincula; nulo si no | merge (`parents > 1`), bot, autor no vinculado, `committer.login` distinto |
| PR fusionado | `merged_at` dentro de la ventana | autor del PR; integrador solo si el API lo devuelve de forma verificable | bot, PR sin autor, cambio de rama base, PR fusionado fuera de la ventana |
| Revisión de PR | `submitted_at` dentro de la ventana; estados `APPROVED`, `CHANGES_REQUESTED` o `COMMENTED` | `user.login` del revisor | bot, revisión sin actor o fecha, varias revisiones de una misma persona en un PR |
| Release de GitHub | `published_at` dentro de la ventana y `draft=false` | `author.login` del release si existe | prerelease, release sin actor, tags sin release de GitHub |

Los cuatro tipos se cuentan por separado. No se suman como horas, esfuerzo, autoridad ni riesgo. Una ausencia de evento en GitHub no prueba abandono ni ausencia de trabajo fuera de GitHub.

## Identidades y automatización

- Conservar `user.id`, `user.login` y `user.type` cuando estén disponibles; no guardar correos ni nombres personales de los objetos de commit si no son necesarios para el conteo.
- Marcar bot si GitHub declara `type=Bot` o si el login termina en `[bot]`; conservar la regla aplicada y tratar cuentas ambiguas como desconocidas. La clasificación no pretende identificar todas las automatizaciones.
- No fusionar alias por coincidencia de nombre o correo. Actores sin cuenta vinculada quedan en una categoría no atribuible. La reconciliación manual, con evidencia pública y bitácora, pertenece al análisis posterior.
- Mantener el autor del PR, el integrador del PR, el autor del commit, el committer, el revisor y el publicador del release como roles distintos.

## Consultas y completitud

Usar la API REST de GitHub con versión fijada `2026-03-10` para metadatos, commits y releases. Para PR y revisiones usar GraphQL con cursores y conexiones de hasta 100 nodos: en el piloto `fastapi/fastapi` hubo 100 PR actualizados en apenas diez días, por lo que una llamada REST por PR no escala a 35 repositorios. Este ajuste se registra antes de recolectar eventos y conserva las definiciones y ventanas originales. Registrar endpoint o consulta, parámetros o cursor, instante UTC de respuesta, número de registros, código de estado, costo GraphQL cuando aplique y SHA-256 del cuerpo recibido. Conservar una extracción normalizada mínima que permita rehacer los conteos, sin cuerpos de comentarios, correos ni textos de PR.

1. Consultar metadatos del repositorio y su rama principal.
2. Listar commits de la rama principal con `since` y `until` que cubran 24 meses; filtrar otra vez por timestamp en cliente y deduplicar por SHA. El API puede interpretar `since` según su propia semántica; contrastar bordes del intervalo en el piloto.
3. Listar PR con GraphQL `pullRequests(orderBy: UPDATED_AT DESC, states: OPEN/CLOSED/MERGED)`; avanzar hasta una página cuyo máximo `updatedAt` sea anterior al inicio de la ventana de 24 meses. Filtrar `mergedAt` para la tabla de PR fusionados. El conjunto de PR actualizado durante la ventana alimenta las consultas de revisiones; documentar si alguna revisión no puede observarse.
4. Incluir hasta 100 revisiones en cada PR de la consulta GraphQL; para conexiones con `hasNextPage`, continuar por cursor hasta agotamiento. Filtrar `submittedAt` en cliente. No inferir revisiones a partir de comentarios ordinarios.
5. Listar releases hasta agotamiento; filtrar `published_at` en cliente. Los tags sin release se mantienen fuera del indicador.

Detener con estado incompleto, no con un cero, ante error de API, límite de tasa, respuesta inesperada o paginación truncada. Conservar el avance parcial para reanudar. Una cobertura `PASS` exige 35 repositorios considerados y cada tipo de evento marcado `complete` o `unavailable` con razón; `unavailable` nunca se interpreta como cero eventos.

## Piloto antes de escalar

Usar `fastapi/fastapi` (directa), `sqlalchemy/mako` (transitiva), `psycopg/psycopg` (repositorio compartido) y el repositorio final de `starlette` (redirect). Comprobar respuestas de 0, 1 y varias páginas, casos sin actor, bots, fechas limítrofes y costo de consultar revisiones. El piloto evalúa el método; no selecciona casos para el relato. Si el costo o las restricciones del API impiden completitud, publicar cobertura y límites y no inventar la métrica.

## Fuentes de especificación

- [GitHub REST: commits](https://docs.github.com/en/rest/commits/commits)
- [GitHub REST: pull requests](https://docs.github.com/en/rest/pulls/pulls)
- [GitHub REST: reviews](https://docs.github.com/en/rest/pulls/reviews)
- [GitHub REST: releases](https://docs.github.com/en/rest/releases/releases)
- [GitHub REST: pagination](https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api)
- [GitHub GraphQL: límites y costos](https://docs.github.com/en/graphql/overview/rate-limits-and-query-limits-for-the-graphql-api)
- [GitHub GraphQL: pull requests](https://docs.github.com/en/graphql/reference/pulls)
