# DeudaMundi

Atlas global e interactivo de deuda soberana por país, con enfoque en visualización clara, rigor económico y potencial viral.

## Estado del proyecto

Actualmente en **Fase 0 (Fundamentos)** del roadmap:

- Monorepo inicial listo (`api/` + `web/`)
- Backend FastAPI con endpoint de salud
- ETL inicial World Bank para deuda externa total
- Trigger admin protegido + scheduler base para ETL
- Seed inicial de gobiernos piloto (AR, US, BR, DE, GR)
- Reporte de gaps de cobertura ETL
- Frontend React + Vite + Tailwind con testing inicial
- Docker Compose para entorno local (PostgreSQL + Redis + servicios)
- CI básica con GitHub Actions

## Estructura del monorepo

```text
.
├── api/          # Backend FastAPI + tests Pytest
├── web/          # Frontend React + Vite + Tailwind + Jest/RTL
├── docker-compose.yml
└── README.md
```

## Stack técnico

- **Backend:** Python 3.12, FastAPI, SQLAlchemy (preparado), Redis (cache), Pytest
- **Frontend:** React 18, Vite, TypeScript, TailwindCSS, Jest + React Testing Library
- **Infra:** Docker Compose, GitHub Actions
- **Datos/DB:** PostgreSQL en Supabase (objetivo de despliegue)
- **Deploy:** Backend en VPS Linux, frontend en Vercel

## Cómo ejecutar localmente

### Opción recomendada: Docker Compose

1. Levanta todo el stack local desde la raíz:
	- PostgreSQL (5432)
	- Redis (6379)
	- API FastAPI (8000)
	- Web Vite (5173)

2. Endpoint inicial disponible:
	- `GET http://localhost:8000/api/v1/health`

### Opción por servicio

#### API

- Ver guía en `api/README.md`

#### Web

- Ver guía en `web/README.md`

## Calidad y CI

Workflow en `.github/workflows/ci.yml` ejecuta:

- API: lint (`ruff`) + tests (`pytest`)
- Web: build (`vite`) + tests (`jest`)

## Convenciones de colaboración

- Commits con **Conventional Commits**
- Estrategia de ramas:
  - `main`: producción
  - `develop`: integración
  - `feature/*`: features por fase

## Cierre Fase 0 ✅

Checklist completado:

- Entorno base de monorepo operativo (`api` + `web`)
- Esquema DB versionado con Alembic (`countries`, `debt_records`, `etl_runs`, `governments`)
- ETL World Bank ejecutable + trazabilidad en `etl_runs`
- Trigger admin y scheduler base para ejecución ETL
- Seed de gobiernos piloto para 5 países
- Reporte de gaps para validar cobertura de datos

### Última validación funcional (local)

- Países procesados ETL: `217`
- Registros deuda procesados: `6279`
- Registros deuda upsertados: `5785`
- Gobiernos seed insertados/actualizados: `22`
- Países con datos de deuda: `121`
- Países sin datos de deuda: `96`
- Rango temporal de deuda: `1970–2024`

## Siguiente fase

Arranca **Fase 1 — Backend MVP**:

- Iteración 1 completada: `countries` listado + detalle y equivalencias básicas
- Iteración 2 completada: `history` y `governments` por país
- Iteración 3 completada: `rankings` (absoluto, %PIB, per cápita)
- Cache base por endpoint iniciada en `rankings` (Redis)
- Iteración 4 completada: CORS + headers de seguridad + rate limiting básico
- Iteración 5 completada: pruebas de integración core + índices de optimización
- Iteración 6 completada: `globe-data` + cache Redis en endpoints de lectura
- Semana 5 (iteración 1) completada: rate limiting migrado a `Slowapi`
- Pendiente: deploy (Railway/Render) y conexión productiva completa a Supabase

---

Autor:  
Daniel Limón <dani@dlimon.net>

