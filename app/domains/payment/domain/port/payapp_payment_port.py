from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class PayAppRequestResult:
    """PayApp payrequest 응답 — 클라이언트 → BE → FE 로 전달되는 결제 페이지 정보."""

    mul_no: str
    payurl: str


class PayAppGatewayError(Exception):
    """PayApp API 호출 실패. PayApp 에러 코드(errno) 포함."""

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        self.code = code


class PayAppPaymentPort(ABC):
    """PayApp 결제 게이트웨이 추상화.

    PayApp 플로:
    1. BE → payrequest API → 결제 페이지 URL(payurl) 수신
    2. FE는 payurl로 리다이렉트 → 사용자 결제
    3. PayApp → BE feedback webhook 으로 결제 상태 통보 (별도 endpoint)
    """

    @abstractmethod
    async def request_payment(
        self,
        *,
        order_id: str,
        amount: int,
        goods_name: str,
        recv_phone: str,
        recv_email: str | None = None,
    ) -> PayAppRequestResult:
        """결제 요청. 성공 시 mul_no + payurl, 실패 시 PayAppGatewayError."""
        ...

    @abstractmethod
    async def cancel_payment(
        self,
        *,
        mul_no: str,
        cancel_memo: str | None = None,
    ) -> None:
        """정산 전 전액 결제 취소. 실패 시 PayAppGatewayError."""
        ...
