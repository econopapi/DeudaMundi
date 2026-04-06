from unittest.mock import Mock

from app.etl import repository
from app.etl.types import DebtRecordSeed


def test_upsert_debt_records_chunks_large_payload(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(repository, "DEBT_UPSERT_BATCH_SIZE", 2)

    db = Mock()
    country_map = {"USA": 1}
    debt_rows = [
        DebtRecordSeed(iso3="USA", year=2020, total_external_debt_usd=1.0),
        DebtRecordSeed(iso3="USA", year=2021, total_external_debt_usd=2.0),
        DebtRecordSeed(iso3="USA", year=2022, total_external_debt_usd=3.0),
        DebtRecordSeed(iso3="USA", year=2023, total_external_debt_usd=4.0),
        DebtRecordSeed(iso3="USA", year=2024, total_external_debt_usd=5.0),
    ]

    upserted = repository.upsert_debt_records(db=db, debt_rows=debt_rows, country_map=country_map)

    assert upserted == 5
    assert db.execute.call_count == 3
