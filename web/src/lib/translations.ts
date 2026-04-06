import type { Locale } from "../store/localeStore";

const dictionary = {
  en: {
    homeTitle: "DeudaMundi · Global Debt Atlas",
    homeSubtitle: "Fase 2 MVP: interactive 3D globe with debt intensity and country navigation.",
    rankingsTitle: "Global rankings",
    rankingsSubtitle: "Top 20 countries by absolute debt, debt/GDP and debt per capita.",
    countryDetailPrefix: "Country detail",
    backToGlobe: "Back to globe",
    viewRankings: "View rankings",
    viewGlobalRankings: "View global rankings",
    webglFallbackTitle: "3D globe unavailable in this browser",
    webglFallbackSubtitle: "Your device does not support WebGL. You can still explore debt data in table format.",
    languageLabel: "Language",
  },
  es: {
    homeTitle: "DeudaMundi · Atlas Global de Deuda",
    homeSubtitle: "Fase 2 MVP: globo 3D interactivo con intensidad de deuda y navegación por país.",
    rankingsTitle: "Rankings globales",
    rankingsSubtitle: "Top 20 de países por deuda total, deuda/PIB y deuda per cápita.",
    countryDetailPrefix: "Detalle de país",
    backToGlobe: "Volver al globo",
    viewRankings: "Ver rankings",
    viewGlobalRankings: "Ver rankings globales",
    webglFallbackTitle: "Globo 3D no disponible en este navegador",
    webglFallbackSubtitle: "Tu dispositivo no soporta WebGL. Puedes explorar los datos en formato tabla.",
    languageLabel: "Idioma",
  },
} as const;

export type TranslationKey = keyof typeof dictionary.en;

export function t(locale: Locale, key: TranslationKey): string {
  return dictionary[locale][key] ?? dictionary.en[key];
}
