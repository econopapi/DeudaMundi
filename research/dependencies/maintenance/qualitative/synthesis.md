# Síntesis científica integrada y triangulación de H1–H4

**Paso 6 · 2 de noviembre de 2026.** Este documento **no recalcula** ninguna
hipótesis: confronta los resultados descriptivos congelados del Paso 5 con la
evidencia cualitativa de los seis expedientes (`cases/`) y ordena las
conclusiones por nivel de evidencia. Los valores de referencia del dictamen se
conservan exactos.

## 0. Respuesta a la pregunta central

**¿Qué puede saberse sobre quién realiza, coordina y publica el mantenimiento
de las dependencias Python de DeudaMundi, y hasta dónde alcanza la evidencia?**

En el nivel que las fuentes permiten —cuentas GitHub, roles documentados y
eventos públicos— se sabe lo siguiente, para **este** universo congelado (37
distribuciones → 35 repositorios; ventana `[2025-10-30, 2026-10-30)`):

1. **Realiza (autoría):** en 14 de 22 repositorios evaluables una única cuenta
   supera el 50 % de los commits no automatizados sin fusiones (H1 12 m), pero
   el grado de concentración varía enormemente entre casos (0,225–1,000 en las
   distintas ventanas) y **no** es un proxy de riesgo.
2. **Coordina (integración y revisión):** la integración suele repartirse más
   que la autoría (H2: 6 de 18 repos cambian de categoría; H4: 6 repos tienen
   cuentas top distintas por rol). En varios repositorios la revisión observable
   incluye automatización no declarada que contamina la lectura literal.
3. **Publica:** la publicación tiene mecanismos propios por proyecto (releases
   de GitHub materializados por bots de pipeline, publicación directa en PyPI
   sin GitHub Releases, o releases humanos): H3 documentó 4 casos con PyPI sin
   releases de GitHub **y** mantenimiento observable.
4. **Organiza y financia (documental, E1/E2):** los seis expedientes muestran
   modelos distintos —organización fundacional (`python/typing_extensions`),
   organización de proyecto con roles nombrados (`sqlalchemy/*`, `psycopg`),
   cuenta individual con procesos automatizados (`kjd/idna`) y proyecto
   transferido de una organización a una cuenta personal (`kludex/starlette`)—
   con patrocinio declarado en cuatro de seis y ausencia de declaración en dos.
5. **Hasta dónde alcanza:** hasta la evidencia pública fechada. El trabajo no
   observable (C8), la identidad real detrás de las cuentas, la dedicación
   remunerada y la continuidad futura **no** son conocibles con estos datos.

---

## 1. Triangulación — H1 (cuota top-1 de commits)

### 1.1 Resultado descriptivo congelado (inamovible)

12 m: **22** repositorios evaluables (≥ 30 commits no-bot sin fusiones);
**15** con cuota numérica > 50 %; **1 inconcluso** por la regla preregistrada de
bots (`fastapi/fastapi`, bots ≥ 50 % de sus commits); **14 conclusivos > 50 %**.
Sensibilidad 24 m: 28 evaluables, 19 > 50 %, 0 inconclusos. De los seis casos:
`sqlalchemy/mako` no es caso, pero entre los casos figuran idna (0,916),
alembic (0,7524), starlette (0,6802), psycopg (0,658), sqlalchemy (0,6342) como
conclusivos, y typing_extensions (0,4565) por debajo del umbral.

### 1.2 Interpretación permitida

La **distribución de commits por cuenta** en la rama principal observada está
concentrada en la cuenta principal en la mayoría de los repositorios
evaluables. Los expedientes muestran que esa cuenta suele coincidir con un rol
documentado de autoría/mantenimiento principal (E1: «creator and primary
maintainer» en psycopg; «developed by Mike Bayer» en alembic; lead declarado en
starlette; autoría singular en idna).

### 1.3 Interpretación NO permitida

«Un solo mantiene X», «riesgo de abandono», «bus factor = 1», «si esa cuenta
desaparece el proyecto muere». La cuota mide eventos atribuidos a una cuenta en
una ventana; no identifica personas, no mide trabajo no registrado y no es una
probabilidad.

### 1.4 Contexto cualitativo

- Donde la documentación nombra roles (sqlalchemy, psycopg, typing_extensions),
  la cuenta top de autoría **coexiste** con segundos contribuidores activos y
  con roles declarados de coordinación que los commits no capturan (psycopg:
  «Operations Lead … project coordination, release support, issue triage»).
- En sqlalchemy/alembic la autoría se concentra más que en ningún otro caso
  (0,7524–1,000 en mako) y aun así hay copropietarios de paquete (PyPI Owners:
  `CaselIT`, `zzzeek`) y cinco miembros públicos de organización.
- typing_extensions (el más dependido: 17 rutas) es el **menos** concentrado:
  exposición y concentración son dimensiones independientes.

### 1.5 Contraejemplo / límite de validez

`python/typing_extensions` (0,4565 en 12 m; 0,2252 en 24 m) y la variación de
identidad top entre ventanas en el mismo repo demuestran que el «actor
principal» es sensible a la ventana y al flujo. Además, las cuotas con bots
incluidos cambian el cuadro (fastapi: top pasa a `github-actions[bot]`).

### 1.6 Redacción editorial recomendada

> En 14 de los 22 repositorios con actividad suficiente, una sola cuenta GitHub
> firmó más de la mitad de los commits no automatizados del año anterior al
> corte. La lectura cualitativa muestra que esa cuenta suele corresponderse con
> el rol de autoría o mantenimiento principal que los propios proyectos
> documentan —pero también que, en los mismos proyectos, existen copropietarios
> de paquetes, revisores activos y tareas de coordinación que ningún commit
> registra. La cifra describe eventos, no personas ni riesgos.

Fuentes: `analysis/results/hypotheses.json` (H1), `final-audits/traceability-h1h4.csv`,
`cases/*` §B/§C. Nivel: E2 + E1 cualificado.

## 2. Triangulación — H2 (cambios de categoría commits vs PR)

### 2.1 Resultado congelado

12 m: **6 cambios de categoría de 18** repos evaluables en ambas métricas
(24 m: 10 de 25). Contraejemplo registrado: `fastapi/fastapi` **no** cambia
(0,722 → 0,694).

### 2.2 Interpretación permitida

La concentración medida por autoría de commits y la medida por autoría de PR
fusionados a rama principal **no son intercambiables**: en los seis casos que
cambian, la cuota por commits es mayor, es decir, la integración de PR observa
una base de contribución más repartida que la autoría de commits.

### 2.3 Interpretación NO permitida

Que «la integración sea más democrática» (juicio de valor), que las dos métricas
se refuercen mutuamente donde coinciden, o que el cambio de categoría implique
cambio en el tiempo (es una comparación entre métricas, no entre fechas).

### 2.4 Contexto cualitativo

- **Mecánica squash verificada** (auditoría fechada 01-11-2026): en
  `kludex/uvicorn`, `python/typing_extensions`, `kludex/starlette` y
  `redis/redis-py` los commits sin merges **igualan exactamente** a los PR
  fusionados (materialización 1:1 vía `web-flow`): allí las dos cuotas miden el
  mismo flujo dos veces y Δ = 0 **no** es confirmación independiente.
- **Canal no-PR (E1/E3):** en sqlalchemy/alembic la revisión ocurre en Gerrit
  («Pull requests for code changes are never merged directly»): el descenso de
  la cuota por PR allí refleja el canal de entrada, no un reparto de autoría.
- psycopg sí cambia (0,658 → 0,4198) y la documentación muestra una base de
  contribución plural (35 cuentas con PR humanos en 12 m).

### 2.5 Contraejemplo / límite

`fastapi/fastapi` (no cambia; ambas cuotas 50–75 %) y los cuatro casos
squash-mirror: el umbral por categorías es grueso y la coincidencia de
categorías no prueba estabilidad del constructo.

### 2.6 Redacción editorial recomendada

> Si medimos por commits o por PR fusionados, la imagen cambia en 6 de los 18
> repositorios comparables: la autoría de commits se concentra más que la de
> PR. Dos advertencias documentadas: donde los proyectos fusionan en squash,
> ambas métricas cuentan el mismo trabajo dos veces; y donde la integración
> real pasa por herramientas externas a GitHub, la métrica de PR observa un
> canal secundario.

Fuentes: `hypotheses.json` (H2), `audits.md` §verificación 01-11-2026,
`cases/sqlalchemy-*.md` §C, `cases/kludex-starlette.md` §C.

## 3. Triangulación — H3 (PyPI sin GitHub Releases)

### 3.1 Resultado congelado

**4 repos califican** (12 m): `psycopg/psycopg`, `certifi/python-certifi`,
`encode/httpx`, `regebro/tzlocal` — publicación en PyPI en la ventana, **0**
releases de GitHub y actividad observable (commits/PR/pares no-bot). Rasgo
inverso (0 releases + actividad + **sin** PyPI): httpcore, h11, pyyaml.

### 3.2 Interpretación permitida

La ausencia de objetos GitHub Release **no** es un indicador de ausencia de
mantenimiento ni de publicación: existen proyectos que distribuyen versiones
por otros canales. H3 fue diseñado para refutar ese atajo.

### 3.3 Interpretación NO permitida

Que «esos proyectos estén sanos» (la inversa del atajo sería igual de
improcedente), que la publicación en PyPI implique mantenimiento completo, o
que los proyectos sin releases y sin PyPI (httpcore, h11, pyyaml) estén
abandonados.

### 3.4 Contexto cualitativo

- psycopg (caso cualitativo): `docs/release.rst` documenta el proceso exacto
  —tags + twine a PyPI— y la API de GitHub devuelve **cero** releases: la
  «ausencia» medida es un **rasgo de proceso documentado** (E1/E2).
- El caso inverso también se documenta: idna publica releases **automáticamente**
  (`github-actions[bot]` + Sigstore): aquí la métrica de «quién publica» registra
  un bot declarado, no a una persona.

### 3.5 Contraejemplo / límite

Los tres casos «inversos» (httpcore, h11, pyyaml) recuerdan que la ausencia es
ambigua en **ambas** direcciones; y starlette, con 23 releases humanos, muestra
que tener releases tampoco dice nada sobre el reparto del trabajo.

### 3.6 Redacción editorial recomendada

> Cuatro repositorios publicaron en PyPI durante el año observado sin crear un
> solo GitHub Release: psycopg, certifi, httpx y tzlocal. La lectura de sus
> procesos confirma que publicar versiones y crear releases de GitHub son
> decisiones distintas. «Sin releases» no significa «sin mantenimiento» —tampoco
> lo contrario: significa que hay que mirar en otro lugar.

Fuentes: `results/h3-test.csv`, `analysis/pypi-evidence/`, `cases/psycopg-psycopg.md` §B/§C.

## 4. Triangulación — H4 (divergencia de roles)

### 4.1 Resultado congelado

12 m: **6 repos con divergencia** entre la cuenta top de commits y la top de
integración (`merged_by`) o revisión (pares únicos): fastapi, pyjwt, click,
typing_extensions, sqlalchemy (integrador `CaselIT`; rol de revisión
contaminado por `sqla-tester`), python-dotenv. Evaluabilidad del rol de revisión
por **pares no-bot totales ≥ 5** (Aclaración 1). Sensibilidad 24 m: los seis
divergentes se mantienen; en typing_extensions los tops cambian de identidad.

### 4.2 Interpretación permitida

En parte del universo, **autoría, integración y revisión recaen en cuentas
distintas**: «quién escribe», «quién fusiona» y «quién revisa» son preguntas
con respuestas distintas. La documentación cualitativa corrobora la distinción
de roles (psycopg nombra funciones separadas; sqlalchemy declara dos
mantenedores con reparto observable entre autoría e integración).

### 4.3 Interpretación NO permitida

Que las cuentas top sean «los verdaderos responsables», que la divergencia
implique distribución de poder o salud organizacional, ni que la coincidencia
(en idna, starlette) signifique unipersonalidad literal.

### 4.4 Contexto cualitativo y automatización no declarada

Patrones documentados (sin recategorizar; `../analysis/audits.md`):

- **`sqla-tester`** (id 8250554, `type=User`): cuenta automatizada de CI de
  SQLAlchemy; es el top de revisión en sqlalchemy (96 pares) y alembic (19) y
  materializa los 23+12 releases de la ventana. La lectura literal de «quién
  revisa/publica» en ambos repos identifica un **mecanismo**, no a personas. El
  contraste H4 de sqlalchemy se apoyó por eso en integración (`CaselIT`).
- **`claude`** (id 81847, `type=User`): top de commits en
  `laurent-laporte-pro/deprecated` (36/45 no-fusión en 12 m). Patrón compatible
  con agente automatizado **no declarado**; la cuenta conserva su clasificación
  congelada y su cuota se reporta con esta advertencia. Ninguna lectura de
  «quién mantiene» ese repo debe ignorar este dato.
- **`invalid-email-address`** (id 148100): cuenta materializadora de GitHub;
  0 eventos en 12 m y 462 commits en 24 m en fastapi. La sensibilidad 24 m de
  fastapi debe leerse con esta marca: su entrada en la ventana ampliada es un
  artefacto de atribución.

### 4.5 Contraejemplo / límite

En 6 de 12 (aprox.) repos evaluables los tres roles **coinciden** en la misma
cuenta (idna, starlette, psycopg…): la divergencia no es la norma universal, y
la coincidencia tampoco prueba concentración de autoridad formal.

### 4.6 Redacción editorial recomendada

> En seis repositorios, la cuenta que más escribe no es la que más fusiona o
> revisa. Es la evidencia más directa de que «mantener» es un conjunto de
> tareas separadas. Una advertencia: parte de la revisión observable la
> realizan automatizaciones no declaradas como bots — sqla-tester en los
> proyectos SQLAlchemy —, y una cuenta como claude puede ser un agente
> automatizado; las métricas identifican cuentas, y la lectura cualitativa es
> quien evita convertir un ranking en un retrato.

Fuentes: `results/hypotheses.json` (H4), `final-audits/traceability-h1h4.csv`,
`audits.md` §identidades, `cases/*` §C.

## 5. Conservación de unidades y sensibilidad (obligatorio)

- **24 meses:** todos los contrastes se conservan con sus valores (H1: 28/19/0/19;
  H2: 10 de 25). Las diferencias entre ventanas se presentan como sensibilidad,
  nunca como tendencia temporal.
- **Revisiones crudas vs pares únicos revisor–PR:** unidades distintas que no se
  intercambian ni se suman. Cuotas de bots 12 m: 21,3 % commits / 16,8 % PR /
  24,8 % revisiones crudas / **28,5 % pares únicos** / 39,3 % releases. Las
  figuras v2 (fig5) las muestran separadas.

## 6. Ordenación de conclusiones por nivel de evidencia

### 6.1 Demostrados (E1/E2, verificables)

1. El universo: 37 distribuciones de ejecución → 35 repositorios únicos, con
   atribución documental verificada y dos repositorios compartidos.
2. Las cifras de H1–H4 y su sensibilidad, con denominadores, evaluabilidad y
   exclusiones publicados y reproducibles.
3. Los procesos documentados de los seis proyectos: políticas de contribución,
   canales de revisión (incluido Gerrit en SQLAlchemy), procesos de release
   (incluida la publicación sin GitHub Releases en psycopg y la automatizada y
   firmada en idna) y roles nombrados (psycopg: dos cargos; sqlalchemy: dos
   mantenedores declarados; starlette: autor y mantenedor nombrados en PyPI).
4. La transferencia de starlette de `encode` a la cuenta `Kludex` (2025-09),
   con redirección activa y metadatos que evolucionan entre la versión congelada
   y la actual.
5. La existencia de patrocinio declarado en cuatro de los seis casos
   (sqlalchemy/alembic, psycopg, starlette; organización `python` sin proyecto
   específico en typing_extensions) y su **ausencia de declaración** en idna y
   typing_extensions (E4/E2 de ausencia).

### 6.2 Cualificados por la lectura documental (E2 + E1 que matiza)

1. Las cuotas top-1 de autoría se corresponden con roles documentados de
   autoría principal, pero los mismos proyectos muestran segundos actores,
   copropiedad de paquetes y reparto de integración/revisión.
2. Las métricas de revisión en sqlalchemy/alembic están contaminadas por
   `sqla-tester`; las de «quién publica» en esos repos identifican un pipeline.
3. La comparación commits/PR en los repos squash-mirror no es doble evidencia.
4. typing_extensions, la dependencia más transversal, es la de autoría más
   repartida; idna, la más concentrada, se autodescribe como «team of
   volunteers»: la documentación y las métricas no siempre coinciden literalmente.

### 6.3 Hipótesis económicas interpretativas (E3; nunca resultados)

1. El patrón de costos (reproducción ≈ 0 / mantenimiento persistente) es
   compatible con lo observado, pero este estudio **no mide costos**.
2. Los modelos organizativos observados (fundación, organización de proyecto,
   cuenta individual, proyecto transferido) son respuestas distintas al
   problema de la provisión de un bien compartido (lente: Benkler; Eghbal;
   Osborne) — **sin** que pueda evaluarse cuál es más sostenible.
3. La financiación declarada tiende a canalizarse por patrocinio de personas o
   suscripciones (Tidelift, GitHub Sponsors, consorcio de empresas en el caso
   psycopg): la literatura (Osborne) sugiere que financiar el mantenimiento es
   una decisión distinta a financiar novedades; aquí queda como hipótesis.

### 6.4 Preguntas aún abiertas

1. La identidad y continuidad reales detrás de las cuentas (¿quiénes son los
   «maintainers» formales donde no hay documento?) — requiere revisión factual
   con los proyectos.
2. El trabajo no observable (soporte, seguridad privada, coordinación): existe
   documentado como categoría (psycopg lo nombra en su rol de operaciones), no
   medido.
3. La sostenibilidad económica de cada proyecto y su relación con la
   concentración observada.
4. La cohorte comparativa de otros backends (diferida;
   `deferred-comparative-cohort.md`).

### 6.5 Límites estructurales de los datos

Los nueve del dictamen y los siete de `limitations.md` (rama por fecha,
`updatedAt`, tags sin release, cobertura ≠ completitud, alias, compartimiento,
corte exclusivo; posterioridad de las fuentes web; documentación ≠ práctica;
cuentas ≠ personas; solo financiación declarada; trabajo no observable).

## 7. Síntesis por caso (una línea cada uno)

| Caso | Lo que la evidencia permite decir |
|---|---|
| `sqlalchemy/sqlalchemy` | Autoría muy concentrada (`zzzeek`), integración y copropiedad repartidas (`CaselIT`); revisión y publicación materializadas por la automatización no declarada `sqla-tester`; canal de entrada real en Gerrit |
| `sqlalchemy/alembic` | Misma organización y procesos; autoría altamente concentrada; flujo PR casi inexistente (no evaluable H2/H4) por diseño del flujo, no por inactividad |
| `python/typing_extensions` | La dependencia más transversal y la menos concentrada; ~6 cuentas con roles de paquete; proceso de release formal con PSF de fondo; sin financiación del proyecto declarada |
| `kjd/idna` | Máxima convergencia de roles en la cuenta `kjd` (H4 coincide, H1 0,916) con autodescripción como «team of volunteers»; publicación automatizada y firmada; sin financiación declarada |
| `psycopg/psycopg` | Caso H3 por excelencia (PyPI sin GitHub Releases, proceso documentado); dos cargos nombrados (técnico y operaciones); patrocinio corporativo declarado; propiedad de paquete ≠ cuenta top de eventos |
| `kludex/starlette` | Concentración alta en todos los roles + transferencia documentada de organización a cuenta personal (2025-09) y debate público sobre el modelo de propiedad: el caso más sensible para revisión factual |
