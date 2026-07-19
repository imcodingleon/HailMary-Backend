from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.domains.payment.application.request._amplitude_ids import (
    AmplitudeDeviceId,
    AmplitudeSessionId,
)
from app.domains.payment.domain.value_object.payment_status import CharacterCode


class SpendLoveReportRequest(BaseModel):
    """연애운 코인 해금 제출 요청. RedeemCouponRequest 에서 code 제외한 버전.

    account_id 는 body가 아니라 get_current_account_id(로그인 필수)로 얻는다 —
    쿠폰과 달리 코인 해금은 로그인 계정 전용(보관함 귀속 필수, 게스트 불가).
    """

    model_config = ConfigDict(populate_by_name=True)

    session_token: str = Field(alias="sessionToken", min_length=1)
    character: CharacterCode
    customer_email: EmailStr = Field(alias="customerEmail")
    # Amplitude 깔때기 조인용 (선택). 신뢰 경계 밖 — 범위 초과 시 절단/폐기(결제 비블록).
    device_id: AmplitudeDeviceId = Field(default=None, alias="deviceId")
    session_id: AmplitudeSessionId = Field(default=None, alias="sessionId")
