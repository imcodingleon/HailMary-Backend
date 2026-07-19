from __future__ import annotations

from datetime import datetime

from app.domains.coin.domain.entity.coin_models import CoinLot, SpendDraw, SpendPlan
from app.domains.coin.domain.error import InsufficientCoinsError
from app.domains.coin.domain.value_object.coin_enums import CoinType


class CoinSpendingPolicy:
    """만료임박 FIFO로 차감 봉투를 선택하는 순수 로직."""

    @staticmethod
    def _sort_key(lot: CoinLot) -> tuple[int, float, int]:
        # (무기한이면 1 아니면 0, 만료 타임스탬프, FREE 우선=0/PAID=1)
        no_expiry = 1 if lot.expires_at is None else 0
        ts = lot.expires_at.timestamp() if lot.expires_at is not None else 0.0
        type_rank = 0 if lot.coin_type == CoinType.FREE else 1
        return (no_expiry, ts, type_rank)

    def plan_spend(self, lots: list[CoinLot], cost: int, now: datetime) -> SpendPlan:
        if cost <= 0:
            raise ValueError("cost must be positive")
        spendable = sorted(
            (lot for lot in lots if lot.is_spendable(now=now)),
            key=self._sort_key,
        )
        available = sum(lot.remaining_amount for lot in spendable)
        if available < cost:
            raise InsufficientCoinsError(available=available, required=cost)
        plan = SpendPlan()
        left = cost
        for lot in spendable:
            if left <= 0:
                break
            take = min(lot.remaining_amount, left)
            assert lot.id is not None
            plan.draws.append(SpendDraw(lot_id=lot.id, amount=take))
            left -= take
        return plan
