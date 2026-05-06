from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.payment.domain.entity.payment import Payment
from app.domains.payment.domain.port.payment_repository_port import (
    PaymentRepositoryPort,
)
from app.domains.payment.infrastructure.mapper.payment_mapper import PaymentMapper
from app.domains.payment.infrastructure.orm.payment_orm import PaymentORM


class PaymentRepository(PaymentRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, payment: Payment) -> Payment:
        orm = PaymentMapper.to_orm(payment)
        self._session.add(orm)
        await self._session.flush()
        return PaymentMapper.to_entity(orm)

    async def find_by_order_id(self, order_id: str) -> Payment | None:
        result = await self._session.execute(
            select(PaymentORM).where(PaymentORM.order_id == order_id),
        )
        orm = result.scalar_one_or_none()
        return PaymentMapper.to_entity(orm) if orm else None

    async def find_by_payment_key(self, payment_key: str) -> Payment | None:
        result = await self._session.execute(
            select(PaymentORM).where(PaymentORM.payment_key == payment_key),
        )
        orm = result.scalar_one_or_none()
        return PaymentMapper.to_entity(orm) if orm else None
