from app.domains.coin.domain.entity.coin_models import CoinLot, Wallet
from app.domains.coin.infrastructure.orm.coin_orm import CoinLotORM, CoinWalletORM


class CoinMapper:
    @staticmethod
    def wallet_to_entity(orm: CoinWalletORM) -> Wallet:
        return Wallet(account_id=orm.account_id, balance=orm.balance)

    @staticmethod
    def lot_to_entity(orm: CoinLotORM) -> CoinLot:
        return CoinLot(
            id=orm.id,
            account_id=orm.account_id,
            coin_type=orm.coin_type,
            source_reason=orm.source_reason,
            original_amount=orm.original_amount,
            remaining_amount=orm.remaining_amount,
            ref=orm.ref,
            acquired_at=orm.acquired_at,
            expires_at=orm.expires_at,
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
