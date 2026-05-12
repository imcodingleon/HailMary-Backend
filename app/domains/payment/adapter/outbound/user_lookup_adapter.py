"""UserLookupPort 구현체.

payment 도메인이 user 도메인을 직접 import하지 않도록, application 레이어에서
역전된 의존성을 어댑터 레이어에서 user_repo와 묶어 제공한다.

- user_repo.find_by_session_token으로 user 조회 (없으면 None)
- 존재하면 user.id 반환
"""

from app.domains.payment.application.usecase.confirm_payment_usecase import (
    UserLookupPort,
)
from app.domains.user.domain.port.user_repository_port import UserRepositoryPort


class UserLookupAdapter(UserLookupPort):
    def __init__(self, *, user_repo: UserRepositoryPort) -> None:
        self._user_repo = user_repo

    async def find_user_id_by_session_token(self, token: str) -> int | None:
        user = await self._user_repo.find_by_session_token(token)
        if user is None or user.id is None:
            return None
        return user.id
