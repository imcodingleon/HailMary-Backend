from collections.abc import AsyncGenerator

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.ai.adapter.inbound.api.paid_report_router import (
    get_paid_report_usecase,
)
from app.domains.ai.adapter.inbound.api.paid_report_router import (
    router as paid_report_router,
)
from app.domains.ai.adapter.inbound.api.paid_report_router import (
    share_router as paid_report_share_router,
)
from app.domains.ai.adapter.outbound.external.claude_client import ClaudeClient
from app.domains.ai.adapter.outbound.persistence.paid_report_repository import (
    PaidReportRepository,
)
from app.domains.ai.application.usecase.compose_paid_report_usecase import (
    ComposePaidReportUseCase,
)
from app.domains.ai.application.usecase.create_paid_report_usecase import (
    CreatePaidReportUseCase,
)
from app.domains.ai.application.usecase.generate_p10_letter_usecase import (
    GenerateP10LetterUseCase,
)
from app.domains.ai.application.usecase.get_paid_report_usecase import (
    GetPaidReportUseCase,
)
from app.domains.ai.application.usecase.send_result_link_email_usecase import (
    SendResultLinkEmailUseCase,
)
from app.domains.payment.adapter.inbound.api.payment_router import (
    get_confirm_payment_usecase,
)
from app.domains.payment.adapter.inbound.api.payment_router import (
    router as payment_router,
)
from app.domains.payment.adapter.outbound.external.amplitude_adapter import (
    AmplitudeAnalyticsAdapter,
)
from app.domains.payment.adapter.outbound.external.toss_client import TossPaymentsClient
from app.domains.payment.adapter.outbound.persistence.payment_repository import (
    PaymentRepository,
)
from app.domains.payment.adapter.outbound.saju_hash_resolver import SajuHashResolver
from app.domains.payment.adapter.outbound.user_lookup_adapter import UserLookupAdapter
from app.domains.payment.application.usecase.confirm_payment_usecase import (
    ConfirmPaymentUseCase,
)
from app.domains.user.adapter.inbound.api.auth import get_user_repository
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
from app.infrastructure.external.amplitude.client import AmplitudeClient
from app.infrastructure.external.fortuneteller.client import FortuneTellerClient
from app.infrastructure.external.ses.client import SESClient

app = FastAPI(title="HailMary Backend", version="0.1.0")

_settings = get_settings()


def _allowed_origins() -> list[str]:
    # local/test 환경: localhost 프론트 dev 서버 + staging 도메인.
    if _settings.app_env in ("local", "test"):
        return [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "https://staging.dohwaseonsaju.com",
        ]
    return [
        "https://dohwaseonsaju.com",
        "https://www.dohwaseonsaju.com",
    ]


# CORSMiddleware는 main.py 가장 마지막에 add — Starlette 미들웨어는 LIFO라
# 가장 마지막 add가 가장 바깥(=모든 응답에 CORS 헤더 박힘). 이 위치에서 add 금지.


# ── DB 세션 ──────────────────────────────────────────────────────────────────

async def _get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session, session.begin():
        yield session


# ── FortuneTeller ─────────────────────────────────────────────────────────────

def _get_ft_adapter() -> FortuneTellerAdapter:
    return FortuneTellerAdapter(FortuneTellerClient(base_url=_settings.fortuneteller_url))


# ── 인증 의존성용 UserRepository 팩토리 ───────────────────────────────────────

def _make_user_repository(
    session: AsyncSession = Depends(_get_session),
) -> UserRepository:
    return UserRepository(session)


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
        survey_repo=SurveyRepository(session),
        saju_result_repo=SajuResultRepository(session),
    )


def _make_get_free_result_usecase(
    session: AsyncSession = Depends(_get_session),
) -> GetFreeResultUseCase:
    return GetFreeResultUseCase(
        saju_result_repo=SajuResultRepository(session),
        charm_service=CharmService(),
        blocking_service=BlockingService(),
        spouse_avoid_service=SpouseAvoidService(),
        spouse_match_service=SpouseMatchService(),
        monthly_romance_flow_service=MonthlyRomanceFlowService(),
    )


# ── Payment Domain UseCase 팩토리 ────────────────────────────────────────────

def _make_confirm_payment_usecase(
    session: AsyncSession = Depends(_get_session),
) -> ConfirmPaymentUseCase:
    if not _settings.toss_secret_key:
        raise RuntimeError("TOSS_SECRET_KEY 환경변수가 설정되지 않았습니다.")
    gateway = TossPaymentsClient(
        secret_key=_settings.toss_secret_key,
        base_url=_settings.toss_base_url,
    )
    paid_report_repo = PaidReportRepository(session)
    # P-10 AI 호출용 Claude 클라이언트 (키 있을 때만, 없으면 폴백)
    p10_letter_usecase: GenerateP10LetterUseCase | None = None
    if _settings.claude_api_key:
        claude_client = ClaudeClient(
            api_key=_settings.claude_api_key,
            model=_settings.claude_model,
        )
        p10_letter_usecase = GenerateP10LetterUseCase(ai_client=claude_client)
    # SES 이메일 발송 (sender + IAM 키 있을 때만, 없으면 폴백)
    email_sender: SendResultLinkEmailUseCase | None = None
    if _settings.aws_ses_sender:
        ses_client = SESClient(
            region=_settings.aws_region,
            sender=_settings.aws_ses_sender,
            access_key_id=_settings.aws_access_key_id,
            secret_access_key=_settings.aws_secret_access_key,
        )
        # 결과지 링크 base URL — 운영/테스트 분기
        base_url = (
            "http://localhost:3000"
            if _settings.app_env in ("local", "test")
            else "https://dohwaseonsaju.com"
        )
        email_sender = SendResultLinkEmailUseCase(
            ses_client=ses_client,
            base_url=base_url,
        )
    create_paid_report_usecase = CreatePaidReportUseCase(
        paid_report_repo=paid_report_repo,
        saju_result_repo=SajuResultRepository(session),
        survey_repo=SurveyRepository(session),
        compose_usecase=ComposePaidReportUseCase(),
        p10_letter_usecase=p10_letter_usecase,
        email_sender=email_sender,
    )
    user_repo = UserRepository(session)
    saju_hash_resolver = SajuHashResolver(
        user_repo=user_repo,
        saju_result_repo=SajuResultRepository(session),
    )
    user_lookup = UserLookupAdapter(user_repo=user_repo)
    analytics = AmplitudeAnalyticsAdapter(
        client=AmplitudeClient(
            api_key=_settings.amplitude_api_key,
            base_url=_settings.amplitude_base_url,
        ),
        environment=_settings.app_env,
    )
    return ConfirmPaymentUseCase(
        gateway=gateway,
        repo=PaymentRepository(session),
        user_lookup=user_lookup,
        paid_report_creator=create_paid_report_usecase,
        saju_hash_resolver=saju_hash_resolver,
        analytics=analytics,
    )


# ── AI Domain UseCase 팩토리 ──────────────────────────────────────────────────

def _make_get_paid_report_usecase(
    session: AsyncSession = Depends(_get_session),
) -> GetPaidReportUseCase:
    return GetPaidReportUseCase(
        paid_report_repo=PaidReportRepository(session),
        payment_repo=PaymentRepository(session),
    )


# ── 의존성 오버라이드 ──────────────────────────────────────────────────────────

app.dependency_overrides[get_user_repository] = _make_user_repository
app.dependency_overrides[get_submit_user_info_usecase] = _make_submit_user_info_usecase
app.dependency_overrides[get_submit_survey_usecase] = _make_submit_survey_usecase
app.dependency_overrides[get_free_result_usecase] = _make_get_free_result_usecase
app.dependency_overrides[get_confirm_payment_usecase] = _make_confirm_payment_usecase
app.dependency_overrides[get_paid_report_usecase] = _make_get_paid_report_usecase

app.include_router(user_router)
app.include_router(payment_router)
app.include_router(paid_report_router)
app.include_router(paid_report_share_router)

# QA 로그인 게이트 — APP_ENV=test 일 때만 등록 (운영 환경 무영향)
if _settings.app_env == "test":
    from app.domains.qa_auth.router import router as qa_auth_router
    from app.middleware.qa_auth import QaAuthMiddleware

    app.include_router(qa_auth_router)
    if _settings.qa_access_token:
        app.add_middleware(QaAuthMiddleware, expected_token=_settings.qa_access_token)


# CORS 미들웨어는 항상 마지막에 add — LIFO 스택의 가장 바깥에 위치해야
# QaAuthMiddleware가 401 던져도 응답에 CORS 헤더가 박힘.
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-QA-Token"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
