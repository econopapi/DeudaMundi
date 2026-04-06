from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.etl.types import CountrySeed, DebtRecordSeed
from app.models import Country, DebtRecord


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
            "capital": stmt.excluded.capital,
            "flag_url": stmt.excluded.flag_url,
        },
    )

    db.execute(stmt)
    db.flush()

    rows = db.execute(select(Country.iso3, Country.id)).all()
    return {iso3: country_id for iso3, country_id in rows}


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
            "debt_pct_gdp": None,
            "debt_per_capita_usd": None,
            "gdp_usd": None,
            "source": r.source,
            "updated_at": now,
        }
        for r in filtered
    ]

    stmt = insert(DebtRecord).values(payload)
    stmt = stmt.on_conflict_do_update(
        constraint="uq_debt_country_year",
        set_={
            "total_external_debt_usd": stmt.excluded.total_external_debt_usd,
            "source": stmt.excluded.source,
            "updated_at": stmt.excluded.updated_at,
        },
    )

    db.execute(stmt)
    return len(payload)
