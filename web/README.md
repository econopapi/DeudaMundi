# Web DeudaMundi

Frontend React + Vite + TailwindCSS para visualizar deuda externa global.

## Estado actual (Fase 2 · MVP frontend)

Implementado en este hito:

- Globo 3D interactivo con `react-globe.gl` + polígonos por país
- Integración con `GET /api/v1/globe-data`
- Países clicables por territorio (fronteras políticas)
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
- Fallback automático de intensidad cuando falta `debt_pct_gdp` (usa deuda total log)
- Cobertura de datos mostrada en leyenda (`X/Y` países)

Avance Semana 9 (detalle de país):

- Hero responsive del país con KPIs principales
- Contadores animados para deuda total, deuda per cápita y deuda/PIB
- Gráfico de evolución histórica con D3 (line + area)
- Overlay de gobiernos sobre la línea temporal histórica
- Pruebas RTL para `CountryDetailPage` y `MetricCounter`

Avance Semanas 10–12 (cierre Fase 2 frontend):

- Nueva ruta `/rankings` con Top 20 por métrica (`absolute`, `pct_gdp`, `per_capita`)
- Filtros por región + búsqueda/autocomplete por país/ISO3
- Share card PNG client-side en detalle de país (download + Web Share API + clipboard fallback)
- Metadatos sociales dinámicos en detalle (`og:*`, `twitter:*`)
- Fallback sin WebGL en HomePage (tabla interactiva enlazada por país)
- Baseline i18n ES/EN con selector rápido de idioma
- Mensajería explícita para datos faltantes de fuente (`Not available from source`)

Actualización UX/UI profesional (abril 2026):

- Idioma por defecto en español (`es`), con inglés como secundario
- Traducciones expandidas para Home, Rankings, detalle de país, leyenda y componentes de sharing
- Ajuste de narrativa de producto a **deuda externa** (copy y etiquetas)
- Rediseño visual con paleta de marca (`#0D1017`, `#F5F4F0`, `#7C6AF5`), tipografías y panels tipo glass
- Estados de carga mejorados con skeleton/shimmer y transiciones suaves
- Corrección de filtro de bandas en globo: los países no seleccionados siguen visibles (atenuados), evitando “huecos” visuales
- Más realismo del globo (textura, bump map, atmósfera y contornos refinados)
- Auto-rotación inteligente: se frena drásticamente en hover y se detiene en drag, con reanudación suave
- Enfoque geográfico consistente: al elegir región, la cámara del globo se centra automáticamente en esa zona

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
