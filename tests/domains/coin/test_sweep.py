from datetime import UTC, datetime

import pytest

from app.domains.coin.application.usecase.sweep_expired_lots_usecase import (
    SweepExpiredLotsUseCase,
)
from app.domains.coin.domain.entity.coin_models import CoinLot, Wallet
from app.domains.coin.domain.value_object.coin_enums import CoinType, SourceReason
from tests.domains.coin.test_coin_repository_contract import FakeLedger


@pytest.mark.asyncio
async def test_sweep_expires_and_counts():
    led = FakeLedger()
    now = datetime(2026, 6, 1, tzinfo=UTC)
    led.wallets[1] = Wallet(account_id=1, balance=30)
    led.lots.append(CoinLot(id=1, account_id=1, coin_type=CoinType.FREE,
        source_reason=SourceReason.SIGNUP_GRANT, original_amount=30, remaining_amount=30,
        ref="signup:1", acquired_at=datetime(2026, 4, 1, tzinfo=UTC),
        expires_at=datetime(2026, 5, 1, tzinfo=UTC), status="ACTIVE"))

    uc = SweepExpiredLotsUseCase(ledger=led, now_fn=lambda: now)
    assert await uc.run() == 1
    assert led.wallets[1].balance == 0
