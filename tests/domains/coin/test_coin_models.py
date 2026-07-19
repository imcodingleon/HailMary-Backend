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
