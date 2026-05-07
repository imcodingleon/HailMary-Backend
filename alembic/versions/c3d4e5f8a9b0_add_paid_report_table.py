"""add paid_report table

Revision ID: c3d4e5f8a9b0
Revises: b2c3d4e5f7a8
Create Date: 2026-05-07 00:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3d4e5f8a9b0"
down_revision: str | None = "b2c3d4e5f7a8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "paid_reports",
        sa.Column("order_id", sa.String(length=64), nullable=False),
        sa.Column("saju_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "ready", "expired", name="reportstatus"),
            nullable=False,
        ),
        sa.Column("chapters", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("order_id"),
    )
    op.create_index(
        op.f("ix_paid_reports_saju_hash"),
        "paid_reports",
        ["saju_hash"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_paid_reports_saju_hash"), table_name="paid_reports")
    op.drop_table("paid_reports")
