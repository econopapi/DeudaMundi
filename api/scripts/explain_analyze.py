from __future__ import annotations

from app.db.session import SessionLocal
from sqlalchemy import text

QUERIES: dict[str, str] = {
    "countries_list": """
EXPLAIN ANALYZE
SELECT
  c.iso3,
  c.name_en,
  c.region,
  dr.total_external_debt_usd,
  dr.debt_pct_gdp,
  dr.debt_per_capita_usd
FROM countries c
LEFT JOIN debt_records dr
  ON dr.country_id = c.id
  AND dr.year = (
    SELECT MAX(dr2.year)
    FROM debt_records dr2
    WHERE dr2.country_id = c.id
  )
ORDER BY c.name_en
LIMIT 50;
""",
    "rankings_absolute": """
EXPLAIN ANALYZE
SELECT c.iso3, c.name_en, dr.total_external_debt_usd, dr.year
FROM countries c
JOIN debt_records dr
  ON dr.country_id = c.id
  AND dr.year = (
    SELECT MAX(dr2.year)
    FROM debt_records dr2
    WHERE dr2.country_id = c.id
  )
WHERE dr.total_external_debt_usd IS NOT NULL
ORDER BY dr.total_external_debt_usd DESC
LIMIT 20;
""",
    "country_history": """
EXPLAIN ANALYZE
SELECT year, total_external_debt_usd, debt_pct_gdp, debt_per_capita_usd
FROM debt_records
WHERE country_id = (
    SELECT id FROM countries WHERE iso3 = 'ARG' LIMIT 1
)
ORDER BY year DESC;
""",
}


def main() -> None:
    db = SessionLocal()
    try:
        for query_name, query_sql in QUERIES.items():
            print(f"\n--- {query_name} ---")
            rows = db.execute(text(query_sql)).all()
            for row in rows:
                print(row[0])
    finally:
        db.close()


if __name__ == "__main__":
    main()
