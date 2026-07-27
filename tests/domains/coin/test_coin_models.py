from datetime import UTC, datetime

from app.domains.coin.domain.entity.coin_models import CoinLot
from app.domains.coin.domain.value_object.coin_enums import CoinType, SourceReason


def test_coinlot_is_active_and_not_expired():
    lot = CoinLot(
        id=1, account_id=1, coin_type=CoinType.FREE,
        source_reason=SourceReason.SIGNUP_GRANT, original_amount=30,
        remaining_amount=30, ref="signup:1",
        acquired_at=datetime(2026, 1, 1, tzinfo=UTC),
        expires_at=datetime(2026, 1, 31, tzinfo=UTC), status="ACTIVE",
    )
    assert lot.is_spendable(now=datetime(2026, 1, 15, tzinfo=UTC)) is True
    assert lot.is_spendable(now=datetime(2026, 2, 1, tzinfo=UTC)) is False  # 만료
    lot.remaining_amount = 0
    assert lot.is_spendable(now=datetime(2026, 1, 15, tzinfo=UTC)) is False  # 소진


def test_coinlot_naive_expires_at_vs_aware_now_does_not_raise():
    """실 MySQL 재현: DB에서 읽은 lot은 naive datetime, now는 UTC-aware.

    수정 전에는 `TypeError: can't compare offset-naive and offset-aware
    datetimes` 가 발생했다 (실 prod 500 트레이스백). naive datetime은 UTC로
    간주해 비교해야 한다.
    """
    lot = CoinLot(
        id=1, account_id=1, coin_type=CoinType.PAID,
        source_reason=SourceReason.CHARGE, original_amount=100,
        remaining_amount=100, ref="charge:1",
        acquired_at=datetime(2026, 1, 1),  # naive (MySQL DATETIME)
        expires_at=datetime(2026, 1, 31),  # naive (MySQL DATETIME)
        status="ACTIVE",
    )
    # 만료 전 (aware now) — 소비 가능해야 한다.
    assert lot.is_expired(now=datetime(2026, 1, 15, tzinfo=UTC)) is False
    assert lot.is_spendable(now=datetime(2026, 1, 15, tzinfo=UTC)) is True
    # 만료 후 (aware now) — 만료 처리돼야 한다.
    assert lot.is_expired(now=datetime(2026, 2, 1, tzinfo=UTC)) is True
    assert lot.is_spendable(now=datetime(2026, 2, 1, tzinfo=UTC)) is False


def test_coinlot_naive_expires_at_and_naive_now_still_correct():
    """양쪽 다 naive인 경우(순수 도메인 유닛테스트)도 기존처럼 동작해야 한다."""
    lot = CoinLot(
        id=1, account_id=1, coin_type=CoinType.PAID,
        source_reason=SourceReason.CHARGE, original_amount=100,
        remaining_amount=100, ref="charge:1",
        acquired_at=datetime(2026, 1, 1),
        expires_at=datetime(2026, 1, 31),
        status="ACTIVE",
    )
    assert lot.is_expired(now=datetime(2026, 1, 15)) is False
    assert lot.is_expired(now=datetime(2026, 2, 1)) is True
