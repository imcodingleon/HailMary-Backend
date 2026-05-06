from datetime import datetime, timezone

from app.domains.payment.application.request.confirm_payment_request import (
    ConfirmPaymentRequest,
)
from app.domains.payment.application.response.payment_response import PaymentResponse
from app.domains.payment.domain.entity.payment import Payment
from app.domains.payment.domain.port.payment_gateway_port import (
    PaymentGatewayError,
    PaymentGatewayPort,
)
from app.domains.payment.domain.port.payment_repository_port import (
    PaymentRepositoryPort,
)
from app.domains.payment.domain.value_object.payment_status import PaymentStatus


class ConfirmPaymentUseCase:
    def __init__(
        self,
        gateway: PaymentGatewayPort,
        repo: PaymentRepositoryPort,
    ) -> None:
        self._gateway = gateway
        self._repo = repo

    async def execute(self, request: ConfirmPaymentRequest) -> PaymentResponse:
        # 1. 동일 orderId 중복 승인 방지 — idempotent
        existing = await self._repo.find_by_order_id(request.order_id)
        if existing is not None:
            return _to_response(existing)

        # 2. 토스 결제 승인 호출
        result = await self._gateway.confirm(
            payment_key=request.payment_key,
            order_id=request.order_id,
            amount=request.amount,
        )

        # 3. 응답 검증 — 금액 위변조 방지
        approved_amount = _read_amount(result)
        if approved_amount != request.amount:
            raise PaymentGatewayError(
                f"결제 금액 불일치: 요청={request.amount}, 승인={approved_amount}",
                code="AMOUNT_MISMATCH",
            )

        status_str = str(result.get("status", "")).upper()
        try:
            status = PaymentStatus(status_str)
        except ValueError:
            raise PaymentGatewayError(
                f"알 수 없는 결제 상태: {status_str}",
                code="UNKNOWN_STATUS",
            ) from None

        approved_at_str = result.get("approvedAt")
        approved_at = (
            _parse_iso8601(approved_at_str)
            if isinstance(approved_at_str, str)
            else datetime.now(timezone.utc)
        )

        # 4. 도메인 엔티티 → 영속화
        payment = Payment.from_approval(
            payment_key=request.payment_key,
            order_id=request.order_id,
            character=request.character,
            amount=request.amount,
            status=status,
            customer_email=request.customer_email,
            approved_at=approved_at,
        )
        saved = await self._repo.save(payment)
        return _to_response(saved)


def _read_amount(result: dict) -> int:  # type: ignore[type-arg]
    """토스 응답의 totalAmount 우선, 없으면 amount.value, 없으면 0."""
    total = result.get("totalAmount")
    if isinstance(total, int):
        return total
    if isinstance(total, str) and total.isdigit():
        return int(total)
    nested = result.get("amount")
    if isinstance(nested, dict):
        v = nested.get("value")
        if isinstance(v, int):
            return v
        if isinstance(v, str) and v.isdigit():
            return int(v)
    return 0


def _parse_iso8601(value: str) -> datetime:
    """토스 approvedAt은 ISO8601 with offset (예: 2024-01-01T12:00:00+09:00)."""
    return datetime.fromisoformat(value)


def _to_response(payment: Payment) -> PaymentResponse:
    return PaymentResponse(
        paymentKey=payment.payment_key,
        orderId=payment.order_id,
        character=payment.character.value,
        amount=payment.amount,
        status=payment.status.value,
        approvedAt=payment.approved_at,
        expiresAt=payment.expires_at,
    )
