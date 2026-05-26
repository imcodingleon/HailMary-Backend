from pydantic import BaseModel, ConfigDict, Field


class PaymentStatusResponse(BaseModel):
    """FE polling 응답. PayApp 결제완료(webhook 수신) 여부 확인용."""

    model_config = ConfigDict(populate_by_name=True)

    order_id: str = Field(alias="orderId")
    # PaymentStatus enum 그대로 (READY/DONE/CANCELED/ABORTED/WAITING_FOR_DEPOSIT/PARTIAL_CANCELED)
    status: str
    character: str
