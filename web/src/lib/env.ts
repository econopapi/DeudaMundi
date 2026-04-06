
const DEFAULT_API_BASE_URL = "https://deudamundi.dlimon.net";
export function getApiBaseUrl(): string {
  if (typeof window !== "undefined" && window.__DEUDAMUNDI_API_BASE_URL__) {
    return window.__DEUDAMUNDI_API_BASE_URL__;
  }

  return DEFAULT_API_BASE_URL;
}
