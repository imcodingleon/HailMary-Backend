from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.domains.payment.domain.value_object.payment_status import CharacterCode


class ConfirmPaymentRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    payment_key: str = Field(alias="paymentKey", min_length=1)
    order_id: str = Field(alias="orderId", min_length=1)
    user_id: int = Field(alias="userId", gt=0)
    amount: int = Field(gt=0)
    character: CharacterCode
    customer_email: EmailStr = Field(alias="customerEmail")
