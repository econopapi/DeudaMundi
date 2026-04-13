from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.etl.types import CountrySeed, DebtRecordSeed
from app.models import Country, DebtRecord


PG_MAX_BIND_PARAMS = 65_535
DEBT_RECORD_INSERT_COLUMNS = 11
DEBT_UPSERT_BATCH_SIZE = max(1, PG_MAX_BIND_PARAMS // DEBT_RECORD_INSERT_COLUMNS)
IMF_PROXY_SOURCE = "imf_dm_proxy_ggxwdg"
QEDS_SOURCE = "wb_qeds_dt_dod_dect_cd_ar_us"


def upsert_countries(db: Session, countries: list[CountrySeed]) -> dict[str, int]:
    if not countries:
        return {}

    payload = [
        {
            "iso2": c.iso2,
            "iso3": c.iso3,
            "name_es": c.name_es,
            "name_en": c.name_en,
            "region": c.region,
            "subregion": c.subregion,
            "population": c.population,
            "capital": c.capital,
            "flag_url": c.flag_url,
        }
        for c in countries
    ]

    stmt = insert(Country).values(payload)
    stmt = stmt.on_conflict_do_update(
        index_elements=["iso3"],
        set_={
            "iso2": stmt.excluded.iso2,
            "name_es": stmt.excluded.name_es,
            "name_en": stmt.excluded.name_en,
            "region": stmt.excluded.region,
            "subregion": stmt.excluded.subregion,
            "population": stmt.excluded.population,
            "capital": stmt.excluded.capital,
            "flag_url": stmt.excluded.flag_url,
        },
    )

    db.execute(stmt)
    db.flush()

    rows = db.execute(select(Country.iso3, Country.id)).all()
    return {iso3: country_id for iso3, country_id in rows}


def delete_imf_proxy_rows(
    db: Session,
    *,
    country_ids: list[int] | None = None,
    min_year_inclusive: int | None = None,
) -> int:
    conditions = [DebtRecord.source == IMF_PROXY_SOURCE]

    if country_ids:
        conditions.append(DebtRecord.country_id.in_(country_ids))
    if min_year_inclusive is not None:
        conditions.append(DebtRecord.year >= min_year_inclusive)

    stmt = delete(DebtRecord).where(*conditions)
    result = db.execute(stmt)
    return int(result.rowcount or 0)


def delete_qeds_rows(db: Session) -> int:
    """Remove all QEDS-sourced debt rows (used when QEDS is disabled)."""
    stmt = delete(DebtRecord).where(DebtRecord.source == QEDS_SOURCE)
    result = db.execute(stmt)
    return int(result.rowcount or 0)


def upsert_debt_records(
    db: Session,
    debt_rows: list[DebtRecordSeed],
    country_map: dict[str, int],
) -> int:
    filtered = [r for r in debt_rows if r.iso3 in country_map]
    if not filtered:
        return 0

    now = datetime.now(tz=UTC)
    payload = [
        {
            "country_id": country_map[r.iso3],
            "year": r.year,
            "total_external_debt_usd": r.total_external_debt_usd,
            "debt_pct_gdp": r.debt_pct_gdp,
            "debt_per_capita_usd": r.debt_per_capita_usd,
            "gdp_usd": r.gdp_usd,
            "source": r.source,
            "debt_concept": r.debt_concept,
            "data_source": r.data_source,
            "data_vintage": r.data_vintage,
            "updated_at": now,
        }
        for r in filtered
    ]

    for start in range(0, len(payload), DEBT_UPSERT_BATCH_SIZE):
        batch = payload[start : start + DEBT_UPSERT_BATCH_SIZE]
        stmt = insert(DebtRecord).values(batch)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_debt_country_year",
            set_={
                "total_external_debt_usd": stmt.excluded.total_external_debt_usd,
                "debt_pct_gdp": stmt.excluded.debt_pct_gdp,
                "debt_per_capita_usd": stmt.excluded.debt_per_capita_usd,
                "gdp_usd": stmt.excluded.gdp_usd,
                "source": stmt.excluded.source,
                "debt_concept": stmt.excluded.debt_concept,
                "data_source": stmt.excluded.data_source,
                "data_vintage": stmt.excluded.data_vintage,
                "updated_at": stmt.excluded.updated_at,
            },
        )

        db.execute(stmt)
    return len(payload)
