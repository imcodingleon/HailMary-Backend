"""add user session_token

Revision ID: a1b2c3d4e5f6
Revises: 5be401e219be
Create Date: 2026-05-04 00:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = 'a1b2c3d4e5f6'
down_revision: str | None = '5be401e219be'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1) NULL 허용 컬럼으로 일단 추가 (기존 행에 빈 값 잠정 부여 가능)
    op.add_column(
        "users",
        sa.Column("session_token", sa.String(length=64), nullable=True),
    )

    # 2) 기존 행이 있으면 무작위 토큰을 채워준다 (MySQL 8.0의 UUID() 사용)
    op.execute("UPDATE users SET session_token = REPLACE(UUID(), '-', '') WHERE session_token IS NULL")

    # 3) NOT NULL + UNIQUE 인덱스 적용
    op.alter_column("users", "session_token", existing_type=sa.String(length=64), nullable=False)
    op.create_index("ix_users_session_token", "users", ["session_token"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_session_token", table_name="users")
    op.drop_column("users", "session_token")
