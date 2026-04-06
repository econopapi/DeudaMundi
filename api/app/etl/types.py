from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class CountrySeed:
    iso2: str
    iso3: str
    name_en: str
    name_es: str
    region: str | None
    subregion: str | None
    capital: str | None
    population: int | None = None
    flag_url: str | None = None


@dataclass(slots=True)
class DebtRecordSeed:
    iso3: str
    year: int
    total_external_debt_usd: float
    gdp_usd: float | None = None
    debt_pct_gdp: float | None = None
    debt_per_capita_usd: float | None = None
    source: str = "wb_ids_dt_dod_dect_cd"
    debt_concept: str = "external_debt_bop"
    data_source: str = "World Bank IDS DT.DOD.DECT.CD"
    data_vintage: date | None = None
