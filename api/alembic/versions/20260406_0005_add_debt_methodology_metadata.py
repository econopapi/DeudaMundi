"""add debt methodology metadata columns

Revision ID: 20260406_0005
Revises: 20260405_0004
Create Date: 2026-04-06 00:20:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260406_0005"
down_revision: str | None = "20260405_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


DEFAULT_SOURCE = "wb_ids_dt_dod_dect_cd"
DEFAULT_CONCEPT = "external_debt_bop"
DEFAULT_DATA_SOURCE = "World Bank IDS DT.DOD.DECT.CD"


def upgrade() -> None:
    op.add_column(
        "debt_records",
        sa.Column(
            "debt_concept",
            sa.String(length=50),
            nullable=False,
            server_default=DEFAULT_CONCEPT,
        ),
    )
    op.add_column(
        "debt_records",
        sa.Column(
            "data_source",
            sa.String(length=120),
            nullable=False,
            server_default=DEFAULT_DATA_SOURCE,
        ),
    )
    op.add_column("debt_records", sa.Column("data_vintage", sa.Date(), nullable=True))

    op.execute(
        sa.text(
            """
            UPDATE debt_records
            SET
                source = :source,
                debt_concept = :concept,
                data_source = :data_source,
                data_vintage = make_date(year, 12, 31)
            """
        ).bindparams(
            source=DEFAULT_SOURCE,
            concept=DEFAULT_CONCEPT,
            data_source=DEFAULT_DATA_SOURCE,
        )
    )

    op.alter_column("debt_records", "source", existing_type=sa.String(length=30), nullable=False)
    op.alter_column("debt_records", "source", server_default=DEFAULT_SOURCE)
    op.alter_column("debt_records", "debt_concept", server_default=None)
    op.alter_column("debt_records", "data_source", server_default=None)


def downgrade() -> None:
    op.alter_column("debt_records", "source", server_default="worldbank")
    op.drop_column("debt_records", "data_vintage")
    op.drop_column("debt_records", "data_source")
    op.drop_column("debt_records", "debt_concept")
