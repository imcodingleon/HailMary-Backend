# 가입 지급 usecase 멱등성 테스트 (Task 5).
from datetime import UTC, datetime

import pytest

from app.domains.coin.application.usecase.grant_signup_coins_usecase import (
    GrantSignupCoinsUseCase,
)
from tests.domains.coin.test_coin_repository_contract import FakeLedger


@pytest.mark.asyncio
async def test_grant_once_and_idempotent():
    led = FakeLedger()
    uc = GrantSignupCoinsUseCase(ledger=led, grant_amount=30, expiry_days=30,
                                 now_fn=lambda: datetime(2026, 6, 1, tzinfo=UTC))
    await uc.grant(account_id=1)
    assert (await led.get_wallet(1)).balance == 30
    await uc.grant(account_id=1)  # 2회차 — 멱등, no-op
    assert (await led.get_wallet(1)).balance == 30
    assert len([lot for lot in led.lots if lot.account_id == 1]) == 1
