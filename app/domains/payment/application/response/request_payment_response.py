from pydantic import BaseModel, ConfigDict, Field


class RequestPaymentResponse(BaseModel):
    """BE → FE. FE는 payurl로 리다이렉트하면 됨."""

    model_config = ConfigDict(populate_by_name=True)

    order_id: str = Field(alias="orderId")
    payurl: str
