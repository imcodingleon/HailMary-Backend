from app.domains.user.application.request.submit_user_info_request import SubmitUserInfoRequest
from app.domains.user.application.response.free_result_response import FreeResultResponse
from app.domains.user.domain.entity.saju_result import SajuResult
from app.domains.user.domain.entity.user import User
from app.domains.user.domain.port.fortuneteller_port import FortuneTellerPort
from app.domains.user.domain.port.saju_result_repository_port import SajuResultRepositoryPort
from app.domains.user.domain.port.user_repository_port import UserRepositoryPort
from app.domains.user.domain.service.saju_data_extractor import SajuDataExtractor
from app.domains.user.domain.value_object.birth_info import BirthInfo


class SubmitUserInfoUseCase:
    def __init__(
        self,
        user_repo: UserRepositoryPort,
        saju_result_repo: SajuResultRepositoryPort,
        fortuneteller: FortuneTellerPort,
        saju_data_extractor: SajuDataExtractor,
    ) -> None:
        self._user_repo = user_repo
        self._saju_result_repo = saju_result_repo
        self._fortuneteller = fortuneteller
        self._extractor = saju_data_extractor

    async def execute(self, request: SubmitUserInfoRequest) -> FreeResultResponse:
        birth_info = BirthInfo(
            birth_date=request.birth_date(),
            calendar_type=request.calendar,
            birth_time=request.birth_time(),
            birth_time_unknown=request.birth_time() is None,
        )
        user = User(birth_info=birth_info, gender=request.gender, name=request.name)
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

        return FreeResultResponse(sajuRequestId=saved_user.id, sajuData=ft_response)
