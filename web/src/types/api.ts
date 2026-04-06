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
