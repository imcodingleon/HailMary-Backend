from abc import ABC, abstractmethod

from app.domains.payment.domain.entity.payment import Payment


class PaymentRepositoryPort(ABC):
    @abstractmethod
    async def save(self, payment: Payment) -> Payment: ...

    @abstractmethod
    async def find_by_order_id(self, order_id: str) -> Payment | None: ...

    @abstractmethod
    async def find_by_payment_key(self, payment_key: str) -> Payment | None: ...
