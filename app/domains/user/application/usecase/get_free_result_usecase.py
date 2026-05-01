from app.domains.user.application.response.free_result_response import FreeResultResponse
from app.domains.user.application.saju_response_builder import build_free_result_response
from app.domains.user.domain.port.saju_result_repository_port import SajuResultRepositoryPort
from app.domains.user.domain.port.user_repository_port import UserRepositoryPort
from app.domains.user.domain.service.blocking_service import BlockingService
from app.domains.user.domain.service.charm_service import CharmService
from app.domains.user.domain.service.monthly_romance_flow_service import MonthlyRomanceFlowService
from app.domains.user.domain.service.spouse_avoid_service import SpouseAvoidService
from app.domains.user.domain.service.spouse_match_service import SpouseMatchService


class GetFreeResultUseCase:
    def __init__(
        self,
        saju_result_repo: SajuResultRepositoryPort,
        user_repo: UserRepositoryPort,
        charm_service: CharmService,
        blocking_service: BlockingService,
        spouse_avoid_service: SpouseAvoidService,
        spouse_match_service: SpouseMatchService,
        monthly_romance_flow_service: MonthlyRomanceFlowService,
    ) -> None:
        self._saju_result_repo = saju_result_repo
        self._user_repo = user_repo
        self._charm = charm_service
        self._blocking = blocking_service
        self._spouse_avoid = spouse_avoid_service
        self._spouse_match = spouse_match_service
        self._monthly_romance_flow = monthly_romance_flow_service

    async def execute(self, user_id: int) -> FreeResultResponse:
        result = await self._saju_result_repo.find_by_user_id(user_id)
        if result is None:
            raise ValueError(f"사주 결과가 없습니다: {user_id}")

        user = await self._user_repo.find_by_id(user_id)
        time_unknown = (
            user.birth_info.birth_time_unknown if user is not None else False
        )

        analysis_input = dict(result.fortuneteller_response)
        if user is not None:
            analysis_input.setdefault("gender", user.gender.value)

        return build_free_result_response(
            saju_request_id=user_id,
            saju_data=result.fortuneteller_response,
            charm=self._charm.calculate(analysis_input),
            blocking=self._blocking.calculate(analysis_input, time_unknown),
            spouse_avoid=self._spouse_avoid.calculate(analysis_input),
            spouse_match=self._spouse_match.calculate(analysis_input),
            monthly_romance_flow=self._monthly_romance_flow.calculate(analysis_input),
        )
