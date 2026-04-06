# API DeudaMundi

Backend en FastAPI para servir datos del Atlas Global de Deuda.

## Desarrollo local

1. Copia `.env.example` como `.env`.
2. Instala dependencias con `pip install -e .[dev]`.
3. Levanta el servidor con `uvicorn app.main:app --reload`.

## Endpoint inicial

- `GET /api/v1/health`

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

## Trigger manual y scheduler

### Endpoint admin

- `POST /api/v1/admin/etl/world-bank/run`
- Header requerido: `X-API-Key: <ADMIN_API_KEY>`

### Scheduler

Variables:

- `ETL_SCHEDULER_ENABLED` (`true`/`false`)
- `ETL_SCHEDULE_CRON` (formato crontab, UTC)

Si el scheduler está habilitado, se registra en startup de FastAPI y ejecuta el ETL según cron.
