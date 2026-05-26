from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import PlainTextResponse

from app.domains.payment.application.request.dev_bypass_request import (
    DevBypassRequest,
)
from app.domains.payment.application.request.request_payment_request import (
    RequestPaymentRequest,
)
from app.domains.payment.application.request.update_email_request import (
    UpdateEmailRequest,
)
from app.domains.payment.application.response.payment_status_response import (
    PaymentStatusResponse,
)
from app.domains.payment.application.response.request_payment_response import (
    RequestPaymentResponse,
)
from app.domains.payment.application.usecase.dev_bypass_payment_usecase import (
    DevBypassPaymentUseCase,
)
from app.domains.payment.application.usecase.get_payment_status_usecase import (
    GetPaymentStatusUseCase,
)
from app.domains.payment.application.usecase.handle_payapp_feedback_usecase import (
    HandlePayAppFeedbackUseCase,
)
from app.domains.payment.application.usecase.request_payment_usecase import (
    RequestPaymentUseCase,
)
from app.domains.payment.application.usecase.update_email_and_resend_usecase import (
    UpdateEmailAndResendUseCase,
)
from app.domains.payment.domain.port.payapp_payment_port import PayAppGatewayError

router = APIRouter(prefix="/api/payments", tags=["payments"])


# main.py에서 dependency_overrides로 교체된다.
def get_request_payment_usecase() -> RequestPaymentUseCase:
    raise NotImplementedError


def get_handle_feedback_usecase() -> HandlePayAppFeedbackUseCase:
    raise NotImplementedError


def get_payment_status_usecase() -> GetPaymentStatusUseCase:
    raise NotImplementedError


def get_update_email_usecase() -> UpdateEmailAndResendUseCase:
    raise NotImplementedError


def get_dev_bypass_usecase() -> DevBypassPaymentUseCase:
    raise NotImplementedError


@router.post(
    "/request",
    response_model=RequestPaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def request_payment(
    body: RequestPaymentRequest,
    usecase: RequestPaymentUseCase = Depends(get_request_payment_usecase),
) -> RequestPaymentResponse:
    """PayApp 결제 요청. 응답의 payurl로 FE가 리다이렉트."""
    try:
        return await usecase.execute(body)
    except PayAppGatewayError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"code": e.code or "PAYAPP_GATEWAY_ERROR", "message": str(e)},
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post(
    "/feedback",
    response_class=PlainTextResponse,
)
async def payapp_feedback(
    request: Request,
    usecase: HandlePayAppFeedbackUseCase = Depends(get_handle_feedback_usecase),
) -> PlainTextResponse:
    """PayApp webhook 수신. 항상 'SUCCESS' 응답 (재시도 방지 위해 처리 실패도 SUCCESS).

    실패는 내부 로그만 남기고 사용자/PayApp에게는 SUCCESS 반환 — 잘못된 webhook은
    재시도해도 결과 동일하므로 재시도 의미 없음.
    """
    form = await request.form()
    form_dict = {k: v for k, v in form.items() if isinstance(v, str)}
    await usecase.execute(form_dict)
    return PlainTextResponse("SUCCESS", status_code=200)


@router.post("/update-email", status_code=status.HTTP_200_OK)
async def update_email(
    body: UpdateEmailRequest,
    usecase: UpdateEmailAndResendUseCase = Depends(get_update_email_usecase),
) -> dict[str, str]:
    """결제 완료 후 사용자가 결과지 받을 이메일을 수정한 경우.

    Payment.customer_email 업데이트 + 이미 합성된 PaidReport 있으면 새 주소로 메일 재발송.
    """
    try:
        await usecase.execute(order_id=body.order_id, new_email=body.new_email)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    return {"status": "updated"}


@router.get(
    "/status",
    response_model=PaymentStatusResponse,
)
async def get_payment_status(
    order_id: str,
    usecase: GetPaymentStatusUseCase = Depends(get_payment_status_usecase),
) -> PaymentStatusResponse:
    """FE polling: PayApp returnurl 도착 후 결제완료 webhook 처리 확인."""
    result = await usecase.execute(order_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="결제 정보를 찾을 수 없습니다.",
        )
    return result


# ⚠️ staging/local 전용 — main.py에서 app_env != "prod" 일 때만 include.
# 결제 단계를 건너뛰고 즉시 DONE 상태로 진입. QA 시 매번 실 결제 안 하기 위함.
dev_router = APIRouter(prefix="/api/payments/dev", tags=["payments-dev"])


@dev_router.post("/bypass", status_code=status.HTTP_201_CREATED)
async def dev_bypass_payment(
    body: DevBypassRequest,
    usecase: DevBypassPaymentUseCase = Depends(get_dev_bypass_usecase),
) -> dict[str, str]:
    """결제 통과 처리. FE는 응답의 orderId로 /saju/paid/{orderId}/loading 진입."""
    try:
        order_id = await usecase.execute(
            session_token=body.session_token,
            character=body.character,
            customer_email=body.customer_email,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    return {"orderId": order_id}
