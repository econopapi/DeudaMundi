"""add query performance indexes

Revision ID: 20260405_0004
Revises: 20260405_0003
Create Date: 2026-04-05 23:55:00

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260405_0004"
down_revision: str | None = "20260405_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "ix_debt_records_total_external_debt_usd",
        "debt_records",
        ["total_external_debt_usd"],
        unique=False,
    )
    op.create_index(
        "ix_debt_records_debt_pct_gdp",
        "debt_records",
        ["debt_pct_gdp"],
        unique=False,
    )
    op.create_index(
        "ix_debt_records_debt_per_capita_usd",
        "debt_records",
        ["debt_per_capita_usd"],
        unique=False,
    )
    op.create_index("ix_countries_region", "countries", ["region"], unique=False)
    op.create_index(
        "ix_governments_country_id_start_date",
        "governments",
        ["country_id", "start_date"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_governments_country_id_start_date", table_name="governments")
    op.drop_index("ix_countries_region", table_name="countries")
    op.drop_index("ix_debt_records_debt_per_capita_usd", table_name="debt_records")
    op.drop_index("ix_debt_records_debt_pct_gdp", table_name="debt_records")
    op.drop_index("ix_debt_records_total_external_debt_usd", table_name="debt_records")
