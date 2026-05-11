"""add_payment_method_columns

Revision ID: 4dda5005e680
Revises: a5b1fc5db05b
Create Date: 2026-05-08 11:53:58.809602

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '4dda5005e680'
down_revision: str | None = 'd4e5f8a9b0c1'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    payment_method_enum = sa.Enum(
        'CARD', 'EASY_PAY', 'TRANSFER', 'VIRTUAL_ACCOUNT', 'MOBILE_PHONE', 'OTHER',
        name='paymentmethod',
    )
    payment_method_enum.create(op.get_bind(), checkfirst=True)
    op.add_column('payments', sa.Column('method', payment_method_enum, nullable=True))
    op.add_column('payments', sa.Column('easy_pay_provider', sa.String(length=32), nullable=True))
    op.add_column('payments', sa.Column('card_issuer_code', sa.String(length=8), nullable=True))
    op.add_column('payments', sa.Column('bank_code', sa.String(length=8), nullable=True))


def downgrade() -> None:
    op.drop_column('payments', 'bank_code')
    op.drop_column('payments', 'card_issuer_code')
    op.drop_column('payments', 'easy_pay_provider')
    op.drop_column('payments', 'method')
    sa.Enum(name='paymentmethod').drop(op.get_bind(), checkfirst=True)
