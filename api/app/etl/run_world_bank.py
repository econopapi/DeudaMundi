from __future__ import annotations

from datetime import UTC, datetime
from time import perf_counter

from app.core.cache import invalidate_read_caches
from app.core.config import settings
from app.db.session import SessionLocal
from app.etl.imf_client import ImfDataMapperClient
from app.etl.repository import delete_imf_proxy_rows, upsert_countries, upsert_debt_records
from app.etl.seed_governments import seed_governments
from app.etl.transform import (
    keep_imf_proxy_for_uncovered_countries,
    latest_population_by_iso3,
    merge_debt_records_by_priority,
    normalize_countries,
    normalize_debt_records,
    normalize_imf_debt_records,
    normalize_indicator_rows,
)
from app.etl.world_bank_client import WorldBankClient
from app.models import EtlRun

PIPELINE_NAME = "global_debt_multisource"


def run_world_bank_etl() -> dict[str, int | str]:
    started_at = datetime.now(tz=UTC)
    perf_start = perf_counter()

    client = WorldBankClient()
    raw_countries = client.fetch_countries()
    raw_external_debt = client.fetch_external_debt()
    raw_gdp = client.fetch_gdp()
    raw_population = client.fetch_population()

    imf_debt_pct_gdp: dict[tuple[str, int], float] = {}
    imf_nominal_gdp_usd_billions: dict[tuple[str, int], float] = {}
    if settings.etl_allow_proxy_debt_fallback:
        imf_client = ImfDataMapperClient()
        imf_debt_pct_gdp = imf_client.fetch_general_government_debt_to_gdp()
        imf_nominal_gdp_usd_billions = imf_client.fetch_nominal_gdp_usd_billions()

    countries_by_iso3 = normalize_countries(raw_countries)
    external_debt_by_country_year = normalize_indicator_rows(raw_external_debt)
    gdp_by_country_year = normalize_indicator_rows(raw_gdp)
    population_by_country_year = normalize_indicator_rows(raw_population)
    imf_nominal_gdp_usd = {
        key: value * 1_000_000_000 for key, value in imf_nominal_gdp_usd_billions.items()
    }

    latest_population = latest_population_by_iso3(population_by_country_year)
    countries_with_population = 0
    for iso3, population in latest_population.items():
        country = countries_by_iso3.get(iso3)
        if country:
            country.population = population
            countries_with_population += 1

    world_bank_debt_rows = normalize_debt_records(
        external_debt_by_country_year=external_debt_by_country_year,
        gdp_by_country_year=gdp_by_country_year,
        population_by_country_year=population_by_country_year,
    )
    imf_debt_rows = []
    imf_debt_rows_dropped_due_to_wb_coverage = 0
    if settings.etl_allow_proxy_debt_fallback:
        raw_imf_debt_rows = normalize_imf_debt_records(
            debt_pct_gdp_by_country_year=imf_debt_pct_gdp,
            gdp_by_country_year={**imf_nominal_gdp_usd, **gdp_by_country_year},
            population_by_country_year=population_by_country_year,
        )
        imf_debt_rows, imf_debt_rows_dropped_due_to_wb_coverage = (
            keep_imf_proxy_for_uncovered_countries(
                world_bank_rows=world_bank_debt_rows,
                imf_rows=raw_imf_debt_rows,
            )
        )
    debt_rows = merge_debt_records_by_priority(world_bank_debt_rows + imf_debt_rows)

    merged_world_bank_rows = sum(1 for row in debt_rows if row.source == "wb_ids_dt_dod_dect_cd")
    merged_imf_proxy_rows = sum(1 for row in debt_rows if row.source == "imf_dm_proxy_ggxwdg")

    result = {
        "countries_processed": len(countries_by_iso3),
        "debt_records_processed": len(debt_rows),
        "world_bank_external_debt_records_processed": len(external_debt_by_country_year),
        "world_bank_gdp_records_processed": len(gdp_by_country_year),
        "world_bank_population_records_processed": len(population_by_country_year),
        "proxy_debt_fallback_enabled": int(settings.etl_allow_proxy_debt_fallback),
        "imf_debt_pct_gdp_records_processed": len(imf_debt_pct_gdp),
        "imf_nominal_gdp_records_processed": len(imf_nominal_gdp_usd),
        "world_bank_debt_rows_normalized": len(world_bank_debt_rows),
        "imf_debt_rows_normalized": len(imf_debt_rows),
        "imf_debt_rows_dropped_due_to_wb_coverage": imf_debt_rows_dropped_due_to_wb_coverage,
        "merged_world_bank_rows": merged_world_bank_rows,
        "merged_imf_proxy_rows": merged_imf_proxy_rows,
        "countries_with_population": countries_with_population,
        "imf_proxy_rows_removed_current_or_future": 0,
        "imf_proxy_rows_removed_wb_covered_countries": 0,
        "imf_proxy_rows_removed_when_fallback_disabled": 0,
        "debt_records_upserted": 0,
        "cache_keys_invalidated": 0,
        "governments_seeded": 0,
        "governments_seed_source": "disabled",
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

            if settings.etl_allow_proxy_debt_fallback:
                wb_country_ids = [
                    country_map[iso3]
                    for iso3 in {row.iso3 for row in world_bank_debt_rows}
                    if iso3 in country_map
                ]
                result["imf_proxy_rows_removed_current_or_future"] = delete_imf_proxy_rows(
                    db,
                    min_year_inclusive=started_at.year,
                )
                result["imf_proxy_rows_removed_wb_covered_countries"] = delete_imf_proxy_rows(
                    db,
                    country_ids=wb_country_ids,
                )
            else:
                result["imf_proxy_rows_removed_when_fallback_disabled"] = delete_imf_proxy_rows(db)

            upserted_records = upsert_debt_records(db, debt_rows, country_map)
            governments_seed_result: dict[str, int | str] = {}
            if settings.etl_seed_governments_enabled:
                governments_seed_result = seed_governments(db=db)
                result["governments_seeded"] = int(governments_seed_result.get("rows_prepared", 0))
                result["governments_seed_source"] = str(
                    governments_seed_result.get("seed_source", "unknown")
                )
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
