# DeudaMundi

Atlas global e interactivo de deuda soberana por país, con enfoque en visualización clara, rigor económico y potencial viral.

## Estado del proyecto

Actualmente en **Fase 0 (Fundamentos)** del roadmap:

- Monorepo inicial listo (`api/` + `web/`)
- Backend FastAPI con endpoint de salud
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

## Próximo hito (Fase 0)

- Conectar backend a PostgreSQL/Supabase con SQLAlchemy + Alembic
- Implementar primer pipeline ETL (World Bank)
- Definir contrato inicial de endpoints del MVP

---

Autor:  
Daniel Limón <dani@dlimon.net>

