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

## Semana 5 (iteración 2)

- Configuración de despliegue backend orientada a **VPS Linux / AWS EC2**:
	- `deploy/vps/systemd/deudamundi-api.service.template`
	- `deploy/vps/systemd/deploy_systemd.sh`
	- `deploy/vps/systemd/nginx.deudamundi-api.conf`
	- Script de arranque productivo: `api/scripts/start_api.sh`
	- Ejecuta `alembic upgrade head` al iniciar (controlado por `RUN_MIGRATIONS=true|false`).

### Variables mínimas de producción

- `APP_ENV=production`
- `API_V1_PREFIX=/api/v1`
- `SUPABASE_DATABASE_URL=<connection string>`
- `REDIS_URL=<redis connection string>`
- `CORS_ALLOWED_ORIGINS=<origins separados por coma>`
- `RATE_LIMIT_REQUESTS_PER_MINUTE=<int>`
- `SECURITY_HSTS_ENABLED=true`
- `ADMIN_API_KEY=<secret>`
- `RUN_MIGRATIONS=true`

### Notas Supabase (producción)

- La app y Alembic priorizan `SUPABASE_DATABASE_URL` sobre `DATABASE_URL`.
- Si usas pooler de Supabase, asegúrate de usar SSL y credenciales de rol con permisos de migración para el despliegue.

## Tutorial rápido: despliegue en VPS Linux (AWS EC2)

### 1) Preparar servidor

- Requisitos:
	- Ubuntu 22.04+
	- puertos abiertos: `22`, `80`, `443`
	- Python 3.12+, `python3-venv`, Nginx, Certbot
	- Redis local (o externo administrado)

### 2) Clonar proyecto y preparar entorno

Desde tu servidor:

```bash
cd /home/admin/apps
git clone <TU_REPO_GIT> deudamundi
cd deudamundi

cp api/.env.example api/.env
nano api/.env
```

Variables críticas a completar en `api/.env`:

- `SUPABASE_DATABASE_URL`
- `ADMIN_API_KEY`
- `CORS_ALLOWED_ORIGINS`
- `REDIS_URL` (ejemplo local: `redis://localhost:6379/0`)

### 3) Instalar Redis (si no lo tienes)

```bash
sudo apt update
sudo apt install -y redis-server
sudo systemctl enable --now redis-server
redis-cli ping
```

### 4) Instalar/actualizar servicio systemd

```bash
cd /home/admin/apps/deudamundi
chmod +x deploy/vps/systemd/deploy_systemd.sh
APP_DIR=/home/admin/apps/deudamundi \
SERVICE_NAME=deudamundi-api \
SERVICE_USER=admin \
SERVICE_GROUP=admin \
SERVICE_PORT=8000 \
UVICORN_WORKERS=2 \
./deploy/vps/systemd/deploy_systemd.sh
```

### 5) Configurar Nginx reverse proxy

```bash
sudo cp deploy/vps/systemd/nginx.deudamundi-api.conf /etc/nginx/sites-available/deudamundi-api
sudo ln -s /etc/nginx/sites-available/deudamundi-api /etc/nginx/sites-enabled/deudamundi-api
sudo nginx -t
sudo systemctl reload nginx
```

Edita `server_name` en el archivo Nginx con tu dominio real (ej. `api.tudominio.com`).

Si ya usas una convención de Nginx como en otras APIs del VPS, puedes reutilizarla con:

- `proxy_pass http://127.0.0.1:8000;`
- `proxy_read_timeout 86400;`
- `proxy_buffering off;`

### 6) Habilitar HTTPS (Let's Encrypt)

```bash
sudo certbot --nginx -d api.tudominio.com
sudo systemctl status certbot.timer
```

### 7) Verificación

```bash
curl -i https://api.tudominio.com/api/v1/health
sudo systemctl status deudamundi-api --no-pager
sudo journalctl -u deudamundi-api -n 100 --no-pager
```

Debe responder `200 OK`.

> Nota: `GET /` devuelve `404` por diseño. El health check correcto es `GET /api/v1/health`.

### Troubleshooting: `requires a different Python: 3.10.x not in '>=3.12'`

Si aparece ese error en EC2, tu `.venv` se creó con Python 3.10. Solución:

**Debian 12/13 (bookworm/trixie):**

```bash
sudo apt update
sudo apt install -y python3 python3-venv

cd /home/admin/apps/deudamundi/api
rm -rf .venv

cd /home/admin/apps/deudamundi
PYTHON_BIN=python3 APP_DIR=/home/admin/apps/deudamundi ./deploy/vps/systemd/deploy_systemd.sh
```

**Ubuntu 22.04 (si `python3` < 3.12):** usa `python3.12` y `python3.12-venv`.

El script ahora valida automáticamente Python `>=3.12` y recrea `.venv` si detecta versión incompatible.

## Semana 6 — Testing y performance del despliegue

### 1) Smoke tests post-deploy (manual)

```bash
curl -i https://api.tudominio.com/api/v1/health
curl -i "https://api.tudominio.com/api/v1/countries?page=1&page_size=5"
curl -i "https://api.tudominio.com/api/v1/rankings?metric=absolute&limit=5"
curl -i "https://api.tudominio.com/api/v1/globe-data"
```

### 2) EXPLAIN ANALYZE en queries críticas

Se agregó script utilitario:

- `api/scripts/explain_analyze.py`

Ejecuta:

```bash
cd /home/admin/apps/deudamundi/api
set -a
source .env
set +a
.venv/bin/python scripts/explain_analyze.py
```

### 3) Load testing básico con Locust (100 usuarios)

Se agregó:

- `api/locustfile.py`

Instala dependencias dev y ejecuta:

```bash
cd /home/admin/apps/deudamundi/api
.venv/bin/pip install -e .[dev]
LOCUST_HOST=https://api.tudominio.com .venv/bin/locust -f locustfile.py --users 100 --spawn-rate 10 --run-time 5m --headless --only-summary
```

Métrica objetivo inicial:

- Errores < 1%
- p95 de endpoints clave < 500ms (ajustable por endpoint)

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

## ETL de deuda (multifuente)

El ETL integra fuentes abiertas y sin API key para mejorar cobertura global:

- World Bank IDS: `DT.DOD.DECT.CD` (external debt stocks, total)

Fallback opcional (mezcla conceptual, desactivado por defecto):

- IMF DataMapper: `GGXWDG_NGDP` (general government gross debt, % GDP)
- IMF DataMapper: `NGDPD` (nominal GDP, USD billions)

Configuración recomendada para rigor metodológico:

- `ETL_ALLOW_PROXY_DEBT_FALLBACK=false` (default): solo deuda externa comparable.
- `ETL_ALLOW_PROXY_DEBT_FALLBACK=true`: rellena huecos con proxy de deuda pública FMI.

La normalización mantiene explícito el concepto de deuda (`debt_concept`) y su fuente (`source`, `data_source`) para no mezclar semánticas de forma opaca.
Cuando existe colisión país/año, se prioriza World Bank external debt; el proxy IMF solo entra cuando se habilita explícitamente el fallback.

La ingesta usa:

- `DT.DOD.DECT.CD` (external debt stocks, total)
- `NY.GDP.MKTP.CD` y/o `NGDPD` (PIB nominal anual en USD)
- `SP.POP.TOTL` (población anual)

Con estos indicadores el ETL calcula y persiste:

- `gdp_usd`
- `total_external_debt_usd` (campo legacy para compatibilidad)
- `debt_stock_usd` (alias semántico recomendado en payload)
- `debt_pct_gdp` derivado como `(total_external_debt_usd / gdp_usd) * 100`
- `debt_per_capita_usd` = `total_external_debt_usd / population`
- `debt_concept` (ej. `external_debt_bop`, `public_debt_proxy`)
- `data_source` (fuente exacta de cada registro)
- `data_vintage` = cierre anual (`YYYY-12-31`)

Solo se persisten años con deuda + PIB válidos. `debt_per_capita_usd` se completa cuando hay población.

### Transparencia metodológica en la API

El endpoint `GET /api/v1/countries/{iso3}` ahora devuelve metadatos explícitos:

- `debt_concept`
- `data_source`
- `data_vintage`

El endpoint `GET /api/v1/countries/{iso3}/history` también incluye estos campos por año.

El ETL descarga países + series históricas, normaliza y hace upsert en:

- `countries`
- `debt_records`

Ejecución:

- `deudamundi-etl-worldbank`
- `deudamundi-etl-global`
- `deudamundi-seed-governments`
- `deudamundi-report-gaps`

### Flujo recomendado de cierre Fase 0

1. `alembic upgrade head`
2. `deudamundi-etl-global`
3. `deudamundi-seed-governments`
4. `deudamundi-report-gaps`

El reporte de gaps se guarda en `api/reports/etl_gap_report_*.json`.

El resumen ahora incluye cobertura de:

- `countries_with_population`
- `debt_records_with_gdp`
- `debt_records_with_debt_pct_gdp`
- `debt_records_with_debt_per_capita`

## Actualización urgente de indicadores (GDP y población) en producción

Cuando se despliegue este cambio, para refrescar datos inmediatamente:

1) desplegar versión nueva del backend (systemd)
2) ejecutar ETL manual admin
3) validar endpoints de métricas

### 1) Despliegue en EC2 (systemd, sin Docker)

```bash
cd /home/admin/apps/deudamundi
git fetch --all
git checkout main
git pull --ff-only

APP_DIR=/home/admin/apps/deudamundi \
SERVICE_NAME=deudamundi-api \
SERVICE_USER=admin \
SERVICE_GROUP=admin \
SERVICE_PORT=8000 \
UVICORN_WORKERS=2 \
./deploy/vps/systemd/deploy_systemd.sh
```

### 2) Ejecutar ETL en producción

```bash
curl -X POST "https://deudamundi.dlimon.net/api/v1/admin/etl/run" \
	-H "X-API-Key: <ADMIN_API_KEY>"
```

Respuesta esperada (ejemplo de campos):

- `countries_processed`
- `debt_records_processed`
- `gdp_records_processed`
- `population_records_processed`
- `countries_with_population`
- `debt_records_upserted`
- `cache_keys_invalidated`

El ETL invalida automáticamente cache de lectura (`countries:*`, `rankings:*`, `globe-data:*`) para que los nuevos datos queden visibles al instante.

### 3) Validación post-refresh

```bash
curl -s "https://deudamundi.dlimon.net/api/v1/countries/MEX" | jq '.gdp_usd, .debt_pct_gdp, .debt_per_capita_usd'
curl -s "https://deudamundi.dlimon.net/api/v1/rankings?metric=pct_gdp&limit=5" | jq '.items | length'
curl -s "https://deudamundi.dlimon.net/api/v1/rankings?metric=per_capita&limit=5" | jq '.items | length'
```

## Trigger manual y scheduler

### Endpoint admin

- `POST /api/v1/admin/etl/world-bank/run`
- Header requerido: `X-API-Key: <ADMIN_API_KEY>`

### Scheduler

Variables:

- `ETL_SCHEDULER_ENABLED` (`true`/`false`)
- `ETL_SCHEDULE_CRON` (formato crontab, UTC)

Si el scheduler está habilitado, se registra en startup de FastAPI y ejecuta el ETL según cron.
