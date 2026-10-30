# Auditoría de aptitud de los datos — 30 de octubre de 2026

**Dictamen:** la extracción del paso 4 está completa como conjunto publicado de eventos observables bajo las reglas implementadas y permite comenzar el análisis descriptivo del caso. No basta, por sí sola, para afirmar quiénes son los mantenedores ni para responder todas las preguntas del protocolo. La cobertura de 35/35 repositorios es cobertura de unidades, no una prueba absoluta de que GitHub entregó todos los eventos históricos posibles.

## Puertas que sí pasaron

- El universo queda anclado al CSV del paso 3 por SHA-256: 37 distribuciones de ejecución → 35 repositorios únicos. El mismo repositorio no se duplica al contar distribuciones compartidas.
- Hay ventana y corte UTC previos, cuatro tipos de evento separados, identificadores de actor y bot, fuente por página, fecha de consulta, recibo SHA-256 del cuerpo, y un manifiesto de los extractos publicados.
- El verificador reconstruye los conteos desde las páginas, detecta huecos e IDs repetidos, confirma el total declarado de revisiones por PR incluido y exige que la paginación de releases termine en una página de menos de 100 registros.
- Un hallazgo de esta auditoría corrigió el corte prematuro de releases: en FastAPI, Pydantic y SQLAlchemy se añadieron tres páginas finales hasta agotar el endpoint. Ninguna contenía eventos dentro de las ventanas; los cuatro totales de eventos quedaron iguales. El CSV cambió en los conteos de páginas y se normalizó a saltos de línea LF.

## Límites que afectan las inferencias

| Dimensión | Evidencia y efecto |
| --- | --- |
| Identidad | En 12 meses, 21 de 7,014 commits carecen de cuenta de autor vinculada; los bots figuran por separado (1,495 commits, 670 PR fusionados y 2,610 revisiones). La alta vinculación de cuentas no convierte al autor en mantenedor formal. Alias y cuentas de automatización no declaradas siguen abiertos. |
| Comparación commits/PR | 195 de 3,981 PR fusionados en 12 meses tienen una rama base distinta de la rama principal observada; aparecen en 13 repositorios. El CSV conserva `base_ref`, de modo que el análisis debe presentar por separado PR a rama principal y PR a otras ramas. La rama principal actual tampoco prueba cuál era la principal en cada fecha histórica. |
| Repositorios de baja actividad | 13 de 35 repositorios registran menos de 30 commits humanos atribuibles en 12 meses; dos registran cero. El valor 30 es un diagnóstico de dispersión, no un umbral de exclusión preaprobado. Antes de H1/H2 hay que fijar una regla de denominador mínimo y mostrar sensibilidad, evitando convertir 1/1 en una conclusión fuerte. |
| Revisiones | En ocho revisiones guardadas, `submittedAt` ocurrió entre 2 y 10 segundos después del `updatedAt` del PR. Ningún PR guardado con `updatedAt` anterior al inicio de la ventana contenía una revisión dentro de ella, pero ese solapamiento observado no demuestra ausencia de PR omitidos fuera de las páginas consultadas. La paginación de PR por `updatedAt` es una vista cambiante, no una foto transaccional. |
| Releases | El endpoint de GitHub solo enumera objetos release; tags sin release quedan fuera. El historial de publicaciones PyPI de cada proyecto durante las ventanas no está en esta extracción. Ausencia de release GitHub no equivale a ausencia de versión publicada. |
| Procedencia | Se conservan extractos mínimos, no cuerpos API brutos. Los hashes del cuerpo son recibos de consulta, pero un lector no puede recalcularlos desde los extractos. `SHA256SUMS` sí permite verificar que los extractos publicados no cambiaron desde el commit. |
| Constructo | Commits, PR y revisiones observan contribución pública, no horas, coordinación privada, autoridad, empleo o remuneración. En monorepos y repos compartidos, la actividad del repo puede incluir código ajeno al paquete congelado. |

## Correspondencia con las preguntas del protocolo

| Pregunta | Aptitud actual | Condición antes de afirmar resultados |
| --- | --- | --- |
| Q1: paquetes y rutas de dependencia | Respondible con los pasos 1–2, para la foto Python/Linux congelada. | Citar versión, plataforma y extras; no extenderlo a toda instalación. |
| Q2: repositorio de cada distribución | Respondible con el paso 3 como atribución documental de 37/37 distribuciones. | No convertir `verified` en prueba independiente del origen del wheel ni en identidad de mantenedores. |
| Q3: quién hace mantenimiento observable | Parcial: hay commits, PR, revisiones y releases; no hay triage de incidencias, documentación clasificada ni trabajo privado. | Separar roles, bots, merges y PR a otras ramas; añadir lectura cualitativa antes de usar «mantenedor». |
| Q4: concentración por tarea | Calculable de forma descriptiva, todavía no calculada. | Fijar denominadores, regla para repos de bajo volumen, tratamiento de cuentas no atribuibles y sensibilidad 12/24 meses antes de ver cuotas y HHI. |
| Q5: gobernanza y financiación | No respondible con estos datos de eventos. | Revisar políticas, equipos, patrocinio y fuentes institucionales por caso, con evidencia fechada. |
| Q6: exposición de DeudaMundi | Parcial: grafo y rutas están en paso 2; la actividad por repo en paso 4. | Unir ambas tablas sin duplicar repos compartidos; no equiparar frecuencia o concentración a riesgo operativo. |
| Q7: otros backends con dependencias similares | Pendiente: la cohorte externa no se levantó. | Subprotocolo, marco de búsqueda, auditoría y denominador propios. |

**Hipótesis H1–H4:** las tablas permiten construir H1, H2 y H4 como contrastes descriptivos tras fijar esas reglas. H3 permite buscar repositorios con paquete congelado publicado en PyPI, cero releases de GitHub y otra actividad observable; si se quiere afirmar publicación *reciente* en PyPI, hace falta recuperar su historial de versiones por proyecto. Ninguna hipótesis valida por sí misma una etiqueta de «riesgo» o «abandono».

## Siguiente puerta analítica

Antes de calcular cuotas o elegir titulares: registrar un plan de análisis para denominadores y mínimos, comparar PR a rama principal frente a todas las ramas, separar eventos de bot, merges y actores sin cuenta, y auditar manualmente los casos extremos y los repos compartidos. Solo después interpretar los contrastes, con la cohorte de backends como módulo aparte. [Especificación oficial de commits](https://docs.github.com/en/rest/commits/commits), [PR y revisiones GraphQL](https://docs.github.com/en/graphql/reference/pulls), [releases](https://docs.github.com/en/rest/releases/releases).
