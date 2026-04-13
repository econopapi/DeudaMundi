# DeudaMundi

![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688)
![React](https://img.shields.io/badge/frontend-React%2018-61DAFB)
![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL%2016-336791)
![Redis](https://img.shields.io/badge/cache-Redis%207-DC382D)
![License](https://img.shields.io/badge/license-proprietary-lightgrey)

Atlas global e interactivo de **deuda externa soberana** por país, orientado a visualización pública, consistencia metodológica y trazabilidad de datos para análisis comparado.

> Estado de madurez (abril 2026): **>90 % de desarrollo funcional** — transición activa hacia formalización académica, estabilidad operativa y documentación "paper-ready".

## Autor

[Daniel Limón](https://econopapi.com) — `dani@dlimon.net`

---

## Tabla de contenidos

1. [Resumen ejecutivo](#1-resumen-ejecutivo)
2. [Motivación y objetivo científico-técnico](#2-motivación-y-objetivo-científico-técnico)
3. [Fuentes de datos y marco metodológico](#3-fuentes-de-datos-y-marco-metodológico)
4. [Arquitectura del sistema](#4-arquitectura-del-sistema)
5. [Modelo de datos](#5-modelo-de-datos)
6. [Pipeline ETL](#6-pipeline-etl)
7. [Contrato funcional de la API REST](#7-contrato-funcional-de-la-api-rest)
8. [Frontend y experiencia de análisis](#8-frontend-y-experiencia-de-análisis)
9. [Ejecución local reproducible](#9-ejecución-local-reproducible)
10. [Calidad, validación y CI](#10-calidad-validación-y-ci)
11. [Despliegue y operación](#11-despliegue-y-operación)
12. [Limitaciones y amenazas a la validez](#12-limitaciones-y-amenazas-a-la-validez)
13. [Roadmap a release estable](#13-roadmap-a-release-estable)
14. [Convenciones de contribución](#14-convenciones-de-contribución)
15. [Cita académica](#15-cita-académica)

---

## 1. Resumen ejecutivo

**DeudaMundi** es una plataforma full-stack que integra un backend analítico (FastAPI + PostgreSQL + Redis) con un frontend interactivo (React + D3 + Three.js) para construir un atlas de deuda externa soberana con cobertura global.

El sistema resuelve un problema recurrente en la divulgación económica: la comparación internacional de deuda pública y externa se realiza frecuentemente con indicadores heterogéneos, sin distinguir entre conceptos (deuda externa BOP vs. deuda pública bruta del gobierno general), sin explicitar la fuente de cada dato y sin exponer las limitaciones de cobertura. DeudaMundi aborda esto con cuatro principios de diseño:

| Principio | Implementación |
|---|---|
| **Consistencia conceptual** | Deuda externa total (BOP) como métrica primaria; QEDS SDDS como fuente intermedia de deuda externa real (~118 países); cualquier proxy de deuda pública se etiqueta explícitamente como `public_debt_proxy`. |
| **Trazabilidad por registro** | Cada observación país-año expone `debt_concept`, `data_source` y `data_vintage` tanto en la API como en la UI. |
| **Reproducibilidad operativa** | ETL versionado, migraciones Alembic idempotentes, CLI parametrizable, scheduler cron y reportes de gaps automatizados. |
| **Accesibilidad analítica** | API REST paginada + globo 3D interactivo + gráficos de series temporales + comparador multi-país + exportación CSV/XLSX/PDF. |

### Cifras clave del dataset (última corrida ETL)

| Indicador | Valor |
|---|---|
| Países en catálogo | 217 |
| Países con datos de deuda | 121 |
| Países sin datos de deuda | 96 |
| Rango temporal observado | 1970–2024 |

---

## 2. Motivación y objetivo científico-técnico

### Problema

Las bases de datos económicas internacionales (World Bank, FMI, OCDE) ofrecen indicadores de deuda con semánticas distintas que frecuentemente se mezclan en visualizaciones públicas:

- **Deuda externa total** (World Bank IDS): obligaciones de un país con acreedores no residentes — concepto de balanza de pagos (BOP).
- **Deuda bruta del gobierno general** (FMI): obligaciones del sector público con todos los acreedores (residentes y no residentes) — concepto fiscal.

Comparar ambos sin distinción produce conclusiones erróneas. Un país puede tener baja deuda externa y alta deuda pública (ej. Japón) o viceversa.

### Objetivos

1. Proveer una infraestructura abierta para explorar deuda externa por país y tiempo, con rigor en la distinción de conceptos.
2. Hacer transparente la cobertura: qué países tienen dato, cuáles no, y por qué.
3. Permitir comparación cross-country en tres dimensiones: stock absoluto (USD), ratio sobre PIB (%) y per cápita (USD/hab).
4. Cuando se incorpore un proxy de fuente alternativa (ej. FMI), que esté siempre etiquetado y sea opt-in. Cuando existan fuentes intermedias de deuda externa real (ej. QEDS SDDS), priorizarlas sobre el proxy.

### Preguntas de investigación que el producto busca responder

- ¿Cómo evoluciona la deuda externa de un país en términos absolutos y relativos al PIB?
- ¿Qué heterogeneidades regionales emergen al comparar stock, ratio y per cápita?
- ¿Qué incertidumbre introduce la falta de cobertura y cómo se comunica al usuario?
- ¿Cómo se correlaciona visualmente la trayectoria de deuda con los periodos de gobierno?

---

## 3. Fuentes de datos y marco metodológico

### 3.1 Fuente primaria: World Bank International Debt Statistics (IDS)

| Atributo | Valor |
|---|---|
| **Indicador de deuda** | `DT.DOD.DECT.CD` — External debt stocks, total (current USD) |
| **Indicador de PIB** | `NY.GDP.MKTP.CD` — GDP (current USD) |
| **Indicador de población** | `SP.POP.TOTL` — Population, total |
| **API** | World Bank API v2 (`https://api.worldbank.org/v2`) |
| **Autenticación** | Ninguna (API abierta) |
| **Cobertura temporal** | ~1970–2024 (varía por país) |
| **Frecuencia** | Anual |
| **Concepto económico** | Deuda externa BOP (`external_debt_bop`) |
| **Prioridad en ETL** | `source_priority = 10` (máxima) |

La serie `DT.DOD.DECT.CD` del World Bank IDS mide el stock total de deuda externa pendiente de un país hacia acreedores no residentes, incluyendo deuda pública y públicamente garantizada (PPG), deuda privada no garantizada (PNG) y créditos del FMI. Es la referencia estándar para comparaciones internacionales de deuda externa ([World Bank Metadata](https://datatopics.worldbank.org/debt/ids/)).

### 3.2 Fuente intermedia: World Bank QEDS SDDS (deuda externa real)

| Atributo | Valor |
|---|---|
| **Indicador** | `DT.DOD.DECT.CD.AR.US` — Gross External Debt Position, All Sectors, All maturities, All instruments (USD) |
| **Source ID** | `22` (Quarterly External Debt Statistics – Special Data Dissemination Standard) |
| **API** | World Bank API v2 (`https://api.worldbank.org/v2`) con parámetro `source=22` |
| **Autenticación** | Ninguna (API abierta) |
| **Cobertura** | ~118 países (incluye economías avanzadas: USA, JPN, GBR, DEU, FRA) |
| **Frecuencia** | Trimestral (el ETL selecciona el mejor trimestre por año: preferencia Q4, luego el más reciente) |
| **Concepto económico** | Posición de deuda externa bruta (`external_debt_qeds`) |
| **Prioridad en ETL** | `source_priority = 15` (inferior a WB IDS, superior a IMF proxy) |
| **Activación** | `ETL_ENABLE_QEDS_EXTERNAL_DEBT=true` (habilitado por defecto) |

> **Nota metodológica:** QEDS SDDS reporta la posición de deuda externa bruta agregando todos los sectores institucionales (gobierno general, bancos, otros sectores, inversión directa intercompañía) y todos los instrumentos. A diferencia del proxy IMF, este indicador mide específicamente deuda *externa*, no deuda pública. Cubre 44 de los 45 países que antes dependían exclusivamente del proxy IMF, reemplazándolos con datos de deuda externa real. Solo Letonia (LVA) queda sin cobertura QEDS entre los antiguos países proxy-only.

### 3.3 Fuente auxiliar (proxy): FMI DataMapper

| Atributo | Valor |
|---|---|
| **Indicador deuda/PIB** | `GGXWDG_NGDP` — General government gross debt (% of GDP) |
| **Indicador PIB nominal** | `NGDPD` — Gross domestic product, current prices (USD billions) |
| **API** | IMF DataMapper REST (`https://www.imf.org/external/datamapper/api/v1`) |
| **Autenticación** | Ninguna |
| **Concepto económico** | Deuda pública bruta del gobierno general (`public_debt_proxy`) |
| **Prioridad en ETL** | `source_priority = 20` (inferior a WB IDS y QEDS) |
| **Activación** | Solo con `ETL_ALLOW_PROXY_DEBT_FALLBACK=true` (deshabilitado por defecto) |

> ⚠️ **Advertencia metodológica:** Esta fuente mide deuda *pública* bruta (no deuda *externa*). Se incluye como último recurso para países sin cobertura World Bank IDS ni QEDS SDDS. Con la incorporación de QEDS, el proxy IMF es necesario solo para ~1 país (LVA). El sistema etiqueta estos registros como `public_debt_proxy` en todos los niveles (base de datos, API, UI).

### 3.4 Fuente de gobiernos: Wikidata (SPARQL)

| Atributo | Valor |
|---|---|
| **Propiedad primaria** | `P6` (head of government) |
| **Propiedad fallback** | `P35` (head of state, cuando `P6` no tiene profundidad suficiente) |
| **Endpoint** | Wikidata SPARQL (`https://query.wikidata.org/sparql`) |
| **Datos extraídos** | Nombre del líder, fecha de inicio/fin del mandato, rol |
| **Modos de ejecución** | `pilot` (solo semillas hardcodeadas), `wikidata` (solo SPARQL), `hybrid` (ambos, recomendado) |

### 3.5 Métricas derivadas

A partir de las fuentes primarias, el ETL calcula y persiste las siguientes métricas:

| Métrica | Fórmula | Unidad |
|---|---|---|
| `total_external_debt_usd` | Directa de `DT.DOD.DECT.CD` / `DT.DOD.DECT.CD.AR.US` (o derivada para proxy FMI) | USD corrientes |
| `gdp_usd` | Directa de `NY.GDP.MKTP.CD` | USD corrientes |
| `debt_pct_gdp` | `total_external_debt_usd / gdp_usd × 100` | % |
| `debt_per_capita_usd` | `total_external_debt_usd / population` | USD / habitante |

### 3.6 Salvaguardas metodológicas implementadas

1. **Exclusión de agregados no-país** en normalización del catálogo World Bank (ej. "World", "Euro Area").
2. **Exclusión de años FMI actuales/futuros** para evitar nowcasts/proyecciones en la serie histórica.
3. **Priorización determinística** por `source_priority` cuando existe colisión país-año entre fuentes (IDS 10 > QEDS 15 > IMF 20).
4. **Purga de proxies obsoletos** en cada corrida ETL: se eliminan filas FMI de año actual/futuro y de países cubiertos por WB IDS o QEDS.
5. **Purga de filas QEDS obsoletas** cuando un país tiene cobertura IDS, o cuando QEDS se deshabilita.
6. **Conversión trimestral→anual** para QEDS: se selecciona el mejor trimestre por año (preferencia Q4, luego el más reciente disponible).
7. **Solo se persisten observaciones con deuda + PIB válidos.** `debt_per_capita_usd` se completa cuando además hay población.
8. **Trazabilidad end-to-end**: `debt_concept`, `data_source` y `data_vintage` viajan desde el ETL hasta la respuesta JSON del endpoint.

---

## 4. Arquitectura del sistema

### 4.1 Estructura del monorepo

```text
.
├── api/                         # Backend: FastAPI + SQLAlchemy + Alembic + ETL + tests
│   ├── app/
│   │   ├── api/v1/endpoints/    # Handlers REST (health, countries, rankings, globe, admin)
│   │   ├── core/                # Config (Pydantic Settings), cache (Redis), security (CORS, rate limit, headers)
│   │   ├── db/                  # Session factory y base class SQLAlchemy
│   │   ├── etl/                 # Clientes WB/IMF/Wikidata, transform, repository, scheduler
│   │   ├── models/              # ORM: Country, DebtRecord, Government, EtlRun
│   │   ├── schemas/             # Pydantic: request/response schemas
│   │   └── services/            # Lógica de negocio: countries, rankings, equivalences
│   ├── alembic/                 # Migraciones de esquema (5 revisiones)
│   ├── tests/                   # Pytest: endpoints, ETL, transformaciones, seguridad
│   ├── scripts/                 # start_api.sh, explain_analyze.py
│   └── reports/                 # Reportes de gap generados por ETL
├── web/                         # Frontend: React 18 + Vite + TypeScript + TailwindCSS
│   ├── src/
│   │   ├── components/          # Globe (3D), Country (hero, charts, share), UI (loading)
│   │   ├── pages/               # Home, CountryDetail, Compare, Rankings
│   │   ├── services/            # Cliente API tipado
│   │   ├── store/               # Zustand: globeStore, localeStore
│   │   ├── lib/                 # Formatters, translations (ES/EN), exports, chart helpers
│   │   └── types/               # Tipos TypeScript alineados a schemas de API
│   └── ...
├── deploy/vps/                  # systemd service, Nginx config, deploy script
├── docker-compose.yml           # Stack local: Postgres 16 + Redis 7 + API + Web
└── README.md                    # ← Este archivo
```

### 4.2 Stack técnico

| Capa | Tecnología | Versión |
|---|---|---|
| **Runtime backend** | Python | 3.12 |
| **Framework API** | FastAPI | ≥ 0.115 |
| **ORM** | SQLAlchemy | 2.x |
| **Migraciones** | Alembic | ≥ 1.14 |
| **Driver PostgreSQL** | psycopg | 3.x (binary) |
| **Base de datos** | PostgreSQL | 16 |
| **Cache** | Redis | 7 |
| **Rate limiting** | Slowapi | ≥ 0.1.9 |
| **HTTP client (ETL)** | httpx | ≥ 0.27 |
| **Scheduler** | APScheduler | 3.x |
| **Configuración** | Pydantic Settings | 2.x |
| **Framework frontend** | React | 18 |
| **Bundler** | Vite | 5 |
| **Lenguaje frontend** | TypeScript | 5 |
| **Estilos** | TailwindCSS | 3.x |
| **Gráficos** | D3.js | 7.x |
| **Globo 3D** | react-globe.gl + Three.js | 2.37+ / 0.170 |
| **Estado global** | Zustand | 4.x |
| **Exportación** | jspdf, xlsx | — |
| **Testing backend** | Pytest, Ruff | 8.x / 0.6+ |
| **Testing frontend** | Jest, React Testing Library | 29.x / 16.x |
| **Infra local** | Docker Compose | — |
| **Deploy backend** | VPS Linux + systemd + Nginx | — |
| **Deploy frontend** | Vercel | — |
| **Analytics** | Vercel Analytics | — |

### 4.3 Diagrama de flujo de datos

```text
┌──────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  World Bank API  │     │  IMF DataMapper  │     │    Wikidata     │
│  (IDS / WDI)     │     │  (proxy, opt-in) │     │    (SPARQL)     │
└────────┬─────────┘     └────────┬─────────┘     └────────┬────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌────────────────────────────────────────────────────────────────────┐
│                         ETL Pipeline                               │
│  fetch → normalize → merge (priority) → upsert → cache invalidate │
└────────────────────────────────┬───────────────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │     PostgreSQL 16       │
                    │  countries              │
                    │  debt_records           │
                    │  governments            │
                    │  etl_runs               │
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
          ┌──────────────┐          ┌──────────────────┐
          │   Redis 7    │◄────────►│  FastAPI REST API │
          │  (cache R/O) │          │  /api/v1/*        │
          └──────────────┘          └────────┬─────────┘
                                             │
                                             ▼
                                   ┌──────────────────┐
                                   │   React SPA      │
                                   │   (Vite + TS)    │
                                   └──────────────────┘
```

---

## 5. Modelo de datos

El esquema relacional consta de **4 tablas** gestionadas con Alembic (5 revisiones de migración).

### 5.1 `countries` — Catálogo de países

| Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | `INTEGER` | PK, indexed | Identificador interno autoincremental |
| `iso2` | `VARCHAR(2)` | UNIQUE, indexed | Código ISO 3166-1 alpha-2 |
| `iso3` | `VARCHAR(3)` | UNIQUE, indexed | Código ISO 3166-1 alpha-3 (clave de negocio) |
| `name_es` | `VARCHAR(150)` | NOT NULL | Nombre en español |
| `name_en` | `VARCHAR(150)` | NOT NULL | Nombre en inglés |
| `region` | `VARCHAR(100)` | nullable, indexed | Región World Bank (ej. "Latin America & Caribbean") |
| `subregion` | `VARCHAR(100)` | nullable | Subregión administrativa |
| `population` | `INTEGER` | nullable | Población más reciente (actualizada por ETL) |
| `capital` | `VARCHAR(120)` | nullable | Capital del país |
| `flag_url` | `VARCHAR(255)` | nullable | URL de bandera (reservado) |

### 5.2 `debt_records` — Serie temporal de deuda por país

| Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | `INTEGER` | PK, indexed | Identificador interno |
| `country_id` | `INTEGER` | FK → `countries.id`, indexed, CASCADE | País asociado |
| `year` | `INTEGER` | indexed | Año de la observación |
| `total_external_debt_usd` | `FLOAT` | nullable | Stock de deuda externa (USD corrientes) |
| `debt_pct_gdp` | `FLOAT` | nullable, indexed | Deuda como % del PIB |
| `debt_per_capita_usd` | `FLOAT` | nullable, indexed | Deuda per cápita (USD) |
| `gdp_usd` | `FLOAT` | nullable | PIB nominal (USD corrientes) |
| `source` | `VARCHAR(30)` | NOT NULL | Clave corta de fuente (ej. `wb_ids_dt_dod_dect_cd`, `wb_qeds_dt_dod_dect_cd_ar_us`) |
| `debt_concept` | `VARCHAR(50)` | NOT NULL | Concepto económico: `external_debt_bop`, `external_debt_qeds` ó `public_debt_proxy` |
| `data_source` | `VARCHAR(120)` | NOT NULL | Descripción legible de la fuente |
| `data_vintage` | `DATE` | nullable | Fecha de referencia del dato (`YYYY-12-31`) |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL | Última actualización del registro |
| | | `UNIQUE(country_id, year)` | Unicidad: un registro por país por año |

### 5.3 `governments` — Periodos de gobierno por país

| Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | `INTEGER` | PK, indexed | Identificador interno |
| `country_id` | `INTEGER` | FK → `countries.id`, CASCADE, indexed | País asociado |
| `leader_name` | `VARCHAR(150)` | NOT NULL | Nombre del jefe de gobierno/estado |
| `party` | `VARCHAR(150)` | nullable | Partido político |
| `start_date` | `DATE` | NOT NULL | Inicio del mandato |
| `end_date` | `DATE` | nullable | Fin del mandato (`NULL` = en funciones) |
| `political_lean` | `VARCHAR(50)` | nullable | Orientación política (reservado) |
| | | `UNIQUE(country_id, leader_name, start_date)` | Unicidad compuesta |

**Índice compuesto:** `ix_governments_country_id_start_date` para consultas de overlay temporal.

### 5.4 `etl_runs` — Registro de ejecuciones ETL

| Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | `INTEGER` | PK, indexed | Identificador interno |
| `pipeline_name` | `VARCHAR(100)` | indexed | Nombre del pipeline (`world_bank_global`, etc.) |
| `status` | `VARCHAR(20)` | indexed | Estado: `running`, `success`, `error` |
| `started_at` | `TIMESTAMPTZ` | NOT NULL | Timestamp de inicio |
| `finished_at` | `TIMESTAMPTZ` | nullable | Timestamp de finalización |
| `countries_processed` | `INTEGER` | default 0 | Países procesados |
| `debt_records_processed` | `INTEGER` | default 0 | Registros de deuda procesados |
| `debt_records_upserted` | `INTEGER` | default 0 | Registros insertados/actualizados |
| `duration_ms` | `INTEGER` | nullable | Duración en milisegundos |
| `error_message` | `TEXT` | nullable | Mensaje de error (si aplica) |

### 5.5 Diagrama entidad-relación

```text
┌─────────────┐        ┌────────────────┐        ┌──────────────┐
│  countries   │───1:N──│  debt_records   │        │   etl_runs   │
│             │        │                │        │              │
│ id (PK)     │        │ id (PK)        │        │ id (PK)      │
│ iso2 (UQ)   │        │ country_id (FK)│        │ pipeline_name│
│ iso3 (UQ)   │        │ year           │        │ status       │
│ name_es     │        │ total_ext...   │        │ started_at   │
│ name_en     │        │ debt_pct_gdp   │        │ finished_at  │
│ region      │        │ debt_per_cap   │        │ ...          │
│ subregion   │        │ gdp_usd        │        └──────────────┘
│ population  │        │ source         │
│ capital     │        │ debt_concept   │
│ flag_url    │        │ data_source    │
│             │        │ data_vintage   │
│             │        │ updated_at     │
└──────┬──────┘        └────────────────┘
       │
       │
       ├───1:N──┌──────────────┐
       │        │  governments │
       │        │              │
       │        │ id (PK)      │
       │        │ country_id   │
       │        │ leader_name  │
       │        │ party        │
       │        │ start_date   │
       │        │ end_date     │
       │        │ political_l. │
       │        └──────────────┘
```

### 5.6 Índices de rendimiento

Además de los índices primarios y de unicidad, se han agregado índices específicos para las queries de ranking y filtrado:

| Índice | Tabla | Columna(s) | Propósito |
|---|---|---|---|
| `ix_debt_records_total_external_debt_usd` | `debt_records` | `total_external_debt_usd` | Rankings por stock absoluto |
| `ix_debt_records_debt_pct_gdp` | `debt_records` | `debt_pct_gdp` | Rankings por % PIB |
| `ix_debt_records_debt_per_capita_usd` | `debt_records` | `debt_per_capita_usd` | Rankings per cápita |
| `ix_countries_region` | `countries` | `region` | Filtro por región |
| `ix_governments_country_id_start_date` | `governments` | `(country_id, start_date)` | Overlay temporal de gobiernos |

---

## 6. Pipeline ETL

### 6.1 Arquitectura del pipeline

El ETL se ejecuta como proceso síncrono dentro del mismo runtime Python, ya sea vía CLI, endpoint admin o scheduler cron. Arquitectura modular:

```text
Clientes (fetch)          Transformación              Persistencia
┌──────────────────┐     ┌─────────────────────┐     ┌────────────────────┐
│ WorldBankClient  │────►│ normalize_countries  │────►│ upsert_countries   │
│ (httpx, paginate)│     │ normalize_indicators │     │ upsert_debt_records│
│ IDS + QEDS SDDS  │     │ normalize_debt_recs  │     │ (batched, ON       │
└──────────────────┘     │ normalize_qeds_recs  │     │  CONFLICT upsert)  │
┌──────────────────┐     │ merge_by_priority    │     │ delete_imf_proxy   │
│ ImfDataMapper    │────►│ keep_imf_uncovered   │     │ delete_qeds_rows   │
│ (httpx)          │     └─────────────────────┘     │ invalidate_caches  │
└──────────────────┘                                  └────────────────────┘
┌──────────────────┐
│ WikidataClient   │────► seed_governments (SPARQL + pilot fallback)
│ (SPARQL, chunked)│
└──────────────────┘
```

### 6.2 CLI y entry points

| Comando | Función |
|---|---|
| `deudamundi-etl-global` | ETL completo: WB IDS + QEDS (si habilitado) + IMF (si habilitado) + gobiernos (si habilitado) |
| `deudamundi-etl-worldbank` | Alias de `deudamundi-etl-global` |
| `deudamundi-seed-governments` | Solo ETL de periodos de gobierno |
| `deudamundi-report-gaps` | Genera reporte JSON de cobertura en `api/reports/` |

### 6.3 Endpoints admin (protegidos por `X-API-Key`)

| Endpoint | Descripción |
|---|---|
| `POST /api/v1/admin/etl/run` | ETL global |
| `POST /api/v1/admin/etl/world-bank/run` | ETL World Bank |
| `POST /api/v1/admin/etl/governments/run?source=hybrid` | ETL de gobiernos |

### 6.4 Scheduler automático

Configurable con variables de entorno:

- `ETL_SCHEDULER_ENABLED=true|false`
- `ETL_SCHEDULE_CRON` (formato crontab, UTC, ej. `0 2 1 2 *`)

Usa APScheduler `BackgroundScheduler` registrado en el lifespan de FastAPI.

### 6.5 Variables de configuración ETL

| Variable | Default | Descripción |
|---|---|---|
| `ETL_ENABLE_QEDS_EXTERNAL_DEBT` | `true` | Habilitar QEDS SDDS (~118 países con deuda externa real) |
| `ETL_ALLOW_PROXY_DEBT_FALLBACK` | `false` | Habilitar fallback FMI para países sin cobertura WB/QEDS |
| `ETL_SEED_GOVERNMENTS_ENABLED` | `true` | Ejecutar seed de gobiernos en ETL global |
| `ETL_GOVERNMENTS_SOURCE` | `hybrid` | Modo: `pilot`, `wikidata`, `hybrid` |
| `ETL_GOVERNMENTS_MIN_START_YEAR` | `1990` | Año mínimo para periodos de gobierno |
| `ETL_GOVERNMENTS_TIMEOUT_SECONDS` | `30.0` | Timeout por request SPARQL |
| `ETL_GOVERNMENTS_CHUNK_SIZE` | `25` | Tamaño de chunk para queries SPARQL |
| `ETL_GOVERNMENTS_MAX_DURATION_SECONDS` | `180.0` | Duración máxima total del seed |

---

## 7. Contrato funcional de la API REST

Prefijo base: `/api/v1`

### 7.1 Endpoints públicos

| Método | Ruta | Descripción | Cache TTL |
|---|---|---|---|
| `GET` | `/health` | Health check | — |
| `GET` | `/globe-data?region=` | Payload liviano para globo 3D | 24 h |
| `GET` | `/countries?page=&page_size=&region=` | Listado paginado de países | 6 h |
| `GET` | `/countries/{iso3}` | Detalle de país + equivalencias | 6 h |
| `GET` | `/countries/{iso3}/history` | Serie histórica anual | 6 h |
| `GET` | `/countries/{iso3}/governments` | Periodos de gobierno | 6 h |
| `GET` | `/countries/compare?iso3=ARG&iso3=USA` | Comparación multi-país (≥ 2) | 6 h |
| `GET` | `/rankings?metric=&region=&limit=` | Ranking global por métrica | 24 h |

### 7.2 Endpoints administrativos (requieren `X-API-Key`)

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/admin/etl/run` | Ejecutar ETL global |
| `POST` | `/admin/etl/world-bank/run` | Ejecutar ETL World Bank |
| `POST` | `/admin/etl/governments/run?source=` | Ejecutar ETL de gobiernos |

### 7.3 Semántica de errores

| Código | Significado |
|---|---|
| `404` | Recurso país inexistente |
| `422` | Parámetros inválidos (ej. comparación con < 2 ISO3, métrica no soportada) |
| `429` | Rate limit excedido (`{"detail": "Rate limit exceeded"}`) |
| `500` | Error interno de ETL u operación |

### 7.4 Cache y seguridad

- **Cache:** Redis cache-aside con TTL configurable. Invalidación automática post-ETL (prefijos `countries:*`, `rankings:*`, `globe-data:*`).
- **CORS:** configurable por `CORS_ALLOWED_ORIGINS` y `CORS_ALLOW_ORIGIN_REGEX`. En `development`, se permiten automáticamente orígenes de red local.
- **Rate limiting:** Slowapi con límite por IP configurable (`RATE_LIMIT_REQUESTS_PER_MINUTE`).
- **Security headers:** `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Content-Security-Policy` (estricto para API, permisivo para `/docs`), HSTS opcional.

---

## 8. Frontend y experiencia de análisis

### 8.1 Rutas y páginas

| Ruta | Componente | Descripción |
|---|---|---|
| `/` | `HomePage` | Globo 3D interactivo, leyenda de intensidad, filtro por región, spotlight de comparación |
| `/country/:iso3` | `CountryDetailPage` | KPIs, gráfico histórico (doble eje), overlay de gobiernos, equivalencias, share/export |
| `/compare` | `CompareCountriesPage` | Selector multi-país, gráfico comparativo doble eje, exportación CSV/XLSX/PDF |
| `/rankings` | `RankingsPage` | Top 20 por métrica y región, búsqueda por país/ISO3 |

### 8.2 Componentes clave

| Componente | Descripción |
|---|---|
| `GlobeScene` | Globo Three.js con polígonos por país, texturas, bump map, atmósfera, auto-rotación inteligente |
| `GlobeLegend` | Leyenda interactiva con bandas de intensidad (low/medium/high) y cobertura de datos |
| `CountryHero` | Hero responsive con KPIs animados (`MetricCounter`) |
| `CountryHistoryChart` | Gráfico D3 de series temporales con doble eje (USD + %PIB) y overlay de gobiernos |
| `CountryComparisonChart` | Gráfico multi-serie para comparación entre países |
| `ShareCardActions` | Generación de share card PNG con mini gráfico, Web Share API, clipboard fallback |
| `AppHeader` / `AppFooter` | Navegación global con créditos de autor y logo |
| `LanguageSwitcher` | Selector ES/EN |
| `LoadingPanel` | Skeleton/shimmer para estados de carga |

### 8.3 Capacidades de producto

- **Visualización 3D:** Globo interactivo con polígonos políticos, hover con métricas, click para navegar. Fallback tabular automático sin WebGL.
- **Doble eje en gráficos:** Series de stock en USD (eje izquierdo) y %PIB (eje derecho) tanto en detalle como en comparación.
- **Overlay de gobiernos:** Periodos de mandato superpuestos en la línea temporal, con etiquetas escalonadas y nombres locale-aware (ES/EN).
- **Exportación client-side:** CSV, XLSX (serie histórica + detalle) y PDF branded con gráficos y resumen de gobiernos.
- **i18n:** Español (default) e inglés, con diccionario centralizado en `lib/translations.ts`.
- **Enfoque geográfico:** Al filtrar por región, la cámara del globo se centra automáticamente.
- **UX mobile:** Autoscroll a años recientes en gráficos cartesianos + hint de scroll horizontal.
- **Equivalencias emocionales:** Traducción del stock de deuda a referentes tangibles (hospitales, salarios docentes, salarios mínimos).
- **Metadatos sociales:** Open Graph y Twitter Cards dinámicos por país.

### 8.4 State management

- **`globeStore`** (Zustand): hover state del país seleccionado en el globo.
- **`localeStore`** (Zustand): idioma activo (`es` | `en`).
- **Data fetching:** llamadas directas al cliente API tipado (`services/deudamundiApi.ts`), sin capa de caché client-side (se delega a Redis en backend).

---

## 9. Ejecución local reproducible

### Opción recomendada: Docker Compose (stack completo)

```bash
docker compose up --build
```

| Servicio | URL |
|---|---|
| API | `http://localhost:8000` |
| Health check | `http://localhost:8000/api/v1/health` |
| API Docs (Swagger) | `http://localhost:8000/docs` |
| Web | `http://localhost:5173` |
| PostgreSQL | `localhost:5432` |
| Redis | `localhost:6379` |

### Opción por servicio

Consultar documentación detallada:
- Backend: [`api/README.md`](api/README.md)
- Frontend: [`web/README.md`](web/README.md)

### Seed de datos inicial

Tras levantar el stack:

```bash
# 1. Aplicar migraciones (automático con RUN_MIGRATIONS=true en Docker)
docker compose exec api alembic upgrade head

# 2. Ejecutar ETL global
docker compose exec api deudamundi-etl-global

# 3. Seed de gobiernos
docker compose exec api deudamundi-seed-governments

# 4. Reporte de cobertura
docker compose exec api deudamundi-report-gaps
```

---

## 10. Calidad, validación y CI

### Backend

```bash
cd api
pip install -e .[dev]
ruff check app tests         # Lint
pytest                        # Tests
```

### Frontend

```bash
cd web
npm install
npm run build                 # TypeScript check + bundle de producción
npm run test -- --runInBand   # Jest + RTL
```

### Cobertura de tests existente

| Área | Tests cubren |
|---|---|
| **Endpoints REST** | countries, rankings, globe, health, security, admin ETL |
| **ETL** | transform (normalize/merge), repository (upserts), IMF client, Wikidata client |
| **Configuración** | DATABASE_URL normalization, fallback development host |
| **Frontend** | Cliente API, HomePage, CountryDetailPage, RankingsPage, CompareCountriesPage, GlobeLegend, MetricCounter, data exports, chart scroll, government labels, equivalences, env detection |

---

## 11. Despliegue y operación

### Backend (VPS Linux)

Ruta de despliegue:

```bash
deploy/vps/systemd/deploy_systemd.sh   # Instala/actualiza servicio systemd
deploy/vps/systemd/nginx.deudamundi-api.conf  # Reverse proxy Nginx
api/scripts/start_api.sh               # Entrypoint: migraciones + uvicorn
```

Variables de producción obligatorias:

| Variable | Ejemplo |
|---|---|
| `APP_ENV` | `production` |
| `SUPABASE_DATABASE_URL` | `postgresql://...` |
| `REDIS_URL` | `redis://localhost:6379/0` |
| `CORS_ALLOWED_ORIGINS` | `https://deudamundi.econopapi.com` |
| `ADMIN_API_KEY` | `<secret>` |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | `100` |
| `SECURITY_HSTS_ENABLED` | `true` |
| `RUN_MIGRATIONS` | `true` |

### Frontend (Vercel)

Despliegue automático desde el monorepo. Variable:

| Variable | Default |
|---|---|
| `VITE_API_BASE_URL` | `https://deudamundi.dlimon.net` |

### Notas operativas

- `GET /` devuelve `404` por diseño; el health check es `GET /api/v1/health`.
- En `development`, la API admite orígenes de red local vía regex para pruebas en dispositivos móviles.
- La app y Alembic priorizan `SUPABASE_DATABASE_URL` sobre `DATABASE_URL` si ambas están definidas.

---

## 12. Limitaciones y amenazas a la validez

| # | Limitación | Impacto | Mitigación |
|---|---|---|---|
| 1 | **Cobertura IDS limitada a economías reportantes** | ~121 de 217 países sin datos IDS de deuda externa. Sesgo hacia economías en desarrollo con financiamiento externo. | QEDS SDDS cubre ~118 países adicionales (incluyendo economías avanzadas). Proxy FMI como último recurso. |
| 2 | **Heterogeneidad conceptual entre fuentes** | IDS mide deuda externa BOP; QEDS mide posición de deuda externa bruta (todos los sectores); IMF proxy mide deuda pública bruta. | Cascada de prioridad (IDS > QEDS > IMF). Etiquetado `debt_concept` end-to-end. IMF proxy desactivado por defecto. |
| 3 | **QEDS: datos trimestrales convertidos a anuales** | Se selecciona un trimestre por año (Q4 preferido); la deuda externa puede fluctuar intra-año. | Documentado; se prefiere Q4 (cierre fiscal) como mejor aproximación anual. |
| 4 | **Dependencia de proveedores externos** | Disponibilidad y formato de APIs de WB/IMF/Wikidata pueden cambiar. | ETL tolerante a fallos, validación de tipos, timeout configurable. |
| 5 | **Frecuencia anual** | No captura dinámicas intra-año ni shocks de liquidez. | Limitación inherente a las fuentes; documentada en UI. |
| 6 | **Nombres de gobiernos** | Wikidata puede tener inconsistencias o vacíos en periodos históricos. | Modo `hybrid` con semillas piloto como fallback. |
| 7 | **Equivalencias emocionales** | Valores de referencia globales (costo de hospital, salario docente) son estimaciones gruesas. | Documentado como MVP; plan de regionalización futura. |
| 8 | **Performance en móviles low-end** | Globo 3D puede ser pesado en hardware limitado. | Fallback tabular automático sin WebGL. |

---

## 13. Roadmap a release estable

| Prioridad | Tarea |
|---|---|
| ~~Alta~~ | ~~Integrar QEDS SDDS como fuente intermedia de deuda externa real~~ ✅ Completado |
| Alta | Auditoría final de cobertura/consistencia por región y series atípicas |
| Alta | Versionado semántico público (`v1.0.0`) y política formal de changelog |
| Media | Performance móvil: optimización del globo en hardware low-end |
| Media | Benchmark longitudinal de latencia/carga documentado |
| Baja | Endurecimiento documental para publicación técnica (metodología formal, amenazas, anexos) |
| Baja | Regionalización de equivalencias emocionales |

---

## 14. Convenciones de contribución

- **Commits:** Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`).
- **Ramas:** `main` (producción), `dev` (integración), `feature/*` (trabajo incremental).
- **Principios:** cambios pequeños, testeados, con actualización documental si aplica.
- **Documentación:** si cambias endpoints, configuración, ETL, copy o metodología, actualiza los READMEs relevantes.

---

## 15. Cita académica

Si usas DeudaMundi en análisis o investigación, cita este repositorio y registra versión y fecha de consulta.

> Limón, D. (2026). *DeudaMundi: Atlas global e interactivo de deuda externa soberana por país* (v0.1.0). GitHub. https://deudamundi.econopapi.com

Formato BibTeX:

```bibtex
@software{limon2026deudamundi,
  author  = {Limón, Daniel},
  title   = {DeudaMundi: Atlas global e interactivo de deuda externa soberana por país},
  year    = {2026},
  url     = {https://deudamundi.econopapi.com},
  version = {0.1.0}
}
```

---

## Documentación por módulo

| Módulo | Archivo |
|---|---|
| Backend / API | [`api/README.md`](api/README.md) |
| Frontend / Web | [`web/README.md`](web/README.md) |

---

**Contacto:** Daniel Limón — `dani@dlimon.net` — [econopapi.com](https://econopapi.com)
