"""잔액조회 usecase (Task 7).

지갑이 없으면 0을 반환한다 — self-heal 지급 금지(지급은 가입 훅에서만).
지갑이 있으면 lazy 만료 정리(expire_stale_lots)를 먼저 수행한 뒤 그 결과 잔액을 반환한다.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from app.domains.coin.application.coin_ports import CoinLedgerPort


class GetBalanceUseCase:
    def __init__(
        self,
        *,
        ledger: CoinLedgerPort,
        now_fn: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self._ledger = ledger
        self._now = now_fn

    async def execute(self, account_id: int) -> int:
        wallet = await self._ledger.get_wallet(account_id)
        if wallet is None:
            return 0  # self-heal 금지 — 지급은 가입 훅에서만
        return await self._ledger.expire_stale_lots(account_id, self._now())
