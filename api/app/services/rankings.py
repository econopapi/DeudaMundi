from __future__ import annotations

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.models import Country, DebtRecord
from app.schemas.ranking import RankingItem, RankingsResponse

METRIC_TO_COLUMN = {
    "absolute": DebtRecord.total_external_debt_usd,
    "pct_gdp": DebtRecord.debt_pct_gdp,
    "per_capita": DebtRecord.debt_per_capita_usd,
}


def get_rankings(
    db: Session,
    metric: str,
    region: str | None,
    limit: int,
) -> RankingsResponse:
    if metric not in METRIC_TO_COLUMN:
        msg = f"Invalid metric '{metric}'"
        raise ValueError(msg)

    metric_column = METRIC_TO_COLUMN[metric]

    latest_year_subquery = (
        select(
            DebtRecord.country_id.label("country_id"),
            func.max(DebtRecord.year).label("latest_year"),
        )
        .group_by(DebtRecord.country_id)
        .subquery()
    )

    stmt = (
        select(Country, DebtRecord)
        .join(latest_year_subquery, latest_year_subquery.c.country_id == Country.id)
        .join(
            DebtRecord,
            (DebtRecord.country_id == Country.id)
            & (DebtRecord.year == latest_year_subquery.c.latest_year),
        )
        .where(metric_column.is_not(None))
        .order_by(desc(metric_column))
        .limit(limit)
    )

    if region:
        stmt = stmt.where(func.lower(Country.region) == region.lower())

    rows = db.execute(stmt).all()

    items: list[RankingItem] = []
    for idx, (country, debt) in enumerate(rows, start=1):
        value = getattr(debt, metric_column.key)
        if value is None:
            continue

        items.append(
            RankingItem(
                rank=idx,
                iso3=country.iso3,
                name_en=country.name_en,
                region=country.region,
                value=float(value),
                latest_year=debt.year,
            )
        )

    return RankingsResponse(
        metric=metric,
        region=region,
        limit=limit,
        items=items,
    )
