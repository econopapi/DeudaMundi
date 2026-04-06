"""initial schema countries and debt records

Revision ID: 20260405_0001
Revises:
Create Date: 2026-04-05 20:30:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260405_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "countries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("iso2", sa.String(length=2), nullable=False),
        sa.Column("iso3", sa.String(length=3), nullable=False),
        sa.Column("name_es", sa.String(length=150), nullable=False),
        sa.Column("name_en", sa.String(length=150), nullable=False),
        sa.Column("region", sa.String(length=100), nullable=True),
        sa.Column("subregion", sa.String(length=100), nullable=True),
        sa.Column("population", sa.Integer(), nullable=True),
        sa.Column("capital", sa.String(length=120), nullable=True),
        sa.Column("flag_url", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_countries_id"), "countries", ["id"], unique=False)
    op.create_index(op.f("ix_countries_iso2"), "countries", ["iso2"], unique=True)
    op.create_index(op.f("ix_countries_iso3"), "countries", ["iso3"], unique=True)

    op.create_table(
        "debt_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("country_id", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("total_external_debt_usd", sa.Float(), nullable=True),
        sa.Column("debt_pct_gdp", sa.Float(), nullable=True),
        sa.Column("debt_per_capita_usd", sa.Float(), nullable=True),
        sa.Column("gdp_usd", sa.Float(), nullable=True),
        sa.Column("source", sa.String(length=30), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["country_id"], ["countries.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("country_id", "year", name="uq_debt_country_year"),
    )
    op.create_index(
        op.f("ix_debt_records_country_id"),
        "debt_records",
        ["country_id"],
        unique=False,
    )
    op.create_index(op.f("ix_debt_records_id"), "debt_records", ["id"], unique=False)
    op.create_index(op.f("ix_debt_records_year"), "debt_records", ["year"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_debt_records_year"), table_name="debt_records")
    op.drop_index(op.f("ix_debt_records_id"), table_name="debt_records")
    op.drop_index(op.f("ix_debt_records_country_id"), table_name="debt_records")
    op.drop_table("debt_records")

    op.drop_index(op.f("ix_countries_iso3"), table_name="countries")
    op.drop_index(op.f("ix_countries_iso2"), table_name="countries")
    op.drop_index(op.f("ix_countries_id"), table_name="countries")
    op.drop_table("countries")
