from datetime import UTC, datetime
from typing import Protocol

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


class PaidReportCreatorPort(Protocol):
    """결제 confirm 직후 호출되는 PaidReport 생성 hook.

    AI 도메인 의존성 역전: payment 도메인은 ai 도메인을 import하지 않는다.
    main.py에서 CreatePaidReportUseCase를 어댑터로 주입한다.
    """

    async def execute(self, *, order_id: str, saju_hash: str) -> object: ...


class SajuHashResolverPort(Protocol):
    """user_id로 사주 해시를 계산해 돌려주는 hook.

    Hexagonal 룰: payment 도메인은 user 도메인을 직접 import하지 않는다.
    main.py가 user_repo + saju_data_extractor + compute_saju_hash 묶음을 어댑터로 주입.
    user나 사주 결과가 없을 경우 None 반환.
    """

    async def resolve(self, user_id: int) -> str | None: ...


class ConfirmPaymentUseCase:
    def __init__(
        self,
        gateway: PaymentGatewayPort,
        repo: PaymentRepositoryPort,
        paid_report_creator: PaidReportCreatorPort | None = None,
        saju_hash_resolver: SajuHashResolverPort | None = None,
    ) -> None:
        self._gateway = gateway
        self._repo = repo
        self._paid_report_creator = paid_report_creator
        self._saju_hash_resolver = saju_hash_resolver

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
            else datetime.now(UTC)
        )

        # 4. 도메인 엔티티 → 영속화
        payment = Payment.from_approval(
            payment_key=request.payment_key,
            order_id=request.order_id,
            user_id=request.user_id,
            character=request.character,
            amount=request.amount,
            status=status,
            customer_email=request.customer_email,
            approved_at=approved_at,
        )
        saved = await self._repo.save(payment)

        # 5. 결제 확정 → PaidReport 자동 생성 트리거 (AI 도메인 hook).
        # saju_hash: resolver가 user_id로 진짜 해시 계산. 실패/미주입 시 order_id로 fallback
        # (캐시 hit 불가능하지만 기능은 유지).
        if self._paid_report_creator is not None:
            saju_hash: str | None = None
            if self._saju_hash_resolver is not None:
                saju_hash = await self._saju_hash_resolver.resolve(saved.user_id)
            await self._paid_report_creator.execute(
                order_id=saved.order_id,
                saju_hash=saju_hash or saved.order_id,
            )

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
        payment_key=payment.payment_key,
        order_id=payment.order_id,
        character=payment.character.value,
        amount=payment.amount,
        status=payment.status.value,
        approved_at=payment.approved_at,
        expires_at=payment.expires_at,
    )
