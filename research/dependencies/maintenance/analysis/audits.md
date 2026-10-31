# Paso 5 — bitácora de auditoría manual de casos

**Fecha:** 30 de octubre de 2026 UTC. **Datos:** la extracción congelada del paso 4 (`../data/`), sin acceso a GitHub.

**Método.** Dos implementaciones independientes (`analyze_activity.py` y `audit_manual.py`, con clasificadores y recorridos escritos por separado) contrastan conteos y actor principal por repositorio y ventana sobre el conjunto preregistrado en `plan.md`: repos que disparan hipótesis, repos con cuota muy alta, muestra aleatoria con semilla 42 (`agronholm/apscheduler`, `fastapi/fastapi`, `pallets/click`) y el repositorio de mayor exposición del grafo (`typing_extensions`, 17 rutas → `python/typing_extensions`): 24 repositorios × 2 ventanas. La evidencia por caso (identidad del actor tal como GitHub la declara: `login`, `id`, `type`, marca de bot, y muestra del registro crudo) está en `results/audit-packs.json`.

**Resultado del contraste:** cero discrepancias en los campos comparados (commits totales/fusión/no-bot/no atribuidos, PR fusionados totales/a rama principal, revisiones, releases, actor top-1 de commits por conteo y por cuota recalcada sobre el denominador).

**Honestidad de proceso.** Durante la auditoría se detectaron y corrigieron tres errores, registrados por separado:

1. Un error del *script de auditoría* (contaba actores sin atribuir como humanos). No afectó los resultados publicados, que contaban bien.
2. Un error del *script principal*, destapado por la discrepancia que la auditoría detectó en fastapi: el denominador de cuotas de commits incluía a los bots. Corregido en la misma sesión, antes de declarar resultados, y todo el conjunto fue re-verificado (consistencia interna y contraste con `../coverage-descriptive.csv`, que tabula los totales sin interpretación).
3. Una falsa alarma de esta bitácora: la cuota 42/45 de mako provenía de separar 3 commits de fusión del total de 45; el denominador correcto es 42 y el cálculo era correcto.

Las reglas y umbrales se mantuvieron exactamente como se preregistraron en `plan.md`. Ningún umbral se ajustó después de ver cifras.

## Identidades y automatización no declarada (sin recategorizar)

El protocolo del paso 4 marca bot solo con `type=Bot` o sufijo `[bot]`. Esta auditoría no recategoriza cuentas; registra patrones para cualificar lecturas y titulares:

- `sqla-tester` (id 8250554, `type=User`) en `sqlalchemy/sqlalchemy` y `sqlalchemy/alembic`: es la cuenta con más pares de revisión en ambos (96 pares en sqlalchemy y 19 en alembic, 12m), por delante de cuentas con patrón humano esperado. Es la cuenta automatizada que reporta ejecuciones de CI de SQLAlchemy. No está declarada bot en los datos. La cuota de "quién revisa" en estos dos repos no debe leerse como personas sin lectura cualitativa. El contraste de H4 para `sqlalchemy/sqlalchemy` se apoya en el rol de *integración* (`CaselIT`, cuenta con patrón humano esperado), no en el de revisión.
- `claude` (id 81847, `type=User`) en `laurent-laporte-pro/deprecated`: actor principal de commits en 12m (36 de 45 no-fusión no-bot; committer igual al autor, sin sufijo de bot). El patrón es compatible con una cuenta de agente automatizado no declarada como bot. La regla del protocolo la clasifica como actor con cuenta; se reporta la cuota con esta advertencia y la lectura de "quién" queda pendiente de verificación pública adicional (paso cualitativo).
- `invalid-email-address` (id 148100, `type=User`): cuenta materializadora de GitHub; en `fastapi/fastapi` acumula 462 commits en la ventana de 24 meses (0 en 12m). Permanece como cuenta propia con login en los denominadores (ni bot ni no-atribuida), con la etiqueta "patrón probablemente automatizado, no declarado". Cuantificado con muestra independientemente recontada en `final-audits/manual-sample-audits.json`.

## H1 — cuota top-1 de commits por actor humano (12 meses, sin fusiones, no-bot)

22 de 35 repos evaluable por commits (≥ 30 en el denominador). En **14 de 22** la cuota supera el 50 %. Tabla generada desde `repo-metrics.csv` (denominador = commits humanos + no atribuidos, sin fusiones):

| Repositorio | Denominador | Actor principal | Cuota | Con fusiones |
| --- | ---: | --- | ---: | ---: |
| sqlalchemy/mako | 42 | zzzeek | 1.000 | 1.000 |
| grahamdumpleton/wrapt | 337 | GrahamDumpleton | 0.964 | 0.969 |
| python-websockets/websockets | 209 | aaugustin | 0.947 | 0.948 |
| kjd/idna | 119 | kjd | 0.916 | 0.945 |
| alisaifee/limits | 30 | alisaifee | 0.900 | 0.900 |
| kludex/uvicorn | 154 | Kludex | 0.818 | 0.818 |
| sqlalchemy/alembic | 105 | zzzeek | 0.752 | 0.780 |
| laurent-laporte-pro/deprecated | 50 | claude | 0.720 | 0.633 |
| kludex/starlette | 222 | Kludex | 0.680 | 0.680 |
| jpadilla/pyjwt | 73 | jpadilla | 0.671 | 0.671 |
| psycopg/psycopg | 231 | dvarrazzo | 0.658 | 0.717 |
| agronholm/apscheduler | 37 | agronholm | 0.649 | 0.649 |
| sqlalchemy/sqlalchemy | 473 | zzzeek | 0.634 | 0.710 |
| pydantic/pydantic | 529 | Viicos | 0.548 | 0.547 |

Sensibilidad 24 meses: 19 de 28 evaluables superan el 50 %; el actor principal sigue siendo el mismo en los casos clave (detalle en `results/hypotheses.json`).

Apuntes que condicionan la interpretación:

- **sqlalchemy/mako (1.000):** los 42 commits no-fusión 12m son todos de `zzzeek` (id 128223); sin bots ni no atribuidos; 3 commits de fusión permanecen excluidos de la métrica principal.
- **zzzeek es actor principal en tres repos distintos** (mako, alembic, sqlalchemy). Sin fusionar alias ni inferir nada sobre personas: es el mismo `login/id` observable según GitHub.
- **grahamdumpleton/wrapt:** rama principal `develop`; los releases 12m son casi todos de automatización declarada, `github-actions[bot]` (32 de 42), y solo 4 de `GrahamDumpleton`; no elimina la cuota de autoría, cualifica la lectura de "quién publica".
- **alisaifee/limits:** la cuota sube de 0.900 sin fusiones a 0.900 con fusiones (coinciden porque alisaifee se auto-fusiona con autorías propias); dependabot aporta 20 de 50 commits no-fusión (40 %). Caso instructivo de por qué las fusiones se separan de la autoría.
- **laurent-laporte-pro/deprecated:** el propio `laurent-laporte-pro` firma 8 de 45; `claude`, ver arriba; los 10 commits de fusión del año corresponden en su mayoría al propio laurent-laporte-pro.
- **certifi/python-certifi:** de 44 commits 12m, 37 son de `dependabot[bot]` y solo 7 humanos (los dos primeros: `alex` con 2, `hugovk` con 1); 43 PR fusionados, 37 de ellos bots; hay 35 pares de revisión humanos. Publica a PyPI cada vez que la lista de CA se actualiza, con cero releases de GitHub (ver H3).

## H2 — cambio de categoría entre cuota por commits y por PR fusionados (12 meses)

Evaluable en ambas métricas (≥30 commits y ≥10 PR fusionados a rama principal, ambos no-bot): 18 repos. Cambio de categoría en **6**:

| Repositorio | Cuota commits | Categoría | Cuota PR | Categoría |
| --- | ---: | --- | ---: | --- |
| agronholm/apscheduler | 0.649 | 50–75 % | 0.077 | ≤50 % |
| grahamdumpleton/wrapt | 0.964 | >75 % | 0.308 | ≤50 % |
| jpadilla/pyjwt | 0.671 | 50–75 % | 0.226 | ≤50 % |
| psycopg/psycopg | 0.658 | 50–75 % | 0.420 | ≤50 % |
| python-websockets/websockets | 0.947 | >75 % | 0.694 | 50–75 % |
| sqlalchemy/sqlalchemy | 0.634 | 50–75 % | 0.133 | ≤50 % |

Sensibilidad 24 meses: cambian 10 de 25. Apuntes:

- En los seis casos, la concentración por autoría de commits es mayor que por PR fusionados: la integración de PR reparte más el trabajo visible.
- **fastapi/fastapi** NO cambia: 0.722 vs 0.694 — ambas caen en 50–75 %. Es un contraejemplo útil del umbral por categorías, no una ausencia de concentración.
- Con bots incluidos en el ranking (variante de la Aclaración 2), el actor top por commits en fastapi pasa a ser `github-actions[bot]` (0.380 de 1.773), y en certifi, `dependabot[bot]` (0.659). La automatización cambia el cuadro y por eso el denominador principal la excluye.

## H3 — repos con publicación en PyPI, cero releases de GitHub y actividad observable (12 meses)

Califican **4** repos (detalle y recibos: `results/h3-test.csv`, `pypi-evidence/`):

- `psycopg/psycopg` — el caso más claro: 0 releases de GitHub en la ventana, publicación de `psycopg` y `psycopg-binary` en PyPI dentro de la ventana, 230 commits no-fusión no-bot, 81 PR fusionados a rama principal y 73 pares de revisión humanos.
- `certifi/python-certifi` — 7 commits humanos, 6 PR fusionados no-bot, 35 pares de revisión; publicación mensual típica de la lista de CA en PyPI.
- `encode/httpx` — 3 commits humanos, 3 PR fusionados no-bot, 32 pares de revisión; publica 0.28.x en PyPI en la ventana.
- `regebro/tzlocal` — 23 commits humanos de `regebro`, 6 PR fusionados no-bot; publica en PyPI en la ventana.

Rasgo informativo inverso (0 releases de GitHub, actividad, pero **sin** publicación en PyPI 12m): `encode/httpcore`, `python-hyper/h11`, `yaml/pyyaml`. La ausencia de release no es, en ninguna dirección, prueba de abandono.

## H4 — divergencia de roles (cuenta top por commits vs revisión e integración)

12 meses, repos evaluables en commits y PR (y ≥5 pares de revisión para el rol de revisión): divergencias en **6**:

| Repositorio | Top commits | Top integración (`merged_by`) | Top revisión (pares) |
| --- | --- | --- | --- |
| fastapi/fastapi | tiangolo | tiangolo | YuriiMotov |
| jpadilla/pyjwt | jpadilla | jpadilla | auvipy |
| pallets/click | kdeldycke | Rowlando13 | Rowlando13 |
| python/typing_extensions | AlexWaygood | AlexWaygood | JelleZijlstra |
| sqlalchemy/sqlalchemy | zzzeek | CaselIT | sqla-tester (automatización) |
| theskumar/python-dotenv | theskumar | theskumar | Wkhanex |

Sensibilidad 24 meses: la comparación se rehace con las mismas reglas (ver `hypotheses.json`). En `python/typing_extensions` el caso cambia de lectura entre ventanas: en 12m AlexWaygood es top de commits y JelleZijlstra de revisión; en 24m JelleZijlstra encabeza commits (34/151) y revisión (86 pares). El actor principal puede depender de la ventana y así se declara.

## Muestra aleatoria y repos por exposición

- `agronholm/apscheduler` (semilla 42; disparador de H2): agronholm 0.649 commits / 0.077 PR; el casi-cruce del umbral de H1 (0.649) y su caída fuerte en PR lo convierten en ejemplo pedagógico de sensibilidad de categorías.
- `fastapi/fastapi` (semilla 42): ver contraejemplo de H2 arriba; bots declarados aportan 1.035 de 1.773 commits 12m (58 %) y son la mayor parte de los PR fusionados en 24m.
- `pallets/click` (semilla 42): 106 de 195 PR fusionados 12m van a bases distintas de `main` (lanes de release/decisiones del proyecto) y no alcanza el mínimo de 10 PR a rama principal: H2 queda no evaluable para click por la regla preregistrada, H4 sí se reporta.
- `python/typing_extensions` (mayor exposición, 17 rutas): ver H4.

## Límites de esta auditoría

- Se observa lo que GitHub declara por cuenta; no se fusionan alias ni se identifica a una persona detrás de varias cuentas. Duplicaciones no detectadas podrían mover las cuotas en cualquier dirección.
- Las revisiones se observan como pares (revisor, PR) dentro de las ventanas y heredan los límites de descubrimiento del paso 4 (PR paginados por `updatedAt`).
- La actividad de repos compartidos (`pydantic`) puede incluir trabajo ajeno al paquete congelado; el protocolo general lo admite y obliga a señalarlo.
- Un incendio de auditoría: cero discrepancias entre implementaciones no certifica que GitHub entregara todo el histórico (límite ya declarado en el paso 4); certifica la reproducibilidad del cálculo sobre los datos congelados.
