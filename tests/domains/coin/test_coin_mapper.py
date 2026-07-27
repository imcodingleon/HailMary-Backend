# CoinMapper 는 persistence 경계에서 ORM row(naive datetime, MySQL DATETIME)를
# Domain entity로 변환한다. 이 경계에서 UTC tzinfo를 부여해, 이후 domain 비교가
# 항상 aware-vs-aware로 이뤄지도록 한다 (실 prod TypeError 재발 방지).
from datetime import UTC, datetime

from app.domains.coin.domain.value_object.coin_enums import CoinType, SourceReason
from app.domains.coin.infrastructure.mapper.coin_mapper import CoinMapper
from app.domains.coin.infrastructure.orm.coin_orm import CoinLotORM, CoinWalletORM


def test_lot_to_entity_attaches_utc_to_naive_db_datetimes():
    orm = CoinLotORM(
        id=1,
        account_id=1,
        coin_type=CoinType.PAID,
        source_reason=SourceReason.CHARGE,
        original_amount=100,
        remaining_amount=100,
        ref="charge:1",
        acquired_at=datetime(2026, 1, 1),  # naive, MySQL이 돌려주는 형태
        expires_at=datetime(2026, 1, 31),  # naive
        status="ACTIVE",
    )

    entity = CoinMapper.lot_to_entity(orm)

    assert entity.acquired_at.tzinfo is not None
    assert entity.acquired_at == datetime(2026, 1, 1, tzinfo=UTC)
    assert entity.expires_at is not None
    assert entity.expires_at.tzinfo is not None
    assert entity.expires_at == datetime(2026, 1, 31, tzinfo=UTC)

    # 경계에서 정규화된 aware datetime은 aware now와 바로 비교 가능해야 한다.
    assert entity.is_expired(now=datetime(2026, 1, 15, tzinfo=UTC)) is False
    assert entity.is_expired(now=datetime(2026, 2, 1, tzinfo=UTC)) is True


def test_lot_to_entity_passthrough_when_already_aware():
    # 방어적 정규화가 이미 aware인 값을 훼손하면 안 된다.
    orm = CoinLotORM(
        id=2,
        account_id=1,
        coin_type=CoinType.FREE,
        source_reason=SourceReason.SIGNUP_GRANT,
        original_amount=30,
        remaining_amount=30,
        ref="signup:1",
        acquired_at=datetime(2026, 1, 1, tzinfo=UTC),
        expires_at=None,
        status="ACTIVE",
    )

    entity = CoinMapper.lot_to_entity(orm)

    assert entity.acquired_at == datetime(2026, 1, 1, tzinfo=UTC)
    assert entity.expires_at is None


def test_lot_to_entity_none_expires_at_stays_none():
    orm = CoinLotORM(
        id=3,
        account_id=1,
        coin_type=CoinType.FREE,
        source_reason=SourceReason.SIGNUP_GRANT,
        original_amount=30,
        remaining_amount=30,
        ref="signup:2",
        acquired_at=datetime(2026, 1, 1),
        expires_at=None,
        status="ACTIVE",
    )

    entity = CoinMapper.lot_to_entity(orm)

    assert entity.expires_at is None


def test_wallet_to_entity_unaffected_no_datetimes():
    orm = CoinWalletORM(account_id=7, balance=42)
    entity = CoinMapper.wallet_to_entity(orm)
    assert entity.account_id == 7
    assert entity.balance == 42
