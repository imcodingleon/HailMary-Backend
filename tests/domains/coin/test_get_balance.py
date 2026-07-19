from datetime import UTC, datetime

import pytest

from app.domains.coin.application.usecase.get_balance_usecase import GetBalanceUseCase
from app.domains.coin.domain.entity.coin_models import CoinLot, Wallet
from app.domains.coin.domain.value_object.coin_enums import CoinType, SourceReason
from tests.domains.coin.test_coin_repository_contract import FakeLedger


@pytest.mark.asyncio
async def test_balance_zero_when_no_wallet():
    uc = GetBalanceUseCase(ledger=FakeLedger(), now_fn=lambda: datetime(2026, 6, 1, tzinfo=UTC))
    assert await uc.execute(account_id=99) == 0


@pytest.mark.asyncio
async def test_balance_reflects_lazy_expiry():
    led = FakeLedger()
    now = datetime(2026, 6, 1, tzinfo=UTC)
    led.wallets[1] = Wallet(account_id=1, balance=30)
    led.lots.append(CoinLot(id=1, account_id=1, coin_type=CoinType.FREE,
        source_reason=SourceReason.SIGNUP_GRANT, original_amount=30, remaining_amount=30,
        ref="signup:1", acquired_at=datetime(2026, 5, 1, tzinfo=UTC),
        expires_at=datetime(2026, 5, 20, tzinfo=UTC), status="ACTIVE"))  # 이미 만료
    uc = GetBalanceUseCase(ledger=led, now_fn=lambda: now)
    assert await uc.execute(account_id=1) == 0  # 만료분 정리되어 0
