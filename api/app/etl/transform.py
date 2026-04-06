from __future__ import annotations

from typing import Any

from app.etl.types import CountrySeed, DebtRecordSeed


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


def normalize_debt_records(raw_debt_rows: list[dict[str, Any]]) -> list[DebtRecordSeed]:
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

        rows.append(
            DebtRecordSeed(
                iso3=iso3,
                year=year,
                total_external_debt_usd=value,
            )
        )

    return rows
