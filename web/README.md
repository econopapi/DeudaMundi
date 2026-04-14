# Web DeudaMundi

Frontend interactivo en **React + Vite + TypeScript** para el Atlas Global de Deuda Externa Soberana.

Ofrece un globo 3D navegable, fichas detalladas por país con series históricas, comparador multi-país, rankings y exportación de datos en múltiples formatos.

> **Licencia y uso:** el código fuente del repositorio se publica bajo licencia MIT, pero esa licencia no sustituye los términos aplicables a datos, APIs, exports, share cards u otros outputs derivados de fuentes externas. El nombre **DeudaMundi**, la marca **econopapi** y la identidad visual del proyecto quedan reservados y no se licencian por MIT.

---

## Tabla de contenidos

1. [Arquitectura del frontend](#1-arquitectura-del-frontend)
2. [Rutas y páginas](#2-rutas-y-páginas)
3. [Componentes](#3-componentes)
4. [State management](#4-state-management)
5. [Cliente API](#5-cliente-api)
6. [Tipos TypeScript](#6-tipos-typescript)
7. [Internacionalización (i18n)](#7-internacionalización-i18n)
8. [Librerías y utilidades](#8-librerías-y-utilidades)
9. [Stack técnico](#9-stack-técnico)
10. [Configuración](#10-configuración)
11. [Desarrollo local](#11-desarrollo-local)
12. [Testing](#12-testing)
13. [Deploy](#13-deploy)

---

## 1. Arquitectura del frontend

```text
src/
├── App.tsx                      # Router principal (react-router-dom v6)
├── main.tsx                     # Entry point (React DOM + BrowserRouter)
├── index.css                    # Estilos globales (TailwindCSS)
├── vite-env.d.ts                # Tipos Vite
├── assets/
│   └── author-logo.svg         # Logo del autor
├── components/
│   ├── AppHeader.tsx            # Header global con navegación y créditos
│   ├── AppFooter.tsx            # Footer global
│   ├── AuthorCredits.tsx        # Card de créditos del autor
│   ├── LanguageSwitcher.tsx     # Selector de idioma ES/EN
│   ├── country/
│   │   ├── CountryHero.tsx      # Hero con KPIs animados
│   │   ├── CountryHistoryChart.tsx     # Gráfico D3 doble eje + overlay gobiernos
│   │   ├── CountryComparisonChart.tsx  # Gráfico comparativo multi-país
│   │   ├── MetricCounter.tsx    # Contador animado de métricas
│   │   └── ShareCardActions.tsx # Share card PNG + export actions
│   ├── globe/
│   │   ├── GlobeScene.tsx       # Globo Three.js (react-globe.gl)
│   │   ├── GlobeLegend.tsx      # Leyenda interactiva con bandas
│   │   ├── CountryMarkers.tsx   # Marcadores de país en globo
│   │   ├── CountryTooltip.tsx   # Tooltip al hover con métricas
│   │   ├── globeColors.ts      # Paleta de colores por intensidad
│   │   └── globeView.ts        # Coordenadas de enfoque por región
│   └── ui/
│       └── LoadingPanel.tsx     # Skeleton/shimmer de carga
├── pages/
│   ├── HomePage.tsx             # Globo 3D + leyenda + spotlight comparación
│   ├── CountryDetailPage.tsx    # Ficha país: KPIs + gráfico + gobiernos + export
│   ├── CompareCountriesPage.tsx # Comparador multi-país
│   └── RankingsPage.tsx         # Rankings por métrica y región
├── services/
│   └── deudamundiApi.ts         # Cliente HTTP tipado (fetch wrapper)
├── store/
│   ├── globeStore.ts            # Zustand: hover state del globo
│   └── localeStore.ts           # Zustand: idioma activo (es/en)
├── lib/
│   ├── translations.ts          # Diccionario i18n ES/EN completo
│   ├── regions.ts               # Opciones de región (Home + Rankings)
│   ├── formatters.ts            # Formateo de números, moneda, porcentaje
│   ├── equivalences.ts          # Equivalencias emocionales (hospitales, salarios)
│   ├── dataExports.ts           # Exportación CSV, XLSX, PDF
│   ├── shareCardChart.ts        # Generación de mini gráfico para share card PNG
│   ├── governmentLabels.ts      # Nombres de líderes locale-aware (ES/EN)
│   ├── chartScroll.ts           # Autoscroll al extremo derecho en gráficos mobile
│   ├── env.ts                   # Detección de API base URL (local vs producción)
│   └── webgl.ts                 # Detección de soporte WebGL
├── types/
│   └── api.ts                   # Tipos TypeScript alineados a schemas de la API
└── test/
    └── fileMock.ts              # Mock de archivos estáticos para Jest
```

### Patrón arquitectónico

- **Pages**: componentes de ruta completa que orquestan data fetching y composición de subcomponentes.
- **Components**: UI reutilizable, agrupada por dominio (`country/`, `globe/`, `ui/`).
- **Services**: capa de acceso a la API (fetch tipado, sin caché client-side).
- **Store**: estado global mínimo con Zustand (solo hover del globo e idioma).
- **Lib**: utilidades puras sin estado ni efectos (formateo, traducciones, exportación, colores).
- **Types**: contratos TypeScript que reflejan los schemas Pydantic de la API.

---

## 2. Rutas y páginas

| Ruta | Componente | Descripción |
|---|---|---|
| `/` | `HomePage` | Globo 3D interactivo con leyenda, filtro por región, CTA a documentación/código fuente, spotlight de comparación y sugerencias rápidas |
| `/country/:iso3` | `CountryDetailPage` | Ficha país: hero con KPIs animados, gráfico histórico doble eje con overlay de gobiernos, equivalencias emocionales, share card, exportación |
| `/compare` | `CompareCountriesPage` | Selector multi-país (chips + búsqueda), gráfico comparativo doble eje, exportación CSV/XLSX/PDF |
| `/rankings` | `RankingsPage` | Top 20 por métrica (`absolute`, `pct_gdp`, `per_capita`), filtro por región, búsqueda por nombre/ISO3 |
| `*` | — | Redirect a `/` |

### HomePage

- Globo 3D con polígonos políticos renderizados sobre esfera con textura realista, bump map, atmósfera y contornos.
- Auto-rotación inteligente: se frena en hover, se detiene en drag, reanuda suavemente.
- Leyenda interactiva con bandas de intensidad (low/medium/high); países no seleccionados se atenúan (no desaparecen).
- Enfoque geográfico automático al seleccionar región.
- Fallback tabular automático si WebGL no está disponible.
- CTA superior con acceso directo a la documentación pública del proyecto y al repositorio fuente.
- Bloque spotlight para descubrir y lanzar comparaciones, con sugerencias priorizando pares latinoamericanos.

### CountryDetailPage

- Hero responsive con KPIs principales y contadores animados.
- Gráfico histórico D3 con doble eje vertical (USD izquierdo, %PIB derecho).
- Overlay de periodos de gobierno con etiquetas escalonadas y nombres locale-aware.
- Sección de equivalencias emocionales con iconografía semántica.
- Share card PNG client-side con mini gráfico histórico real.
- Exportación: CSV, XLSX (datos históricos), PDF branded (gráfico + resumen de gobiernos).
- Metadatos sociales dinámicos (`og:*`, `twitter:*`).

### CompareCountriesPage

- Selector multi-país con chips y búsqueda por nombre/ISO3 (hasta ~5 países para legibilidad).
- Gráfico comparativo con doble eje: stock USD (líneas sólidas, eje izq.) y %PIB (líneas punteadas, eje der.).
- Exportación CSV, XLSX y PDF de la comparación.

### RankingsPage

- Rankings por tres métricas: stock absoluto, deuda/PIB, deuda per cápita.
- Filtros por región con opciones centralizadas.
- Búsqueda/autocomplete por nombre de país o código ISO3.
- Scroll horizontal seguro en tabla para mobile.

---

## 3. Componentes

### 3.1 Globe (`components/globe/`)

| Componente | Responsabilidad |
|---|---|
| `GlobeScene` | Renderiza globo Three.js con `react-globe.gl`. Polígonos de `world-atlas`/`topojson-client`. Texturas, bump map, atmósfera. Maneja auto-rotación y enfoque por región. |
| `GlobeLegend` | Leyenda con bandas de color, cobertura de datos (`X/Y`), y presets de filtrado por intensidad. |
| `CountryMarkers` | Marcadores visuales sobre el globo (si aplica). |
| `CountryTooltip` | Tooltip al hover mostrando nombre, deuda total y deuda/PIB. |
| `globeColors.ts` | Paleta de colores y funciones de mapeo intensidad → color. |
| `globeView.ts` | Coordenadas de cámara por región para enfoque geográfico automático. |

### 3.2 Country (`components/country/`)

| Componente | Responsabilidad |
|---|---|
| `CountryHero` | Header del detalle con KPIs principales (deuda, per cápita, %PIB) usando `MetricCounter`. |
| `CountryHistoryChart` | Gráfico D3 de series temporales. Doble eje: USD (izq) + %PIB (der). Overlay de gobiernos con etiquetas escalonadas. |
| `CountryComparisonChart` | Gráfico D3 multi-serie para comparación. Líneas sólidas (USD) y punteadas (%PIB). |
| `MetricCounter` | Contador animado que interpola desde 0 hasta el valor final. |
| `ShareCardActions` | Botones de compartir: genera PNG con canvas (`shareCardChart.ts`), usa Web Share API con clipboard fallback. También botones de export CSV/XLSX/PDF. |

### 3.3 UI (`components/ui/`)

| Componente | Responsabilidad |
|---|---|
| `LoadingPanel` | Skeleton/shimmer genérico para estados de carga. |

### 3.4 Layout

| Componente | Responsabilidad |
|---|---|
| `AppHeader` | Header global con enlace a Home, créditos de autor y acciones opcionales como CTA externos. |
| `AppFooter` | Footer global con nombre del proyecto, procedencia del build y link al autor. |
| `AuthorCredits` | Card de información del autor con logo incorporado. |
| `LanguageSwitcher` | Toggle ES/EN que actualiza `localeStore`. |

---

## 4. State management

Estado global mínimo con **Zustand** (sin boilerplate Redux). Solo dos stores:

### `globeStore`

```typescript
type HoveredCountry = {
  iso3: string;
  name: string;
  debtPctGdp: number | null;
  debtTotalUsd: number | null;
};

type GlobeState = {
  hoveredCountry: HoveredCountry | null;
  setHoveredCountry: (country: HoveredCountry | null) => void;
};
```

Se usa para sincronizar el hover del globo con la leyenda y el tooltip.

### `localeStore`

```typescript
type Locale = "en" | "es";

type LocaleState = {
  locale: Locale;  // default: "es"
  setLocale: (locale: Locale) => void;
};
```

Controla el idioma activo para toda la app. Consumido por todos los componentes que renderizan copy.

### Sin caché client-side

El data fetching se realiza con `fetch` directo al backend. No hay capa de cache en el cliente (SWR, React Query, etc.) porque el backend ya implementa cache-aside con Redis con TTLs apropiados.

---

## 5. Cliente API

Archivo: `services/deudamundiApi.ts`

Un wrapper tipado sobre `fetch` que:
1. Construye URLs a partir de `getApiBaseUrl()` + path.
2. Lanza `Error` con `status` si la respuesta no es `ok`.
3. Retorna JSON tipado contra los tipos de `types/api.ts`.

### Funciones disponibles

| Función | Endpoint | Retorno |
|---|---|---|
| `fetchGlobeData(region?)` | `GET /api/v1/globe-data` | `GlobeDataResponse` |
| `fetchCountryDetail(iso3)` | `GET /api/v1/countries/{iso3}` | `CountryDetailResponse` |
| `fetchCountryHistory(iso3)` | `GET /api/v1/countries/{iso3}/history` | `CountryHistoryResponse` |
| `fetchCountryGovernments(iso3)` | `GET /api/v1/countries/{iso3}/governments` | `CountryGovernmentsResponse` |
| `fetchCountriesCompare(iso3[])` | `GET /api/v1/countries/compare` | `CountriesCompareResponse` |
| `fetchRankings(metric, region?, limit?)` | `GET /api/v1/rankings` | `RankingsResponse` |

---

## 6. Tipos TypeScript

Archivo: `types/api.ts`

Tipos alineados 1:1 con los schemas Pydantic de la API:

| Tipo | Descripción |
|---|---|
| `GlobeDataPoint` | Punto del globo: iso3, name_en, region, métricas, trazabilidad |
| `GlobeDataResponse` | Wrapper: item_count + items[] |
| `CountryDetailResponse` | Detalle país: datos generales + métricas + equivalencias |
| `CountryHistoryItem` | Fila de serie histórica: año, métricas, source |
| `CountryHistoryResponse` | Wrapper: iso3 + items[] |
| `CountryGovernmentItem` | Periodo de gobierno: leader, party, dates, lean |
| `CountryGovernmentsResponse` | Wrapper: iso3 + items[] |
| `CountryCompareItem` | Un país en comparación: detail + history |
| `CountriesCompareResponse` | Resultado de comparación: requested, missing, items[] |
| `EquivalenceItem` | Equivalencia emocional: label, value, description |
| `RankingItem` | Fila de ranking: rank, iso3, value, year |
| `RankingsResponse` | Wrapper: metric, region, limit, items[] |
| `RankingMetric` | Union: `"absolute"` \| `"pct_gdp"` \| `"per_capita"` |

---

## 7. Internacionalización (i18n)

### Arquitectura

- Diccionario centralizado en `lib/translations.ts` con claves para `en` y `es`.
- Idioma por defecto: **español** (`es`).
- Store global: `localeStore` (Zustand).
- Selector: `LanguageSwitcher` en el header.

### Cobertura de traducciones

Incluye todas las cadenas visibles al usuario:
- Títulos y subtítulos de todas las páginas.
- Etiquetas de métricas, filtros, regiones.
- Mensajes de carga, error y estados vacíos.
- Tooltips de interacción del globo.
- Copy de exportación, comparación, share.
- Equivalencias emocionales.
- Metadatos sociales.

### Nombres de líderes locale-aware

En español, los nombres de gobierno priorizan nombre completo; si no cabe, usan fallback tipo nombre + dos apellidos finales (ej. "López Obrador", "de Kirchner"). Implementado en `lib/governmentLabels.ts`.

---

## 8. Librerías y utilidades

### `lib/` — Funciones puras

| Archivo | Responsabilidad |
|---|---|
| `translations.ts` | Diccionario i18n completo ES/EN (~120 claves) |
| `regions.ts` | Listas de regiones para Home y Rankings (centralizadas) |
| `formatters.ts` | Formateo de números (compactos), moneda USD, porcentaje |
| `equivalences.ts` | Cálculo de equivalencias emocionales (hospitales, salarios docentes, salarios mínimos) |
| `dataExports.ts` | Generación client-side de CSV, XLSX (con `xlsx`) y PDF (con `jspdf`) |
| `shareCardChart.ts` | Dibuja mini gráfico histórico real en canvas para share card PNG |
| `governmentLabels.ts` | Lógica de nombres compactos de líderes por locale |
| `chartScroll.ts` | Autoscroll al extremo derecho en gráficos mobile |
| `env.ts` | Detección de API base URL: usa `VITE_API_BASE_URL` o infiere desde hostname |
| `webgl.ts` | Detección de soporte WebGL en el navegador |

---

## 9. Stack técnico

| Tecnología | Versión | Propósito |
|---|---|---|
| **React** | 18 | UI framework |
| **Vite** | 5 | Bundler y dev server |
| **TypeScript** | 5 | Tipado estático |
| **TailwindCSS** | 3.x | Estilos utility-first |
| **D3.js** | 7.x | Gráficos de series temporales |
| **react-globe.gl** | 2.37+ | Globo 3D |
| **Three.js** | 0.170 | Motor 3D (peer dep de react-globe.gl) |
| **Zustand** | 4.x | State management minimal |
| **react-router-dom** | 6.x | Routing SPA |
| **topojson-client** | 3.x | Parsing de geometrías de países |
| **world-atlas** | 2.x | GeoJSON de países |
| **jspdf** | 2.x | Generación de PDF client-side |
| **xlsx** | 0.18 | Generación de Excel client-side |
| **@vercel/analytics** | 2.x | Web analytics |
| **Jest** | 29 | Test runner |
| **React Testing Library** | 16 | Testing de componentes |

---

## 10. Configuración

### Variables de entorno

| Variable | Default | Descripción |
|---|---|---|
| `VITE_API_BASE_URL` | `https://deudamundi.dlimon.net` | URL base del backend API |

### Detección automática de entorno local

Si el frontend se abre desde `localhost` o red local (`192.168.x.x`, `10.x.x.x`, `172.16-31.x.x`, `*.local`), el cliente usa automáticamente `http://<host>:8000` como API base. Esto permite probar en iPhone/Android accediendo a `http://<tu-ip-local>:5173`.

Para forzar un backend específico, crear `.env.local`:

```bash
VITE_API_BASE_URL=http://192.168.3.109:8000
```

---

## 11. Desarrollo local

### Con Docker Compose (recomendado)

Desde la raíz del repo:

```bash
docker compose up --build
```

El frontend queda disponible en `http://localhost:5173`.

### Standalone

```bash
cd web
npm install
npm run dev        # Dev server en http://localhost:5173
```

### Scripts disponibles

| Script | Descripción |
|---|---|
| `npm run dev` | Inicia Vite dev server con HMR |
| `npm run build` | TypeScript check (`tsc --noEmit`) + build de producción (`vite build`) |
| `npm run typecheck` | Solo validación de tipos TypeScript |
| `npm run preview` | Preview del bundle de producción |
| `npm run test` | Ejecuta tests con Jest |
| `npm run test:watch` | Jest en modo watch |

---

## 12. Testing

### Ejecutar tests

```bash
cd web
npm install
npm run test -- --runInBand
```

### Cobertura de tests

| Archivo de test | Alcance |
|---|---|
| `services/deudamundiApi.test.ts` | Cliente API: fetch, errores, query params |
| `pages/HomePage.test.ts` | HomePage: render, globe data loading |
| `pages/CountryDetailPage.test.tsx` | Detalle país: KPIs, historia, gobiernos |
| `pages/CompareCountriesPage.test.tsx` | Comparación: selector, gráfico, estados |
| `pages/RankingsPage.test.tsx` | Rankings: métricas, filtros, búsqueda |
| `components/AppHeader.test.tsx` | Header: créditos y acciones opcionales |
| `components/AppFooter.test.tsx` | Footer: branding local y créditos compactos |
| `components/globe/GlobeLegend.test.tsx` | Leyenda: bandas, cobertura |
| `components/globe/globeView.test.ts` | Coordenadas de cámara por región |
| `components/country/MetricCounter.test.tsx` | Contador animado |
| `lib/dataExports.test.ts` | Exportación CSV/XLSX/PDF |
| `lib/chartScroll.test.ts` | Autoscroll mobile |
| `lib/equivalences.test.ts` | Equivalencias emocionales |
| `lib/governmentLabels.test.ts` | Nombres de líderes locale-aware |
| `lib/shareCardChart.test.ts` | Share card canvas rendering |
| `lib/env.test.ts` | Detección de API base URL |

### Stack de testing

- **Jest** 29 como runner con `jest-environment-jsdom`.
- **React Testing Library** para rendering y assertions de componentes.
- **ts-jest** para soporte TypeScript.
- Mocks de archivos estáticos (`test/fileMock.ts`) y estilos (`identity-obj-proxy`).

---

## 13. Deploy

### Vercel (producción)

El frontend se despliega automáticamente en Vercel desde el monorepo.

Configuración de `vercel.json` para SPA routing (todas las rutas → `index.html`).

Variable de entorno en Vercel:

| Variable | Valor |
|---|---|
| `VITE_API_BASE_URL` | `https://deudamundi.dlimon.net` |

### Build manual

```bash
cd web
npm run build    # Genera dist/
```

El output en `dist/` es un bundle estático listo para servir desde cualquier CDN o servidor web.
