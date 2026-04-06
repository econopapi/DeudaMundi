from __future__ import annotations

from datetime import UTC, datetime
from time import perf_counter

from app.core.cache import invalidate_read_caches
from app.db.session import SessionLocal
from app.etl.repository import upsert_countries, upsert_debt_records
from app.etl.transform import (
    latest_population_by_iso3,
    normalize_countries,
    normalize_debt_records,
    normalize_indicator_rows,
)
from app.etl.world_bank_client import WorldBankClient
from app.models import EtlRun

PIPELINE_NAME = "world_bank_external_debt"


def run_world_bank_etl() -> dict[str, int]:
    started_at = datetime.now(tz=UTC)
    perf_start = perf_counter()

    client = WorldBankClient()
    raw_countries = client.fetch_countries()
    raw_debt_pct_gdp = client.fetch_debt_pct_gdp()
    raw_gdp = client.fetch_gdp()
    raw_population = client.fetch_population()

    countries_by_iso3 = normalize_countries(raw_countries)
    debt_pct_gdp_by_country_year = normalize_indicator_rows(raw_debt_pct_gdp)
    gdp_by_country_year = normalize_indicator_rows(raw_gdp)
    population_by_country_year = normalize_indicator_rows(raw_population)

    latest_population = latest_population_by_iso3(population_by_country_year)
    for iso3, population in latest_population.items():
        country = countries_by_iso3.get(iso3)
        if country:
            country.population = population

    debt_rows = normalize_debt_records(
        debt_pct_gdp_by_country_year=debt_pct_gdp_by_country_year,
        gdp_by_country_year=gdp_by_country_year,
        population_by_country_year=population_by_country_year,
    )

    result = {
        "countries_processed": len(countries_by_iso3),
        "debt_records_processed": len(debt_rows),
    "debt_pct_gdp_records_processed": len(debt_pct_gdp_by_country_year),
        "gdp_records_processed": len(gdp_by_country_year),
        "population_records_processed": len(population_by_country_year),
        "countries_with_population": len(latest_population),
        "debt_records_upserted": 0,
        "cache_keys_invalidated": 0,
    }

    with SessionLocal() as db:
        run = EtlRun(
            pipeline_name=PIPELINE_NAME,
            status="running",
            started_at=started_at,
            countries_processed=0,
            debt_records_processed=0,
            debt_records_upserted=0,
        )
        db.add(run)
        db.flush()

        try:
            country_map = upsert_countries(db, list(countries_by_iso3.values()))
            upserted_records = upsert_debt_records(db, debt_rows, country_map)
            invalidated_cache_keys = invalidate_read_caches()

            result["debt_records_upserted"] = upserted_records
            result["cache_keys_invalidated"] = invalidated_cache_keys

            run.status = "success"
            run.countries_processed = result["countries_processed"]
            run.debt_records_processed = result["debt_records_processed"]
            run.debt_records_upserted = result["debt_records_upserted"]
            run.finished_at = datetime.now(tz=UTC)
            run.duration_ms = int((perf_counter() - perf_start) * 1000)

            db.commit()
            return result

        except Exception as exc:
            run.status = "failed"
            run.finished_at = datetime.now(tz=UTC)
            run.duration_ms = int((perf_counter() - perf_start) * 1000)
            run.error_message = str(exc)[:4000]

            db.commit()
            raise


def main() -> None:
    result = run_world_bank_etl()
    print(
        "World Bank ETL completed:",
        result,
    )


if __name__ == "__main__":
    main()
