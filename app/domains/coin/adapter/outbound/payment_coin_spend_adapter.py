"""payment 도메인 CoinSpendPort 어댑터 (도화선 2.0 P4 Unit B).

payment 도메인은 coin 도메인을 직접 import하지 않는다 — CoinSpendPort(Protocol)만 알고,
실제 소진 로직(SpendCoinsUseCase)은 이 어댑터가 감싸서 main.py DI에서 주입한다.
"""

from __future__ import annotations

from app.domains.coin.application.usecase.spend_coins_usecase import SpendCoinsUseCase


class PaymentCoinSpendAdapter:
    """CoinSpendPort 구현 — SpendCoinsUseCase.spend 위임."""

    def __init__(self, usecase: SpendCoinsUseCase) -> None:
        self._usecase = usecase

    async def spend(self, account_id: int, cost: int, ref: str) -> int:
        return await self._usecase.spend(account_id, cost, ref)
