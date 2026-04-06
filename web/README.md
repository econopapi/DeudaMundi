# Web DeudaMundi

Frontend React + Vite + TailwindCSS para visualizar deuda soberana global.

## Estado actual (Fase 2 · MVP frontend)

Implementado en este hito:

- Globo 3D base con `@react-three/fiber` + `@react-three/drei`
- Integración con `GET /api/v1/globe-data`
- Marcadores por país (ISO3 + lat/lng) con intensidad por deuda/PIB
- Tooltip al hover con métricas principales
- Navegación por click a `/country/:iso3`
- Vista inicial de detalle de país con `GET /api/v1/countries/{iso3}`
- Estado global liviano para hover con `zustand`
- Tests unitarios para cliente API y leyenda del globo

Mejoras iteración siguiente (Semana 8 inicial):

- Filtro por región conectado a `GET /api/v1/globe-data?region=...`
- Carga diferida del módulo 3D con `React.lazy` + `Suspense`
- Persistencia del filtro de región en URL (`?region=...`)
- Leyenda interactiva para filtrar visualmente por banda de deuda (low/medium/high)
- Mejora visual del globo (iluminación + atmósfera) para evitar esfera negra
- Estado vacío cuando un filtro no devuelve países visibles
- Render de países como polígonos con fronteras visibles (no solo puntos)
- Territorio del país clicable para navegar al detalle (`/country/:iso3`)

Avance Semana 9 (detalle de país):

- Hero responsive del país con KPIs principales
- Contadores animados para deuda total, deuda per cápita y deuda/PIB
- Pruebas RTL para `CountryDetailPage` y `MetricCounter`

## Configuración

Variable opcional para cambiar el backend:

- `VITE_API_BASE_URL` (default: `https://deudamundi.dlimon.net`)

Ejemplo de archivo `.env.local`:

```bash
VITE_API_BASE_URL=https://deudamundi.dlimon.net
```

## Scripts

- `npm run dev`: inicia entorno de desarrollo.
- `npm run build`: ejecuta typecheck y genera bundle de producción.
- `npm run test`: ejecuta pruebas con Jest + React Testing Library.
- `npm run typecheck`: valida tipos TypeScript.
