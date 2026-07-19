from __future__ import annotations

from datetime import datetime
from typing import Any, cast

from sqlalchemy import CursorResult, func, or_, select, update
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

    async def get_available_balance(self, account_id: int, now: datetime) -> int:
        """live 소비가능 잔액 = ACTIVE·미만료 lot들의 remaining_amount 합.

        순수 읽기 — 락도, 쓰기도 없다. 잔액조회(GET)가 원장을 변형하지 않도록
        balance 스냅샷 대신 lot 합을 직접 계산한다. lot이 없으면 SUM은
        coalesce로 0을 돌려준다.
        """
        result = await self._session.execute(
            select(func.coalesce(func.sum(CoinLotORM.remaining_amount), 0)).where(
                CoinLotORM.account_id == account_id,
                CoinLotORM.status == "ACTIVE",
                or_(CoinLotORM.expires_at.is_(None), CoinLotORM.expires_at > now),
            )
        )
        return int(result.scalar_one())

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
        """SPEND 는 연산(operation)당 정확히 tx row 1개, ref에 대해 멱등.

        coin_transactions 는 UNIQUE(type, ref) 제약이 있다 — 이를 연산 단위
        멱등으로 실제로 활용하려면 재시도 시 ref가 그대로 유지되어야 한다.
        호출자가 같은 트랜잭션 안에서 이미 get_wallet_for_update 로 지갑 행을
        잠근 뒤 호출한다는 전제 하에, 먼저 (type, ref) 로 이미 처리된 tx가
        있는지 조회한다. 있으면 동일 요청의 재시도이므로 lot을 다시 차감하지
        않고 현재 잔액만 그대로 반환한다. 없으면 draw(봉투)별로
        lot.remaining_amount 를 차감한 뒤, SPEND tx row를 정확히 1개만
        INSERT 하고 balance -= total 한다.
        """
        tx_enum = TransactionType(tx_type)

        wallet_orm = await self._get_wallet_orm(account_id)
        if wallet_orm is None:
            raise ValueError(f"coin wallet not found: {account_id}")

        existing = await self._session.execute(
            select(CoinTransactionORM).where(
                CoinTransactionORM.account_id == account_id,
                CoinTransactionORM.type == tx_enum,
                CoinTransactionORM.ref == ref,
            )
        )
        if existing.scalar_one_or_none() is not None:
            return wallet_orm.balance

        lot_orms: dict[int, CoinLotORM] = {}
        for draw in plan.draws:
            if draw.lot_id not in lot_orms:
                orm = await self._get_lot_orm(draw.lot_id)
                if orm is None:
                    raise ValueError(f"coin lot not found: {draw.lot_id}")
                lot_orms[draw.lot_id] = orm
            lot_orms[draw.lot_id].remaining_amount -= draw.amount

        wallet_orm.balance -= plan.total
        self._session.add(
            CoinTransactionORM(
                account_id=account_id,
                type=tx_enum,
                delta=-plan.total,
                lot_id=None,
                ref=ref,
                balance_after=wallet_orm.balance,
            )
        )

        await self._session.flush()
        return wallet_orm.balance

    async def expire_stale_lots(self, account_id: int, now: datetime) -> int:
        """만료된 ACTIVE lot -> EXPIRED(remaining=0) + EXPIRE tx(봉투당) + balance 차감.

        이 메서드는 항상 wallet 행 락을 보유한 상태에서만 호출된다(spend/sweep).
        balance 는 절대값 대입이 아니라 상대 SQL 차감(``balance = balance - freed``)
        으로 갱신해, 동일 트랜잭션 내 여러 봉투 만료가 합성(compose)되게 한다.
        lot 전이는 ``WHERE id AND status=='ACTIVE'`` 로 가드해, 이미 만료된 lot을
        재차 EXPIRE 하지 않는다(rowcount!=1 이면 skip).
        """
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
        running = wallet_orm.balance if wallet_orm is not None else 0

        for lot_orm in stale:
            freed = lot_orm.remaining_amount
            transitioned = cast(
                "CursorResult[Any]",
                await self._session.execute(
                    update(CoinLotORM)
                    .where(CoinLotORM.id == lot_orm.id, CoinLotORM.status == "ACTIVE")
                    .values(status="EXPIRED", remaining_amount=0)
                ),
            )
            if transitioned.rowcount != 1:
                # 동시 writer가 이미 만료 처리 — 이중 EXPIRE/이중 차감 방지
                continue
            if wallet_orm is not None and freed > 0:
                running -= freed
                await self._session.execute(
                    update(CoinWalletORM)
                    .where(CoinWalletORM.account_id == account_id)
                    .values(balance=CoinWalletORM.balance - freed)
                )
                self._session.add(
                    CoinTransactionORM(
                        account_id=account_id,
                        type=TransactionType.EXPIRE,
                        delta=-freed,
                        lot_id=lot_orm.id,
                        ref=None,  # 배치 만료 — 외부 idempotency key 없음
                        balance_after=running,
                    )
                )

        await self._session.flush()
        if wallet_orm is not None:
            # Core update()로 DB balance만 상대 차감했으므로 identity-map의
            # in-memory balance는 아직 옛 값이다. 만료된다(expire). 뒤이어
            # apply_spend가 같은 wallet_orm.balance를 읽을 때 차감 반영본을
            # 재로딩하도록 강제해, 만료 차감이 spend에 의해 덮어써지지 않게 한다.
            self._session.expire(wallet_orm, ["balance"])
        return running

    async def accounts_with_stale_lots(self, now: datetime) -> list[int]:
        """만료 대상(ACTIVE + expires_at 통과) lot이 하나라도 있는 account_id 목록."""
        result = await self._session.execute(
            select(CoinLotORM.account_id)
            .where(
                CoinLotORM.status == "ACTIVE",
                CoinLotORM.expires_at.is_not(None),
                CoinLotORM.expires_at <= now,
            )
            .distinct()
        )
        return [row for row in result.scalars().all()]
