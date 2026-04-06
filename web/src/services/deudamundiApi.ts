import { getApiBaseUrl } from "../lib/env";
import type { CountryDetailResponse, GlobeDataResponse } from "../types/api";

type ApiError = Error & {
  status?: number;
};

async function request<T>(path: string): Promise<T> {
  const url = `${getApiBaseUrl()}${path}`;
  const response = await fetch(url);

  if (!response.ok) {
    const error: ApiError = new Error(`Request failed with status ${response.status}`);
    error.status = response.status;
    throw error;
  }

  return (await response.json()) as T;
}

export async function fetchGlobeData(region?: string): Promise<GlobeDataResponse> {
  const params = new URLSearchParams();

  if (region) {
    params.set("region", region);
  }

  const query = params.toString();
  const suffix = query ? `?${query}` : "";
  return request<GlobeDataResponse>(`/api/v1/globe-data${suffix}`);
}

export async function fetchCountryDetail(iso3: string): Promise<CountryDetailResponse> {
  return request<CountryDetailResponse>(`/api/v1/countries/${iso3.toUpperCase()}`);
}
