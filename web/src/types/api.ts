export type GlobeDataPoint = {
  iso3: string;
  name_en: string;
  region: string | null;
  latest_year: number | null;
  total_external_debt_usd: number | null;
  debt_per_capita_usd: number | null;
  debt_pct_gdp: number | null;
};

export type GlobeDataResponse = {
  item_count: number;
  items: GlobeDataPoint[];
};

export type EquivalenceItem = {
  label: string;
  value: number;
  description: string;
};

export type CountryDetailResponse = {
  iso3: string;
  iso2: string;
  name_es: string;
  name_en: string;
  region: string | null;
  subregion: string | null;
  population: number | null;
  capital: string | null;
  latest_year: number | null;
  total_external_debt_usd: number | null;
  debt_per_capita_usd: number | null;
  debt_pct_gdp: number | null;
  gdp_usd: number | null;
  equivalences: EquivalenceItem[];
};

export type CountryHistoryItem = {
  year: number;
  total_external_debt_usd: number | null;
  debt_per_capita_usd: number | null;
  debt_pct_gdp: number | null;
  gdp_usd: number | null;
  source: string;
};

export type CountryHistoryResponse = {
  iso3: string;
  items: CountryHistoryItem[];
};

export type CountryGovernmentItem = {
  leader_name: string;
  party: string | null;
  start_date: string;
  end_date: string | null;
  political_lean: string | null;
};

export type CountryGovernmentsResponse = {
  iso3: string;
  items: CountryGovernmentItem[];
};

export type RankingMetric = "absolute" | "pct_gdp" | "per_capita";

export type RankingItem = {
  rank: number;
  iso3: string;
  name_en: string;
  region: string | null;
  value: number | null;
  latest_year: number | null;
};

export type RankingsResponse = {
  metric: RankingMetric;
  region: string | null;
  limit: number;
  items: RankingItem[];
};
