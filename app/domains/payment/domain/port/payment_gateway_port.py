from abc import ABC, abstractmethod
from typing import Any


class PaymentGatewayError(Exception):
    """결제 게이트웨이(토스 등) 호출 실패. 메시지에 가능하면 게이트웨이 코드 포함."""

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        self.code = code


class PaymentGatewayPort(ABC):
    """결제 게이트웨이 추상화 — 토스/PayApp 등 구체 어댑터로 교체 가능."""

    @abstractmethod
    async def confirm(
        self,
        *,
        payment_key: str,
        order_id: str,
        amount: int,
    ) -> dict[str, Any]:
        """결제 승인 요청. 성공 시 게이트웨이 응답 dict 반환, 실패 시 PaymentGatewayError."""
        ...
