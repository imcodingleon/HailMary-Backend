import secrets

from app.domains.user.application.request.submit_user_info_request import SubmitUserInfoRequest
from app.domains.user.application.response.free_result_response import FreeResultResponse
from app.domains.user.application.saju_response_builder import build_free_result_response
from app.domains.user.domain.entity.saju_result import SajuResult
from app.domains.user.domain.entity.user import User
from app.domains.user.domain.port.fortuneteller_port import FortuneTellerPort
from app.domains.user.domain.port.saju_result_repository_port import SajuResultRepositoryPort
from app.domains.user.domain.port.user_repository_port import UserRepositoryPort
from app.domains.user.domain.service.blocking_service import BlockingService
from app.domains.user.domain.service.charm_service import CharmService
from app.domains.user.domain.service.monthly_romance_flow_service import MonthlyRomanceFlowService
from app.domains.user.domain.service.saju_data_extractor import SajuDataExtractor
from app.domains.user.domain.service.spouse_avoid_service import SpouseAvoidService
from app.domains.user.domain.service.spouse_match_service import SpouseMatchService
from app.domains.user.domain.value_object.birth_info import BirthInfo


class SubmitUserInfoUseCase:
    def __init__(
        self,
        user_repo: UserRepositoryPort,
        saju_result_repo: SajuResultRepositoryPort,
        fortuneteller: FortuneTellerPort,
        saju_data_extractor: SajuDataExtractor,
        charm_service: CharmService,
        blocking_service: BlockingService,
        spouse_avoid_service: SpouseAvoidService,
        spouse_match_service: SpouseMatchService,
        monthly_romance_flow_service: MonthlyRomanceFlowService,
    ) -> None:
        self._user_repo = user_repo
        self._saju_result_repo = saju_result_repo
        self._fortuneteller = fortuneteller
        self._extractor = saju_data_extractor
        self._charm = charm_service
        self._blocking = blocking_service
        self._spouse_avoid = spouse_avoid_service
        self._spouse_match = spouse_match_service
        self._monthly_romance_flow = monthly_romance_flow_service

    async def execute(self, request: SubmitUserInfoRequest) -> FreeResultResponse:
        birth_info = BirthInfo(
            birth_date=request.birth_date(),
            calendar_type=request.calendar,
            birth_time=request.birth_time(),
            birth_time_unknown=request.birth_time() is None,
        )
        session_token = secrets.token_urlsafe(32)
        user = User(
            birth_info=birth_info,
            gender=request.gender,
            name=request.name,
            session_token=session_token,
            character_id=request.character_id,
        )
        saved_user = await self._user_repo.save(user)
        assert saved_user.id is not None

        saju_data = self._extractor.extract(saved_user)
        ft_response = await self._fortuneteller.analyze(saju_data)

        saju_result = SajuResult(
            user_id=saved_user.id,
            fortuneteller_request=saju_data,
            fortuneteller_response=ft_response,
        )
        await self._saju_result_repo.save(saju_result)

        time_unknown = birth_info.birth_time_unknown
        # FortuneTeller 응답의 gender 형식("M"/"남" 등)이 다를 수 있어 도메인 값("male"/"female")으로 강제.
        # spouse_avoid/match가 `gender == "male"`로 비교하므로 SSOT를 User 엔티티로 통일한다.
        analysis_input = dict(ft_response)
        analysis_input["gender"] = saved_user.gender.value

        return build_free_result_response(
            session_token=saved_user.session_token,
            saju_data=ft_response,
            charm=self._charm.calculate(analysis_input),
            blocking=self._blocking.calculate(analysis_input, time_unknown),
            spouse_avoid=self._spouse_avoid.calculate(analysis_input),
            spouse_match=self._spouse_match.calculate(analysis_input),
            monthly_romance_flow=self._monthly_romance_flow.calculate(analysis_input),
        )
