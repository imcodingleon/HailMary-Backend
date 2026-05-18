from fastapi import APIRouter, Depends, HTTPException, status

from app.domains.ai.application.response.paid_report_response import (
    PaidReportResponse,
    PaidReportStatusResponse,
    PaidUserPropertiesResponse,
)
from app.domains.ai.application.usecase.get_paid_report_usecase import (
    GetPaidReportUseCase,
    PaidReportExpiredError,
    PaidReportNotFoundError,
)
from app.domains.user.domain.entity.user import User
from app.domains.user.domain.service import pii_redaction

router = APIRouter(prefix="/api/saju/paid", tags=["paid-report"])
# 재접속 토큰(share_code) 기반 진입점 — order_id 노출 없이 결과지 조회.
share_router = APIRouter(prefix="/api/saju/result", tags=["paid-report-share"])


# main.py에서 dependency_overrides로 교체된다.
def get_paid_report_usecase() -> GetPaidReportUseCase:
    raise NotImplementedError


def _build_user_properties(
    user: User | None, customer_email: str
) -> PaidUserPropertiesResponse | None:
    """User + Payment.customer_email → Amplitude user property DTO 매핑.

    User 조회 실패 시 None 반환 (결과지 응답은 막지 않음).
    """
    if user is None or user.id is None:
        return None
    # Amplitude 는 user_id 최소 5자 요구 → "usr_" prefix 로 패딩 (User.id 가 작은 정수여도 안전).
    return PaidUserPropertiesResponse(
        user_id=f"usr_{user.id}",
        user_nickname=None,  # User.nickname 도입 시 채움
        user_name_initial=pii_redaction.name_initial(user.name),
        user_email_domain=pii_redaction.email_domain(customer_email),
        user_email_hash=pii_redaction.email_hash(customer_email),
        birth_year=pii_redaction.birth_year(user.birth_info.birth_date),
        age_group=pii_redaction.age_group(user.birth_info.birth_date),
        birth_branch=pii_redaction.birth_branch(user.birth_info.birth_time),
        gender=pii_redaction.gender_code(user.gender),
    )


@router.get("/{order_id}/status", response_model=PaidReportStatusResponse)
async def get_status(
    order_id: str,
    usecase: GetPaidReportUseCase = Depends(get_paid_report_usecase),
) -> PaidReportStatusResponse:
    try:
        report, _payment, _user = await usecase.execute(order_id)
    except PaidReportNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="paid report not found",
        ) from e
    except PaidReportExpiredError:
        # status 조회는 만료여도 정보 자체는 알려줌. (410은 본문 조회에서만)
        return PaidReportStatusResponse(status="expired")
    return PaidReportStatusResponse(status=report.status.value)


@router.get("/{order_id}", response_model=PaidReportResponse)
async def get_report(
    order_id: str,
    usecase: GetPaidReportUseCase = Depends(get_paid_report_usecase),
) -> PaidReportResponse:
    try:
        report, payment, user = await usecase.execute(order_id)
    except PaidReportNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="paid report not found",
        ) from e
    except PaidReportExpiredError as e:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="paid report expired",
        ) from e
    # chapters는 dict[str, dict] 형식으로 저장됨 (PaidChaptersResponse.model_dump 결과).
    # Pydantic이 nested dict를 PaidChaptersResponse로 자동 역직렬화.
    return PaidReportResponse(
        order_id=report.order_id,
        status=report.status.value,
        chapters=report.chapters,
        expires_at=payment.expires_at,
        character=payment.character.value,
        user=_build_user_properties(user, payment.customer_email),
    )


# ─────────────────────────────────────────────────────────────────────
# share_code 기반 엔드포인트 — 이메일 링크 재접속용
# ─────────────────────────────────────────────────────────────────────


@share_router.get("/{share_code}/status", response_model=PaidReportStatusResponse)
async def get_status_by_share(
    share_code: str,
    usecase: GetPaidReportUseCase = Depends(get_paid_report_usecase),
) -> PaidReportStatusResponse:
    try:
        report, _payment, _user = await usecase.execute_by_share_code(share_code)
    except PaidReportNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="paid report not found",
        ) from e
    except PaidReportExpiredError:
        return PaidReportStatusResponse(status="expired")
    return PaidReportStatusResponse(status=report.status.value)


@share_router.get("/{share_code}", response_model=PaidReportResponse)
async def get_report_by_share(
    share_code: str,
    usecase: GetPaidReportUseCase = Depends(get_paid_report_usecase),
) -> PaidReportResponse:
    try:
        report, payment, user = await usecase.execute_by_share_code(share_code)
    except PaidReportNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="paid report not found",
        ) from e
    except PaidReportExpiredError as e:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="paid report expired",
        ) from e
    return PaidReportResponse(
        order_id=report.order_id,
        status=report.status.value,
        chapters=report.chapters,
        expires_at=payment.expires_at,
        character=payment.character.value,
        user=_build_user_properties(user, payment.customer_email),
    )
