# Paso 5 — plan de análisis registrado antes de calcular resultados

**Estado:** plan preregistrado. Este archivo se creó antes de ejecutar cualquier cálculo de cuotas, HHI o contrastes de hipótesis sobre los datos del paso 4, y antes de consultar el historial de versiones de PyPI que exige H3. Cualquier regla añadida después queda marcada como análisis exploratorio con fecha. La extracción del paso 4 ya estaba cerrada y publicada en el commit `1363af84d5089ca4260645012dcb34ccc93d4c6c`; este plan no altera definiciones, ventanas ni universo.

## Fuente de los datos

- `../data/`: 443 JSON normalizados del paso 4 (commits de rama principal, PR con revisiones, releases, metadatos), con recibos SHA-256 y cobertura 35/35. Hashes en `../SHA256SUMS` y registro en `../verification.txt`.
- `../../attributions/source-repos.csv`: mapa 37 distribuciones de ejecución → 35 repositorios únicos, SHA-256 `f1d2884a5907652236848be559f168a535eb898e4ef2db14e57e352472fea12c`. El verificador del paso 4 lo comprueba antes de leer.
- `../../graph/nodes.csv` y `../../graph/paths.txt`: exposición de cada distribución (directa/transitiva, rutas simples desde `deudamundi-api`, saltos), del paso 2.

## Reglas fijadas en el paso 4 (no se renegocian aquí)

- Corte UTC exclusivo: `2026-10-30T00:00:00Z`. Ventana principal: `[2025-10-30T00:00:00Z, 2026-10-30T00:00:00Z)`. Sensibilidad: `[2024-10-30T00:00:00Z, 2026-10-30T00:00:00Z)`.
- Unidad de conteo de repositorio: 35 repositorios únicos; `psycopg/psycopg` y `pydantic/pydantic` (dos distribuciones cada uno) cuentan una sola vez. Las 37 distribuciones se reportan como tabla de mapeo aparte.
- Los cuatro tipos de evento (commits de rama principal, PR fusionados, revisiones, releases de GitHub) se cuentan y se contrastan por separado; nunca se suman entre sí.
- Bots: `type=Bot` o login con sufijo `[bot]`, tal como quedó guardado en cada JSON del paso 4. Se presentan como subconjunto separado; nunca como personas.
- Actores sin cuenta de GitHub vinculada (`author == null`): categoría «no atribuido» propia, excluida de rankings de personas, e incluida en denominadores cuando la métrica así lo define (ver abajo). No se reconcilian alias en este paso; sin evidencia pública adicional, fusionar por apariencia sería invención.

## Definiciones operativas de este paso

### Commits

- Atribución por `author.login` cuando GitHub la devuelve. `committer.login` se reporta aparte cuando difiere del autor, sin fusionar: `web-flow` (id 19864447) materializa PR y no es la autoría del cambio.
- Commits con `parent_count > 1` (merge) se presentan por separado: observan integración, no escritura de código. La métrica principal de concentración por commits excluye merges; una versión con merges incluidos se reporta como sensibilidad paralela.
- `invalid-email-address` (id 148100, `type=User`) es una cuenta que GitHub emplea cuando el commit se materializa sin correo vinculable. El protocolo del paso 4 no la marca bot; se mantiene como actor propio y la auditoría manual la etiqueta como «patrón probablemente automatizado, no declarado». No se recategoriza.

### PR fusionados

- Evento: `merged_at` dentro de la ventana. Atribución: `author.login` del PR (autoría del cambio). `merged_by` se conserva como rol de integración aparte (se usa en H4).
- Métrica principal de concentración: PR fusionados hacia la rama principal observada (`base_ref == default_branch` de los metadatos del paso 4).
- Sensibilidad paralela: PR fusionados a cualquier rama; los PR con `base_ref != default_branch` se desglosan por repositorio (la auditoría del paso 4 identificó 195 en 12 meses, en 13 repositorios).

### Revisiones

- Evento: `submitted_at` dentro de la ventana y estados `APPROVED`, `CHANGES_REQUESTED` o `COMMENTED`.
- Métrica principal de concentración: pares únicos (revisor, PR) dentro de la ventana. El número crudo de revisiones se reporta como estadística paralela: varias revisiones de la misma persona en un mismo PR cuentan una sola vez en el par.
- Un revisor que es también autor del PR conserva su par (la revisión existió); no se filtra para no sobreenmendar. En la lectura cualitativa posterior se anotará ese solapamiento.

### Releases

- Evento: `published_at` dentro de la ventana con `draft=false`. Atribución: `author.login` del release si existe. Los releases sin actor quedan en la categoría «no atribuido».

## Cuotas y HHI (por métrica, repositorio y ventana)

- Denominador commits: commits no-bot en la ventana (sin merges en la métrica principal). Denominador PR fusionados: PR no-bot fusionados con la base elegida en la ventana. Denominador revisiones: pares únicos (revisor, PR) no-bot en la ventana. Denominador releases: releases no-bot en la ventana.
- Cuota top-1 (y top-2): participación del actor humano con más eventos en ese denominador. La categoría «no atribuido» permanece dentro del denominador para no inflar la cuota del actor principal y se reporta también como propia cuota.
- HHI: Σ de cuotas al cuadrado sobre el mismo denominador, con «no atribuido» como categoría propia y bots fuera. El HHI se presenta como indicador descriptivo de concentración, nunca como probabilidad de fallo ni «riesgo».

### Regla de denominador mínimo (evaluabilidad), fijada antes de mirar cuotas

- Evaluable por commits: ≥ 30 commits no-bot en la ventana. El 30 replica el diagnóstico de dispersión de la auditoría del paso 4 («menos de 30 commits humanos atribuibles»), aquí formalizado. Los repos no evaluables no se excluyen de las tablas: se muestran con etiqueta «baja actividad» y sus valores, pero no deciden H1/H2.
- Evaluable por PR fusionados (rama principal): ≥ 10 PR no-bot fusionados en la ventana. Orden de magnitud elegido antes de ver resultados, inferior a 30 porque la fusión de PR es un evento más grueso que un commit; se reporta sensibilidad con umbral 20.
- La regla aplica en ambas ventanas con los mismos valores numéricos.

## Hipótesis del protocolo (contrastes preregistrados)

- **H1 (commits):** existe al menos un repositorio evaluable cuyo actor humano principal concentra más del 50 % de los commits no automatizados (no bots) en los 12 meses anteriores al corte. Métrica principal sin merges; se reporta también la versión con merges. Si el repositorio con cuota máxima tiene ≥ 20 % de commits «no atribuido» o ≥ 50 % de bots en su ventana, se declara "inconclusa" en el repositorio que dispare el contraste. Cuota de umbral cruzada aparecerá como tal en la tabla; los casos entre 30 y 50 % no se reportan como «cuasi H1».
- **H2 (commits vs PR fusionados):** clasificación de concentración por cuota del actor humano principal por commits y por PR fusionados a rama principal, con categorías predefinidas: ≤50 %, >50–75 %, >75 %. El contraste «cambia» si algún repo evaluable en ambas métricas cae en categorías distintas. Se reporta cuántos repos cambian y cuáles.
- **H3:** al menos un repositorio con publicación de su paquete en PyPI en la ventana de 12 meses que no registra release de GitHub en la misma ventana, pero sí actividad de mantenimiento observable (algún commit no-bot, PR fusionado no-bot o revisión no-bot en la ventana). La publicación en PyPI se recoge en `pypi-evidence/` después de este plan y antes de correr el contraste, con la API JSON de PyPI al estilo del paso 3: un JSON por distribución con fecha de consulta UTC, conteo de versiones, fechas de publicación registradas en PyPI y SHA-256 del cuerpo. Cualquier error de consulta deja esa distribución como `unavailable`, no como cero. El contraste compara repos (no distribuciones), contando que al menos una de sus distribuciones haya publicado en PyPI dentro de la ventana.
- **H4 (exploratoria):** en al menos un repositorio evaluable en ambos roles, la cuenta con más commits (autoría, no-bot, sin merges) difiere de la cuenta que más PR fusionados a rama principal integra (`merged_by`) o de la cuenta revisora principal (pares únicos). Se reporta una comparación de tres roles por repositorio evaluable. Las métricas identifican cuentas GitHub y actividad observable, no mantenedores formales ni personas: una misma persona puede estar detrás de varias cuentas y viceversa, y la lectura cualitativa es quien cualifica.
- Reportar también los resultados negativos, la sensibilidad a 24 meses, y el efecto de bots, merges y actores no atribuidos. No se ajusta ningún umbral después de ver cifras; si se hace alguna exploración adicional, queda fechada como análisis exploratorio.

## Sensibilidad 12 frente a 24 meses

Todos los contrastes y tablas se calculan en ambas ventanas con las mismas reglas fijas. Los cambios de clasificación se reportan como listas de repositorios que entran o salen de cada umbral. No se recalcula ningún resultado «con otro corte» sin versionar una enmienda a este plan.

## Revisión manual (controles del protocolo general)

- Cada repositorio que dispare una hipótesis (H1–H4) o pueda titularse recibe revisión manual documentada en `audits.md`: identificación del actor principal campo por campo desde los JSON de página, conteo del denominador y registro de cualquier patrón automatizado no declarado o alias sospechoso.
- Repos no mapeados de mayor exposición: no aplica (35/35 mapeados y verificados). Para cubrir exposición se audita el repositorio de la distribución con mayor `paths_from_root` en el grafo congelado.
- Muestra aleatoria de repos adicional con semilla fija: `python3 -c "import random; random.seed(42); print(sorted(random.sample(range(35), 3)))"` sobre la lista de 35 repos ordenada alfabéticamente; solo se auditan los que no coincidan con los anteriores.
- La bitácora de decisiones, cambios de URL, forks, monorepos y actividad importada se apoya en los metadatos del paso 4 (`repository.json` y registro de redirect del paso 3).

## Productos de este paso

- `results/`: tablas derivadas reproducibles (CSV y JSON) con denominadores visibles; el script descentralizado `analyze_activity.py` las genera desde los JSON congelados y compara cada total con `../coverage-descriptive.csv`.
- `pypi-evidence/`: respuestas de PyPI fechadas y con hash (solo H3).
- `figures/`: gráficos interactivos Plotly autocontenidos, con identidad visual de Econopapi, legibles en móvil y en modo claro/oscuro, con cifras de unidad, ventanas y denominadores en pantalla; datos de cada figura exportados junto al HTML.
- `audits.md`: bitácora de auditoría manual de casos extremos.
- `README.md`: guía de reproducción y notas editoriales.
- `SHA256SUMS` y `verification.txt` propios del directorio.

## Lo que estos datos no permiten afirmar

- Quiénes son formalmente los mantenedores de cada paquete (roles, permisos, gobernanza).
- Horas trabajadas, coordinación privada, pagos, empleo o financiación.
- «Bus factor», riesgo operativo de DeudaMundi, probabilidad de abandono y calidad del software: ningún contraste de este paso es una probabilidad de fallo.
- Actividad fuera de GitHub: triage de incidencias, soporte, seguridad privada, documentación, enseñanza.
- Características del ecosistema Python general: la cohorte complementaria de otros backends queda como módulo separado con su propio subprotocolo y denominador.

## Aclaración 1 — criterio de observabilidad del rol de revisión (H4)

Registrada en el mismo commit que el plan, antes de ejecutar el cálculo. Para comparar el rol de revisión en H4, un repositorio es evaluable por ese rol si acumula ≥ 5 pares únicos (revisor, PR) no-bot en la ventana: por debajo, un único revisor concentraría el factor sin contraste real. El resto de reglas del plan no cambia.

## Aclaración 2 — variables de continuidad y variante con bots (completar el diccionario del protocolo)

Registrada al contrastar el plan con el diccionario de variables del protocolo en Notion. Dos omisiones se corrigen antes de calcular estos resultados, con fecha, sin cambiar nada de lo anterior:

1. **Continuidad**: por repositorio, ventana y tipo de evento se calculan (a) meses cubiertos con al menos un evento del flujo (escala 0–12 o 0–24), (b) fecha del último evento observable del flujo dentro de la ventana y (c) para releases, días transcurridos entre los dos releases in-window más recientes, como descripción de cadencia. Se calculan sobre todos los eventos del flujo, incluidos los bots, y en paralelo la última fecha observable de actividad no bot (humana o no atribuida), porque un repositorio cuya única actividad es automatizada debe verse distinto de uno con cualquier actividad humana. La cadencia es descriptiva y no equivale a «salud».
2. **Inclusión/exclusión de bots**: además de las cuotas con bots fuera (métrica principal preregistrada), se reporta la variante con bots incluidos como categorías propias en el mismo ranking, con denominador de todos los eventos en la ventana. Sirve para mostrar dónde la automatización cambia la lectura; no sustituye a la principal.

## Aclaración 3 — selección de casos para lectura profunda

El protocolo exige hasta 6 repositorios «elegidos antes de ver métricas»: dos directos centrales, dos transitivos con más rutas y dos de función distinta (por ejemplo datos, servidor o seguridad), con desempate alfabético por nombre normalizado. Se aplica esa regla de forma mecánica sobre el grafo congelado del paso 2 (directo/transitivo según `nodes.csv`, centralidad por `paths_from_root`, capa funcional según la categoría del paso 1). Resultado de la aplicación mecánica (30 de octubre de 2026):

- Directos centrales por rutas desde la raíz: `SQLAlchemy` (2 rutas) y `alembic` (1, desempate alfabético con apscheduler/fastapi/httpx/psycopg, todos con 1).
- Transitivos con más rutas: `typing_extensions` (17) e `idna` (4).
- Función distinta, dos de tres capas con repositorio atribuido — datos: `psycopg`; servidor: `starlette` (orden «datos, servidor o seguridad» del propio protocolo; la capa de seguridad, `certifi`, queda fuera por el tope de 6).

Casos de lectura profunda: sqlalchemy, alembic, typing_extensions, idna, psycopg (repos. `psycopg/psycopg`), starlette (`kludex/starlette`) — seis repositorios. La regla determinista no depende de ninguna métrica de actividad pública. Nota de transparencia de proceso: durante la depuración de los agregados de este paso se vieron cuotas agregadas; la regla de selección siguió siendo mecánica sobre los datos del paso 2 y en ningún momento se seleccionó por resultados de actividad. La lectura cualitativa profunda pertenece al paso posterior, con las plantillas del protocolo (madurez, gobernanza, trabajo invisible, financiación declarada).
