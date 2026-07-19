from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.domains.coin.domain.value_object.coin_enums import (
    CoinType,
    SourceReason,
    TransactionType,
)
from app.infrastructure.database.session import Base


class CoinWalletORM(Base):
    __tablename__ = "coin_wallets"

    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("accounts.id"), primary_key=True
    )
    balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class CoinLotORM(Base):
    __tablename__ = "coin_lots"
    __table_args__ = (
        UniqueConstraint("source_reason", "ref", name="uq_coin_lots_reason_ref"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("accounts.id"), nullable=False, index=True
    )
    coin_type: Mapped[CoinType] = mapped_column(
        SAEnum(CoinType, values_callable=lambda e: [x.value for x in e]),
        nullable=False,
    )
    source_reason: Mapped[SourceReason] = mapped_column(
        SAEnum(SourceReason, values_callable=lambda e: [x.value for x in e]),
        nullable=False,
    )
    original_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    remaining_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    ref: Mapped[str] = mapped_column(String(191), nullable=False)
    acquired_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class CoinTransactionORM(Base):
    __tablename__ = "coin_transactions"
    __table_args__ = (
        UniqueConstraint(
            "account_id", "type", "ref", name="uq_coin_tx_account_type_ref"
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("accounts.id"), nullable=False, index=True
    )
    type: Mapped[TransactionType] = mapped_column(
        SAEnum(TransactionType, values_callable=lambda e: [x.value for x in e]),
        nullable=False,
    )
    delta: Mapped[int] = mapped_column(Integer, nullable=False)
    lot_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("coin_lots.id"), nullable=True
    )
    ref: Mapped[str | None] = mapped_column(String(191), nullable=True)
    balance_after: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
