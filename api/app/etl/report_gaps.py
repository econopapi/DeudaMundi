from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import func, select

from app.db.session import SessionLocal
from app.models import Country, DebtRecord


def build_gap_report() -> dict[str, object]:
    with SessionLocal() as db:
        total_countries = db.scalar(select(func.count()).select_from(Country)) or 0

        countries_with_debt = db.scalar(
            select(func.count(func.distinct(DebtRecord.country_id))).select_from(DebtRecord)
        ) or 0

        countries_without_debt_rows = db.execute(
            select(Country.iso3)
            .outerjoin(DebtRecord, DebtRecord.country_id == Country.id)
            .where(DebtRecord.id.is_(None))
            .order_by(Country.iso3)
        ).all()
        countries_without_debt = [row[0] for row in countries_without_debt_rows]

        year_bounds = db.execute(
            select(func.min(DebtRecord.year), func.max(DebtRecord.year)).select_from(DebtRecord)
        ).one()

        top_country_rows = db.execute(
            select(Country.iso3, func.count(DebtRecord.id).label("records"))
            .join(DebtRecord, DebtRecord.country_id == Country.id)
            .group_by(Country.iso3)
            .order_by(func.count(DebtRecord.id).desc(), Country.iso3)
            .limit(10)
        ).all()

    return {
        "generated_at": datetime.now(tz=UTC).isoformat(),
        "summary": {
            "total_countries": int(total_countries),
            "countries_with_debt_data": int(countries_with_debt),
            "countries_without_debt_data": len(countries_without_debt),
            "min_year": year_bounds[0],
            "max_year": year_bounds[1],
        },
        "countries_without_debt_data": countries_without_debt,
        "top_coverage_countries": [
            {"iso3": iso3, "records": int(records)} for iso3, records in top_country_rows
        ],
    }


def write_gap_report(output_path: str | None = None) -> dict[str, object]:
    report = build_gap_report()

    if output_path:
        target = Path(output_path)
    else:
        timestamp = datetime.now(tz=UTC).strftime("%Y%m%d_%H%M%S")
        target = Path("reports") / f"etl_gap_report_{timestamp}.json"

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    report = write_gap_report()
    print("Gap report generated:", report["summary"])


if __name__ == "__main__":
    main()
