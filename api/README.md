# API DeudaMundi

Backend en FastAPI para servir datos del Atlas Global de Deuda.

## Desarrollo local

1. Copia `.env.example` como `.env`.
2. Instala dependencias con `pip install -e .[dev]`.
3. Levanta el servidor con `uvicorn app.main:app --reload`.

## Endpoint inicial

- `GET /api/v1/health`

## Endpoints Fase 1 (iteración 1)

- `GET /api/v1/countries`
	- Query params: `page`, `page_size`, `region`
	- Devuelve listado paginado con último dato de deuda disponible por país.
- `GET /api/v1/countries/{iso3}`
	- Devuelve detalle del país con último dato de deuda y equivalencias narrativas iniciales.

## Endpoints Fase 1 (iteración 2)

- `GET /api/v1/countries/{iso3}/history`
	- Devuelve la serie histórica de deuda del país ordenada por año desc.
- `GET /api/v1/countries/{iso3}/governments`
	- Devuelve los gobiernos cargados para el país ordenados por fecha de inicio desc.

## Endpoints Fase 1 (iteración 3)

- `GET /api/v1/rankings`
	- Query params:
		- `metric`: `absolute` | `pct_gdp` | `per_capita`
		- `region`: opcional
		- `limit`: default 20, máximo 100
	- Devuelve ranking usando último año disponible por país.

- `GET /api/v1/globe-data`
	- Query params:
		- `region`: opcional
	- Devuelve payload liviano para visualización global (iso3 + último dato de deuda por país).

### Cache Redis (lectura)

Se incorporó cache-aside con Redis para:

- `GET /api/v1/countries`
- `GET /api/v1/countries/{iso3}`
- `GET /api/v1/countries/{iso3}/history`
- `GET /api/v1/countries/{iso3}/governments`
- `GET /api/v1/rankings`
- `GET /api/v1/globe-data`

## Hardening Fase 1 (iteración 4)

- CORS configurable por `CORS_ALLOWED_ORIGINS`
- Rate limiting básico por IP (`RATE_LIMIT_REQUESTS_PER_MINUTE`)
- Security headers:
	- `X-Content-Type-Options: nosniff`
	- `X-Frame-Options: DENY`
	- `Referrer-Policy: no-referrer`
	- `Content-Security-Policy` restrictivo para API
	- `Strict-Transport-Security` opcional (`SECURITY_HSTS_ENABLED=true`)

## Semana 5 (iteración 1)

- Rate limiting migrado a **Slowapi** con límite configurable por `RATE_LIMIT_REQUESTS_PER_MINUTE`.
- Se conserva el comportamiento de respuesta `429` con `{"detail": "Rate limit exceeded"}`.

## Calidad Fase 1 (iteración 5)

- Pruebas de integración reales para:
	- `GET /api/v1/countries/{iso3}/history`
	- `GET /api/v1/countries/{iso3}/governments`
	- `GET /api/v1/rankings`
- Optimización de base de datos con índices en métricas de ranking y filtros frecuentes.

## Cierre Semana 4 (iteración 6)

- Implementado `GET /api/v1/globe-data` con payload liviano para mapa.
- Cache Redis integrada en todos los endpoints de lectura del MVP de Fase 1.

## Base de datos y migraciones

Este backend está preparado para PostgreSQL local y Supabase (producción).

### Variables de entorno relevantes

- `DATABASE_URL`: conexión principal (local o VPS).
- `SUPABASE_DATABASE_URL`: opcional; si está presente, la app y Alembic la priorizan.

### Flujo Alembic

1. Crear migración nueva:
	- `alembic revision -m "descripcion"`
2. Aplicar migraciones:
	- `alembic upgrade head`
3. Revertir última migración:
	- `alembic downgrade -1`

### Esquema inicial implementado

- `countries`
- `debt_records` (relación con `countries` y unicidad por país/año)

## ETL inicial (World Bank)

Se incluye un ETL base para ingestar deuda externa total usando el indicador:

- `DT.DOD.DECT.CD`

El ETL descarga países + series históricas, normaliza y hace upsert en:

- `countries`
- `debt_records`

Ejecución:

- `deudamundi-etl-worldbank`
- `deudamundi-seed-governments`
- `deudamundi-report-gaps`

### Flujo recomendado de cierre Fase 0

1. `alembic upgrade head`
2. `deudamundi-etl-worldbank`
3. `deudamundi-seed-governments`
4. `deudamundi-report-gaps`

El reporte de gaps se guarda en `api/reports/etl_gap_report_*.json`.

## Trigger manual y scheduler

### Endpoint admin

- `POST /api/v1/admin/etl/world-bank/run`
- Header requerido: `X-API-Key: <ADMIN_API_KEY>`

### Scheduler

Variables:

- `ETL_SCHEDULER_ENABLED` (`true`/`false`)
- `ETL_SCHEDULE_CRON` (formato crontab, UTC)

Si el scheduler está habilitado, se registra en startup de FastAPI y ejecuta el ETL según cron.
