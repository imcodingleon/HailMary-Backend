# CoinLedgerPort 를 구현한 usecase 테스트가 의존하는 계약을 인메모리로 고정.
from datetime import UTC, datetime

import pytest

from app.domains.coin.application.coin_ports import CoinLedgerPort
from app.domains.coin.domain.entity.coin_models import CoinLot, SpendDraw, SpendPlan, Wallet
from app.domains.coin.domain.value_object.coin_enums import CoinType, SourceReason


class FakeLedger(CoinLedgerPort):
    def __init__(self) -> None:
        self.wallets: dict[int, Wallet] = {}
        self.lots: list[CoinLot] = []
        self._next = 1

    async def get_wallet(self, account_id):
        return self.wallets.get(account_id)

    async def get_wallet_for_update(self, account_id):
        return self.wallets.get(account_id)

    async def get_active_lots_for_update(self, account_id, now):
        return [
            lot
            for lot in self.lots
            if lot.account_id == account_id and lot.is_spendable(now=now)
        ]

    async def create_wallet_with_lot(self, lot):
        if any(
            existing.source_reason == lot.source_reason and existing.ref == lot.ref
            for existing in self.lots
        ):
            raise ValueError("duplicate lot ref")  # UNIQUE 시뮬레이션
        lot.id = self._next
        self._next += 1
        self.lots.append(lot)
        w = self.wallets.setdefault(lot.account_id, Wallet(account_id=lot.account_id, balance=0))
        w.balance += lot.original_amount
        return w

    async def apply_spend(self, account_id, plan, ref, tx_type):
        by_id = {lot.id: lot for lot in self.lots}
        for d in plan.draws:
            by_id[d.lot_id].remaining_amount -= d.amount
        self.wallets[account_id].balance -= plan.total
        return self.wallets[account_id].balance

    async def expire_stale_lots(self, account_id, now):
        freed = 0
        for lot in self.lots:
            if (
                lot.account_id == account_id
                and lot.status == "ACTIVE"
                and lot.is_expired(now=now)
            ):
                freed += lot.remaining_amount
                lot.status = "EXPIRED"
                lot.remaining_amount = 0
        if account_id in self.wallets:
            self.wallets[account_id].balance -= freed
        return self.wallets[account_id].balance if account_id in self.wallets else 0


@pytest.mark.asyncio
async def test_fake_ledger_grant_then_spend():
    led = FakeLedger()
    now = datetime(2026, 6, 1, tzinfo=UTC)
    lot = CoinLot(account_id=1, coin_type=CoinType.FREE, source_reason=SourceReason.SIGNUP_GRANT,
                  original_amount=30, remaining_amount=30, ref="signup:1",
                  acquired_at=now, expires_at=None, status="ACTIVE")
    w = await led.create_wallet_with_lot(lot)
    assert w.balance == 30
    plan = SpendPlan(draws=[SpendDraw(lot_id=1, amount=5)])
    assert await led.apply_spend(1, plan, ref="t1", tx_type="SPEND") == 25
