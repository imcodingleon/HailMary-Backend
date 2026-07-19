from __future__ import annotations

from datetime import datetime

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.coin.application.coin_ports import CoinLedgerPort
from app.domains.coin.domain.entity.coin_models import CoinLot, SpendPlan, Wallet
from app.domains.coin.domain.value_object.coin_enums import TransactionType
from app.domains.coin.infrastructure.mapper.coin_mapper import CoinMapper
from app.domains.coin.infrastructure.orm.coin_orm import (
    CoinLotORM,
    CoinTransactionORM,
    CoinWalletORM,
)


class CoinRepository(CoinLedgerPort):
    """CoinLedgerPort 구현 — 요청당 AsyncSession 생성자 주입.

    커밋은 호출자(요청 스코프 세션/트랜잭션)가 소유한다. 여기서는 flush()로
    생성 id/기본값만 확보하고 commit은 하지 않는다.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get_wallet_orm(self, account_id: int) -> CoinWalletORM | None:
        result = await self._session.execute(
            select(CoinWalletORM).where(CoinWalletORM.account_id == account_id)
        )
        return result.scalar_one_or_none()

    async def _get_lot_orm(self, lot_id: int) -> CoinLotORM | None:
        result = await self._session.execute(
            select(CoinLotORM).where(CoinLotORM.id == lot_id)
        )
        return result.scalar_one_or_none()

    async def get_wallet(self, account_id: int) -> Wallet | None:
        orm = await self._get_wallet_orm(account_id)
        return CoinMapper.wallet_to_entity(orm) if orm else None

    async def get_wallet_for_update(self, account_id: int) -> Wallet | None:
        result = await self._session.execute(
            select(CoinWalletORM)
            .where(CoinWalletORM.account_id == account_id)
            .with_for_update()
        )
        orm = result.scalar_one_or_none()
        return CoinMapper.wallet_to_entity(orm) if orm else None

    async def get_active_lots_for_update(
        self, account_id: int, now: datetime
    ) -> list[CoinLot]:
        result = await self._session.execute(
            select(CoinLotORM)
            .where(
                CoinLotORM.account_id == account_id,
                CoinLotORM.status == "ACTIVE",
                CoinLotORM.remaining_amount > 0,
                or_(CoinLotORM.expires_at.is_(None), CoinLotORM.expires_at > now),
            )
            .with_for_update()
        )
        return [CoinMapper.lot_to_entity(orm) for orm in result.scalars().all()]

    async def create_wallet_with_lot(self, lot: CoinLot) -> Wallet:
        """지갑 upsert + lot INSERT + GRANT tx INSERT, balance += original_amount.

        lot INSERT 는 UNIQUE(source_reason, ref) 위반 시 IntegrityError 를 던질 수
        있다 (예: AUTH 로그인 트랜잭션 안에서 중복 signup grant 재시도/레이스).
        wallet-upsert-if-missing + lot INSERT 를 SAVEPOINT(`begin_nested`) 로 감싸,
        충돌 시 그 SAVEPOINT만 롤백되고 바깥 트랜잭션은 계속 사용 가능한 상태로
        남는다. 에러는 여기서 삼키지 않고 그대로 전파한다 — 호출자(Task 5
        usecase)가 catch 해서 기존 지갑 재조회 등으로 합류한다.
        """
        wallet_orm = await self._get_wallet_orm(lot.account_id)
        lot_orm = CoinMapper.lot_to_orm(lot)

        async with self._session.begin_nested():
            if wallet_orm is None:
                wallet_orm = CoinWalletORM(account_id=lot.account_id, balance=0)
                self._session.add(wallet_orm)
            self._session.add(lot_orm)
            await self._session.flush()

        wallet_orm.balance += lot.original_amount
        tx_orm = CoinTransactionORM(
            account_id=lot.account_id,
            type=TransactionType.GRANT,
            delta=lot.original_amount,
            lot_id=lot_orm.id,
            ref=None,  # coin_lots(source_reason, ref) UNIQUE가 GRANT 멱등을 보장
            balance_after=wallet_orm.balance,
        )
        self._session.add(tx_orm)
        await self._session.flush()
        return CoinMapper.wallet_to_entity(wallet_orm)

    async def apply_spend(
        self, account_id: int, plan: SpendPlan, ref: str, tx_type: str
    ) -> int:
        """draw(봉투)당 lot.remaining_amount 차감 + SPEND tx INSERT, balance -= total.

        coin_transactions 는 UNIQUE(type, ref) 제약이 있다 — 한 SpendPlan이 여러
        lot(봉투)에 걸쳐 있으면 draw마다 별도 tx row가 필요하므로, 저장되는
        ref는 `f"{ref}:{lot_id}"`로 봉투별로 구분해 유일성을 만족시키면서도
        같은 요청이 그대로 재시도되면 각 draw 조합이 다시 충돌해 멱등을 지킨다.
        """
        lot_orms: dict[int, CoinLotORM] = {}
        for draw in plan.draws:
            if draw.lot_id not in lot_orms:
                orm = await self._get_lot_orm(draw.lot_id)
                if orm is None:
                    raise ValueError(f"coin lot not found: {draw.lot_id}")
                lot_orms[draw.lot_id] = orm
            lot_orms[draw.lot_id].remaining_amount -= draw.amount

        wallet_orm = await self._get_wallet_orm(account_id)
        if wallet_orm is None:
            raise ValueError(f"coin wallet not found: {account_id}")
        wallet_orm.balance -= plan.total

        tx_enum = TransactionType(tx_type)
        for draw in plan.draws:
            self._session.add(
                CoinTransactionORM(
                    account_id=account_id,
                    type=tx_enum,
                    delta=-draw.amount,
                    lot_id=draw.lot_id,
                    ref=f"{ref}:{draw.lot_id}",
                    balance_after=wallet_orm.balance,
                )
            )

        await self._session.flush()
        return wallet_orm.balance

    async def expire_stale_lots(self, account_id: int, now: datetime) -> int:
        """만료된 ACTIVE lot -> EXPIRED(remaining=0) + EXPIRE tx(봉투당) + balance 차감."""
        result = await self._session.execute(
            select(CoinLotORM).where(
                CoinLotORM.account_id == account_id,
                CoinLotORM.status == "ACTIVE",
                CoinLotORM.expires_at.is_not(None),
                CoinLotORM.expires_at <= now,
            )
        )
        stale = result.scalars().all()
        wallet_orm = await self._get_wallet_orm(account_id)

        for lot_orm in stale:
            freed = lot_orm.remaining_amount
            lot_orm.status = "EXPIRED"
            lot_orm.remaining_amount = 0
            if wallet_orm is not None and freed > 0:
                wallet_orm.balance -= freed
                self._session.add(
                    CoinTransactionORM(
                        account_id=account_id,
                        type=TransactionType.EXPIRE,
                        delta=-freed,
                        lot_id=lot_orm.id,
                        ref=None,  # 배치 만료 — 외부 idempotency key 없음
                        balance_after=wallet_orm.balance,
                    )
                )

        await self._session.flush()
        return wallet_orm.balance if wallet_orm is not None else 0
