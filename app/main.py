from collections.abc import AsyncGenerator

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.user.adapter.inbound.api.user_router import (
    get_free_result_usecase,
    get_submit_survey_usecase,
    get_submit_user_info_usecase,
)
from app.domains.user.adapter.inbound.api.user_router import (
    router as user_router,
)
from app.domains.user.adapter.outbound.persistence.saju_result_repository import (
    SajuResultRepository,
)
from app.domains.user.adapter.outbound.persistence.survey_repository import SurveyRepository
from app.domains.user.adapter.outbound.persistence.user_repository import UserRepository
from app.domains.user.application.usecase.get_free_result_usecase import GetFreeResultUseCase
from app.domains.user.application.usecase.submit_survey_usecase import SubmitSurveyUseCase
from app.domains.user.application.usecase.submit_user_info_usecase import SubmitUserInfoUseCase
from app.domains.user.domain.service.blocking_service import BlockingService
from app.domains.user.domain.service.charm_service import CharmService
from app.domains.user.domain.service.monthly_romance_flow_service import MonthlyRomanceFlowService
from app.domains.user.domain.service.saju_data_extractor import SajuDataExtractor
from app.domains.user.domain.service.spouse_avoid_service import SpouseAvoidService
from app.domains.user.domain.service.spouse_match_service import SpouseMatchService
from app.domains.user.infrastructure.fortuneteller_adapter import FortuneTellerAdapter
from app.infrastructure.config.settings import get_settings
from app.infrastructure.database.session import AsyncSessionLocal
from app.infrastructure.external.fortuneteller.client import FortuneTellerClient

app = FastAPI(title="HailMary Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_settings = get_settings()


# ── DB 세션 ──────────────────────────────────────────────────────────────────

async def _get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session, session.begin():
        yield session


# ── FortuneTeller ─────────────────────────────────────────────────────────────

def _get_ft_adapter() -> FortuneTellerAdapter:
    return FortuneTellerAdapter(FortuneTellerClient(base_url=_settings.fortuneteller_url))


# ── User Domain UseCase 팩토리 ────────────────────────────────────────────────

def _make_submit_user_info_usecase(
    session: AsyncSession = Depends(_get_session),
    ft: FortuneTellerAdapter = Depends(_get_ft_adapter),
) -> SubmitUserInfoUseCase:
    return SubmitUserInfoUseCase(
        user_repo=UserRepository(session),
        saju_result_repo=SajuResultRepository(session),
        fortuneteller=ft,
        saju_data_extractor=SajuDataExtractor(),
        charm_service=CharmService(),
        blocking_service=BlockingService(),
        spouse_avoid_service=SpouseAvoidService(),
        spouse_match_service=SpouseMatchService(),
        monthly_romance_flow_service=MonthlyRomanceFlowService(),
    )


def _make_submit_survey_usecase(
    session: AsyncSession = Depends(_get_session),
) -> SubmitSurveyUseCase:
    return SubmitSurveyUseCase(
        user_repo=UserRepository(session),
        survey_repo=SurveyRepository(session),
        saju_result_repo=SajuResultRepository(session),
    )


def _make_get_free_result_usecase(
    session: AsyncSession = Depends(_get_session),
) -> GetFreeResultUseCase:
    return GetFreeResultUseCase(
        saju_result_repo=SajuResultRepository(session),
        user_repo=UserRepository(session),
        charm_service=CharmService(),
        blocking_service=BlockingService(),
        spouse_avoid_service=SpouseAvoidService(),
        spouse_match_service=SpouseMatchService(),
        monthly_romance_flow_service=MonthlyRomanceFlowService(),
    )


# ── 의존성 오버라이드 ──────────────────────────────────────────────────────────

app.dependency_overrides[get_submit_user_info_usecase] = _make_submit_user_info_usecase
app.dependency_overrides[get_submit_survey_usecase] = _make_submit_survey_usecase
app.dependency_overrides[get_free_result_usecase] = _make_get_free_result_usecase

app.include_router(user_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
