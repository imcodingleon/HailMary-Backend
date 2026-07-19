"""잔액조회 usecase (Task 7).

GET은 순수 읽기다 — 원장을 변형하지 않는다. 소비가능 잔액을
get_available_balance(ACTIVE·미만료 lot들의 remaining 합)로 즉시 계산해 반환한다.
지갑/lot이 없으면 SUM이 자연히 0을 돌려주므로 self-heal 지급은 발생하지 않는다
(지급은 가입 훅에서만).
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
        # 순수 읽기: 락도 쓰기도 없다. lot이 없으면 SUM이 0을 반환한다.
        return await self._ledger.get_available_balance(account_id, self._now())
