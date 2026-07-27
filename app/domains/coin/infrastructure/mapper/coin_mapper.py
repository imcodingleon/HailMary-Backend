from app.domains.coin.domain.entity.coin_models import CoinLot, Wallet, as_aware_utc
from app.domains.coin.infrastructure.orm.coin_orm import CoinLotORM, CoinWalletORM


class CoinMapper:
    @staticmethod
    def wallet_to_entity(orm: CoinWalletORM) -> Wallet:
        return Wallet(account_id=orm.account_id, balance=orm.balance)

    @staticmethod
    def lot_to_entity(orm: CoinLotORM) -> CoinLot:
        """ORM -> Domain 변환 지점(persistence 경계)에서 tz 정규화.

        MySQL DATETIME 컬럼은 timezone이 없어 asyncmy가 naive datetime을
        돌려준다(DB에는 항상 UTC 값이 저장된다). 여기서 UTC tzinfo를 부여해
        entity가 항상 aware datetime을 갖도록 한다 — 이후 domain에서
        `datetime.now(UTC)`(aware)와 비교할 때 TypeError가 나지 않는다.
        """
        expires_at = orm.expires_at
        return CoinLot(
            id=orm.id,
            account_id=orm.account_id,
            coin_type=orm.coin_type,
            source_reason=orm.source_reason,
            original_amount=orm.original_amount,
            remaining_amount=orm.remaining_amount,
            ref=orm.ref,
            acquired_at=as_aware_utc(orm.acquired_at),
            expires_at=as_aware_utc(expires_at) if expires_at is not None else None,
            status=orm.status,
        )

    @staticmethod
    def lot_to_orm(entity: CoinLot) -> CoinLotORM:
        """신규 lot INSERT용 — entity.id는 보통 None (autoincrement로 확보)."""
        return CoinLotORM(
            id=entity.id,
            account_id=entity.account_id,
            coin_type=entity.coin_type,
            source_reason=entity.source_reason,
            original_amount=entity.original_amount,
            remaining_amount=entity.remaining_amount,
            ref=entity.ref,
            acquired_at=entity.acquired_at,
            expires_at=entity.expires_at,
            status=entity.status,
        )
