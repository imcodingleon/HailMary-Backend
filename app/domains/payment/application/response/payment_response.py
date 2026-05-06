from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PaymentResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    payment_key: str = Field(alias="paymentKey")
    order_id: str = Field(alias="orderId")
    character: str
    amount: int
    status: str
    approved_at: datetime = Field(alias="approvedAt")
    expires_at: datetime = Field(alias="expiresAt")
