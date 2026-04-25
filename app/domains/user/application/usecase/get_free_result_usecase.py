from app.domains.user.application.response.free_result_response import FreeResultResponse
from app.domains.user.domain.port.saju_result_repository_port import SajuResultRepositoryPort


class GetFreeResultUseCase:
    def __init__(self, saju_result_repo: SajuResultRepositoryPort) -> None:
        self._saju_result_repo = saju_result_repo

    async def execute(self, user_id: int) -> FreeResultResponse:
        result = await self._saju_result_repo.find_by_user_id(user_id)
        if result is None:
            raise ValueError(f"사주 결과가 없습니다: {user_id}")
        return FreeResultResponse(
            sajuRequestId=user_id,
            sajuData=result.fortuneteller_response,
        )
