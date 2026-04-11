# DeudaMundi


![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688)
![React](https://img.shields.io/badge/frontend-React%2018-61DAFB)
![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-336791)
![Redis](https://img.shields.io/badge/cache-Redis-DC382D)

Atlas global e interactivo de **deuda externa** por país, orientado a visualización pública, consistencia metodológica y trazabilidad de datos para análisis comparado.

> Estado de madurez (abril 2026): **>90% de desarrollo funcional** y transición activa hacia formalización académica, estabilidad operativa y documentación “paper-ready”.

## Autor

[Daniel Limón](https://econopapi.com) — `dani@dlimon.net`

## Tabla de contenidos

- [1. Resumen ejecutivo](#1-resumen-ejecutivo)
- [2. Objetivo científico-técnico](#2-objetivo-científico-técnico)
- [3. Estado actual del proyecto](#3-estado-actual-del-proyecto)
- [4. Arquitectura del sistema](#4-arquitectura-del-sistema)
- [5. Modelo de datos y rigor metodológico](#5-modelo-de-datos-y-rigor-metodológico)
- [6. Contrato funcional de API (MVP)](#6-contrato-funcional-de-api-mvp)
- [7. Frontend y experiencia de análisis](#7-frontend-y-experiencia-de-análisis)
- [8. Ejecución local reproducible](#8-ejecución-local-reproducible)
- [9. Calidad, validación y CI](#9-calidad-validación-y-ci)
- [10. Despliegue y operación](#10-despliegue-y-operación)
- [11. Limitaciones actuales y riesgos conocidos](#11-limitaciones-actuales-y-riesgos-conocidos)
- [12. Roadmap a release estable](#12-roadmap-a-release-estable)
- [13. Convenciones de contribución](#13-convenciones-de-contribución)
- [14. Cita académica (sugerida)](#14-cita-académica-sugerida)

## 1. Resumen ejecutivo

`DeudaMundi` integra un backend en FastAPI + PostgreSQL + Redis con un frontend React para producir un atlas interactivo de deuda externa soberana y métricas derivadas.

El sistema prioriza:

1. **Consistencia conceptual** (deuda externa real como fuente principal).
2. **Trazabilidad por registro** (`debt_concept`, `data_source`, `data_vintage`).
3. **Reproducibilidad operativa** (ETL versionado, migraciones Alembic, CI automatizada).
4. **Accesibilidad analítica** (API REST + visualización 3D/2D + exportación `CSV/XLSX/PDF`).

## 2. Objetivo científico-técnico

Construir una infraestructura abierta para explorar deuda externa por país y tiempo, minimizando sesgos metodológicos frecuentes en comparativas internacionales.

### Preguntas que el proyecto busca responder

- ¿Cómo evoluciona la deuda externa por país en términos absolutos y relativos?
- ¿Qué heterogeneidades regionales aparecen al comparar stock, %PIB y per cápita?
- ¿Qué incertidumbre introduce la falta de cobertura y cómo se explicita en el producto?

## 3. Estado actual del proyecto

### Progreso por fases

- **Fase 0 (fundacional):** completada.
- **Fase 1 (Backend MVP):** completada en sus iteraciones funcionales principales.
- **Fase 2 (Frontend MVP):** completada con mejoras de UX, comparación multi-país y exportaciones.
- **Fase actual:** consolidación de calidad, formalización documental y preparación de release estable.

### Hitos técnicos ya implementados

- ETL World Bank para deuda externa, PIB y población.
- Fallback IMF **opcional** y explícitamente etiquetado como proxy (`public_debt_proxy`) solo para países sin cobertura World Bank externa.
- Endpoints REST para salud, países, histórico, gobiernos, ranking, globo y comparación.
- Cache Redis en endpoints de lectura (`countries:*`, `rankings:*`, `globe-data:*`).
- Seguridad base de API: CORS configurable, headers defensivos y rate limiting con `Slowapi`.
- Frontend con globo 3D, fallback no-WebGL, i18n base ES/EN, comparación 2+ países y exportaciones.

### Última evidencia ETL reportada (local)

Según `api/reports/etl_gap_report_20260406_003423.json`:

- Países procesados: `217`
- Países con datos de deuda: `121`
- Países sin datos de deuda: `96`
- Rango temporal observado: `1970–2024`

## 4. Arquitectura del sistema

### Monorepo

```text
.
├── api/                         # FastAPI + SQLAlchemy + Alembic + ETL + tests
├── web/                         # React + Vite + TypeScript + tests RTL/Jest
├── deploy/vps/                  # systemd + Nginx para despliegue backend en Linux
├── docker-compose.yml           # entorno local integrado (postgres + redis + api + web)
└── README.md
```

### Stack técnico

- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2, Alembic, Redis, Slowapi.
- **Frontend:** React 18, Vite 5, TypeScript 5, TailwindCSS, D3, react-globe.gl.
- **Testing:** Pytest + Ruff (API), Jest + RTL + TypeScript build (Web).
- **Infra local:** Docker Compose.
- **Deploy backend:** VPS Linux/EC2 con `systemd + venv + Nginx + Certbot`.

## 5. Modelo de datos y rigor metodológico

### Definiciones base

- Métrica principal: `total_external_debt_usd`.
- Métricas derivadas:
	- `debt_pct_gdp = total_external_debt_usd / gdp_usd * 100`
	- `debt_per_capita_usd = total_external_debt_usd / population`

### Fuentes y prioridad

1. **Fuente primaria (prioridad alta):** World Bank IDS `DT.DOD.DECT.CD`.
2. **Fuente auxiliar opcional:** IMF DataMapper proxy (`GGXWDG_NGDP` + `NGDPD`) solo si `ETL_ALLOW_PROXY_DEBT_FALLBACK=true` y únicamente para países sin cobertura WB externa.

### Trazabilidad expuesta al consumidor

Cada registro de deuda puede incluir metadatos de trazabilidad:

- `debt_concept` (ej. `external_debt_bop`, `public_debt_proxy`)
- `data_source` (ej. `World Bank IDS DT.DOD.DECT.CD`)
- `data_vintage` (fecha de referencia anual)

### Salvaguardas metodológicas implementadas

- Exclusión de agregados no-país en normalización de catálogo.
- Exclusión de años IMF actuales/futuros para evitar nowcasts/proyecciones en histórico.
- Priorización determinística por `source_priority` para conflictos país-año.
- Limpieza de proxies IMF obsoletos al ejecutar ETL para evitar distorsión del `latest_year`.

## 6. Contrato funcional de API (MVP)

Prefijo base: `/api/v1`

### Endpoints públicos

- `GET /health`
- `GET /globe-data?region=<optional>`
- `GET /countries?page=1&page_size=20&region=<optional>`
- `GET /countries/{iso3}`
- `GET /countries/{iso3}/history`
- `GET /countries/{iso3}/governments`
- `GET /countries/compare?iso3=ARG&iso3=USA` (mínimo 2 códigos válidos)
- `GET /rankings?metric=absolute|pct_gdp|per_capita&region=<optional>&limit=20`

### Endpoints administrativos (protegidos por `X-API-Key`)

- `POST /admin/etl/run`
- `POST /admin/etl/world-bank/run`
- `POST /admin/etl/governments/run?source=pilot|wikidata|hybrid`

### Semántica de errores relevante

- `404`: recurso país inexistente.
- `422`: parámetros inválidos (ej. comparación con <2 ISO3 válidos, métrica no soportada).
- `429`: rate limit excedido (`{"detail": "Rate limit exceeded"}`).

## 7. Frontend y experiencia de análisis

Rutas principales (`web/src/App.tsx`):

- `/` → Home (globo 3D, leyenda/filtros, entrada al análisis)
- `/country/:iso3` → ficha país (KPIs, histórico, gobiernos, share/export)
- `/compare` → comparación multi-país (series superpuestas y exportables)
- `/rankings` → ranking por métrica, región y búsqueda

Capacidades de producto:

- Visualización 3D y fallback tabular sin WebGL.
- Doble eje en histórico/comparación (USD y %PIB).
- Exportación de resultados (`CSV`, `XLSX`, `PDF`).
- i18n base español/inglés y UX responsive mobile/desktop.

## 8. Ejecución local reproducible

### Opción recomendada: stack completo con Docker Compose

Desde raíz del repositorio:

```bash
docker compose up --build
```

Servicios esperados:

- API: `http://localhost:8000`
- Health: `http://localhost:8000/api/v1/health`
- Web: `http://localhost:5173`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

### Opción por servicio

- Backend: ver `api/README.md`
- Frontend: ver `web/README.md`

## 9. Calidad, validación y CI

Pipeline de CI (`.github/workflows/ci.yml`):

- **API**
	- instalación `pip install -e .[dev]`
	- lint `ruff check app tests`
	- tests `pytest`
- **Web**
	- instalación `npm install`
	- build/typecheck `npm run build`
	- tests `npm run test -- --runInBand`

Cobertura de pruebas existente incluye (no exhaustivo):

- Endpoints de países, rankings, globo, salud, seguridad y admin ETL.
- Transformaciones ETL y repositorio de upserts.
- Cliente API frontend y páginas clave (`Home`, `CountryDetail`, `Rankings`, `Compare`).

## 10. Despliegue y operación

Ruta recomendada backend productivo:

- `deploy/vps/systemd/deploy_systemd.sh`
- `deploy/vps/systemd/deudamundi-api.service.template`
- `deploy/vps/systemd/nginx.deudamundi-api.conf`
- `api/scripts/start_api.sh` (incluye migraciones con `RUN_MIGRATIONS=true`)

Variables críticas (producción):

- `APP_ENV=production`
- `SUPABASE_DATABASE_URL`
- `REDIS_URL`
- `CORS_ALLOWED_ORIGINS`
- `ADMIN_API_KEY`
- `RATE_LIMIT_REQUESTS_PER_MINUTE`
- `SECURITY_HSTS_ENABLED=true`

Notas operativas:

- `GET /` devuelve `404` por diseño; usar `GET /api/v1/health` para health checks.
- En `development`, la API admite orígenes LAN vía regex para pruebas en dispositivos móviles.

## 11. Limitaciones actuales y riesgos conocidos

1. **Cobertura incompleta de países** bajo definición estricta de deuda externa WB.
2. **Dependencia de proveedores externos** (World Bank/IMF) para actualización periódica.
3. **Fallback IMF** es útil para cobertura, pero conceptualmente distinto (proxy de deuda pública).
4. **Documentación de benchmark formal** (latencia/carga longitudinal) aún en consolidación.

## 12. Roadmap a release estable

Prioridades recomendadas para cierre de ciclo >90%:

- Auditoría final de cobertura/consistencia por región y series atípicas.
- Cierre de performance móvil (globo en hardware low-end).
- Endurecimiento documental para publicación técnica (metodología, amenazas a la validez, anexos).
- Versionado semántico público (`v1.0.0`) y política formal de changelog.

## 13. Convenciones de contribución

- Commits con **Conventional Commits**.
- Estrategia de ramas:
	- `main`: producción
	- `develop`: integración
	- `feature/*`: trabajo incremental
- Mantener cambios pequeños, testeados y con actualización documental cuando aplique.

## 14. Cita académica (sugerida)

Si usas DeudaMundi en análisis o investigación, cita este repositorio y registra versión/fecha de consulta.

Referencia sugerida (formato libre):

`Limón, D. (2026). DeudaMundi: Atlas global e interactivo de deuda externa por país (vX.Y.Z). GitHub. https://github.com/econopapi/DeudaMundi`

---

## Documentación específica por módulo

- Backend/API: `api/README.md`
- Frontend/Web: `web/README.md`

---

**Contacto**  
Daniel Limón — `dani@dlimon.net`

