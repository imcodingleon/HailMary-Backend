"""결제 confirm 직후 호출되는 PaidReport 생성 + 합성 UseCase.

Phase 2 — 합성 wiring 통합:
  1. order_id 중복 → idempotent 반환
  2. saju_hash 캐시 hit → chapters 복사 + ready
  3. miss 시:
     a. SajuResult, Survey 조회 (user_id 기반)
     b. ComposePaidReportUseCase 호출 (P-0~P-9 + P-10 폴백)
     c. step3 있으면 GenerateP10LetterUseCase로 AI 답장 호출 → P-10 박스 3 갱신
     d. chapters에 박고 mark_ready
  4. AI 또는 합성 실패 시 graceful — pending 유지 (사용자가 폴링으로 다시 시도 가능)

Hexagonal 원칙 위배 (user 도메인 repo 직접 import). 추후 Port 추출 예정.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any

from app.domains.ai.application.usecase.compose_paid_report_usecase import (
    ComposePaidReportUseCase,
)
from app.domains.ai.domain.entity.paid_report import PaidReport
from app.domains.ai.domain.port.paid_report_repository_port import (
    PaidReportRepositoryPort,
)
from app.domains.ai.domain.templates.yeonwoo_p10_letter import compose_box3
from app.domains.ai.domain.value_object.character_persona import YEONWOO_PERSONA
from app.domains.ai.domain.value_object.report_status import ReportStatus

if TYPE_CHECKING:
    from app.domains.ai.application.usecase.generate_p10_letter_usecase import (
        GenerateP10LetterUseCase,
    )
    from app.domains.ai.application.usecase.send_result_link_email_usecase import (
        SendResultLinkEmailUseCase,
    )
    from app.domains.user.adapter.outbound.persistence.saju_result_repository import (
        SajuResultRepository,
    )
    from app.domains.user.adapter.outbound.persistence.survey_repository import (
        SurveyRepository,
    )

logger = logging.getLogger(__name__)

# fire-and-forget asyncio.create_task가 GC로 사라지는 것 방지용 강한 참조 보관소.
# task가 완료되면 done_callback에서 자동 discard.
_PENDING_EMAIL_TASKS: set[asyncio.Task[None]] = set()


# 일간 한자 매핑 (compose에서 가져온 값 재구성용)
_STEM_HANJA: dict[str, str] = {
    "갑": "甲", "을": "乙", "병": "丙", "정": "丁", "무": "戊",
    "기": "己", "경": "庚", "신": "辛", "임": "壬", "계": "癸",
}
_OHANG_HANJA: dict[str, str] = {
    "목": "木", "화": "火", "토": "土", "금": "金", "수": "水",
}


def _ilgan_with_hanja(ilgan: str) -> str:
    if len(ilgan) != 2:
        return ilgan
    stem = _STEM_HANJA.get(ilgan[0])
    ohang = _OHANG_HANJA.get(ilgan[1])
    if not stem or not ohang:
        return ilgan
    return f"{ilgan}({stem}{ohang})"


def _ohang_with_hanja(ohang: str) -> str:
    h = _OHANG_HANJA.get(ohang)
    return f"{ohang}({h})" if h else ohang


class CreatePaidReportUseCase:
    """결제 confirm 직후 호출 — PaidReport 생성 + chapters 합성.

    1. 동일 order_id row 있으면 idempotent.
    2. saju_hash cache hit → chapters 복사 + ready.
    3. miss → 합성 시도. 실패 시 pending 유지.
    """

    def __init__(
        self,
        *,
        paid_report_repo: PaidReportRepositoryPort,
        saju_result_repo: SajuResultRepository | None = None,
        survey_repo: SurveyRepository | None = None,
        compose_usecase: ComposePaidReportUseCase | None = None,
        p10_letter_usecase: GenerateP10LetterUseCase | None = None,
        email_sender: SendResultLinkEmailUseCase | None = None,
    ) -> None:
        self._repo = paid_report_repo
        self._saju_result_repo = saju_result_repo
        self._survey_repo = survey_repo
        self._compose_usecase = compose_usecase
        self._p10_letter_usecase = p10_letter_usecase
        self._email_sender = email_sender

    async def execute(
        self,
        *,
        order_id: str,
        saju_hash: str,
        user_id: int | None = None,
        customer_email: str | None = None,
        expires_at: datetime | None = None,
        character: str | None = None,
    ) -> PaidReport:
        # 1. 중복 체크 (idempotent)
        existing = await self._repo.find_by_order_id(order_id)
        if existing is not None:
            return existing

        # 2. 결정 (2026-05-14): saju_hash 캐시 폐기. 매 결제마다 새 합성.
        # 이유: 템플릿 기반 P-0~P-9는 결정론적이라 같은 사주면 어차피 동일.
        # P-10 AI 답장만 매번 새로 호출되어 21원 추가 — 재결제 사용자한테 새 답을 보장.
        # saju_hash 컬럼은 유지 (디버깅/복원용).
        report = PaidReport.new_pending(order_id=order_id, saju_hash=saju_hash)

        # 3. 합성 시도 (deps + user_id 있을 때만)
        if (
            user_id is not None
            and self._saju_result_repo is not None
            and self._survey_repo is not None
            and self._compose_usecase is not None
        ):
            try:
                chapters = await self._compose_chapters(user_id)
                if chapters:
                    report.mark_ready(chapters)
            except Exception:
                logger.exception(
                    "chapters compose failed for order_id=%s user_id=%s",
                    order_id,
                    user_id,
                )
                # pending 유지 — 폴링이 다시 시도 가능

        saved = await self._repo.save(report)

        # 4. ready 상태면 이메일 발송 트리거 (fire-and-forget)
        if saved.status == ReportStatus.READY:
            self._trigger_email(saved, customer_email, expires_at, character)

        return saved

    def _trigger_email(
        self,
        report: PaidReport,
        customer_email: str | None,
        expires_at: datetime | None,
        character: str | None,
    ) -> None:
        """이메일 발송 비동기 트리거. fire-and-forget — 실패해도 PaidReport는 ready 유지."""
        if (
            self._email_sender is None
            or customer_email is None
            or expires_at is None
            or character is None
        ):
            return  # deps 부족 시 발송 스킵 (로그도 X — 정상 폴백)
        # Python 3.12+ 에서 asyncio.create_task 결과를 변수에 안 잡으면
        # task가 즉시 GC되어 실행 자체가 안 될 수 있음 (공식 docs 권장 패턴).
        # 모듈 레벨 set에 강한 참조로 보관하고, 완료 시 자동 제거.
        task = asyncio.create_task(
            self._email_sender.execute(
                to=customer_email,
                share_code=report.share_code,
                character=character,
                expires_at=expires_at,
            )
        )
        _PENDING_EMAIL_TASKS.add(task)
        task.add_done_callback(_PENDING_EMAIL_TASKS.discard)

    async def _compose_chapters(self, user_id: int) -> dict[str, Any]:
        """user_id로 saju/survey 조회 → P-0~P-10 합성 → chapters dict 반환."""
        assert self._saju_result_repo is not None
        assert self._survey_repo is not None
        assert self._compose_usecase is not None

        # SajuResult 조회
        saju_result = await self._saju_result_repo.find_by_user_id(user_id)
        if saju_result is None:
            logger.warning("saju not found for user_id=%s", user_id)
            return {}
        saju_raw = saju_result.fortuneteller_response

        # Survey 조회 (없을 수 있음)
        survey = await self._survey_repo.find_by_user_id(user_id)
        step1: tuple[str, ...] = tuple(survey.step1_slugs) if survey else ()
        step2: tuple[str, ...] = tuple(survey.step2_slugs) if survey else ()
        step3: str | None = survey.step3_text if survey else None

        # 1차 합성 — P-0~P-9 + P-10 (AI 없음, 폴백 박스 3)
        response = self._compose_usecase.execute(
            saju_raw,
            step1=step1,
            step2=step2,
            step3=step3,
            ai_letter_body=None,
        )

        # 2차 — step3 있고 AI 가능하면 AI 답장 → 박스 3 갱신
        if (
            step3 is not None
            and step3.strip()
            and self._p10_letter_usecase is not None
            and response.p10 is not None
        ):
            vars_ = self._compose_usecase._extractor.extract_paid_variables(saju_raw)
            ilgan = vars_.get("ILGAN", "")
            ohang_excess = vars_.get("OHANG_EXCESS", "")
            ohang_lack = vars_.get("OHANG_LACK", "")

            try:
                ai_body = await self._p10_letter_usecase.execute(
                    # TODO(도윤): 캐릭터별 페르소나 분기점. 현재 강연우 고정.
                    persona=YEONWOO_PERSONA,
                    ilgan=_ilgan_with_hanja(ilgan),
                    ilju=response.p10.ilju_with_hanja,
                    ohang_excess=_ohang_with_hanja(ohang_excess),
                    ohang_lack=_ohang_with_hanja(ohang_lack),
                    box1_body=response.p10.box1_body,
                    box2_body=response.p10.box2_body,
                    step3=step3,
                    emphasis=response.p10.emphasis,
                )
                # 박스 3만 재합성 (compose_box3는 ai_letter_body를 직접 받음)
                new_box3 = compose_box3(
                    ilgan=ilgan,
                    step3=step3,
                    step1=step1,
                    ai_letter_body=ai_body,
                )
                response.p10.box3_body = str(new_box3["body"])
                response.p10.uses_ai = bool(new_box3["uses_ai"])
            except Exception:
                logger.exception("P-10 AI letter generation failed for user_id=%s", user_id)
                # 폴백 그대로 유지 (uses_ai=False)

        # chapters dict로 직렬화 (PaidChaptersResponse → dict[str, dict])
        chapters = response.model_dump(exclude_none=True, mode="json")
        return chapters
