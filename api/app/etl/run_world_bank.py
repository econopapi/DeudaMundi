from __future__ import annotations

from app.db.session import SessionLocal
from app.etl.repository import upsert_countries, upsert_debt_records
from app.etl.transform import normalize_countries, normalize_debt_records
from app.etl.world_bank_client import WorldBankClient


def run_world_bank_etl() -> dict[str, int]:
    client = WorldBankClient()
    raw_countries = client.fetch_countries()
    raw_debt = client.fetch_external_debt()

    countries_by_iso3 = normalize_countries(raw_countries)
    debt_rows = normalize_debt_records(raw_debt)

    with SessionLocal.begin() as db:
        country_map = upsert_countries(db, list(countries_by_iso3.values()))
        upserted_records = upsert_debt_records(db, debt_rows, country_map)

    return {
        "countries_processed": len(countries_by_iso3),
        "debt_records_processed": len(debt_rows),
        "debt_records_upserted": upserted_records,
    }


def main() -> None:
    result = run_world_bank_etl()
    print(
        "World Bank ETL completed:",
        result,
    )


if __name__ == "__main__":
    main()
