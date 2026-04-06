from __future__ import annotations

from datetime import UTC, datetime
from time import perf_counter

from app.db.session import SessionLocal
from app.etl.repository import upsert_countries, upsert_debt_records
from app.etl.transform import normalize_countries, normalize_debt_records
from app.etl.world_bank_client import WorldBankClient
from app.models import EtlRun

PIPELINE_NAME = "world_bank_external_debt"


def run_world_bank_etl() -> dict[str, int]:
    started_at = datetime.now(tz=UTC)
    perf_start = perf_counter()

    client = WorldBankClient()
    raw_countries = client.fetch_countries()
    raw_debt = client.fetch_external_debt()

    countries_by_iso3 = normalize_countries(raw_countries)
    debt_rows = normalize_debt_records(raw_debt)

    result = {
        "countries_processed": len(countries_by_iso3),
        "debt_records_processed": len(debt_rows),
        "debt_records_upserted": 0,
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

            result["debt_records_upserted"] = upserted_records

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
