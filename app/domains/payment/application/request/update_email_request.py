from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UpdateEmailRequest(BaseModel):
    """결제 완료 후 이메일 수정 요청. orderId + 새 이메일만 받음."""

    model_config = ConfigDict(populate_by_name=True)

    order_id: str = Field(alias="orderId", min_length=1)
    new_email: EmailStr = Field(alias="newEmail")
