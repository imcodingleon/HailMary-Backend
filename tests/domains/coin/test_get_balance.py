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
async def test_balance_excludes_expired_via_live_sum():
    """만료 lot은 live 합에서 제외 — 소비가능 잔액만 반환한다."""
    led = FakeLedger()
    now = datetime(2026, 6, 1, tzinfo=UTC)
    led.wallets[1] = Wallet(account_id=1, balance=30)
    led.lots.append(CoinLot(id=1, account_id=1, coin_type=CoinType.FREE,
        source_reason=SourceReason.SIGNUP_GRANT, original_amount=30, remaining_amount=30,
        ref="signup:1", acquired_at=datetime(2026, 5, 1, tzinfo=UTC),
        expires_at=datetime(2026, 5, 20, tzinfo=UTC), status="ACTIVE"))  # 이미 만료
    uc = GetBalanceUseCase(ledger=led, now_fn=lambda: now)
    assert await uc.execute(account_id=1) == 0  # 만료분 제외되어 0


@pytest.mark.asyncio
async def test_balance_sum_of_active_lots():
    """소비가능 잔액 = ACTIVE·미만료 lot들의 remaining 합."""
    led = FakeLedger()
    now = datetime(2026, 6, 1, tzinfo=UTC)
    led.wallets[1] = Wallet(account_id=1, balance=999)  # 스냅샷은 무시됨
    led.lots.append(CoinLot(id=1, account_id=1, coin_type=CoinType.FREE,
        source_reason=SourceReason.SIGNUP_GRANT, original_amount=30, remaining_amount=20,
        ref="a", acquired_at=now, expires_at=datetime(2026, 7, 1, tzinfo=UTC), status="ACTIVE"))
    led.lots.append(CoinLot(id=2, account_id=1, coin_type=CoinType.PAID,
        source_reason=SourceReason.CHARGE, original_amount=50, remaining_amount=50,
        ref="b", acquired_at=now, expires_at=None, status="ACTIVE"))
    led.lots.append(CoinLot(id=3, account_id=1, coin_type=CoinType.FREE,
        source_reason=SourceReason.SIGNUP_GRANT, original_amount=100, remaining_amount=100,
        ref="c", acquired_at=now, expires_at=datetime(2026, 5, 1, tzinfo=UTC), status="ACTIVE"))  # 만료
    uc = GetBalanceUseCase(ledger=led, now_fn=lambda: now)
    assert await uc.execute(account_id=1) == 70  # 20 + 50, 만료 100 제외


@pytest.mark.asyncio
async def test_get_balance_is_read_only():
    """GET은 lot/wallet을 변형하지 않는다 (만료 처리·차감·EXPIRE row 없음)."""
    led = FakeLedger()
    now = datetime(2026, 6, 1, tzinfo=UTC)
    led.wallets[1] = Wallet(account_id=1, balance=30)
    expired = CoinLot(id=1, account_id=1, coin_type=CoinType.FREE,
        source_reason=SourceReason.SIGNUP_GRANT, original_amount=30, remaining_amount=30,
        ref="signup:1", acquired_at=datetime(2026, 5, 1, tzinfo=UTC),
        expires_at=datetime(2026, 5, 20, tzinfo=UTC), status="ACTIVE")  # 이미 만료
    led.lots.append(expired)
    uc = GetBalanceUseCase(ledger=led, now_fn=lambda: now)

    result = await uc.execute(account_id=1)

    assert result == 0  # live 합에서 만료 제외
    # 원장 불변: lot 상태/잔량 그대로, wallet 스냅샷 그대로.
    assert expired.status == "ACTIVE"
    assert expired.remaining_amount == 30
    assert led.wallets[1].balance == 30
