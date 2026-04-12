# API DeudaMundi

Backend REST en **FastAPI** para el Atlas Global de Deuda Externa Soberana.

Sirve datos históricos de deuda externa por país, rankings comparativos, periodos de gobierno y un pipeline ETL multifuente con trazabilidad metodológica.

---

## Tabla de contenidos

1. [Arquitectura interna](#1-arquitectura-interna)
2. [Modelo de datos](#2-modelo-de-datos)
3. [Pipeline ETL](#3-pipeline-etl)
4. [Referencia de API REST](#4-referencia-de-api-rest)
5. [Cache y rendimiento](#5-cache-y-rendimiento)
6. [Seguridad](#6-seguridad)
7. [Configuración](#7-configuración)
8. [Desarrollo local](#8-desarrollo-local)
9. [Testing](#9-testing)
10. [Base de datos y migraciones](#10-base-de-datos-y-migraciones)
11. [Despliegue en producción](#11-despliegue-en-producción)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. Arquitectura interna

```text
app/
├── api/
│   ├── dependencies.py          # Dependency injection (admin API key guard)
│   └── v1/
│       ├── router.py            # Agrupa todos los sub-routers
│       └── endpoints/
│           ├── health.py        # GET /health
│           ├── countries.py     # GET /countries, /countries/{iso3}, /history, /governments, /compare
│           ├── rankings.py      # GET /rankings
│           ├── globe_data.py    # GET /globe-data
│           └── admin.py         # POST /admin/etl/*
├── core/
│   ├── config.py                # Pydantic Settings (env vars, defaults, normalización de DB URL)
│   ├── cache.py                 # Redis cache-aside (get/set/invalidate)
│   └── security.py              # CORS, rate limiting (Slowapi), security headers
├── db/
│   ├── base_class.py            # Base declarativa SQLAlchemy
│   └── session.py               # SessionLocal factory + engine
├── etl/
│   ├── world_bank_client.py     # Cliente HTTP World Bank API v2 (httpx, paginado)
│   ├── imf_client.py            # Cliente HTTP IMF DataMapper (proxy opcional)
│   ├── governments_wikidata_client.py  # Cliente SPARQL Wikidata (chunked, con fallback P6/P35)
│   ├── transform.py             # Normalización, cálculo de métricas derivadas, merge por prioridad
│   ├── types.py                 # Dataclasses: CountrySeed, DebtRecordSeed
│   ├── repository.py            # Upserts PostgreSQL (ON CONFLICT), delete proxy rows
│   ├── run_world_bank.py        # Orquestador principal del ETL global
│   ├── seed_governments.py      # Orquestador ETL de gobiernos
│   ├── report_gaps.py           # Generador de reportes de cobertura
│   └── scheduler.py             # APScheduler cron (BackgroundScheduler)
├── models/
│   ├── country.py               # ORM: Country
│   ├── debt_record.py           # ORM: DebtRecord
│   ├── government.py            # ORM: Government
│   └── etl_run.py               # ORM: EtlRun
├── schemas/
│   ├── country.py               # Pydantic: request/response para countries, history, governments, globe, compare
│   └── ranking.py               # Pydantic: request/response para rankings
├── services/
│   ├── countries.py             # Lógica de negocio: listado, detalle, historia, comparación, globe data
│   ├── rankings.py              # Lógica de negocio: rankings por métrica
│   └── equivalences.py          # Equivalencias emocionales (hospitales, salarios)
└── main.py                      # App factory: FastAPI + lifespan (scheduler) + security + router
```

### Capas y responsabilidades

| Capa | Responsabilidad | Archivos clave |
|---|---|---|
| **Endpoints** | Validación HTTP, serialización, cache lookup/store | `api/v1/endpoints/*` |
| **Services** | Queries SQLAlchemy, lógica de negocio, construcción de DTOs | `services/*` |
| **Models** | Definición ORM, relaciones, constraints | `models/*` |
| **Schemas** | Contratos Pydantic de entrada/salida | `schemas/*` |
| **ETL** | Extracción, transformación, carga, reportes | `etl/*` |
| **Core** | Configuración, cache, seguridad | `core/*` |

---

## 2. Modelo de datos

### 2.1 Diagrama entidad-relación

```text
┌─────────────────┐        ┌─────────────────────┐
│   countries      │───1:N──│   debt_records        │
│                 │        │                     │
│ id         PK   │        │ id            PK    │
│ iso2       UQ   │        │ country_id    FK    │
│ iso3       UQ   │        │ year                │
│ name_es         │        │ total_ext_debt_usd  │
│ name_en         │        │ debt_pct_gdp        │
│ region     IDX  │        │ debt_per_capita_usd │
│ subregion       │        │ gdp_usd             │
│ population      │        │ source              │
│ capital         │        │ debt_concept        │
│ flag_url        │        │ data_source         │
│                 │        │ data_vintage        │
│                 │        │ updated_at          │
│                 │        │ UQ(country_id,year) │
└────────┬────────┘        └─────────────────────┘
         │
         ├───1:N──┌─────────────────────────────────┐
         │        │   governments                    │
         │        │                                 │
         │        │ id            PK                │
         │        │ country_id    FK                │
         │        │ leader_name                     │
         │        │ party                           │
         │        │ start_date                      │
         │        │ end_date                        │
         │        │ political_lean                  │
         │        │ UQ(country_id,leader_name,start)│
         │        └─────────────────────────────────┘
         │
                   ┌──────────────────┐
                   │   etl_runs       │
                   │                  │
                   │ id          PK   │
                   │ pipeline_name    │
                   │ status           │
                   │ started_at       │
                   │ finished_at      │
                   │ countries_proc   │
                   │ debt_recs_proc   │
                   │ debt_recs_ups    │
                   │ duration_ms      │
                   │ error_message    │
                   └──────────────────┘
```

### 2.2 Tablas en detalle

#### `countries`

Catálogo de países normalizado desde World Bank API. Solo se incluyen entidades con región definida (excluye agregados como "World", "Euro Area").

| Columna | Tipo | Constraints | Descripción |
|---|---|---|---|
| `id` | `INTEGER` | PK, auto | ID interno |
| `iso2` | `VARCHAR(2)` | UNIQUE, INDEX | ISO 3166-1 alpha-2 |
| `iso3` | `VARCHAR(3)` | UNIQUE, INDEX | ISO 3166-1 alpha-3 — clave de negocio |
| `name_es` | `VARCHAR(150)` | NOT NULL | Nombre localizado (español) |
| `name_en` | `VARCHAR(150)` | NOT NULL | Nombre localizado (inglés) |
| `region` | `VARCHAR(100)` | INDEX | Región World Bank |
| `subregion` | `VARCHAR(100)` | nullable | Subregión administrativa |
| `population` | `INTEGER` | nullable | Última población conocida (ETL) |
| `capital` | `VARCHAR(120)` | nullable | Capital |
| `flag_url` | `VARCHAR(255)` | nullable | URL de bandera (reservado) |

#### `debt_records`

Serie temporal de deuda y métricas derivadas. Un registro por país por año. Cada registro porta metadatos de trazabilidad metodológica.

| Columna | Tipo | Constraints | Descripción |
|---|---|---|---|
| `id` | `INTEGER` | PK, auto | ID interno |
| `country_id` | `INTEGER` | FK(`countries.id`), INDEX, CASCADE | Relación al país |
| `year` | `INTEGER` | INDEX | Año de la observación |
| `total_external_debt_usd` | `FLOAT` | nullable, INDEX | Stock de deuda externa (USD corrientes) |
| `debt_pct_gdp` | `FLOAT` | nullable, INDEX | Deuda / PIB × 100 |
| `debt_per_capita_usd` | `FLOAT` | nullable, INDEX | Deuda / población |
| `gdp_usd` | `FLOAT` | nullable | PIB nominal (USD corrientes) |
| `source` | `VARCHAR(30)` | NOT NULL | Clave corta: `wb_ids_dt_dod_dect_cd` o `imf_dm_proxy_ggxwdg` |
| `debt_concept` | `VARCHAR(50)` | NOT NULL | `external_debt_bop` o `public_debt_proxy` |
| `data_source` | `VARCHAR(120)` | NOT NULL | Descripción legible de la fuente |
| `data_vintage` | `DATE` | nullable | Fecha de referencia (`YYYY-12-31`) |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL | Última escritura |
| | | `UNIQUE(country_id, year)` | Un registro por país-año |

**Valores de `debt_concept`:**

| Valor | Significado | Fuente |
|---|---|---|
| `external_debt_bop` | Deuda externa total en sentido de balanza de pagos | World Bank IDS `DT.DOD.DECT.CD` |
| `public_debt_proxy` | Proxy: deuda bruta del gobierno general (no estrictamente externa) | IMF DataMapper `GGXWDG_NGDP` + `NGDPD` |

#### `governments`

Periodos de gobierno por país para overlay en gráficos históricos.

| Columna | Tipo | Constraints | Descripción |
|---|---|---|---|
| `id` | `INTEGER` | PK, auto | ID interno |
| `country_id` | `INTEGER` | FK(`countries.id`), INDEX, CASCADE | Relación al país |
| `leader_name` | `VARCHAR(150)` | NOT NULL | Jefe de gobierno/estado |
| `party` | `VARCHAR(150)` | nullable | Partido político |
| `start_date` | `DATE` | NOT NULL | Inicio del mandato |
| `end_date` | `DATE` | nullable | Fin (`NULL` = en funciones) |
| `political_lean` | `VARCHAR(50)` | nullable | Orientación política (reservado) |
| | | `UNIQUE(country_id, leader_name, start_date)` | Unicidad compuesta |

**Índice compuesto:** `ix_governments_country_id_start_date`.

#### `etl_runs`

Auditoría de ejecuciones del pipeline ETL.

| Columna | Tipo | Constraints | Descripción |
|---|---|---|---|
| `id` | `INTEGER` | PK, auto | ID interno |
| `pipeline_name` | `VARCHAR(100)` | INDEX | Nombre del pipeline |
| `status` | `VARCHAR(20)` | INDEX | `running`, `success`, `error` |
| `started_at` | `TIMESTAMPTZ` | NOT NULL | Inicio |
| `finished_at` | `TIMESTAMPTZ` | nullable | Fin |
| `countries_processed` | `INTEGER` | default 0 | Países procesados |
| `debt_records_processed` | `INTEGER` | default 0 | Registros procesados |
| `debt_records_upserted` | `INTEGER` | default 0 | Registros upserted |
| `duration_ms` | `INTEGER` | nullable | Duración en ms |
| `error_message` | `TEXT` | nullable | Error si aplica |

### 2.3 Migraciones Alembic

| Revisión | Descripción |
|---|---|
| `20260405_0001` | Schema inicial: `countries` + `debt_records` |
| `20260405_0002` | Tabla `etl_runs` |
| `20260405_0003` | Tabla `governments` |
| `20260405_0004` | Índices de rendimiento (métricas ranking, región, gobierno) |
| `20260406_0005` | Columnas de trazabilidad metodológica: `debt_concept`, `data_source`, `data_vintage` |

---

## 3. Pipeline ETL

### 3.1 Fuentes y conceptos

| Fuente | Indicador(es) | Concepto | Prioridad | Activación |
|---|---|---|---|---|
| **World Bank IDS** | `DT.DOD.DECT.CD`, `NY.GDP.MKTP.CD`, `SP.POP.TOTL` | `external_debt_bop` | 10 (alta) | Siempre |
| **IMF DataMapper** | `GGXWDG_NGDP`, `NGDPD` | `public_debt_proxy` | 20 (baja) | `ETL_ALLOW_PROXY_DEBT_FALLBACK=true` |
| **Wikidata SPARQL** | Propiedades `P6`, `P35` | Periodos de gobierno | — | `ETL_SEED_GOVERNMENTS_ENABLED=true` |

### 3.2 Flujo del pipeline global

```text
1. Fetch countries (WB API v2, paginado)
2. Fetch external debt series (DT.DOD.DECT.CD)
3. Fetch GDP series (NY.GDP.MKTP.CD)
4. Fetch population series (SP.POP.TOTL)
5. Normalize countries → dict[iso3, CountrySeed]
6. Normalize indicator rows → dict[(iso3, year), float]
7. Build DebtRecordSeed rows (only where debt + GDP valid)
   - Calculate debt_pct_gdp, debt_per_capita_usd
8. [Optional] Fetch IMF proxy if enabled
   - Normalize IMF records
   - Filter: keep only countries NOT covered by WB
   - Merge by source_priority
9. Upsert countries (ON CONFLICT iso3)
10. Delete stale IMF proxy rows (current/future years, WB-covered countries)
11. Upsert debt_records (batched, ON CONFLICT country_id+year)
12. Update country population from latest year
13. [Optional] Seed governments (Wikidata + pilot)
14. Invalidate Redis read caches
15. Record EtlRun with stats
```

### 3.3 Contadores de control del ETL

El resumen de cada corrida expone:

- `countries_processed`, `debt_records_processed`, `debt_records_upserted`
- `gdp_records_processed`, `population_records_processed`
- `countries_with_population`
- `merged_world_bank_rows`, `merged_imf_proxy_rows`
- `imf_debt_rows_dropped_due_to_wb_coverage`
- `imf_proxy_rows_removed_current_or_future`
- `imf_proxy_rows_removed_wb_covered_countries`
- `cache_keys_invalidated`

### 3.4 CLI entry points

Definidos en `pyproject.toml` → `[project.scripts]`:

```bash
deudamundi-etl-global          # ETL completo (WB + IMF opt-in + gobiernos opt-in)
deudamundi-etl-worldbank       # Alias de etl-global
deudamundi-seed-governments    # Solo gobiernos
deudamundi-report-gaps         # Reporte de cobertura → api/reports/
```

### 3.5 Flujo recomendado post-deploy

```bash
alembic upgrade head
deudamundi-etl-global
deudamundi-seed-governments
deudamundi-report-gaps
```

---

## 4. Referencia de API REST

Prefijo base: `/api/v1` (configurable via `API_V1_PREFIX`).

### 4.1 Endpoints públicos

#### `GET /health`

Health check. Respuesta `200 OK`.

#### `GET /globe-data`

Payload liviano para visualización de globo 3D.

| Param | Tipo | Default | Descripción |
|---|---|---|---|
| `region` | string | — | Filtro opcional por región |

Respuesta: `GlobeDataResponse` con `item_count` + array de `GlobeDataPoint` (iso3, name_en, region, latest_year, métricas de deuda, trazabilidad).

#### `GET /countries`

Listado paginado de países con último dato de deuda.

| Param | Tipo | Default | Descripción |
|---|---|---|---|
| `page` | int | 1 | Página |
| `page_size` | int | 20 | Tamaño de página |
| `region` | string | — | Filtro por región |

Respuesta: `CountriesListResponse` con `page`, `page_size`, `total`, `items[]`.

#### `GET /countries/{iso3}`

Detalle de un país con último dato de deuda, metadatos de trazabilidad y equivalencias emocionales.

Respuesta: `CountryDetailResponse` con datos del país + `equivalences[]` (hospitales, salarios docentes, salarios mínimos).

#### `GET /countries/{iso3}/history`

Serie histórica completa de deuda del país, ordenada por año descendente.

Respuesta: `CountryHistoryResponse` con `iso3` + `items[]` (año, métricas, source, trazabilidad).

#### `GET /countries/{iso3}/governments`

Periodos de gobierno del país, ordenados por fecha de inicio descendente.

Respuesta: `CountryGovernmentsResponse` con `iso3` + `items[]` (leader_name, party, start_date, end_date, political_lean).

#### `GET /countries/compare`

Comparación multi-país (mínimo 2 ISO3 válidos).

| Param | Tipo | Descripción |
|---|---|---|
| `iso3` | string (repetible) | Códigos ISO3 a comparar (ej. `?iso3=ARG&iso3=USA&iso3=MEX`) |

Respuesta: `CountriesCompareResponse` con `requested_iso3`, `missing_iso3`, `item_count`, `items[]` (cada uno con `detail` + `history`).

Error `422` si se proporcionan menos de 2 ISO3 válidos.

#### `GET /rankings`

Ranking de países por métrica.

| Param | Tipo | Default | Descripción |
|---|---|---|---|
| `metric` | string | — | `absolute`, `pct_gdp` o `per_capita` |
| `region` | string | — | Filtro opcional |
| `limit` | int | 20 | Máximo 100 |

Respuesta: `RankingsResponse` con `metric`, `region`, `limit`, `items[]` (rank, iso3, name_en, region, value, latest_year).

### 4.2 Endpoints administrativos

Requieren header `X-API-Key` con valor de `ADMIN_API_KEY`.

#### `POST /admin/etl/run`

Ejecuta ETL global. Devuelve resumen con contadores.

#### `POST /admin/etl/world-bank/run`

Ejecuta ETL World Bank (alias del global).

#### `POST /admin/etl/governments/run`

| Param | Tipo | Default | Descripción |
|---|---|---|---|
| `source` | string | config default | `pilot`, `wikidata` o `hybrid` |

Ejecuta seed de gobiernos.

### 4.3 Códigos de error

| Código | Cuándo |
|---|---|
| `401` | Falta `X-API-Key` en endpoints admin |
| `404` | País no encontrado |
| `422` | Parámetros inválidos |
| `429` | Rate limit excedido |
| `500` | Error interno (ETL, DB) |

---

## 5. Cache y rendimiento

### 5.1 Estrategia de cache

Cache-aside con Redis. Cada endpoint de lectura:
1. Busca en Redis por clave (`{prefix}:{params}`).
2. Si hay hit, retorna directamente (sin tocar PostgreSQL).
3. Si hay miss, ejecuta query, almacena resultado en Redis con TTL, retorna.

### 5.2 TTLs por prefijo

| Prefijo | TTL | Endpoints |
|---|---|---|
| `countries:*` | 6 horas | countries list, detail, history, governments, compare |
| `rankings:*` | 24 horas | rankings |
| `globe-data:*` | 24 horas | globe-data |

### 5.3 Invalidación

Post-ETL se invoca `invalidate_read_caches()` que borra todas las claves bajo los tres prefijos via `SCAN + DELETE`.

### 5.4 Índices de base de datos

| Índice | Columna(s) | Propósito |
|---|---|---|
| `ix_debt_records_total_external_debt_usd` | `total_external_debt_usd` | Ranking absoluto |
| `ix_debt_records_debt_pct_gdp` | `debt_pct_gdp` | Ranking % PIB |
| `ix_debt_records_debt_per_capita_usd` | `debt_per_capita_usd` | Ranking per cápita |
| `ix_countries_region` | `region` | Filtro por región |
| `ix_governments_country_id_start_date` | `(country_id, start_date)` | Overlay temporal |

### 5.5 Performance testing

- **EXPLAIN ANALYZE:** `api/scripts/explain_analyze.py` para queries críticas.
- **Locust:** `api/locustfile.py` para load testing (100 usuarios, p95 < 500 ms objetivo).

---

## 6. Seguridad

### 6.1 CORS

- `CORS_ALLOWED_ORIGINS`: lista separada por comas.
- `CORS_ALLOW_ORIGIN_REGEX`: regex opcional.
- En `development`, se auto-habilita regex para orígenes de red local (`localhost`, `192.168.*`, `10.*`, `172.16-31.*`, `*.local`).

### 6.2 Rate limiting

Slowapi con límite por IP configurable (`RATE_LIMIT_REQUESTS_PER_MINUTE`, default 100). Respuesta `429` con body `{"detail": "Rate limit exceeded"}`.

### 6.3 Security headers

Aplicados vía middleware en cada respuesta:

| Header | Valor |
|---|---|
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `Referrer-Policy` | `no-referrer` |
| `Content-Security-Policy` | Estricto para API; permisivo para `/docs` y `/redoc` |
| `Strict-Transport-Security` | Condicional (`SECURITY_HSTS_ENABLED=true`) |

### 6.4 Admin authentication

Header `X-API-Key` validado contra `ADMIN_API_KEY` en endpoints bajo `/admin/*`.

---

## 7. Configuración

Toda la configuración se lee desde variables de entorno (o archivo `.env`), usando Pydantic Settings.

### 7.1 Variables principales

| Variable | Default | Descripción |
|---|---|---|
| `APP_ENV` | `development` | Entorno: `development` o `production` |
| `API_V1_PREFIX` | `/api/v1` | Prefijo de la API |
| `DATABASE_URL` | `postgresql+psycopg://postgres:postgres@localhost:5432/deudamundi` | Conexión PostgreSQL |
| `SUPABASE_DATABASE_URL` | — | Si presente, prioriza sobre `DATABASE_URL` |
| `REDIS_URL` | `redis://localhost:6379/0` | Conexión Redis |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173` | Orígenes CORS |
| `CORS_ALLOW_ORIGIN_REGEX` | — | Regex opcional para orígenes dinámicos |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | `100` | Rate limit por IP |
| `SECURITY_HSTS_ENABLED` | `false` | HSTS header |
| `ADMIN_API_KEY` | — | API key para endpoints admin |

### 7.2 Variables ETL

| Variable | Default | Descripción |
|---|---|---|
| `ETL_SCHEDULER_ENABLED` | `false` | Activar scheduler cron |
| `ETL_SCHEDULE_CRON` | `0 2 1 2 *` | Expresión crontab (UTC) |
| `ETL_ALLOW_PROXY_DEBT_FALLBACK` | `false` | Habilitar proxy FMI |
| `ETL_SEED_GOVERNMENTS_ENABLED` | `true` | Seed de gobiernos en ETL global |
| `ETL_GOVERNMENTS_SOURCE` | `hybrid` | `pilot`, `wikidata`, `hybrid` |
| `ETL_GOVERNMENTS_MIN_START_YEAR` | `1990` | Año mínimo para gobiernos |
| `ETL_GOVERNMENTS_TIMEOUT_SECONDS` | `30.0` | Timeout SPARQL |
| `ETL_GOVERNMENTS_CHUNK_SIZE` | `25` | Chunk size SPARQL |
| `ETL_GOVERNMENTS_MAX_DURATION_SECONDS` | `180.0` | Duración máxima seed |

### 7.3 Normalización automática de DATABASE_URL

- `postgres://` → `postgresql+psycopg://` (compatibilidad Heroku/Supabase).
- `postgresql://` → `postgresql+psycopg://` (driver explícito).
- En `development` fuera de Docker, `@postgres` → `@localhost` (fallback automático).

---

## 8. Desarrollo local

### 8.1 Opción recomendada: Docker Compose (stack completo)

Desde la raíz del repo:

```bash
docker compose up --build
```

Servicios:
- API: `http://localhost:8000`
- Health: `http://localhost:8000/api/v1/health`
- Docs: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

### 8.2 Opción standalone

```bash
cd api
cp .env.example .env           # Ajustar variables
pip install -e .[dev]
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 8.3 Probar desde red local (iPhone/Android)

El backend escucha en `0.0.0.0:8000` y en `development` permite automáticamente orígenes de red local vía regex.

Si necesitas control explícito:

```bash
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://192.168.x.x:5173
```

---

## 9. Testing

### 9.1 Ejecutar tests

```bash
cd api
pip install -e .[dev]
ruff check app tests    # Lint
pytest                   # Tests
```

### 9.2 Cobertura de tests

| Archivo de test | Alcance |
|---|---|
| `test_health.py` | Health check endpoint |
| `test_countries_endpoints.py` | CRUD de países, detalle, historia |
| `test_countries_integration.py` | Integración real de endpoints de países |
| `test_rankings_endpoint.py` | Rankings por métrica y región |
| `test_globe_data_endpoint.py` | Globe data payload |
| `test_admin_etl.py` | Endpoints admin ETL |
| `test_security_middleware.py` | CORS, rate limiting, security headers |
| `test_etl_transform.py` | Normalización, merge por prioridad, filtrado IMF |
| `test_etl_repository.py` | Upserts PostgreSQL |
| `test_etl_imf_client.py` | Cliente IMF DataMapper |
| `test_governments_wikidata_client.py` | Cliente SPARQL Wikidata |
| `test_seed_governments.py` | Seed de gobiernos |
| `test_equivalences.py` | Equivalencias emocionales |
| `test_config_database_url.py` | Normalización de DATABASE_URL |

---

## 10. Base de datos y migraciones

### 10.1 Driver y conexión

- Driver: `psycopg` 3.x (binary).
- La app prioriza `SUPABASE_DATABASE_URL` sobre `DATABASE_URL`.
- Normalización automática de esquema de URL (ver sección 7.3).

### 10.2 Comandos Alembic

```bash
alembic upgrade head         # Aplicar todas las migraciones
alembic downgrade -1         # Revertir última migración
alembic revision -m "desc"   # Crear nueva migración
alembic history              # Ver historial
```

### 10.3 Historial de migraciones

| Revisión | Fecha | Descripción |
|---|---|---|
| `20260405_0001` | 2026-04-05 | Schema inicial (countries + debt_records) |
| `20260405_0002` | 2026-04-05 | Tabla etl_runs |
| `20260405_0003` | 2026-04-05 | Tabla governments |
| `20260405_0004` | 2026-04-05 | Índices de rendimiento |
| `20260406_0005` | 2026-04-06 | Columnas de trazabilidad metodológica |

---

## 11. Despliegue en producción

### 11.1 Requisitos del servidor

- Ubuntu 22.04+ / Debian 12+
- Python 3.12+, `python3-venv`
- Nginx, Certbot
- Redis (local o administrado)
- Puertos: 22, 80, 443

### 11.2 Flujo de despliegue (systemd)

```bash
# 1. Clonar y configurar
cd /home/admin/apps
git clone <REPO_URL> deudamundi
cd deudamundi
cp api/.env.example api/.env
nano api/.env  # Completar variables de producción

# 2. Instalar/actualizar servicio
APP_DIR=/home/admin/apps/deudamundi \
SERVICE_NAME=deudamundi-api \
SERVICE_USER=admin \
SERVICE_GROUP=admin \
SERVICE_PORT=8000 \
UVICORN_WORKERS=2 \
./deploy/vps/systemd/deploy_systemd.sh

# 3. Configurar Nginx
sudo cp deploy/vps/systemd/nginx.deudamundi-api.conf /etc/nginx/sites-available/deudamundi-api
sudo ln -s /etc/nginx/sites-available/deudamundi-api /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 4. HTTPS
sudo certbot --nginx -d api.tudominio.com

# 5. Verificar
curl -i https://api.tudominio.com/api/v1/health
```

### 11.3 Variables de producción

| Variable | Valor |
|---|---|
| `APP_ENV` | `production` |
| `SUPABASE_DATABASE_URL` | `<connection string>` |
| `REDIS_URL` | `redis://localhost:6379/0` |
| `CORS_ALLOWED_ORIGINS` | `https://deudamundi.econopapi.com` |
| `ADMIN_API_KEY` | `<secret>` |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | `100` |
| `SECURITY_HSTS_ENABLED` | `true` |
| `RUN_MIGRATIONS` | `true` |

### 11.4 ETL en producción

```bash
curl -X POST "https://api.tudominio.com/api/v1/admin/etl/run" \
  -H "X-API-Key: <ADMIN_API_KEY>"
```

### 11.5 Smoke tests post-deploy

```bash
curl -i https://api.tudominio.com/api/v1/health
curl -i "https://api.tudominio.com/api/v1/countries?page=1&page_size=5"
curl -i "https://api.tudominio.com/api/v1/rankings?metric=absolute&limit=5"
curl -i "https://api.tudominio.com/api/v1/globe-data"
curl -s "https://api.tudominio.com/api/v1/countries/MEX" | jq '.gdp_usd, .debt_pct_gdp, .debt_per_capita_usd'
```

---

## 12. Troubleshooting

### `requires a different Python: 3.10.x not in '>=3.12'`

El `.venv` se creó con Python < 3.12. Solución:

```bash
# Debian 12/13
sudo apt update && sudo apt install -y python3 python3-venv
cd /home/admin/apps/deudamundi/api
rm -rf .venv
cd /home/admin/apps/deudamundi
PYTHON_BIN=python3 APP_DIR=/home/admin/apps/deudamundi ./deploy/vps/systemd/deploy_systemd.sh
```

Para Ubuntu 22.04 con Python < 3.12: usar `python3.12` y `python3.12-venv`.

El script de deploy valida automáticamente Python ≥ 3.12 y recrea `.venv` si detecta versión incompatible.

### `GET /` devuelve 404

Por diseño. El health check es `GET /api/v1/health`.

### Conexión a Postgres falla fuera de Docker

En `development`, el backend aplica fallback automático de `@postgres` a `@localhost` cuando no detecta `/.dockerenv`.
