"""auth 도메인 SignupBonusPort 어댑터 (Task 7).

auth 도메인은 coin 도메인을 직접 import하지 않는다 — SignupBonusPort(Protocol)만 알고,
실제 지급 로직(GrantSignupCoinsUseCase)은 이 어댑터가 감싸서 main.py DI에서 주입한다.
"""

from __future__ import annotations

from app.domains.coin.application.usecase.grant_signup_coins_usecase import (
    GrantSignupCoinsUseCase,
)


class CoinSignupBonusAdapter:
    """SignupBonusPort 구현 — GrantSignupCoinsUseCase.grant 위임."""

    def __init__(self, usecase: GrantSignupCoinsUseCase) -> None:
        self._usecase = usecase

    async def grant(self, account_id: int) -> None:
        await self._usecase.grant(account_id)
