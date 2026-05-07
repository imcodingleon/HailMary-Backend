"""SajuHashResolverPort 구현체.

payment 도메인이 user 도메인을 직접 import하지 않도록 application 레이어 Port에서
역전된 의존성을, 어댑터 레이어에서 user 도메인 객체와 묶어 제공한다.

- user_repo로 user 조회 (없으면 None)
- saju_result_repo로 사주 raw 조회 (없으면 None)
- compute_saju_hash 호출 (개인정보 hash 결과만 사용)

캐시 hit 키이므로 같은 사주 → 같은 hash → 30일 내 재결제 시 AI 호출 0회.
"""

from app.domains.ai.domain.service.saju_hash import compute_saju_hash
from app.domains.payment.application.usecase.confirm_payment_usecase import (
    SajuHashResolverPort,
)
from app.domains.user.domain.port.saju_result_repository_port import (
    SajuResultRepositoryPort,
)
from app.domains.user.domain.port.user_repository_port import UserRepositoryPort


class SajuHashResolver(SajuHashResolverPort):
    def __init__(
        self,
        *,
        user_repo: UserRepositoryPort,
        saju_result_repo: SajuResultRepositoryPort,
    ) -> None:
        self._user_repo = user_repo
        self._saju_result_repo = saju_result_repo

    async def resolve(self, user_id: int) -> str | None:
        user = await self._user_repo.find_by_id(user_id)
        if user is None:
            return None

        saju_result = await self._saju_result_repo.find_by_user_id(user_id)
        if saju_result is None:
            return None

        birth_time = user.birth_info.birth_time_str() or "unknown"
        return compute_saju_hash(
            birth_date=user.birth_info.birth_date.strftime("%Y-%m-%d"),
            birth_time=birth_time,
            name=user.name,
            gender=user.gender.value,
            calendar_type=user.birth_info.calendar_type.value,
        )
