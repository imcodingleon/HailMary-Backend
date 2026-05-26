from abc import ABC, abstractmethod
from datetime import datetime

from app.domains.payment.domain.entity.payment import Payment
from app.domains.payment.domain.value_object.payment_status import PaymentStatus


class PaymentRepositoryPort(ABC):
    @abstractmethod
    async def save(self, payment: Payment) -> Payment: ...

    @abstractmethod
    async def find_by_order_id(self, order_id: str) -> Payment | None: ...

    @abstractmethod
    async def find_by_payment_key(self, payment_key: str) -> Payment | None: ...

    @abstractmethod
    async def update_status(
        self,
        *,
        order_id: str,
        status: PaymentStatus,
        approved_at: datetime | None = None,
    ) -> Payment | None:
        """결제 상태 갱신 (PayApp webhook 처리용). 없으면 None 반환."""
        ...

    @abstractmethod
    async def update_customer_email(
        self,
        *,
        order_id: str,
        new_email: str,
    ) -> Payment | None:
        """결제 완료 후 사용자가 메일 수정 시 호출. 없으면 None 반환."""
        ...
