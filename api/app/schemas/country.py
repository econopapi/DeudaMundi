from pydantic import BaseModel, Field


class CountryListItem(BaseModel):
    iso3: str
    iso2: str
    name_es: str
    name_en: str
    region: str | None
    latest_year: int | None
    total_external_debt_usd: float | None
    debt_per_capita_usd: float | None
    debt_pct_gdp: float | None


class CountriesListResponse(BaseModel):
    page: int
    page_size: int
    total: int
    items: list[CountryListItem]


class EquivalenceItem(BaseModel):
    label: str
    value: float = Field(..., ge=0)
    description: str


class CountryDetailResponse(BaseModel):
    iso3: str
    iso2: str
    name_es: str
    name_en: str
    region: str | None
    subregion: str | None
    population: int | None
    capital: str | None
    latest_year: int | None
    total_external_debt_usd: float | None
    debt_per_capita_usd: float | None
    debt_pct_gdp: float | None
    gdp_usd: float | None
    equivalences: list[EquivalenceItem]


class CountryHistoryItem(BaseModel):
    year: int
    total_external_debt_usd: float | None
    debt_per_capita_usd: float | None
    debt_pct_gdp: float | None
    gdp_usd: float | None
    source: str


class CountryHistoryResponse(BaseModel):
    iso3: str
    items: list[CountryHistoryItem]


class CountryGovernmentItem(BaseModel):
    leader_name: str
    party: str | None
    start_date: str
    end_date: str | None
    political_lean: str | None


class CountryGovernmentsResponse(BaseModel):
    iso3: str
    items: list[CountryGovernmentItem]


class GlobeDataPoint(BaseModel):
    iso3: str
    name_en: str
    region: str | None
    latest_year: int | None
    total_external_debt_usd: float | None
    debt_per_capita_usd: float | None
    debt_pct_gdp: float | None


class GlobeDataResponse(BaseModel):
    item_count: int
    items: list[GlobeDataPoint]
