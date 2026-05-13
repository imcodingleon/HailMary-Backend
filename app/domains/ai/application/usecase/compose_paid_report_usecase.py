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

from typing import Any, cast

from app.domains.ai.application.response.paid_report_response import (
    CandleRow,
    CharmSalView,
    EndingCard,
    IlganCardP0,
    IllusionGoodCard,
    IllusionSignal,
    InfoRow,
    InnerCard,
    OhangKey,
    OhangStrength,
    PaidChapterP0,
    PaidChapterP1,
    PaidChapterP2,
    PaidChapterP3,
    PaidChapterP4,
    PaidChapterP5,
    PaidChapterP6,
    PaidChapterP7,
    PaidChaptersResponse,
    PointCard,
    RecoveryAccel,
    RecoveryTimelineRow,
    ReverseCard,
    SajuPillarsP0,
    StageCard,
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
from app.domains.ai.domain.value_object.ilgan_cards import get_ilgan_card
from app.domains.user.domain.service.charm_service import CharmService
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
    ) -> None:
        self._extractor = saju_extractor or SajuDataExtractor()
        self._charm = charm_service or CharmService()
        self._spouse_avoid = spouse_avoid_service or SpouseAvoidService()
        self._spouse_match = spouse_match_service or SpouseMatchService()

    def execute(self, saju_raw: dict[str, Any]) -> PaidChaptersResponse:
        """사주 raw → 12 페이지 응답 (현재 P-0~P-7만 채움)."""
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

        return PaidChaptersResponse(
            p0=self._build_p0(vars_, ilgan, ohang_excess, ohang_lack),
            p1=self._build_p1(ilgan, ilju),
            p2=self._build_p2(ilgan),
            p3=self._build_p3(ilgan, ohang_excess),
            p4=self._build_p4(ilgan, akyon_slot_id, ohang_excess),
            p5=self._build_p5(ilgan, charm, sal_keys),
            p6=self._build_p6(ilgan, match_slot_id, ohang_lack),
            p7=self._build_p7(ilgan),
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
