"""연애운 코인 해금 라우터 (도화선 2.0 P4 Unit B).

coin_enabled=True 일 때만 main.py 에서 include_router 된다. 미설정 시
/api/coins/spend/love-report 는 404 (완전 차단) — coin_router(잔액조회)와 동일 게이트.

payment 도메인 어댑터가 coin 도메인의 InsufficientCoinsError 를 import하는 것은
어댑터 계층 경계 교차로 허용된다(usecase는 CoinSpendPort만 알고 coin을 모른다).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.domains.auth.adapter.inbound.api.auth_router import get_current_account_id
from app.domains.coin.domain.error import InsufficientCoinsError
from app.domains.payment.application.request.spend_love_report_request import (
    SpendLoveReportRequest,
)
from app.domains.payment.application.usecase.spend_love_report_usecase import (
    SpendLoveReportUseCase,
)

router = APIRouter(prefix="/api/coins", tags=["coin"])


# main.py에서 app.dependency_overrides로 교체된다.
def get_spend_love_report_usecase() -> SpendLoveReportUseCase:
    raise NotImplementedError


@router.post("/spend/love-report", status_code=status.HTTP_201_CREATED)
async def spend_love_report(
    body: SpendLoveReportRequest,
    account_id: int = Depends(get_current_account_id),
    usecase: SpendLoveReportUseCase = Depends(get_spend_love_report_usecase),
) -> dict[str, str]:
    """코인 소진 + 무료 결과지 발급. 로그인 필수(401, get_current_account_id).

    잔액 부족 시 402. FE는 orderId로 결과 폴링 진입(쿠폰/일반결제와 동일 계약).
    """
    try:
        order_id = await usecase.execute(
            session_token=body.session_token,
            character=body.character,
            customer_email=body.customer_email,
            account_id=account_id,
            device_id=body.device_id,
            session_id=body.session_id,
        )
    except InsufficientCoinsError as e:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=str(e),
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    return {"orderId": order_id}
