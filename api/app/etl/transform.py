from __future__ import annotations

from datetime import date
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
    external_debt_by_country_year: dict[tuple[str, int], float],
    gdp_by_country_year: dict[tuple[str, int], float],
    population_by_country_year: dict[tuple[str, int], float],
) -> list[DebtRecordSeed]:
    rows: list[DebtRecordSeed] = []

    common_keys = (
        set(external_debt_by_country_year)
        & set(gdp_by_country_year)
        & set(population_by_country_year)
    )

    for iso3, year in sorted(common_keys):
        total_external_debt_usd = external_debt_by_country_year.get((iso3, year))
        gdp_usd = gdp_by_country_year.get((iso3, year))
        population = population_by_country_year.get((iso3, year))

        if total_external_debt_usd is None or gdp_usd is None or population is None:
            continue
        if gdp_usd <= 0 or population <= 0 or total_external_debt_usd < 0:
            continue

        debt_pct_gdp = (total_external_debt_usd / gdp_usd) * 100
        debt_per_capita = total_external_debt_usd / population

        rows.append(
            DebtRecordSeed(
                iso3=iso3,
                year=year,
                total_external_debt_usd=total_external_debt_usd,
                gdp_usd=gdp_usd,
                debt_pct_gdp=debt_pct_gdp,
                debt_per_capita_usd=debt_per_capita,
                source="wb_ids_dt_dod_dect_cd",
                debt_concept="external_debt_bop",
                data_source="World Bank IDS DT.DOD.DECT.CD",
                data_vintage=date(year, 12, 31),
                source_priority=10,
            )
        )

    return rows


def normalize_imf_debt_records(
    debt_pct_gdp_by_country_year: dict[tuple[str, int], float],
    gdp_by_country_year: dict[tuple[str, int], float],
    population_by_country_year: dict[tuple[str, int], float],
) -> list[DebtRecordSeed]:
    rows: list[DebtRecordSeed] = []
    latest_population = latest_population_by_iso3(population_by_country_year)

    common_keys = set(debt_pct_gdp_by_country_year) & set(gdp_by_country_year)

    for iso3, year in sorted(common_keys):
        debt_pct_gdp = debt_pct_gdp_by_country_year.get((iso3, year))
        gdp_usd = gdp_by_country_year.get((iso3, year))

        if debt_pct_gdp is None or gdp_usd is None:
            continue
        if debt_pct_gdp < 0 or gdp_usd <= 0:
            continue

        debt_stock_usd = (debt_pct_gdp / 100.0) * gdp_usd
        if debt_stock_usd < 0:
            continue

        population = population_by_country_year.get((iso3, year))
        if population is None:
            population = latest_population.get(iso3)
        debt_per_capita = None
        if population is not None and population > 0:
            debt_per_capita = debt_stock_usd / population

        rows.append(
            DebtRecordSeed(
                iso3=iso3,
                year=year,
                total_external_debt_usd=debt_stock_usd,
                gdp_usd=gdp_usd,
                debt_pct_gdp=debt_pct_gdp,
                debt_per_capita_usd=debt_per_capita,
                source="imf_dm_proxy_ggxwdg",
                debt_concept="public_debt_proxy",
                data_source="IMF DataMapper proxy (GGXWDG_NGDP + NGDPD)",
                data_vintage=date(year, 12, 31),
                source_priority=20,
            )
        )

    return rows


def merge_debt_records_by_priority(rows: list[DebtRecordSeed]) -> list[DebtRecordSeed]:
    best_by_key: dict[tuple[str, int], DebtRecordSeed] = {}

    for row in rows:
        key = (row.iso3, row.year)
        current = best_by_key.get(key)

        if current is None:
            best_by_key[key] = row
            continue

        if row.source_priority < current.source_priority:
            best_by_key[key] = row

    return [best_by_key[key] for key in sorted(best_by_key)]


def keep_imf_proxy_for_uncovered_countries(
    world_bank_rows: list[DebtRecordSeed],
    imf_rows: list[DebtRecordSeed],
) -> tuple[list[DebtRecordSeed], int]:
    wb_countries = {row.iso3 for row in world_bank_rows}
    filtered_imf_rows = [row for row in imf_rows if row.iso3 not in wb_countries]
    dropped_count = len(imf_rows) - len(filtered_imf_rows)
    return filtered_imf_rows, dropped_count
