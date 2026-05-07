from fastapi import APIRouter, Depends, HTTPException, status

from app.domains.ai.application.response.paid_report_response import (
    PaidReportResponse,
    PaidReportStatusResponse,
)
from app.domains.ai.application.usecase.get_paid_report_usecase import (
    GetPaidReportUseCase,
    PaidReportExpiredError,
    PaidReportNotFoundError,
)

router = APIRouter(prefix="/api/saju/paid", tags=["paid-report"])


# main.py에서 dependency_overrides로 교체된다.
def get_paid_report_usecase() -> GetPaidReportUseCase:
    raise NotImplementedError


@router.get("/{order_id}/status", response_model=PaidReportStatusResponse)
async def get_status(
    order_id: str,
    usecase: GetPaidReportUseCase = Depends(get_paid_report_usecase),
) -> PaidReportStatusResponse:
    try:
        report, _payment = await usecase.execute(order_id)
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
        report, payment = await usecase.execute(order_id)
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
    )
