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
from app.domains.ai.domain.value_object.character_persona import (
    DOYOON_PERSONA,
    YEONWOO_PERSONA,
)
from app.domains.ai.domain.value_object.report_status import ReportStatus

if TYPE_CHECKING:
    from app.domains.ai.application.usecase.generate_p0_diagnosis_usecase import (
        GenerateP0DiagnosisUseCase,
    )
    from app.domains.ai.application.usecase.generate_p1_emotion_usecase import (
        GenerateP1EmotionUseCase,
    )
    from app.domains.ai.application.usecase.generate_p1_opening_usecase import (
        GenerateP1OpeningUseCase,
    )
    from app.domains.ai.application.usecase.generate_p1_trigger_usecase import (
        GenerateP1TriggerUseCase,
    )
    from app.domains.ai.application.usecase.generate_p2_hurt_usecase import (
        GenerateP2HurtUseCase,
    )
    from app.domains.ai.application.usecase.generate_p2_recovery_usecase import (
        GenerateP2RecoveryUseCase,
    )
    from app.domains.ai.application.usecase.generate_p3_blockade_usecase import (
        GenerateP3BlockadeUseCase,
    )
    from app.domains.ai.application.usecase.generate_p3_pattern_usecase import (
        GenerateP3PatternUseCase,
    )
    from app.domains.ai.application.usecase.generate_p4_akyon_usecase import (
        GenerateP4AkyonUseCase,
    )
    from app.domains.ai.application.usecase.generate_p4_illusion_usecase import (
        GenerateP4IllusionUseCase,
    )
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
    from app.domains.user.adapter.outbound.persistence.user_repository import (
        UserRepository,
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
        p0_diagnosis_usecase: GenerateP0DiagnosisUseCase | None = None,
        p1_opening_usecase: GenerateP1OpeningUseCase | None = None,
        p1_trigger_usecase: GenerateP1TriggerUseCase | None = None,
        p1_emotion_usecase: GenerateP1EmotionUseCase | None = None,
        p2_hurt_usecase: GenerateP2HurtUseCase | None = None,
        p2_recovery_usecase: GenerateP2RecoveryUseCase | None = None,
        p3_blockade_usecase: GenerateP3BlockadeUseCase | None = None,
        p3_pattern_usecase: GenerateP3PatternUseCase | None = None,
        p4_akyon_usecase: GenerateP4AkyonUseCase | None = None,
        p4_illusion_usecase: GenerateP4IllusionUseCase | None = None,
        email_sender: SendResultLinkEmailUseCase | None = None,
        user_repo: UserRepository | None = None,
    ) -> None:
        self._repo = paid_report_repo
        self._saju_result_repo = saju_result_repo
        self._survey_repo = survey_repo
        self._compose_usecase = compose_usecase
        self._p10_letter_usecase = p10_letter_usecase
        self._p0_diagnosis_usecase = p0_diagnosis_usecase
        self._p1_opening_usecase = p1_opening_usecase
        self._p1_trigger_usecase = p1_trigger_usecase
        self._p1_emotion_usecase = p1_emotion_usecase
        self._p2_hurt_usecase = p2_hurt_usecase
        self._p2_recovery_usecase = p2_recovery_usecase
        self._p3_blockade_usecase = p3_blockade_usecase
        self._p3_pattern_usecase = p3_pattern_usecase
        self._p4_akyon_usecase = p4_akyon_usecase
        self._p4_illusion_usecase = p4_illusion_usecase
        self._email_sender = email_sender
        self._user_repo = user_repo

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
                chapters = await self._compose_chapters(user_id, character)
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

    async def _compose_chapters(
        self, user_id: int, character: str | None
    ) -> dict[str, Any]:
        """user_id로 saju/survey 조회 → P-0~P-10 합성 → chapters dict 반환.

        character로 P-10 persona 분기. 도윤일 때만 user_name 조회 (호명용).
        """
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

        # 도윤일 때 user_name 미리 조회 (P-0 호명용). 연우일 땐 None 그대로.
        user_name_for_compose: str | None = None
        if character == "doyoon" and self._user_repo is not None:
            user_for_p0 = await self._user_repo.find_by_id(user_id)
            user_name_for_compose = user_for_p0.name if user_for_p0 else None
            if user_name_for_compose is None:
                logger.warning(
                    "doyoon p0 wanted user_name but user not found, user_id=%s",
                    user_id,
                )
                # 도윤이지만 user 없으면 합성 자체 불가 → 연우 fallback
                # (실제 운영에선 거의 불가능 — Payment.user_id가 결제 시 박혀 있음)

        # 1차 합성 — P-0~P-9 + P-10 (AI 없음, 폴백 박스 3)
        response = self._compose_usecase.execute(
            saju_raw,
            step1=step1,
            step2=step2,
            step3=step3,
            ai_letter_body=None,
            character=character or "yeonwoo",
            user_name=user_name_for_compose,
        )

        # 1.5차 — 도윤 P-0 ai_intro + P-1 3슬롯 AI 갱신 (실패 시 룰 유지)
        # P-0 1슬롯 + P-1 3슬롯 = 총 4 AI 호출을 asyncio.gather로 병렬 실행.
        # return_exceptions=True — 한 슬롯이 죽어도 다른 슬롯은 살림.
        if character == "doyoon" and user_name_for_compose:
            vars_dy = self._compose_usecase._extractor.extract_paid_variables(saju_raw)
            ilgan_dy = vars_dy.get("ILGAN", "")
            excess_dy = vars_dy.get("OHANG_EXCESS", "")
            lack_dy = vars_dy.get("OHANG_LACK", "")
            if ilgan_dy:
                await self._run_doyoon_ai_slots(
                    user_id=user_id,
                    user_name=user_name_for_compose,
                    ilgan=ilgan_dy,
                    excess=excess_dy,
                    lack=lack_dy,
                    response=response,
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

            # 캐릭터별 페르소나 분기. user_name은 P-0에서 이미 조회됨 (재사용).
            persona = DOYOON_PERSONA if character == "doyoon" else YEONWOO_PERSONA
            user_name = user_name_for_compose

            try:
                ai_body = await self._p10_letter_usecase.execute(
                    persona=persona,
                    user_name=user_name,
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

    async def _run_doyoon_ai_slots(
        self,
        *,
        user_id: int,
        user_name: str,
        ilgan: str,
        excess: str,
        lack: str,
        response: Any,
    ) -> None:
        """도윤 P-0 ai_intro + P-1 3슬롯 (opening/trigger/emotion) 병렬 AI 호출.

        asyncio.gather(return_exceptions=True)로 한 슬롯 실패해도 다른 슬롯 살림.
        각 usecase 자체에 AI 실패/검증 실패 시 룰 fallback 내장 — 본 메서드는
        주입 deps 가용성·예외 경계만 처리.
        """
        # 사용 가능한 슬롯 task 모음 (deps + 필요 데이터 모두 있을 때만 실행)
        tasks: list[tuple[str, Any]] = []

        # P-0 ai_intro
        if (
            self._p0_diagnosis_usecase is not None
            and response.p0_doyoon is not None
            and excess
            and lack
        ):
            tasks.append((
                "p0_intro",
                self._p0_diagnosis_usecase.execute(
                    user_name=user_name,
                    ilgan=ilgan,
                    ohang_excess=excess,
                    ohang_lack=lack,
                ),
            ))

        # P-1 ai_opening (ilju_hanja는 response.p1_doyoon.ilju에 이미 한자 박힘)
        if (
            self._p1_opening_usecase is not None
            and response.p1_doyoon is not None
        ):
            tasks.append((
                "p1_opening",
                self._p1_opening_usecase.execute(
                    user_name=user_name,
                    ilgan=ilgan,
                    ilju_hanja=response.p1_doyoon.ilju,
                ),
            ))

        # P-1 ai_trigger
        if (
            self._p1_trigger_usecase is not None
            and response.p1_doyoon is not None
        ):
            tasks.append((
                "p1_trigger",
                self._p1_trigger_usecase.execute(user_name=user_name, ilgan=ilgan),
            ))

        # P-1 ai_emotion
        if (
            self._p1_emotion_usecase is not None
            and response.p1_doyoon is not None
        ):
            tasks.append((
                "p1_emotion",
                self._p1_emotion_usecase.execute(user_name=user_name, ilgan=ilgan),
            ))

        # P-2 ai_hurt
        if (
            self._p2_hurt_usecase is not None
            and response.p2_doyoon is not None
        ):
            tasks.append((
                "p2_hurt",
                self._p2_hurt_usecase.execute(user_name=user_name, ilgan=ilgan),
            ))

        # P-2 ai_recovery
        if (
            self._p2_recovery_usecase is not None
            and response.p2_doyoon is not None
        ):
            tasks.append((
                "p2_recovery",
                self._p2_recovery_usecase.execute(user_name=user_name, ilgan=ilgan),
            ))

        # P-3 ai_blockade (ohang_excess 필요)
        if (
            self._p3_blockade_usecase is not None
            and response.p3_doyoon is not None
            and excess
        ):
            tasks.append((
                "p3_blockade",
                self._p3_blockade_usecase.execute(
                    user_name=user_name, ilgan=ilgan, ohang_excess=excess
                ),
            ))

        # P-3 ai_pattern
        if (
            self._p3_pattern_usecase is not None
            and response.p3_doyoon is not None
        ):
            tasks.append((
                "p3_pattern",
                self._p3_pattern_usecase.execute(user_name=user_name, ilgan=ilgan),
            ))

        # P-4 ai_akyon (akyon_slot_id는 response.p4_doyoon에서 가져옴)
        if (
            self._p4_akyon_usecase is not None
            and response.p4_doyoon is not None
        ):
            tasks.append((
                "p4_akyon",
                self._p4_akyon_usecase.execute(
                    user_name=user_name,
                    ilgan=ilgan,
                    akyon_slot_id=response.p4_doyoon.akyon_slot_id,
                ),
            ))

        # P-4 ai_illusion
        if (
            self._p4_illusion_usecase is not None
            and response.p4_doyoon is not None
        ):
            tasks.append((
                "p4_illusion",
                self._p4_illusion_usecase.execute(user_name=user_name, ilgan=ilgan),
            ))

        if not tasks:
            return

        names = [name for name, _ in tasks]
        coros = [coro for _, coro in tasks]
        results = await asyncio.gather(*coros, return_exceptions=True)

        for name, result in zip(names, results, strict=True):
            if isinstance(result, BaseException):
                logger.exception(
                    "doyoon AI slot %s failed for user_id=%s: %r",
                    name, user_id, result,
                )
                continue
            ai_text = str(result)
            if name == "p0_intro" and response.p0_doyoon is not None:
                response.p0_doyoon.ai_intro = ai_text
            elif name == "p1_opening" and response.p1_doyoon is not None:
                response.p1_doyoon.ai_opening = ai_text
            elif name == "p1_trigger" and response.p1_doyoon is not None:
                response.p1_doyoon.ai_trigger = ai_text
            elif name == "p1_emotion" and response.p1_doyoon is not None:
                response.p1_doyoon.ai_emotion = ai_text
            elif name == "p2_hurt" and response.p2_doyoon is not None:
                response.p2_doyoon.ai_hurt = ai_text
            elif name == "p2_recovery" and response.p2_doyoon is not None:
                response.p2_doyoon.ai_recovery = ai_text
            elif name == "p3_blockade" and response.p3_doyoon is not None:
                response.p3_doyoon.ai_blockade = ai_text
            elif name == "p3_pattern" and response.p3_doyoon is not None:
                response.p3_doyoon.ai_pattern = ai_text
            elif name == "p4_akyon" and response.p4_doyoon is not None:
                response.p4_doyoon.ai_akyon = ai_text
            elif name == "p4_illusion" and response.p4_doyoon is not None:
                response.p4_doyoon.ai_illusion = ai_text
