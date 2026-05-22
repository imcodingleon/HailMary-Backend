"""사주 raw → P-0~P-5 유료 결과지 통합 합성.

DB 연동 시 `saju_raw`(FortuneTeller 결과 dict) 하나만 넘기면
프론트가 그대로 렌더할 수 있는 `PaidChaptersResponse`(Pydantic)가 떨어진다.

원칙:
- Domain templates(`yeonwoo_pN_*.compose_*`)와 service(`charm_service`, `spouse_avoid_service`)는
  변경하지 않고 호출만 한다.
- Pydantic 변환은 이 Application Layer에서 수행.
- AI 호출 없음 (Phase 0 fast-path).

P-6~P-11은 templates 미작성 → `None` 반환 (프론트 MOCK fallback).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, cast

from app.domains.ai.application.response.paid_report_response import (
    CandleRow,
    CharmPracticeCard,
    CharmSalView,
    DoyoonIlganCardP0,
    EmotionPointDoyoon,
    EndingCard,
    IlganCardP0,
    IllusionGoodCard,
    IllusionSignal,
    InfoRow,
    InnerCard,
    MonthRow,
    OhangKey,
    OhangMethodCard,
    OhangStrength,
    PaidChapterP0,
    PaidChapterP0Doyoon,
    PaidChapterP1,
    PaidChapterP1Doyoon,
    PaidChapterP2,
    PaidChapterP2Doyoon,
    PaidChapterP3,
    PaidChapterP3Doyoon,
    PaidChapterP4Doyoon,
    PaidChapterP5Doyoon,
    PaidChapterP6Doyoon,
    PaidChapterP7Doyoon,
    PaidChapterP8Doyoon,
    PaidChapterP4,
    PaidChapterP5,
    PaidChapterP6,
    PaidChapterP7,
    PaidChapterP8,
    PaidChapterP9,
    PaidChapterP10,
    PaidChaptersResponse,
    PointCard,
    RecoveryAccel,
    RecoveryTimelineRow,
    ReverseCard,
    SajuPillarsP0,
    StageCard,
)
from app.domains.ai.domain.templates.doyoon_p0_intro import compose_doyoon_p0_intro
from app.domains.ai.domain.templates.doyoon_p1_emotion import compose_doyoon_p1_emotion
from app.domains.ai.domain.templates.doyoon_p1_opening import compose_doyoon_p1_opening
from app.domains.ai.domain.templates.doyoon_p1_trigger import compose_doyoon_p1_trigger
from app.domains.ai.domain.templates.doyoon_p2_hurt import compose_doyoon_p2_hurt
from app.domains.ai.domain.templates.doyoon_p2_recovery import compose_doyoon_p2_recovery
from app.domains.ai.domain.templates.doyoon_p3_blocking import (
    compose_doyoon_p3_blockade,
    compose_doyoon_p3_pattern,
)
from app.domains.ai.domain.templates.doyoon_p4_blocking2 import (
    compose_doyoon_p4_akyon,
    compose_doyoon_p4_illusion,
)
from app.domains.ai.domain.templates.doyoon_p5_charm import (
    compose_doyoon_p5_appeal,
    compose_doyoon_p5_charm_index,
    compose_doyoon_p5_conversion,
)
from app.domains.ai.domain.templates.doyoon_p6_destined import (
    compose_doyoon_p6_meeting,
    compose_doyoon_p6_pattern,
    compose_doyoon_p6_profile,
)
from app.domains.ai.domain.templates.doyoon_p7_ending import (
    compose_doyoon_p7_ending,
)
from app.domains.ai.domain.templates.doyoon_p8_timing import (
    compose_doyoon_p8_timing,
)
from app.domains.ai.domain.templates.yeonwoo_p0_intro import compose_p0_intro
from app.domains.ai.domain.templates.yeonwoo_p1_chapter_opening import (
    compose_p1_chapter_opening,
    get_love_type,
)
from app.domains.ai.domain.templates.yeonwoo_p1_emotion import (
    compose_p1_emotion,
    get_candle_pattern,
    get_emotion_bubble,
)
from app.domains.ai.domain.templates.yeonwoo_p1_trigger import (
    compose_p1_trigger,
    get_trigger_descriptions,
    get_triggers,
)
from app.domains.ai.domain.templates.yeonwoo_p2_hurt import compose_p2_hurt
from app.domains.ai.domain.templates.yeonwoo_p2_recovery import compose_p2_recovery
from app.domains.ai.domain.templates.yeonwoo_p3_blocking import compose_p3_blocking
from app.domains.ai.domain.templates.yeonwoo_p4_blocking2 import (
    VALID_SLOTID,
    compose_p4_blocking2,
)
from app.domains.ai.domain.templates.yeonwoo_p5_charm import compose_p5_charm
from app.domains.ai.domain.templates.yeonwoo_p6_destined import (
    VALID_SLOTID as VALID_MATCH_SLOTID,
)
from app.domains.ai.domain.templates.yeonwoo_p6_destined import (
    compose_p6_destined,
)
from app.domains.ai.domain.templates.yeonwoo_p7_inner import compose_p7_inner
from app.domains.ai.domain.templates.yeonwoo_p8_timing import compose_p8_timing
from app.domains.ai.domain.templates.yeonwoo_p9_charm import compose_p9_charm
from app.domains.ai.domain.templates.yeonwoo_p9_practice import compose_p9_practice
from app.domains.ai.domain.templates.yeonwoo_p10_letter import (
    compose_box1_body,
    compose_box2_body,
    compose_box3,
)
from app.domains.ai.domain.value_object.doyoon_ilgan_cards import DOYOON_ILGAN_CARDS
from app.domains.ai.domain.value_object.doyoon_p1_data import DOYOON_P1_DATA
from app.domains.ai.domain.value_object.ilgan_cards import get_ilgan_card
from app.domains.user.domain.service.charm_service import CharmService
from app.domains.user.domain.service.monthly_romance_flow_service import (
    MonthlyRomanceFlowService,
)
from app.domains.user.domain.service.saju_data_extractor import SajuDataExtractor
from app.domains.user.domain.service.spouse_avoid_service import SpouseAvoidService
from app.domains.user.domain.service.spouse_match_service import SpouseMatchService

# ── 한글 오행 → 응답 코드 매핑 ──────────────────────────────────
_OHANG_HANGUL_TO_CODE: dict[str, OhangKey] = {
    "목": "mok",
    "화": "hwa",
    "토": "to",
    "금": "geum",
    "수": "su",
}

# ── 천간/오행 → 한자 (이름 한자 합성용) ─────────────────────────
_STEM_HANJA: dict[str, str] = {
    "갑": "甲", "을": "乙", "병": "丙", "정": "丁", "무": "戊",
    "기": "己", "경": "庚", "신": "辛", "임": "壬", "계": "癸",
}
_BRANCH_HANJA: dict[str, str] = {
    "자": "子", "축": "丑", "인": "寅", "묘": "卯", "진": "辰", "사": "巳",
    "오": "午", "미": "未", "신": "申", "유": "酉", "술": "戌", "해": "亥",
}
_OHANG_HANJA: dict[str, str] = {
    "목": "木", "화": "火", "토": "土", "금": "金", "수": "水",
}


def _ilgan_with_hanja(ilgan: str) -> str:
    """'임수' → '임수(壬水)'."""
    if len(ilgan) != 2:
        return ilgan
    stem_h = _STEM_HANJA.get(ilgan[0])
    ohang_h = _OHANG_HANJA.get(ilgan[1])
    if not stem_h or not ohang_h:
        return ilgan
    return f"{ilgan}({stem_h}{ohang_h})"


def _ilju_with_hanja(ilju: str) -> str:
    """'임술' → '임술(壬戌)'."""
    if len(ilju) != 2:
        return ilju
    stem_h = _STEM_HANJA.get(ilju[0])
    branch_h = _BRANCH_HANJA.get(ilju[1])
    if not stem_h or not branch_h:
        return ilju
    return f"{ilju}({stem_h}{branch_h})"


def _ohang_code(hangul: str) -> OhangKey:
    """오행 한글 한 글자 → 응답 코드. 비정상 입력은 'su' 기본값."""
    return _OHANG_HANGUL_TO_CODE.get(hangul, "su")


class ComposePaidReportUseCase:
    """사주 raw → P-0~P-6 페이지 dict 통합 합성.

    DB 연동 후 `GetPaidReportUseCase`가 `PaidReport.chapters` (이미 합성된 JSON)을
    그대로 반환할 예정. 그 합성 시점에 이 UseCase를 호출하면 됨.
    Phase 0(현재)에서는 운영 API에서도 매 요청 합성 가능 (AI 호출 0, 비용 0).
    """

    def __init__(
        self,
        *,
        saju_extractor: SajuDataExtractor | None = None,
        charm_service: CharmService | None = None,
        spouse_avoid_service: SpouseAvoidService | None = None,
        spouse_match_service: SpouseMatchService | None = None,
        monthly_flow_service: MonthlyRomanceFlowService | None = None,
    ) -> None:
        self._extractor = saju_extractor or SajuDataExtractor()
        self._charm = charm_service or CharmService()
        self._spouse_avoid = spouse_avoid_service or SpouseAvoidService()
        self._spouse_match = spouse_match_service or SpouseMatchService()
        self._monthly_flow = monthly_flow_service or MonthlyRomanceFlowService()

    def execute(
        self,
        saju_raw: dict[str, Any],
        *,
        start_year: int | None = None,
        start_month: int | None = None,
        step1: tuple[str, ...] = (),
        step2: tuple[str, ...] = (),
        step3: str | None = None,
        ai_letter_body: str | None = None,
        character: str = "yeonwoo",
        user_name: str | None = None,
    ) -> PaidChaptersResponse:
        """사주 raw → 12 페이지 응답 (P-0~P-10).

        Args:
            saju_raw: FortuneTeller raw 응답 dict.
            start_year, start_month: P-8 12개월 운명선의 시작 시점. None이면 현재.
            step1, step2: 설문 객관식 슬러그 튜플 (P-10 박스 1·2 합성).
            step3: 설문 자유 텍스트 (P-10 박스 3 quote + AI 답장 트리거).
            ai_letter_body: P-10 AI 호출 결과. None이면 폴백 (compose_box3 내부).
                AI 호출은 별도 비동기 경로에서 수행되고 그 결과를 여기 주입.
            character: "yeonwoo" 또는 "doyoon". 도윤일 때 p0_doyoon 합성.
            user_name: 도윤일 때 필수 (P-0 호명용).
        """
        if start_year is None or start_month is None:
            now = datetime.now()
            start_year = now.year
            start_month = now.month
        vars_ = self._extractor.extract_paid_variables(saju_raw)
        ilgan: str = vars_["ILGAN"]
        ilju: str = vars_["ILJU"]
        ohang_excess: str = vars_["OHANG_EXCESS"]
        ohang_lack: str = vars_["OHANG_LACK"]

        # 데이터 부족(빈 ilgan 등)이면 chapters 전부 None으로 fallback.
        if not ilgan or not ohang_excess or not ohang_lack:
            return PaidChaptersResponse()

        charm = self._charm.calculate(saju_raw)
        sal_keys = tuple(self._charm.get_user_charm_sals(saju_raw))
        akyon_slot_id = self._resolve_akyon_slot_id(saju_raw)
        match_slot_id = self._resolve_match_slot_id(saju_raw)

        # P-6, P-8 먼저 빌드 — P-10 박스 2가 P-6 keyword_tags / P-8 peak labels 참조
        p6 = self._build_p6(ilgan, match_slot_id, ohang_lack)
        p8 = self._build_p8(saju_raw, ilgan, start_year, start_month)

        # 도윤 P-0~P-3는 별도 chapters key. 다른 페이지는 점진 추가 예정.
        if character == "doyoon":
            p0_doyoon = self._build_p0_doyoon(
                vars_, ilgan, ohang_excess, ohang_lack, user_name or ""
            )
            p1_doyoon = self._build_p1_doyoon(ilgan, ilju, user_name or "")
            p2_doyoon = self._build_p2_doyoon(ilgan, user_name or "")
            p3_doyoon = self._build_p3_doyoon(
                ilgan, ohang_excess, user_name or ""
            )
            p4_doyoon = self._build_p4_doyoon(
                ilgan, akyon_slot_id, user_name or ""
            )
            p5_doyoon = self._build_p5_doyoon(ilgan, charm, sal_keys, user_name or "")
            p6_doyoon = self._build_p6_doyoon(
                ilgan, match_slot_id, ohang_lack, charm, user_name or ""
            )
            p7_doyoon = self._build_p7_doyoon(ilgan, user_name or "")
            p8_doyoon = self._build_p8_doyoon(
                saju_raw, ilgan, start_year, start_month, user_name or ""
            )
            p0_yeonwoo = None
            p1_yeonwoo = None
            p2_yeonwoo = None
            p3_yeonwoo = None
            p4_yeonwoo = None
            p5_yeonwoo = None
        else:
            p0_doyoon = None
            p1_doyoon = None
            p2_doyoon = None
            p3_doyoon = None
            p4_doyoon = None
            p5_doyoon = None
            p6_doyoon = None
            p7_doyoon = None
            p8_doyoon = None
            p0_yeonwoo = self._build_p0(vars_, ilgan, ohang_excess, ohang_lack)
            p1_yeonwoo = self._build_p1(ilgan, ilju)
            p2_yeonwoo = self._build_p2(ilgan)
            p3_yeonwoo = self._build_p3(ilgan, ohang_excess)
            p4_yeonwoo = self._build_p4(ilgan, akyon_slot_id, ohang_excess)
            p5_yeonwoo = self._build_p5(ilgan, charm, sal_keys)

        return PaidChaptersResponse(
            p0=p0_yeonwoo,
            p0_doyoon=p0_doyoon,
            p1=p1_yeonwoo,
            p1_doyoon=p1_doyoon,
            p2=p2_yeonwoo,
            p2_doyoon=p2_doyoon,
            p3=p3_yeonwoo,
            p3_doyoon=p3_doyoon,
            p4=p4_yeonwoo,
            p4_doyoon=p4_doyoon,
            p5_doyoon=p5_doyoon,
            p5=p5_yeonwoo,
            p6_doyoon=p6_doyoon,
            p7_doyoon=p7_doyoon,
            p8_doyoon=p8_doyoon,
            p6=p6,
            p7=self._build_p7(ilgan),
            p8=p8,
            p9=self._build_p9(ilgan, ohang_lack, sal_keys, charm),
            p10=self._build_p10(
                ilgan=ilgan,
                ilju=ilju,
                step1=step1,
                step2=step2,
                step3=step3,
                p6=p6,
                p8=p8,
                ai_letter_body=ai_letter_body,
            ),
        )

    # ── P-0 ──────────────────────────────────────────────────
    def _build_p0(
        self,
        vars_: dict[str, Any],
        ilgan: str,
        ohang_excess: str,
        ohang_lack: str,
    ) -> PaidChapterP0:
        pillars = SajuPillarsP0(
            si_g=vars_["SI_G"], si_j=vars_["SI_J"],
            il_g=vars_["IL_G"], il_j=vars_["IL_J"],
            wl_g=vars_["WL_G"], wl_j=vars_["WL_J"],
            yr_g=vars_["YR_G"], yr_j=vars_["YR_J"],
        )
        strength = OhangStrength(
            mok=vars_["OHANG_MOK"],
            hwa=vars_["OHANG_HWA"],
            to=vars_["OHANG_TO"],
            geum=vars_["OHANG_GEUM"],
            su=vars_["OHANG_SU"],
        )
        card = get_ilgan_card(ilgan)
        ilgan_card = IlganCardP0(
            name_kor=card.name_kor,
            name_han=card.name_han,
            subtitle=card.subtitle,
            essence=card.essence,
            in_love=list(card.in_love),
            caution=card.caution,
        )
        return PaidChapterP0(
            saju_pillars=pillars,
            ohang_strength=strength,
            ohang_excess=_ohang_code(ohang_excess),
            ohang_lack=_ohang_code(ohang_lack),
            ilgan=ilgan,
            ilgan_card=ilgan_card,
            ai_intro=compose_p0_intro(
                ilgan=ilgan,
                ohang_excess=ohang_excess,
                ohang_lack=ohang_lack,
            ),
        )

    # ── P-0 (도윤 패널) ──────────────────────────────────────
    def _build_p0_doyoon(
        self,
        vars_: dict[str, Any],
        ilgan: str,
        ohang_excess: str,
        ohang_lack: str,
        user_name: str,
    ) -> PaidChapterP0Doyoon:
        """도윤 P-0 합성 — 8글자 + 오행 5강도 + 도윤 일간 카드 + 4단락 ai_intro.

        user_name 비어 있으면 KeyError·ValueError로 합성 자체가 실패 →
        호출자 (create_paid_report_usecase)가 graceful 처리.
        """
        pillars = SajuPillarsP0(
            si_g=vars_["SI_G"], si_j=vars_["SI_J"],
            il_g=vars_["IL_G"], il_j=vars_["IL_J"],
            wl_g=vars_["WL_G"], wl_j=vars_["WL_J"],
            yr_g=vars_["YR_G"], yr_j=vars_["YR_J"],
        )
        strength = OhangStrength(
            mok=vars_["OHANG_MOK"],
            hwa=vars_["OHANG_HWA"],
            to=vars_["OHANG_TO"],
            geum=vars_["OHANG_GEUM"],
            su=vars_["OHANG_SU"],
        )
        dy_card = DOYOON_ILGAN_CARDS[ilgan]
        ilgan_card = DoyoonIlganCardP0(
            name_kor=dy_card.name_kor,
            name_han=dy_card.name_han,
            subtitle=dy_card.subtitle,
            data_traits=list(dy_card.data_traits),
            love_variables=list(dy_card.love_variables),
            main_conflict=dy_card.main_conflict,
        )
        return PaidChapterP0Doyoon(
            saju_pillars=pillars,
            ohang_strength=strength,
            ohang_excess=_ohang_code(ohang_excess),
            ohang_lack=_ohang_code(ohang_lack),
            ilgan=ilgan,
            user_name=user_name,
            ilgan_card=ilgan_card,
            ai_intro=compose_doyoon_p0_intro(
                user_name=user_name,
                ilgan=ilgan,
                ohang_excess=ohang_excess,
                ohang_lack=ohang_lack,
            ),
        )

    # ── P-1 (도윤 패널) ──────────────────────────────────────
    def _build_p1_doyoon(
        self, ilgan: str, ilju: str, user_name: str
    ) -> PaidChapterP1Doyoon:
        """도윤 P-1 합성 — 연애 유형 + 트리거 flow + 감정 곡선 + 3 AI 슬롯 룰 합성."""
        data = DOYOON_P1_DATA[ilgan]
        labels = ("초반", "중반", "위기", "회복")
        curve = [
            EmotionPointDoyoon(
                label=labels[i],
                pct=data.emotion_curve[i],
                is_crisis=(labels[i] == "위기"),
            )
            for i in range(4)
        ]
        return PaidChapterP1Doyoon(
            user_name=user_name,
            ilgan=_ilgan_with_hanja(ilgan),
            ilju=_ilju_with_hanja(ilju),
            love_type=data.love_type,
            pct_value=data.pct_value,
            distribution_pct=data.distribution_pct,
            ai_opening=compose_doyoon_p1_opening(
                user_name=user_name,
                ilgan=ilgan,
                ilju=_ilju_with_hanja(ilju),
            ),
            trigger_1=data.trigger_1,
            trigger_2=data.trigger_2,
            trigger_3=data.trigger_3,
            trigger_flow_pcts=(30, 62, 88),
            ai_trigger=compose_doyoon_p1_trigger(
                user_name=user_name, ilgan=ilgan
            ),
            emotion_curve=curve,
            crisis_multiplier=data.crisis_multiplier,
            ai_emotion=compose_doyoon_p1_emotion(
                user_name=user_name, ilgan=ilgan
            ),
            bubble_quote="이거 알고 계신 것만으로도 달라져요. 진짜로요.",
        )

    # ── P-8 (도윤 패널) ──────────────────────────────────────
    def _build_p8_doyoon(
        self,
        saju_raw: dict[str, Any],
        ilgan: str,
        start_year: int,
        start_month: int,
        user_name: str,
    ) -> PaidChapterP8Doyoon | None:
        """도윤 P-8 합성 — 12개월 접촉 확률 타임라인."""
        try:
            from app.domains.ai.application.response.paid_report_response import (
                MonthRowDoyoon,
            )
            from app.domains.ai.domain.value_object.doyoon_p8_data import (
                P8_SD_ASSET,
            )

            raw_months = self._monthly_flow.compute_full_months(
                saju_raw, start_year=start_year, start_month=start_month
            )
            d = compose_doyoon_p8_timing(
                user_name=user_name, ilgan=ilgan,
                raw_months=raw_months,
                start_year=start_year, start_month=start_month,
            )
        except (KeyError, ValueError):
            return None

        return PaidChapterP8Doyoon(
            user_name=user_name,
            months=[
                MonthRowDoyoon(
                    label=cast(str, m["label"]),
                    hearts=cast(int, m["hearts"]),
                    pct=cast(int, m["pct"]),
                    state=cast(str, m["state"]),
                    desc=cast(str, m["desc"]),
                    is_peak=cast(bool, m["is_peak"]),
                )
                for m in cast(list[dict[str, object]], d["months"])
            ],
            ai_intro=cast(str, d["ai_intro"]),
            sd_avatar_asset=P8_SD_ASSET,
            bubble=cast(str, d["bubble"]),
        )

    # ── P-7 (도윤 패널) ──────────────────────────────────────
    def _build_p7_doyoon(
        self, ilgan: str, user_name: str,
    ) -> PaidChapterP7Doyoon | None:
        """도윤 P-7 합성 — 결말 시나리오."""
        try:
            from app.domains.ai.application.response.paid_report_response import (
                ScenarioCardDoyoon,
            )
            from app.domains.ai.domain.value_object.doyoon_p7_data import (
                DOYOON_P7_DATA,
            )

            ai_ending = compose_doyoon_p7_ending(user_name=user_name, ilgan=ilgan)
            d = DOYOON_P7_DATA[ilgan]
        except (KeyError, ValueError):
            return None

        return PaidChapterP7Doyoon(
            user_name=user_name,
            scenarios=[
                ScenarioCardDoyoon(
                    prob_label=s.prob_label,
                    prob_tone=s.prob_tone,  # type: ignore[arg-type]
                    title=s.title.replace("{USER_NAME}", user_name),
                    desc=s.desc,
                )
                for s in d.scenarios
            ],
            ai_ending=ai_ending,
            sd_avatar_asset=d.sd_ending_asset,
            ending_bubble=d.ending_bubble.replace("{USER_NAME}", user_name),
        )

    # ── P-6 (도윤 패널) ──────────────────────────────────────
    def _build_p6_doyoon(
        self,
        ilgan: str,
        match_slot_id: str,
        ohang_lack: str,
        charm: dict[str, Any],
        user_name: str,
    ) -> PaidChapterP6Doyoon | None:
        """도윤 P-6 합성 — 인연 프로파일 + 만남 + 행동 패턴."""
        try:
            from app.domains.ai.application.response.paid_report_response import (
                BehaviorCardDoyoon,
                InyonInfoRowDoyoon,
            )
            from app.domains.ai.domain.value_object.doyoon_p6_data import (
                DOYOON_INYON_BY_SLOT,
                DOYOON_P6_DATA,
                P6_SD_BEHAVIOR_ASSET,
            )

            raw_percentile = int(charm.get("charmPercentile", 0))
            pct_value_int = max(1, min(99, 100 - raw_percentile))

            ai_profile = compose_doyoon_p6_profile(
                user_name=user_name, ilgan=ilgan,
                match_slot_id=match_slot_id, pct_value=pct_value_int,
                ohang_lack=ohang_lack,
            )
            ai_meeting = compose_doyoon_p6_meeting(
                user_name=user_name, ilgan=ilgan, match_slot_id=match_slot_id
            )
            ai_pattern = compose_doyoon_p6_pattern(user_name=user_name, ilgan=ilgan)
            i = DOYOON_INYON_BY_SLOT.get(match_slot_id) or DOYOON_INYON_BY_SLOT["f-water-yang"]
            d = DOYOON_P6_DATA[ilgan]
        except (KeyError, ValueError):
            return None

        return PaidChapterP6Doyoon(
            user_name=user_name,
            match_slot_id=match_slot_id,
            pct_value=f"상위 {pct_value_int}%",
            keyword_tags=list(i.keyword_tags),
            info_rows=[
                InyonInfoRowDoyoon(key=r.key, val=r.val) for r in i.info_rows
            ],
            compatibility_pct=i.compatibility_pct,
            ai_profile=ai_profile,
            ai_meeting=ai_meeting,
            profile_bubble=i.profile_bubble.replace("{USER_NAME}", user_name),
            interest_score=d.interest_score,
            expression_score=d.expression_score,
            durability_score=d.durability_score,
            behavior_cards=[
                BehaviorCardDoyoon(label=c.label, keyword=c.keyword, desc=c.desc)
                for c in d.behavior_cards
            ],
            ai_pattern=ai_pattern,
            sd_avatar_asset=P6_SD_BEHAVIOR_ASSET,
        )

    # ── P-5 (도윤 패널) ──────────────────────────────────────
    def _build_p5_doyoon(
        self,
        ilgan: str,
        charm: dict[str, Any],
        sal_keys: tuple[str, ...],
        user_name: str,
    ) -> PaidChapterP5Doyoon | None:
        """도윤 P-5 합성 — 매력 지수 + 전환율 + 호감 유발."""
        try:
            from app.domains.ai.application.response.paid_report_response import (
                AppealMeterDoyoon,
                ConversionStepDoyoon,
                RadarAxisDoyoon,
            )
            from app.domains.ai.domain.value_object.doyoon_p5_data import (
                CONVERSION_STEPS,
                DOYOON_P5_DATA,
            )

            d = DOYOON_P5_DATA[ilgan]
            raw_percentile = int(charm.get("charmPercentile", 0))
            charm_pct_int = max(1, min(99, 100 - raw_percentile))
            ai_charm_index = compose_doyoon_p5_charm_index(
                user_name=user_name, ilgan=ilgan, charm_pct=charm_pct_int
            )
            ai_conversion = compose_doyoon_p5_conversion(
                user_name=user_name, ilgan=ilgan
            )
            ai_appeal = compose_doyoon_p5_appeal(
                user_name=user_name, ilgan=ilgan
            )
        except (KeyError, ValueError):
            return None

        return PaidChapterP5Doyoon(
            user_name=user_name,
            charm_pct=f"상위 {charm_pct_int}%",
            radar=[RadarAxisDoyoon(name=r.name, value=r.value) for r in d.radar],
            strength_axis_1=d.strength_axis_1,
            strength_axis_2=d.strength_axis_2,
            strength_multiplier=d.strength_multiplier,
            ai_charm_index=ai_charm_index,
            sd_avatar_asset=d.sd_charm_asset,
            charm_bubble=d.charm_bubble,
            conversion_steps=[
                ConversionStepDoyoon(label=label, pct=pct)
                for label, pct in CONVERSION_STEPS
            ],
            ai_conversion=ai_conversion,
            appeal_meters=[
                AppealMeterDoyoon(name=m.name, value=m.value)
                for m in d.appeal_meters
            ],
            ai_appeal=ai_appeal,
        )

    # ── P-4 (도윤 패널) ──────────────────────────────────────
    def _build_p4_doyoon(
        self, ilgan: str, akyon_slot_id: str, user_name: str
    ) -> PaidChapterP4Doyoon | None:
        """도윤 P-4 합성 — 비호환 유형 + 착각 인연."""
        try:
            from app.domains.ai.application.response.paid_report_response import (
                AkyonInfoRowDoyoon,
                IllusionSignDoyoon,
            )
            from app.domains.ai.domain.value_object.doyoon_p4_data import (
                ACCURACY_MULTIPLIER,
                DECISIVE_GRADIENT_LABEL,
                DOYOON_AKYON_BY_SLOT,
                DOYOON_P4_DATA,
                FAKE_DROP_PCT,
                REAL_GROWTH_PCT,
            )

            ai_akyon = compose_doyoon_p4_akyon(
                user_name=user_name, ilgan=ilgan, akyon_slot_id=akyon_slot_id
            )
            ai_illusion = compose_doyoon_p4_illusion(
                user_name=user_name, ilgan=ilgan
            )
            a = DOYOON_AKYON_BY_SLOT.get(akyon_slot_id) or DOYOON_AKYON_BY_SLOT["m-water-yang"]
            d = DOYOON_P4_DATA[ilgan]
        except (KeyError, ValueError):
            return None

        return PaidChapterP4Doyoon(
            user_name=user_name,
            akyon_slot_id=akyon_slot_id,
            keyword_tags=list(a.keyword_tags),
            info_rows=[
                AkyonInfoRowDoyoon(key=r.key, val=r.val) for r in a.info_rows
            ],
            ai_akyon=ai_akyon,
            sd_avatar_asset=a.sd_avatar_asset,
            akyon_bubble=a.akyon_bubble,
            illusion_signs=[
                IllusionSignDoyoon(keyword=s.keyword, pct=s.pct, desc=s.desc)
                for s in d.illusion_signs
            ],
            ai_illusion=ai_illusion,
            illusion_bubble=d.illusion_bubble,
            decisive_gradient_label=DECISIVE_GRADIENT_LABEL,
            real_growth_pct=REAL_GROWTH_PCT,
            fake_drop_pct=FAKE_DROP_PCT,
            accuracy_multiplier=ACCURACY_MULTIPLIER,
        )

    # ── P-3 (도윤 패널) ──────────────────────────────────────
    def _build_p3_doyoon(
        self, ilgan: str, ohang_excess: str, user_name: str
    ) -> PaidChapterP3Doyoon | None:
        """도윤 P-3 합성 — 구조적 원인 + 반복 패턴 + 변수 통제.

        ilgan/ohang_excess unknown 시 None (graceful).
        """
        try:
            from app.domains.ai.application.response.paid_report_response import (
                BlockadeOhangP3Doyoon,
                ControlStrategyDoyoon,
                PatternEntryDoyoon,
            )
            from app.domains.ai.domain.value_object.doyoon_p3_data import (
                BLOCKADE_BY_OHANG,
                DOYOON_P3_DATA,
                P3_SD_ASSET,
            )

            ai_blockade = compose_doyoon_p3_blockade(
                user_name=user_name, ilgan=ilgan, ohang_excess=ohang_excess
            )
            ai_pattern = compose_doyoon_p3_pattern(
                user_name=user_name, ilgan=ilgan
            )
            b = BLOCKADE_BY_OHANG[ohang_excess]
            d = DOYOON_P3_DATA[ilgan]
        except (KeyError, ValueError):
            return None

        return PaidChapterP3Doyoon(
            user_name=user_name,
            blockade=BlockadeOhangP3Doyoon(
                ohang_excess=ohang_excess,
                ohang_excess_hanja=b.ohang_hanja,
                blockade_pct=b.blockade_pct,
                blockade_multiplier=b.blockade_multiplier,
            ),
            ai_blockade=ai_blockade,
            blockade_bubble=d.blockade_bubble
                .replace("{USER_NAME}", user_name)
                .replace("{OHANG_EXCESS}", f"{ohang_excess}({b.ohang_hanja})"),
            patterns=[
                PatternEntryDoyoon(keyword=p.keyword, pct=p.pct, desc=p.desc)
                for p in d.patterns
            ],
            ai_pattern=ai_pattern,
            pattern_bubble=d.pattern_bubble,
            strategies=[
                ControlStrategyDoyoon(
                    keyword=s.keyword, desc=s.desc, effect_pct=s.effect_pct
                )
                for s in d.strategies
            ],
            strategy_bubble=d.strategy_bubble,
            sd_avatar_asset=P3_SD_ASSET,
        )

    # ── P-2 (도윤 패널) ──────────────────────────────────────
    def _build_p2_doyoon(
        self, ilgan: str, user_name: str
    ) -> PaidChapterP2Doyoon | None:
        """도윤 P-2 합성 — 원본 도윤_final.html 구조 정합 (재설계 2026-05-21).

        - 1-4: hurt_type × 2 (keyword + risk_pct + desc)
        - 1-5: meters × 4 (직후/1개월/3개월/6개월 %) + SD + 한도윤 버블

        ilgan unknown 시 None 반환 (graceful — 프론트 MOCK fallback).
        """
        try:
            hurt = compose_doyoon_p2_hurt(user_name=user_name, ilgan=ilgan)
            recovery = compose_doyoon_p2_recovery(
                user_name=user_name, ilgan=ilgan
            )
        except (KeyError, ValueError):
            return None

        from app.domains.ai.application.response.paid_report_response import (
            HurtTypeDoyoon,
            RecoveryMeterDoyoon,
        )
        from app.domains.ai.domain.value_object.doyoon_p2_data import (
            DOYOON_P2_DATA,
        )
        data = DOYOON_P2_DATA[ilgan]

        return PaidChapterP2Doyoon(
            user_name=user_name,
            hurt_type_1=HurtTypeDoyoon(
                keyword=data.hurt_type_1.keyword,
                risk_pct=data.hurt_type_1.risk_pct,
                desc=data.hurt_type_1.desc,
            ),
            hurt_type_2=HurtTypeDoyoon(
                keyword=data.hurt_type_2.keyword,
                risk_pct=data.hurt_type_2.risk_pct,
                desc=data.hurt_type_2.desc,
            ),
            ai_hurt=hurt["ai_hurt"],
            meters=[
                RecoveryMeterDoyoon(label=m.label, pct=m.pct)
                for m in data.meters
            ],
            recovery_lag_multiplier=data.recovery_lag_multiplier,
            ai_recovery=recovery["ai_recovery"],
            sd_avatar_asset=data.sd_avatar_asset,
            recovery_bubble=data.recovery_bubble,
        )

    # ── P-1 ──────────────────────────────────────────────────
    def _build_p1(self, ilgan: str, ilju: str) -> PaidChapterP1:
        t1, t2, t3 = get_triggers(ilgan)
        d1, d2, d3 = get_trigger_descriptions(ilgan)
        candle = get_candle_pattern(ilgan)
        return PaidChapterP1(
            ilgan=_ilgan_with_hanja(ilgan),
            ilju=_ilju_with_hanja(ilju),
            love_type=get_love_type(ilgan),
            trigger_1=t1, trigger_2=t2, trigger_3=t3,
            trigger_desc_1=d1, trigger_desc_2=d2, trigger_desc_3=d3,
            candle_rows=[
                CandleRow(
                    label=row.label,
                    flames=[cast(Any, f) for f in row.flames],
                    desc=row.desc,
                    is_peak=row.is_peak,
                )
                for row in candle
            ],
            emotion_bubble=get_emotion_bubble(ilgan),
            ai_opening=compose_p1_chapter_opening(ilgan=ilgan, ilju=ilju),
            ai_trigger=compose_p1_trigger(ilgan=ilgan),
            ai_emotion=compose_p1_emotion(ilgan=ilgan),
        )

    # ── P-2 ──────────────────────────────────────────────────
    def _build_p2(self, ilgan: str) -> PaidChapterP2:
        hurt = compose_p2_hurt(ilgan=ilgan)
        rec = compose_p2_recovery(ilgan=ilgan)
        return PaidChapterP2(
            scenario_1_when=hurt["scenario_1_when"],
            scenario_1_desc=hurt["scenario_1_desc"],
            scenario_2_when=hurt["scenario_2_when"],
            scenario_2_desc=hurt["scenario_2_desc"],
            ai_hurt=hurt["ai_hurt"],
            hurt_bubble=hurt["bubble"],
            recovery_timeline=[
                RecoveryTimelineRow(time=r["time"], title=r["title"], desc=r["desc"])
                for r in rec["timeline"]
            ],
            recovery_accel=RecoveryAccel(
                value=rec["accel"]["value"],
                sub=rec["accel"]["sub"],
            ),
            ai_recovery=rec["ai_recovery"],
        )

    # ── P-3 ──────────────────────────────────────────────────
    def _build_p3(self, ilgan: str, ohang_excess: str) -> PaidChapterP3:
        d = compose_p3_blocking(ilgan=ilgan, ohang_excess=ohang_excess)
        return PaidChapterP3(
            ohang_excess=d["ohang_excess"],
            blockade_card_sub=d["blockade_card_sub"],
            ai_blockade=d["ai_blockade"],
            pattern_body=d["pattern_body"],
            ai_pattern=d["ai_pattern"],
            reverse_card_1=ReverseCard(
                value=d["reverse_card_1"]["value"],
                sub=d["reverse_card_1"]["sub"],
            ),
            reverse_card_2=ReverseCard(
                value=d["reverse_card_2"]["value"],
                sub=d["reverse_card_2"]["sub"],
            ),
        )

    # ── P-4 ──────────────────────────────────────────────────
    def _build_p4(
        self, ilgan: str, akyon_slot_id: str, ohang_excess: str,
    ) -> PaidChapterP4 | None:
        if akyon_slot_id not in VALID_SLOTID:
            return None
        d = compose_p4_blocking2(
            ilgan=ilgan,
            akyon_slot_id=akyon_slot_id,
            ohang_excess=ohang_excess,
        )
        return PaidChapterP4(
            akyon_slot_id=d["akyon_slot_id"],
            akyon_keyword_tags=list(d["akyon_keyword_tags"]),
            akyon_info_rows=[InfoRow(key=r["key"], val=r["val"]) for r in d["akyon_info_rows"]],
            ai_akyon=d["ai_akyon"],
            illusion_stitle=d["illusion_stitle"],
            illusion_signals=[
                IllusionSignal(value=s["value"], sub=s["sub"])
                for s in d["illusion_signals"]
            ],
            illusion_good_card=IllusionGoodCard(
                value=d["illusion_good_card"]["value"],
                sub=d["illusion_good_card"]["sub"],
            ),
            ai_illusion=d["ai_illusion"],
        )

    # ── P-5 ──────────────────────────────────────────────────
    def _build_p5(
        self,
        ilgan: str,
        charm: dict[str, Any],
        sal_keys: tuple[str, ...],
    ) -> PaidChapterP5:
        charm_score = int(charm.get("charmStrength", 0))
        # charmPercentile (높을수록 매력 강함) → 상위 N% (낮을수록 상위) 변환.
        raw_percentile = int(charm.get("charmPercentile", 0))
        top_percentile = max(0, min(100, 100 - raw_percentile))

        d = compose_p5_charm(
            ilgan=ilgan,
            charm_score=charm_score,
            charm_percentile=top_percentile,
            user_sal_keys=sal_keys,
        )
        return PaidChapterP5(
            charm_score=d["charm_score"],
            charm_percentile=d["charm_percentile"],
            charm_sals=[
                CharmSalView(
                    charm_key=s["charm_key"],
                    name_kor=s["name_kor"],
                    name_han=s["name_han"],
                    trait=s["trait"],
                )
                for s in d["charm_sals"]
            ],
            stage_cards=[
                StageCard(label=c["label"], value=c["value"], sub=c["sub"])
                for c in d["stage_cards"]
            ],
            point_cards=[
                PointCard(
                    label=c["label"],
                    strength=cast(Any, c["strength"]),
                    flame_label=c["flame_label"],
                    sub=c["sub"],
                )
                for c in d["point_cards"]
            ],
            ai_charm=d["ai_charm"],
            ai_mechanism=d["ai_mechanism"],
            ai_sense=d["ai_sense"],
        )

    # ── P-6 ──────────────────────────────────────────────────
    def _build_p6(
        self, ilgan: str, match_slot_id: str, ohang_lack: str,
    ) -> PaidChapterP6 | None:
        if match_slot_id not in VALID_MATCH_SLOTID:
            return None
        d = compose_p6_destined(
            ilgan=ilgan,
            match_slot_id=match_slot_id,
            ohang_lack=ohang_lack,
        )
        return PaidChapterP6(
            match_slot_id=d["match_slot_id"],
            keyword_tags=list(d["keyword_tags"]),
            info_rows=[InfoRow(key=r["key"], val=r["val"]) for r in d["info_rows"]],
            ai_looks=d["ai_looks"],
            ai_match=d["ai_match"],
            ai_first_meeting=d["ai_first_meeting"],
            bubble=d["bubble"],
            inner_cards=[
                InnerCard(label=c["label"], value=c["value"], sub=c["sub"])
                for c in d["inner_cards"]
            ],
            ai_inner=d["ai_inner"],
        )

    # ── P-7 ──────────────────────────────────────────────────
    def _build_p7(self, ilgan: str) -> PaidChapterP7:
        d = compose_p7_inner(ilgan=ilgan)
        return PaidChapterP7(
            ending_card_1=EndingCard(**d["ending_card_1"]),
            ending_card_2=EndingCard(**d["ending_card_2"]),
            ending_card_3=EndingCard(**d["ending_card_3"]),
            ai_ending=d["ai_ending"],
            notice=d["notice"],
            bubble=d["bubble"],
        )

    # ── P-8 ──────────────────────────────────────────────────
    def _build_p8(
        self,
        saju_raw: dict[str, Any],
        ilgan: str,
        start_year: int,
        start_month: int,
    ) -> PaidChapterP8:
        raw_months = self._monthly_flow.compute_full_months(
            saju_raw, start_year=start_year, start_month=start_month
        )
        d = compose_p8_timing(
            ilgan=ilgan,
            raw_months=raw_months,
            start_year=start_year,
            start_month=start_month,
        )
        return PaidChapterP8(
            months=[
                MonthRow(
                    label=cast(str, m["label"]),
                    hearts=cast(int, m["hearts"]),
                    knot=cast(Any, m["knot"]),
                    state=cast(str, m["state"]),
                    desc=cast(str, m["desc"]),
                    is_peak=cast(bool, m["is_peak"]),
                )
                for m in cast(list[dict[str, object]], d["months"])
            ],
            ai_intro=cast(str, d["ai_intro"]),
            bubble=cast(str, d["bubble"]),
        )

    # ── P-9 ──────────────────────────────────────────────────
    def _build_p9(
        self,
        ilgan: str,
        ohang_lack: str,
        sal_keys: tuple[str, ...],
        charm: dict[str, Any],
    ) -> PaidChapterP9:
        # 6-1 오행 보완
        d = compose_p9_practice(ilgan=ilgan, ohang_lack=ohang_lack)
        # 6-2 매력살 활용 — sal_keys 정렬은 charm_service에서 SAL_PRIORITY 순. Primary = sal_keys[0].
        charm_score = int(charm.get("charmStrength", 0))
        c = compose_p9_charm(ilgan=ilgan, sal_keys=sal_keys, charm_score=charm_score)
        return PaidChapterP9(
            # 6-1
            ohang_lack=cast(str, d["ohang_lack"]),
            ohang_method_cards=[
                OhangMethodCard(label=card["label"], value=card["value"], sub=card["sub"])
                for card in cast(list[dict[str, str]], d["ohang_method_cards"])
            ],
            ai_ohang=cast(str, d["ai_ohang"]),
            # 6-2
            primary_charm_key=cast(str, c["primary_charm_key"]),
            primary_charm_label=cast(str, c["primary_charm_label"]),
            charm_count=cast(int, c["charm_count"]),
            charm_current=cast(Any, c["charm_current"]),
            charm_target=cast(Any, c["charm_target"]),
            charm_practice_cards=[
                CharmPracticeCard(label=card["label"], value=card["value"], sub=card["sub"])
                for card in cast(list[dict[str, str]], c["charm_practice_cards"])
            ],
            charm_practice_body=cast(str, c["charm_practice_body"]),
            ai_charm=cast(str, c["ai_charm"]),
        )

    # ── P-10 ──────────────────────────────────────────────────
    def _build_p10(
        self,
        *,
        ilgan: str,
        ilju: str,
        step1: tuple[str, ...],
        step2: tuple[str, ...],
        step3: str | None,
        p6: PaidChapterP6 | None,
        p8: PaidChapterP8 | None,
        ai_letter_body: str | None,
    ) -> PaidChapterP10 | None:
        """P-10 편지 합성 — 박스 1·2·3 통합.

        step1 비어있으면 박스 1 합성 불가 → None 반환 (프론트 폴백 의지).
        AI 호출(step3 있을 때)은 외부에서 수행되고 ai_letter_body로 주입.
        ai_letter_body=None + step3 있음 = compose_box3 폴백 사용.
        """
        # 박스 1: step1 필요. 빈 튜플이면 합성 못함 → None
        if not step1:
            return None

        # 박스 1 본문 (도입 멘트 + step1 부분집합 본문)
        box1_body = compose_box1_body(ilgan=ilgan, step1=step1)

        # 박스 2 본문 (step2 부분집합 × 일간 + P-6/P-8 placeholder)
        # step2 없으면 박스 2 없는 셈 — 폴백으로 step2=(soulmate,)
        effective_step2 = step2 if step2 else ("soulmate",)
        keyword_tags: tuple[str, ...] | None = None
        peak_labels: tuple[str, str] | None = None
        if p6 is not None and p6.keyword_tags:
            keyword_tags = tuple(p6.keyword_tags)
        if p8 is not None and p8.months:
            peaks = [m.label for m in p8.months if m.is_peak]
            if len(peaks) >= 2:
                peak_labels = (peaks[0], peaks[1])
        box2_body = compose_box2_body(
            ilgan=ilgan,
            step2=effective_step2,
            keyword_tags=keyword_tags,
            peak_month_labels=peak_labels,
        )

        # 박스 3: step3 + AI 결과 또는 폴백
        ilju_with_hanja = _ilju_with_hanja(ilju)
        box3 = compose_box3(
            ilgan=ilgan,
            step3=step3,
            step1=step1,
            ai_letter_body=ai_letter_body,
        )

        return PaidChapterP10(
            ilju_with_hanja=ilju_with_hanja,
            box1_body=box1_body,
            box2_body=box2_body,
            quote_text=cast(str, box3["quote_text"]),
            quote_label=cast(str, box3["quote_label"]),
            box3_body=cast(str, box3["body"]),
            emphasis=cast(str, box3["emphasis"]),
            tail=cast(str, box3["tail"]),
            uses_ai=cast(bool, box3["uses_ai"]),
        )

    # ── 헬퍼: 악연 slotId 추출 ──────────────────────────────────
    def _resolve_akyon_slot_id(self, saju_raw: dict[str, Any]) -> str:
        """무료 응답의 SpouseAvoidView.slotId 재사용. 'neutral'이면 빈 문자열."""
        view = self._spouse_avoid.calculate(saju_raw)
        slot_id = str(view.get("slotId") or "")
        if slot_id.endswith("-neutral"):
            return ""
        return slot_id

    # ── 헬퍼: 인연 slotId 추출 ──────────────────────────────────
    def _resolve_match_slot_id(self, saju_raw: dict[str, Any]) -> str:
        """무료 응답의 SpouseMatchView.slotId 재사용. neutral은 빈 문자열."""
        view = self._spouse_match.calculate(saju_raw)
        slot_id = str(view.get("slotId") or "")
        if slot_id.endswith("-neutral"):
            return ""
        return slot_id
