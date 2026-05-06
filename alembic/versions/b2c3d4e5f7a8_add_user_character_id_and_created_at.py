"""add user character_id and created_at

Revision ID: b2c3d4e5f7a8
Revises: a5b1fc5db05b
Create Date: 2026-05-06 21:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b2c3d4e5f7a8'
down_revision: Union[str, None] = 'a5b1fc5db05b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 신규 사용자부터 어떤 캐릭터(yeonwoo/doyoon) 설문인지, 작성 시각을 수집한다.
    # 기존 행 호환을 위해 둘 다 nullable.
    op.add_column(
        "users",
        sa.Column(
            "character_id",
            sa.Enum("yeonwoo", "doyoon", name="charactertype"),
            nullable=True,
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "created_at")
    op.drop_column("users", "character_id")
