from datetime import UTC, datetime

import pytest

from app.domains.coin.application.usecase.spend_coins_usecase import SpendCoinsUseCase
from app.domains.coin.domain.entity.coin_models import CoinLot
from app.domains.coin.domain.error import InsufficientCoinsError
from app.domains.coin.domain.service.spending_policy import CoinSpendingPolicy
from app.domains.coin.domain.value_object.coin_enums import CoinType, SourceReason
from tests.domains.coin.test_coin_repository_contract import FakeLedger

NOW = datetime(2026, 6, 1, tzinfo=UTC)


def _seed(led, account_id, amount, expires_at, coin_type=CoinType.FREE):
    led._next_seed = getattr(led, "_next_seed", 100) + 1
    lot = CoinLot(id=led._next_seed, account_id=account_id, coin_type=coin_type,
                  source_reason=SourceReason.SIGNUP_GRANT, original_amount=amount,
                  remaining_amount=amount, ref=f"seed{led._next_seed}",
                  acquired_at=NOW, expires_at=expires_at, status="ACTIVE")
    led.lots.append(lot)
    from app.domains.coin.domain.entity.coin_models import Wallet
    w = led.wallets.setdefault(account_id, Wallet(account_id=account_id, balance=0))
    w.balance += amount


@pytest.mark.asyncio
async def test_spend_deducts_and_returns_balance():
    led = FakeLedger()
    _seed(led, 1, 30, datetime(2026, 6, 30, tzinfo=UTC))
    uc = SpendCoinsUseCase(ledger=led, policy=CoinSpendingPolicy(), now_fn=lambda: NOW)
    assert await uc.spend(account_id=1, cost=5, ref="req-1") == 25


@pytest.mark.asyncio
async def test_spend_insufficient_raises_and_no_deduct():
    led = FakeLedger()
    _seed(led, 1, 3, datetime(2026, 6, 30, tzinfo=UTC))
    uc = SpendCoinsUseCase(ledger=led, policy=CoinSpendingPolicy(), now_fn=lambda: NOW)
    with pytest.raises(InsufficientCoinsError):
        await uc.spend(account_id=1, cost=5, ref="req-2")
    assert led.wallets[1].balance == 3  # 미변경
