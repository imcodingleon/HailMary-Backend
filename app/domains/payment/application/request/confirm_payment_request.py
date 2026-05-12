from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.domains.payment.domain.value_object.payment_status import CharacterCode


class ConfirmPaymentRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    payment_key: str = Field(alias="paymentKey", min_length=1)
    order_id: str = Field(alias="orderId", min_length=1)
    session_token: str = Field(alias="sessionToken", min_length=1)
    amount: int = Field(gt=0)
    character: CharacterCode
    customer_email: EmailStr = Field(alias="customerEmail")
    # Amplitude 깔때기 조인용 — 프론트가 amplitude.getDeviceId()/getSessionId() 동봉.
    # 누락이어도 confirm 동작에는 영향 없음. user_id 기반으로만 합류.
    device_id: str | None = Field(default=None, alias="deviceId")
    session_id: int | None = Field(default=None, alias="sessionId")
