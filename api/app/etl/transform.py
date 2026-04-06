from __future__ import annotations

from typing import Any

from app.etl.types import CountrySeed, DebtRecordSeed


def normalize_indicator_rows(raw_rows: list[dict[str, Any]]) -> dict[tuple[str, int], float]:
    normalized: dict[tuple[str, int], float] = {}

    for item in raw_rows:
        iso3 = str(item.get("countryiso3code") or "").strip().upper()
        year_raw = item.get("date")
        value_raw = item.get("value")

        if len(iso3) != 3 or value_raw is None:
            continue

        try:
            year = int(str(year_raw))
            value = float(value_raw)
        except (TypeError, ValueError):
            continue

        normalized[(iso3, year)] = value

    return normalized


def latest_population_by_iso3(
    population_by_country_year: dict[tuple[str, int], float],
) -> dict[str, int]:
    latest: dict[str, tuple[int, int]] = {}

    for (iso3, year), value in population_by_country_year.items():
        population_int = int(value)
        current = latest.get(iso3)

        if current is None or year > current[0]:
            latest[iso3] = (year, population_int)

    return {iso3: population for iso3, (_, population) in latest.items()}


def normalize_countries(raw_countries: list[dict[str, Any]]) -> dict[str, CountrySeed]:
    countries_by_iso3: dict[str, CountrySeed] = {}

    for item in raw_countries:
        iso3 = str(item.get("id") or "").strip().upper()
        iso2 = str(item.get("iso2Code") or "").strip().upper()
        name = str(item.get("name") or "").strip()

        region_obj = item.get("region") if isinstance(item.get("region"), dict) else {}
        region_value = str(region_obj.get("value") or "").strip()
        region = region_value if region_value and region_value.lower() != "aggregates" else None

        if len(iso3) != 3 or len(iso2) != 2 or not name or region is None:
            continue

        admin_region_obj = (
            item.get("adminregion") if isinstance(item.get("adminregion"), dict) else {}
        )
        admin_region_value = str(admin_region_obj.get("value") or "").strip()
        admin_region = admin_region_value or None

        capital_city = str(item.get("capitalCity") or "").strip() or None

        countries_by_iso3[iso3] = CountrySeed(
            iso2=iso2,
            iso3=iso3,
            name_en=name,
            name_es=name,
            region=region,
            subregion=admin_region,
            capital=capital_city,
        )

    return countries_by_iso3


def normalize_debt_records(
    raw_debt_rows: list[dict[str, Any]],
    gdp_by_country_year: dict[tuple[str, int], float],
    population_by_country_year: dict[tuple[str, int], float],
) -> list[DebtRecordSeed]:
    rows: list[DebtRecordSeed] = []

    for item in raw_debt_rows:
        iso3 = str(item.get("countryiso3code") or "").strip().upper()
        year_raw = item.get("date")
        value_raw = item.get("value")

        if len(iso3) != 3:
            continue

        if value_raw is None:
            continue

        try:
            year = int(str(year_raw))
            value = float(value_raw)
        except (TypeError, ValueError):
            continue

        gdp_usd = gdp_by_country_year.get((iso3, year))
        population = population_by_country_year.get((iso3, year))
        debt_pct_gdp = (value / gdp_usd) * 100 if gdp_usd and gdp_usd > 0 else None
        debt_per_capita = value / population if population and population > 0 else None

        rows.append(
            DebtRecordSeed(
                iso3=iso3,
                year=year,
                total_external_debt_usd=value,
                gdp_usd=gdp_usd,
                debt_pct_gdp=debt_pct_gdp,
                debt_per_capita_usd=debt_per_capita,
            )
        )

    return rows
