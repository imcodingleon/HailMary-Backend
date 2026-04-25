from fastapi import APIRouter, Depends, HTTPException, status

from app.infrastructure.external.fortuneteller.client import FortuneTellerError

from app.domains.user.application.request.submit_survey_request import SubmitSurveyRequest
from app.domains.user.application.request.submit_user_info_request import SubmitUserInfoRequest
from app.domains.user.application.response.free_result_response import FreeResultResponse
from app.domains.user.application.response.survey_response import SurveyResponse
from app.domains.user.application.usecase.get_free_result_usecase import GetFreeResultUseCase
from app.domains.user.application.usecase.submit_survey_usecase import SubmitSurveyUseCase
from app.domains.user.application.usecase.submit_user_info_usecase import SubmitUserInfoUseCase

router = APIRouter(prefix="/api/saju", tags=["saju"])


# main.py에서 app.dependency_overrides로 교체된다.
def get_submit_user_info_usecase() -> SubmitUserInfoUseCase:
    raise NotImplementedError


def get_submit_survey_usecase() -> SubmitSurveyUseCase:
    raise NotImplementedError


def get_free_result_usecase() -> GetFreeResultUseCase:
    raise NotImplementedError


@router.post("/free", response_model=FreeResultResponse, status_code=status.HTTP_201_CREATED)
async def submit_free(
    body: SubmitUserInfoRequest,
    usecase: SubmitUserInfoUseCase = Depends(get_submit_user_info_usecase),
) -> FreeResultResponse:
    try:
        return await usecase.execute(body)
    except FortuneTellerError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post("/survey", response_model=SurveyResponse, status_code=status.HTTP_201_CREATED)
async def submit_survey(
    body: SubmitSurveyRequest,
    usecase: SubmitSurveyUseCase = Depends(get_submit_survey_usecase),
) -> SurveyResponse:
    try:
        return await usecase.execute(body)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.get("/result/{saju_request_id}", response_model=FreeResultResponse)
async def get_free_result(
    saju_request_id: int,
    usecase: GetFreeResultUseCase = Depends(get_free_result_usecase),
) -> FreeResultResponse:
    try:
        return await usecase.execute(saju_request_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
