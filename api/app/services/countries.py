from __future__ import annotations

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, aliased

from app.models import Country, DebtRecord, Government
from app.schemas.country import (
    CountriesCompareResponse,
    CountriesListResponse,
    CountryCompareItem,
    CountryDetailResponse,
    CountryGovernmentItem,
    CountryGovernmentsResponse,
    CountryHistoryItem,
    CountryHistoryResponse,
    CountryListItem,
    GlobeDataPoint,
    GlobeDataResponse,
)
from app.services.equivalences import build_equivalences


def _base_country_with_latest_debt_query() -> Select[tuple[Country, DebtRecord | None]]:
    latest_year_subquery = (
        select(
            DebtRecord.country_id.label("country_id"),
            func.max(DebtRecord.year).label("latest_year"),
        )
        .group_by(DebtRecord.country_id)
        .subquery()
    )
    latest_debt = aliased(DebtRecord)

    return (
        select(Country, latest_debt)
        .outerjoin(
            latest_year_subquery,
            latest_year_subquery.c.country_id == Country.id,
        )
        .outerjoin(
            latest_debt,
            (latest_debt.country_id == Country.id)
            & (latest_debt.year == latest_year_subquery.c.latest_year),
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
            debt_stock_usd=debt.total_external_debt_usd if debt else None,
            total_external_debt_usd=debt.total_external_debt_usd if debt else None,
            debt_per_capita_usd=debt.debt_per_capita_usd if debt else None,
            debt_pct_gdp=debt.debt_pct_gdp if debt else None,
            debt_concept=debt.debt_concept if debt else None,
            data_source=debt.data_source if debt else None,
            data_vintage=debt.data_vintage.isoformat() if debt and debt.data_vintage else None,
        )
        for country, debt in rows
    ]

    return CountriesListResponse(
        page=page,
        page_size=page_size,
        total=total,
        items=items,
    )


def _build_country_detail(country: Country, debt: DebtRecord | None) -> CountryDetailResponse:
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
        debt_stock_usd=total_external_debt_usd,
        total_external_debt_usd=total_external_debt_usd,
        debt_per_capita_usd=debt.debt_per_capita_usd if debt else None,
        debt_pct_gdp=debt.debt_pct_gdp if debt else None,
        gdp_usd=debt.gdp_usd if debt else None,
        debt_concept=debt.debt_concept if debt else None,
        data_source=debt.data_source if debt else None,
        data_vintage=debt.data_vintage.isoformat() if debt and debt.data_vintage else None,
        equivalences=build_equivalences(total_external_debt_usd),
    )


def get_country_detail(db: Session, iso3: str) -> CountryDetailResponse | None:
    stmt = _base_country_with_latest_debt_query().where(func.upper(Country.iso3) == iso3.upper())
    row = db.execute(stmt).first()

    if not row:
        return None

    country, debt = row
    return _build_country_detail(country, debt)


def get_countries_compare(db: Session, iso3: list[str]) -> CountriesCompareResponse:
    normalized_iso3: list[str] = []
    seen: set[str] = set()
    for raw in iso3:
        current = raw.upper()
        if current in seen:
            continue
        seen.add(current)
        normalized_iso3.append(current)

    if not normalized_iso3:
        return CountriesCompareResponse(
            requested_iso3=[],
            missing_iso3=[],
            item_count=0,
            items=[],
        )

    detail_rows = db.execute(
        _base_country_with_latest_debt_query().where(Country.iso3.in_(normalized_iso3))
    ).all()

    detail_by_iso3 = {
        country.iso3: _build_country_detail(country, debt)
        for country, debt in detail_rows
    }
    country_id_by_iso3 = {
        country.iso3: country.id
        for country, _ in detail_rows
    }

    history_by_country_id: dict[int, list[CountryHistoryItem]] = {
        country_id: [] for country_id in country_id_by_iso3.values()
    }
    if history_by_country_id:
        history_rows = db.execute(
            select(DebtRecord)
            .where(DebtRecord.country_id.in_(history_by_country_id.keys()))
            .order_by(DebtRecord.country_id, DebtRecord.year.desc())
        ).scalars().all()

        for row in history_rows:
            history_by_country_id[row.country_id].append(
                CountryHistoryItem(
                    year=row.year,
                    debt_stock_usd=row.total_external_debt_usd,
                    total_external_debt_usd=row.total_external_debt_usd,
                    debt_per_capita_usd=row.debt_per_capita_usd,
                    debt_pct_gdp=row.debt_pct_gdp,
                    gdp_usd=row.gdp_usd,
                    source=row.source,
                    debt_concept=row.debt_concept,
                    data_source=row.data_source,
                    data_vintage=row.data_vintage.isoformat() if row.data_vintage else None,
                )
            )

    items: list[CountryCompareItem] = []
    missing_iso3: list[str] = []
    for requested_iso3 in normalized_iso3:
        detail = detail_by_iso3.get(requested_iso3)
        country_id = country_id_by_iso3.get(requested_iso3)
        if not detail or not country_id:
            missing_iso3.append(requested_iso3)
            continue

        items.append(
            CountryCompareItem(
                detail=detail,
                history=history_by_country_id.get(country_id, []),
            )
        )

    return CountriesCompareResponse(
        requested_iso3=normalized_iso3,
        missing_iso3=missing_iso3,
        item_count=len(items),
        items=items,
    )


def get_country_history(db: Session, iso3: str) -> CountryHistoryResponse | None:
    country = db.execute(
        select(Country).where(func.upper(Country.iso3) == iso3.upper())
    ).scalar_one_or_none()
    if not country:
        return None

    rows = db.execute(
        select(DebtRecord)
        .where(DebtRecord.country_id == country.id)
        .order_by(DebtRecord.year.desc())
    ).scalars().all()

    return CountryHistoryResponse(
        iso3=country.iso3,
        items=[
            CountryHistoryItem(
                year=row.year,
                debt_stock_usd=row.total_external_debt_usd,
                total_external_debt_usd=row.total_external_debt_usd,
                debt_per_capita_usd=row.debt_per_capita_usd,
                debt_pct_gdp=row.debt_pct_gdp,
                gdp_usd=row.gdp_usd,
                source=row.source,
                debt_concept=row.debt_concept,
                data_source=row.data_source,
                data_vintage=row.data_vintage.isoformat() if row.data_vintage else None,
            )
            for row in rows
        ],
    )


def get_country_governments(db: Session, iso3: str) -> CountryGovernmentsResponse | None:
    country = db.execute(
        select(Country).where(func.upper(Country.iso3) == iso3.upper())
    ).scalar_one_or_none()
    if not country:
        return None

    rows = db.execute(
        select(Government)
        .where(Government.country_id == country.id)
        .order_by(Government.start_date.desc())
    ).scalars().all()

    return CountryGovernmentsResponse(
        iso3=country.iso3,
        items=[
            CountryGovernmentItem(
                leader_name=row.leader_name,
                party=row.party,
                start_date=row.start_date.isoformat(),
                end_date=row.end_date.isoformat() if row.end_date else None,
                political_lean=row.political_lean,
            )
            for row in rows
        ],
    )


def get_globe_data(db: Session, region: str | None) -> GlobeDataResponse:
    stmt = _base_country_with_latest_debt_query().order_by(Country.iso3)
    if region:
        stmt = stmt.where(func.lower(Country.region) == region.lower())

    rows = db.execute(stmt).all()

    items = [
        GlobeDataPoint(
            iso3=country.iso3,
            name_en=country.name_en,
            region=country.region,
            latest_year=debt.year if debt else None,
            debt_stock_usd=debt.total_external_debt_usd if debt else None,
            total_external_debt_usd=debt.total_external_debt_usd if debt else None,
            debt_per_capita_usd=debt.debt_per_capita_usd if debt else None,
            debt_pct_gdp=debt.debt_pct_gdp if debt else None,
            debt_concept=debt.debt_concept if debt else None,
            data_source=debt.data_source if debt else None,
            data_vintage=debt.data_vintage.isoformat() if debt and debt.data_vintage else None,
        )
        for country, debt in rows
    ]

    return GlobeDataResponse(item_count=len(items), items=items)
