"""가입 지급 훅 포트 — auth 도메인이 coin 도메인 구현을 몰라도 되게 하는 경계.

SocialLoginUseCase/TestLoginUseCase는 이 Protocol만 알고, 실제 구현
(GrantSignupCoinsUseCase 어댑터)은 main.py DI에서 주입한다.
"""

from typing import Protocol


class SignupBonusPort(Protocol):
    async def grant(self, account_id: int) -> None: ...
