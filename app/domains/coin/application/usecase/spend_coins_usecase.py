from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from app.domains.coin.application.coin_ports import CoinLedgerPort
from app.domains.coin.domain.service.spending_policy import CoinSpendingPolicy
from app.domains.coin.domain.value_object.coin_enums import TransactionType


class SpendCoinsUseCase:
    def __init__(
        self,
        *,
        ledger: CoinLedgerPort,
        policy: CoinSpendingPolicy,
        now_fn: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self._ledger = ledger
        self._policy = policy
        self._now = now_fn

    async def spend(self, account_id: int, cost: int, ref: str) -> int:
        now = self._now()
        await self._ledger.expire_stale_lots(account_id, now)
        await self._ledger.get_wallet_for_update(account_id)  # 계정 행 잠금
        lots = await self._ledger.get_active_lots_for_update(account_id, now)
        plan = self._policy.plan_spend(lots, cost, now)  # 부족 시 InsufficientCoinsError
        return await self._ledger.apply_spend(
            account_id, plan, ref=ref, tx_type=TransactionType.SPEND.value
        )
