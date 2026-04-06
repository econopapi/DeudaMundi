"""add etl_runs table

Revision ID: 20260405_0002
Revises: 20260405_0001
Create Date: 2026-04-05 22:40:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260405_0002"
down_revision: str | None = "20260405_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "etl_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pipeline_name", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("countries_processed", sa.Integer(), nullable=False),
        sa.Column("debt_records_processed", sa.Integer(), nullable=False),
        sa.Column("debt_records_upserted", sa.Integer(), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_etl_runs_id"), "etl_runs", ["id"], unique=False)
    op.create_index(op.f("ix_etl_runs_pipeline_name"), "etl_runs", ["pipeline_name"], unique=False)
    op.create_index(op.f("ix_etl_runs_status"), "etl_runs", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_etl_runs_status"), table_name="etl_runs")
    op.drop_index(op.f("ix_etl_runs_pipeline_name"), table_name="etl_runs")
    op.drop_index(op.f("ix_etl_runs_id"), table_name="etl_runs")
    op.drop_table("etl_runs")
