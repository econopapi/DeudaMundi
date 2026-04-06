"""add governments table

Revision ID: 20260405_0003
Revises: 20260405_0002
Create Date: 2026-04-05 23:15:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260405_0003"
down_revision: str | None = "20260405_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "governments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("country_id", sa.Integer(), nullable=False),
        sa.Column("leader_name", sa.String(length=150), nullable=False),
        sa.Column("party", sa.String(length=150), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("political_lean", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(["country_id"], ["countries.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "country_id",
            "leader_name",
            "start_date",
            name="uq_government_country_leader_start",
        ),
    )
    op.create_index(op.f("ix_governments_country_id"), "governments", ["country_id"], unique=False)
    op.create_index(op.f("ix_governments_id"), "governments", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_governments_id"), table_name="governments")
    op.drop_index(op.f("ix_governments_country_id"), table_name="governments")
    op.drop_table("governments")
