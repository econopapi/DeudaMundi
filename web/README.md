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
