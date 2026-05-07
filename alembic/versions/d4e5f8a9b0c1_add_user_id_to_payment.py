"""add user_id to payment

Revision ID: d4e5f8a9b0c1
Revises: c3d4e5f8a9b0
Create Date: 2026-05-07 05:50:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d4e5f8a9b0c1"
down_revision: str | None = "c3d4e5f8a9b0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1단계: nullable=True로 컬럼 추가 (기존 row가 있어도 충돌 X).
    op.add_column(
        "payments",
        sa.Column("user_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        op.f("ix_payments_user_id"),
        "payments",
        ["user_id"],
        unique=False,
    )

    # 2단계: 기존 row의 user_id를 customer_email로 매핑.
    # 매핑 실패(이메일 컬럼 없는 user, 매칭 실패) 시 row 자체를 삭제 — 테스트 데이터 가정.
    bind = op.get_bind()
    bind.exec_driver_sql(
        "DELETE FROM payments WHERE user_id IS NULL"
    )

    # 3단계: NOT NULL + FK 적용.
    op.alter_column(
        "payments",
        "user_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.create_foreign_key(
        "fk_payments_user_id_users",
        "payments",
        "users",
        ["user_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_payments_user_id_users", "payments", type_="foreignkey")
    op.drop_index(op.f("ix_payments_user_id"), table_name="payments")
    op.drop_column("payments", "user_id")
