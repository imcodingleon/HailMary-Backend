from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.domains.payment.domain.value_object.payment_status import CharacterCode


class RequestPaymentRequest(BaseModel):
    """PayApp 결제 요청 — FE → BE.

    가격(amount)은 BE의 character_price 마스터가 결정. FE는 character + email 만 전달.
    orderId는 BE가 발급.
    """

    model_config = ConfigDict(populate_by_name=True)

    session_token: str = Field(alias="sessionToken", min_length=1)
    character: CharacterCode
    customer_email: EmailStr = Field(alias="customerEmail")
    # Amplitude 깔때기 조인용 (선택)
    device_id: str | None = Field(default=None, alias="deviceId")
    session_id: int | None = Field(default=None, alias="sessionId")
