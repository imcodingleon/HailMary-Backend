from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.domains.coin.domain.value_object.coin_enums import (
    CoinType,
    SourceReason,
    TransactionType,
)


def as_aware_utc(dt: datetime) -> datetime:
    """naive datetime을 UTC로 간주해 tzinfo를 부여한다.

    MySQL DATETIME 컬럼은 timezone 정보가 없어 naive datetime으로 돌아온다
    (DB에는 항상 UTC 값이 저장된다). 반면 usecase의 `now`는 보통
    `datetime.now(UTC)`로 aware하다. naive/aware를 직접 `>=` 비교하면
    `TypeError: can't compare offset-naive and offset-aware datetimes`가
    발생한다(실 prod 500 사례). 여기서 방어적으로 정규화해 이 비교가 이
    money-critical 경로를 다시는 죽이지 못하게 한다. Domain은 순수 Python이어야
    하므로 stdlib `datetime`만 사용한다 — 외부 라이브러리 의존 없음.
    """
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)


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
        if self.expires_at is None:
            return False
        return as_aware_utc(now) >= as_aware_utc(self.expires_at)

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
