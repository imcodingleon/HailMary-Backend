"""ConfirmPaymentUseCase 핵심 분기 단위 테스트.

대상 분기:
    1. Idempotent — 동일 orderId 중복 승인 방지 (gateway 호출 없이 기존 결과 반환)
    2. AMOUNT_MISMATCH — 게이트웨이 응답 금액이 요청 금액과 다르면 PaymentGatewayError
    3. UNKNOWN_STATUS — 게이트웨이 응답 status가 PaymentStatus enum에 없으면 PaymentGatewayError

Mock 전략: 표준 라이브러리 unittest.mock 대신 Port 직접 구현 fake. 의도가 명확하다.
"""

from datetime import UTC, datetime
from typing import Any

import pytest

from app.domains.payment.application.request.confirm_payment_request import (
    ConfirmPaymentRequest,
)
from app.domains.payment.application.usecase.confirm_payment_usecase import (
    ConfirmPaymentUseCase,
)
from app.domains.payment.domain.entity.payment import Payment
from app.domains.payment.domain.port.payment_gateway_port import (
    PaymentGatewayError,
    PaymentGatewayPort,
)
from app.domains.payment.domain.port.payment_repository_port import (
    PaymentRepositoryPort,
)
from app.domains.payment.domain.value_object.payment_status import (
    CharacterCode,
    PaymentStatus,
)

# ── Test fakes ────────────────────────────────────────────────────────────────


class FakePaymentRepository(PaymentRepositoryPort):
    """In-memory PaymentRepository — order_id로 조회/저장."""

    def __init__(self) -> None:
        self._by_order_id: dict[str, Payment] = {}
        self.save_calls: list[Payment] = []

    async def save(self, payment: Payment) -> Payment:
        self.save_calls.append(payment)
        # 운영 코드에서 id가 채워지는 시점을 흉내 — 첫 저장이면 1 부여.
        saved = Payment(
            payment_key=payment.payment_key,
            order_id=payment.order_id,
            user_id=payment.user_id,
            character=payment.character,
            amount=payment.amount,
            status=payment.status,
            customer_email=payment.customer_email,
            approved_at=payment.approved_at,
            expires_at=payment.expires_at,
            id=payment.id or len(self._by_order_id) + 1,
        )
        self._by_order_id[payment.order_id] = saved
        return saved

    async def find_by_order_id(self, order_id: str) -> Payment | None:
        return self._by_order_id.get(order_id)

    async def find_by_payment_key(self, payment_key: str) -> Payment | None:
        for p in self._by_order_id.values():
            if p.payment_key == payment_key:
                return p
        return None

    def seed(self, payment: Payment) -> None:
        """기존 결제 row를 미리 심는다 (idempotent 테스트용)."""
        self._by_order_id[payment.order_id] = payment


class FakePaymentGateway(PaymentGatewayPort):
    """가짜 게이트웨이 — confirm 호출 시 미리 세팅한 응답을 반환한다."""

    def __init__(self, response: dict[str, Any]) -> None:
        self._response = response
        self.confirm_calls: list[dict[str, Any]] = []

    async def confirm(
        self,
        *,
        payment_key: str,
        order_id: str,
        amount: int,
    ) -> dict[str, Any]:
        self.confirm_calls.append(
            {"payment_key": payment_key, "order_id": order_id, "amount": amount}
        )
        return self._response


# ── Helpers ───────────────────────────────────────────────────────────────────


def _request(
    *,
    order_id: str = "ORDER-001",
    payment_key: str = "PKEY-ABC",
    user_id: int = 42,
    amount: int = 19900,
    character: CharacterCode = CharacterCode.YEONWOO,
    customer_email: str = "buyer@example.com",
) -> ConfirmPaymentRequest:
    return ConfirmPaymentRequest(
        payment_key=payment_key,
        order_id=order_id,
        user_id=user_id,
        amount=amount,
        character=character,
        customer_email=customer_email,
    )


def _existing_payment(
    *,
    order_id: str = "ORDER-001",
    payment_key: str = "PKEY-ABC",
    user_id: int = 42,
    amount: int = 19900,
) -> Payment:
    approved_at = datetime(2026, 5, 1, 12, 0, 0, tzinfo=UTC)
    return Payment.from_approval(
        payment_key=payment_key,
        order_id=order_id,
        user_id=user_id,
        character=CharacterCode.YEONWOO,
        amount=amount,
        status=PaymentStatus.DONE,
        customer_email="buyer@example.com",
        approved_at=approved_at,
    )


# ── Tests ─────────────────────────────────────────────────────────────────────


async def test_idempotent_returns_existing_without_gateway_call() -> None:
    """동일 orderId가 이미 저장돼 있으면 gateway를 호출하지 않고 기존 결과를 반환한다."""

    request = _request(order_id="ORDER-DUP", amount=19900)
    existing = _existing_payment(order_id="ORDER-DUP", amount=19900)

    repo = FakePaymentRepository()
    repo.seed(existing)
    gateway = FakePaymentGateway(response={})  # 호출되면 안 되므로 응답 무관
    usecase = ConfirmPaymentUseCase(gateway=gateway, repo=repo)

    response = await usecase.execute(request)

    assert gateway.confirm_calls == [], "기존 결제가 있으면 gateway.confirm 호출 금지"
    assert repo.save_calls == [], "기존 결제가 있으면 save 호출 금지"
    assert response.order_id == existing.order_id
    assert response.payment_key == existing.payment_key
    assert response.amount == existing.amount
    assert response.status == existing.status.value


async def test_amount_mismatch_raises_payment_gateway_error() -> None:
    """게이트웨이가 승인한 금액이 요청 금액과 다르면 AMOUNT_MISMATCH 에러."""

    request = _request(amount=19900)
    repo = FakePaymentRepository()
    gateway = FakePaymentGateway(
        response={
            "status": "DONE",
            "totalAmount": 100,  # 위변조 흉내 — 요청 19900 vs 승인 100
            "approvedAt": "2026-05-01T12:00:00+09:00",
        }
    )
    usecase = ConfirmPaymentUseCase(gateway=gateway, repo=repo)

    with pytest.raises(PaymentGatewayError) as exc_info:
        await usecase.execute(request)

    assert exc_info.value.code == "AMOUNT_MISMATCH"
    assert repo.save_calls == [], "금액 불일치 시 save 호출 금지"


async def test_unknown_status_raises_payment_gateway_error() -> None:
    """게이트웨이가 PaymentStatus enum에 없는 status 값을 반환하면 UNKNOWN_STATUS 에러."""

    request = _request(amount=19900)
    repo = FakePaymentRepository()
    gateway = FakePaymentGateway(
        response={
            "status": "MYSTERY_STATE",  # PaymentStatus enum에 없는 값
            "totalAmount": 19900,
            "approvedAt": "2026-05-01T12:00:00+09:00",
        }
    )
    usecase = ConfirmPaymentUseCase(gateway=gateway, repo=repo)

    with pytest.raises(PaymentGatewayError) as exc_info:
        await usecase.execute(request)

    assert exc_info.value.code == "UNKNOWN_STATUS"
    assert repo.save_calls == [], "알 수 없는 status 시 save 호출 금지"
