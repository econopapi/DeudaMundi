from __future__ import annotations

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models import Country, DebtRecord
from app.schemas.country import CountriesListResponse, CountryDetailResponse, CountryListItem
from app.services.equivalences import build_equivalences


def _base_country_with_latest_debt_query() -> Select[tuple[Country, DebtRecord | None]]:
    latest_year_subquery = (
        select(func.max(DebtRecord.year))
        .where(DebtRecord.country_id == Country.id)
        .correlate(Country)
        .scalar_subquery()
    )

    return (
        select(Country, DebtRecord)
        .outerjoin(
            DebtRecord,
            (DebtRecord.country_id == Country.id) & (DebtRecord.year == latest_year_subquery),
        )
        .order_by(Country.name_en)
    )


def list_countries(
    db: Session,
    page: int,
    page_size: int,
    region: str | None,
) -> CountriesListResponse:
    total_stmt = select(func.count()).select_from(Country)

    base_stmt = _base_country_with_latest_debt_query()

    if region:
        total_stmt = total_stmt.where(func.lower(Country.region) == region.lower())
        base_stmt = base_stmt.where(func.lower(Country.region) == region.lower())

    total = int(db.scalar(total_stmt) or 0)

    offset = (page - 1) * page_size
    rows = db.execute(base_stmt.offset(offset).limit(page_size)).all()

    items = [
        CountryListItem(
            iso3=country.iso3,
            iso2=country.iso2,
            name_es=country.name_es,
            name_en=country.name_en,
            region=country.region,
            latest_year=debt.year if debt else None,
            total_external_debt_usd=debt.total_external_debt_usd if debt else None,
            debt_per_capita_usd=debt.debt_per_capita_usd if debt else None,
            debt_pct_gdp=debt.debt_pct_gdp if debt else None,
        )
        for country, debt in rows
    ]

    return CountriesListResponse(
        page=page,
        page_size=page_size,
        total=total,
        items=items,
    )


def get_country_detail(db: Session, iso3: str) -> CountryDetailResponse | None:
    stmt = _base_country_with_latest_debt_query().where(func.upper(Country.iso3) == iso3.upper())
    row = db.execute(stmt).first()

    if not row:
        return None

    country, debt = row
    total_external_debt_usd = debt.total_external_debt_usd if debt else None

    return CountryDetailResponse(
        iso3=country.iso3,
        iso2=country.iso2,
        name_es=country.name_es,
        name_en=country.name_en,
        region=country.region,
        subregion=country.subregion,
        population=country.population,
        capital=country.capital,
        latest_year=debt.year if debt else None,
        total_external_debt_usd=total_external_debt_usd,
        debt_per_capita_usd=debt.debt_per_capita_usd if debt else None,
        debt_pct_gdp=debt.debt_pct_gdp if debt else None,
        gdp_usd=debt.gdp_usd if debt else None,
        equivalences=build_equivalences(total_external_debt_usd),
    )
