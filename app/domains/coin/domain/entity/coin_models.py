from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from app.domains.coin.domain.value_object.coin_enums import (
    CoinType,
    SourceReason,
    TransactionType,
)


@dataclass
class Wallet:
    account_id: int
    balance: int = 0


@dataclass
class CoinLot:
    account_id: int
    coin_type: CoinType
    source_reason: SourceReason
    original_amount: int
    remaining_amount: int
    ref: str
    acquired_at: datetime
    expires_at: datetime | None
    status: str = "ACTIVE"
    id: int | None = None

    def is_expired(self, *, now: datetime) -> bool:
        return self.expires_at is not None and now >= self.expires_at

    def is_spendable(self, *, now: datetime) -> bool:
        return (
            self.status == "ACTIVE"
            and self.remaining_amount > 0
            and not self.is_expired(now=now)
        )


@dataclass
class CoinTransaction:
    account_id: int
    type: TransactionType
    delta: int
    balance_after: int
    lot_id: int | None = None
    ref: str | None = None
    id: int | None = None


@dataclass
class SpendDraw:
    lot_id: int
    amount: int


@dataclass
class SpendPlan:
    draws: list[SpendDraw] = field(default_factory=list)

    @property
    def total(self) -> int:
        return sum(d.amount for d in self.draws)
