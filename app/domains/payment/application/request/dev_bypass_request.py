from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.domains.payment.domain.value_object.payment_status import CharacterCode


class DevBypassRequest(BaseModel):
    """staging/local 결제 패스 요청. prod 환경에서는 endpoint 자체가 등록 X."""

    model_config = ConfigDict(populate_by_name=True)

    session_token: str = Field(alias="sessionToken", min_length=1)
    character: CharacterCode
    customer_email: EmailStr = Field(alias="customerEmail")
