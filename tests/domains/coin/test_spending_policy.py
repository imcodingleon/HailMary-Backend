from datetime import UTC, datetime

import pytest

from app.domains.coin.domain.entity.coin_models import CoinLot
from app.domains.coin.domain.error import InsufficientCoinsError
from app.domains.coin.domain.service.spending_policy import CoinSpendingPolicy
from app.domains.coin.domain.value_object.coin_enums import CoinType, SourceReason

NOW = datetime(2026, 6, 1, tzinfo=UTC)


def _lot(lot_id, remaining, expires_at, coin_type=CoinType.PAID):
    return CoinLot(
        id=lot_id, account_id=1, coin_type=coin_type,
        source_reason=SourceReason.CHARGE, original_amount=remaining,
        remaining_amount=remaining, ref=f"r{lot_id}",
        acquired_at=NOW, expires_at=expires_at, status="ACTIVE",
    )


def test_fifo_imminent_expiry_first():
    soon = _lot(1, 100, datetime(2026, 6, 10, tzinfo=UTC))
    later = _lot(2, 100, datetime(2026, 12, 1, tzinfo=UTC))
    plan = CoinSpendingPolicy().plan_spend([later, soon], cost=30, now=NOW)
    assert plan.draws == [type(plan.draws[0])(lot_id=1, amount=30)]


def test_spans_multiple_lots():
    a = _lot(1, 20, datetime(2026, 6, 10, tzinfo=UTC))
    b = _lot(2, 50, datetime(2026, 7, 10, tzinfo=UTC))
    plan = CoinSpendingPolicy().plan_spend([a, b], cost=35, now=NOW)
    assert [(d.lot_id, d.amount) for d in plan.draws] == [(1, 20), (2, 15)]


def test_free_preferred_when_never_expiring_still_last():
    never_free = _lot(1, 100, None, coin_type=CoinType.FREE)
    paid_5yr = _lot(2, 100, datetime(2031, 6, 1, tzinfo=UTC))
    plan = CoinSpendingPolicy().plan_spend([never_free, paid_5yr], cost=10, now=NOW)
    assert plan.draws[0].lot_id == 2  # 만료 있는 유료가 먼저, 무기한은 뒤


def test_excludes_expired_and_zero():
    expired = _lot(1, 100, datetime(2026, 5, 1, tzinfo=UTC))
    ok = _lot(2, 100, datetime(2026, 7, 1, tzinfo=UTC))
    plan = CoinSpendingPolicy().plan_spend([expired, ok], cost=10, now=NOW)
    assert plan.draws[0].lot_id == 2


def test_insufficient_raises():
    a = _lot(1, 5, datetime(2026, 7, 1, tzinfo=UTC))
    with pytest.raises(InsufficientCoinsError) as exc:
        CoinSpendingPolicy().plan_spend([a], cost=10, now=NOW)
    assert exc.value.available == 5
    assert exc.value.required == 10


def test_cost_zero_raises_value_error():
    a = _lot(1, 100, datetime(2026, 7, 1, tzinfo=UTC))
    with pytest.raises(ValueError):
        CoinSpendingPolicy().plan_spend([a], cost=0, now=NOW)


def test_cost_negative_raises_value_error():
    a = _lot(1, 100, datetime(2026, 7, 1, tzinfo=UTC))
    with pytest.raises(ValueError):
        CoinSpendingPolicy().plan_spend([a], cost=-5, now=NOW)
