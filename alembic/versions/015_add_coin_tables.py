"""코인 도메인 (도화선 2.0 Phase 2) — coin_wallets / coin_lots / coin_transactions

coin_wallets: 계정당 1건, 잔액 스냅샷.
coin_lots: FIFO 소비 대상 코인 배치. UNIQUE(source_reason, ref)로 GRANT 멱등 보장.
coin_transactions: 원장. UNIQUE(type, ref)로 CHARGE/SPEND 등 멱등 보장
(MySQL은 NULL을 서로 다른 값으로 취급하므로 ref가 NULL인 행끼리는 중복 허용됨 — GRANT 초기 등은 ref 규칙 준수 전제).

Revision ID: 015_add_coin_tables
Revises: 014_add_chat_saju_profiles
Create Date: 2026-07-20

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "015_add_coin_tables"
down_revision: str | Sequence[str] | None = "014_add_chat_saju_profiles"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "coin_wallets",
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("balance", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["account_id"], ["accounts.id"], name="fk_coin_wallets_account_id"
        ),
        sa.PrimaryKeyConstraint("account_id"),
    )
    op.create_table(
        "coin_lots",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column(
            "coin_type", sa.Enum("PAID", "FREE", name="cointype"), nullable=False
        ),
        sa.Column(
            "source_reason",
            sa.Enum("SIGNUP_GRANT", "CHARGE", "EVENT", name="sourcereason"),
            nullable=False,
        ),
        sa.Column("original_amount", sa.Integer(), nullable=False),
        sa.Column("remaining_amount", sa.Integer(), nullable=False),
        sa.Column("ref", sa.String(length=191), nullable=False),
        sa.Column("acquired_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column(
            "status", sa.String(length=16), nullable=False, server_default="ACTIVE"
        ),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["account_id"], ["accounts.id"], name="fk_coin_lots_account_id"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_reason", "ref", name="uq_coin_lots_reason_ref"),
    )
    op.create_index(
        "ix_coin_lots_account_id", "coin_lots", ["account_id"], unique=False
    )
    op.create_index(
        "ix_coin_lots_expires_at", "coin_lots", ["expires_at"], unique=False
    )
    op.create_table(
        "coin_transactions",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column(
            "type",
            sa.Enum(
                "GRANT", "CHARGE", "SPEND", "REFUND", "EXPIRE", name="transactiontype"
            ),
            nullable=False,
        ),
        sa.Column("delta", sa.Integer(), nullable=False),
        sa.Column("lot_id", sa.BigInteger(), nullable=True),
        sa.Column("ref", sa.String(length=191), nullable=True),
        sa.Column("balance_after", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["account_id"], ["accounts.id"], name="fk_coin_transactions_account_id"
        ),
        sa.ForeignKeyConstraint(
            ["lot_id"], ["coin_lots.id"], name="fk_coin_transactions_lot_id"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("type", "ref", name="uq_coin_tx_type_ref"),
    )
    op.create_index(
        "ix_coin_transactions_account_id", "coin_transactions", ["account_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_coin_transactions_account_id", table_name="coin_transactions")
    op.drop_table("coin_transactions")
    op.drop_index("ix_coin_lots_expires_at", table_name="coin_lots")
    op.drop_index("ix_coin_lots_account_id", table_name="coin_lots")
    op.drop_table("coin_lots")
    op.drop_table("coin_wallets")
