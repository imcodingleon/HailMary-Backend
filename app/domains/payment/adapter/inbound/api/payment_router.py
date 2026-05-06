from fastapi import APIRouter, Depends, HTTPException, status

from app.domains.payment.application.request.confirm_payment_request import (
    ConfirmPaymentRequest,
)
from app.domains.payment.application.response.payment_response import PaymentResponse
from app.domains.payment.application.usecase.confirm_payment_usecase import (
    ConfirmPaymentUseCase,
)
from app.domains.payment.domain.port.payment_gateway_port import PaymentGatewayError

router = APIRouter(prefix="/api/payments", tags=["payments"])


# main.py에서 dependency_overrides로 교체된다.
def get_confirm_payment_usecase() -> ConfirmPaymentUseCase:
    raise NotImplementedError


@router.post(
    "/confirm",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def confirm_payment(
    body: ConfirmPaymentRequest,
    usecase: ConfirmPaymentUseCase = Depends(get_confirm_payment_usecase),
) -> PaymentResponse:
    try:
        return await usecase.execute(body)
    except PaymentGatewayError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"code": e.code or "PAYMENT_GATEWAY_ERROR", "message": str(e)},
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
