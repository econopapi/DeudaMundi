
const DEFAULT_API_BASE_URL = "https://deudamundi.dlimon.net";
const LOCAL_API_BASE_URL = "http://localhost:8000";
const LOCAL_API_PORT = "8000";

function isPrivateIpv4(hostname: string): boolean {
  const match = hostname.match(/^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/);
  if (!match) {
    return false;
  }

  const octets = match.slice(1).map(Number);
  if (octets.some((octet) => Number.isNaN(octet) || octet < 0 || octet > 255)) {
    return false;
  }

  const [a, b] = octets;
  return a === 10 || (a === 172 && b >= 16 && b <= 31) || (a === 192 && b === 168);
}

function isLanHostname(hostname: string): boolean {
  return hostname.endsWith(".local") || isPrivateIpv4(hostname);
}

function resolveLocalApiBaseUrl(hostname: string): string {
  if (isLanHostname(hostname)) {
    return `http://${hostname}:${LOCAL_API_PORT}`;
  }

  return LOCAL_API_BASE_URL;
}

function isLocalFrontendHost(): boolean {
  if (typeof window === "undefined") {
    return false;
  }

  const localHosts = new Set(["localhost", "127.0.0.1", "0.0.0.0"]);
  const hostname = window.location.hostname;
  return localHosts.has(hostname) || isLanHostname(hostname);
}

export function getApiBaseUrlForHost(hostname: string): string {
  const localHosts = new Set(["localhost", "127.0.0.1", "0.0.0.0"]);
  if (localHosts.has(hostname) || isLanHostname(hostname)) {
    return resolveLocalApiBaseUrl(hostname);
  }

  return DEFAULT_API_BASE_URL;
}

export function getApiBaseUrl(): string {
  if (typeof window !== "undefined" && window.__DEUDAMUNDI_API_BASE_URL__) {
    return window.__DEUDAMUNDI_API_BASE_URL__;
  }

  if (isLocalFrontendHost() && typeof window !== "undefined") {
    return getApiBaseUrlForHost(window.location.hostname);
  }

  return DEFAULT_API_BASE_URL;
}
