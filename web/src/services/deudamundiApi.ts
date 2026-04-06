import { getApiBaseUrl } from "../lib/env";
import type {
  CountryDetailResponse,
  CountryGovernmentsResponse,
  CountryHistoryResponse,
  GlobeDataResponse,
  RankingMetric,
  RankingsResponse,
} from "../types/api";

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

export async function fetchCountryHistory(iso3: string): Promise<CountryHistoryResponse> {
  return request<CountryHistoryResponse>(`/api/v1/countries/${iso3.toUpperCase()}/history`);
}

export async function fetchCountryGovernments(iso3: string): Promise<CountryGovernmentsResponse> {
  return request<CountryGovernmentsResponse>(`/api/v1/countries/${iso3.toUpperCase()}/governments`);
}

export async function fetchRankings(metric: RankingMetric, region?: string, limit = 20): Promise<RankingsResponse> {
  const params = new URLSearchParams();
  params.set("metric", metric);
  params.set("limit", String(limit));

  if (region) {
    params.set("region", region);
  }

  return request<RankingsResponse>(`/api/v1/rankings?${params.toString()}`);
}
