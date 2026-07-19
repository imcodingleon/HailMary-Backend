"""코인 잔액조회 라우터 (Task 7).

coin_enabled=True 일 때만 main.py 에서 include_router 된다. 미설정 시 라우터 자체가
등록되지 않아 /api/coins/* 는 404 (완전 차단).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.domains.auth.adapter.inbound.api.auth_router import get_current_account_id
from app.domains.coin.application.response.balance_response import BalanceResponse
from app.domains.coin.application.usecase.get_balance_usecase import GetBalanceUseCase

router = APIRouter(prefix="/api/coins", tags=["coin"])


# main.py에서 app.dependency_overrides로 교체된다.
def get_balance_usecase() -> GetBalanceUseCase:
    raise NotImplementedError


@router.get("/balance", response_model=BalanceResponse)
async def get_balance(
    account_id: int = Depends(get_current_account_id),
    usecase: GetBalanceUseCase = Depends(get_balance_usecase),
) -> BalanceResponse:
    return BalanceResponse(balance=await usecase.execute(account_id))
