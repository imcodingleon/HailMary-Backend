"""FE polling용 결제 상태 조회 UseCase."""

from __future__ import annotations

from app.domains.payment.application.response.payment_status_response import (
    PaymentStatusResponse,
)
from app.domains.payment.domain.port.payment_repository_port import (
    PaymentRepositoryPort,
)


class GetPaymentStatusUseCase:
    def __init__(self, repo: PaymentRepositoryPort) -> None:
        self._repo = repo

    async def execute(self, order_id: str) -> PaymentStatusResponse | None:
        payment = await self._repo.find_by_order_id(order_id)
        if payment is None:
            return None
        return PaymentStatusResponse(
            order_id=payment.order_id,
            status=payment.status.value,
            character=payment.character.value,
        )
