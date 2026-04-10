
const DEFAULT_API_BASE_URL = "https://deudamundi.dlimon.net";
const LOCAL_API_BASE_URL = "http://localhost:8000";

function isLocalFrontendHost(): boolean {
  if (typeof window === "undefined") {
    return false;
  }

  const localHosts = new Set(["localhost", "127.0.0.1", "0.0.0.0"]);
  return localHosts.has(window.location.hostname);
}

export function getApiBaseUrl(): string {
  if (typeof window !== "undefined" && window.__DEUDAMUNDI_API_BASE_URL__) {
    return window.__DEUDAMUNDI_API_BASE_URL__;
  }

  if (isLocalFrontendHost()) {
    return LOCAL_API_BASE_URL;
  }

  return DEFAULT_API_BASE_URL;
}
