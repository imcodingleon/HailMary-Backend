from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from app.domains.coin.application.coin_ports import CoinLedgerPort


class SweepExpiredLotsUseCase:
    """만료된 lot이 있는 모든 account를 순회하며 만료 처리하는 배치 유스케이스.

    account 단위로 `CoinLedgerPort.expire_stale_lots` 를 호출한다 — 트랜잭션
    범위나 커밋 시점은 ledger(호출자의 세션)가 소유한다.
    """

    def __init__(
        self,
        *,
        ledger: CoinLedgerPort,
        now_fn: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self._ledger = ledger
        self._now = now_fn

    async def run(self) -> int:
        now = self._now()
        account_ids = await self._ledger.accounts_with_stale_lots(now)
        for account_id in account_ids:
            # 계정 wallet 행 락 선점 — sweep 만료가 동시 spend와 직렬화되게 한다.
            # (락은 트랜잭션 종료 시 해제된다.)
            await self._ledger.get_wallet_for_update(account_id)
            await self._ledger.expire_stale_lots(account_id, now)
        return len(account_ids)
