from dataclasses import dataclass
from datetime import datetime, timedelta

from app.domains.payment.domain.value_object.payment_status import (
    CharacterCode,
    PaymentMethod,
    PaymentStatus,
)

REVIEW_PERIOD_DAYS = 30


@dataclass
class Payment:
    """결제 도메인 엔티티 — 토스페이먼츠 승인 결과를 우리 도메인 표현으로."""

    payment_key: str
    order_id: str
    user_id: int
    character: CharacterCode
    amount: int
    status: PaymentStatus
    customer_email: str
    approved_at: datetime
    expires_at: datetime
    method: PaymentMethod | None = None
    easy_pay_provider: str | None = None
    card_issuer_code: str | None = None
    bank_code: str | None = None
    id: int | None = None

    @classmethod
    def from_approval(
        cls,
        *,
        payment_key: str,
        order_id: str,
        user_id: int,
        character: CharacterCode,
        amount: int,
        status: PaymentStatus,
        customer_email: str,
        approved_at: datetime,
        method: PaymentMethod | None = None,
        easy_pay_provider: str | None = None,
        card_issuer_code: str | None = None,
        bank_code: str | None = None,
    ) -> "Payment":
        return cls(
            payment_key=payment_key,
            order_id=order_id,
            user_id=user_id,
            character=character,
            amount=amount,
            status=status,
            customer_email=customer_email,
            approved_at=approved_at,
            expires_at=approved_at + timedelta(days=REVIEW_PERIOD_DAYS),
            method=method,
            easy_pay_provider=easy_pay_provider,
            card_issuer_code=card_issuer_code,
            bank_code=bank_code,
        )

    def is_active(self, now: datetime) -> bool:
        return self.status == PaymentStatus.DONE and now < self.expires_at
