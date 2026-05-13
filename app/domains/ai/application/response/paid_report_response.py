"""유료 결과지 응답 DTO.

12 페이지 (P-0 ~ P-11)별 명시 타입 정의. 프론트 `paidReport.ts`와 1:1 매칭.
P-0~P-5만 백엔드 templates 작성 완료 → 명시 타입 채움.
P-6~P-11은 templates 작성 후 점진 확장 (현재 응답에 없음 → 프론트 MOCK fallback).
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

# ═════════════════════════════════════════════════════════════════
# Nested 공용 타입
# ═════════════════════════════════════════════════════════════════

OhangKey = Literal["mok", "hwa", "to", "geum", "su"]


class SajuPillarsP0(BaseModel):
    """P-0 사주 원국 8자 (천간/지지 한자)."""
    model_config = ConfigDict(populate_by_name=True)

    si_g: str
    si_j: str
    il_g: str
    il_j: str
    wl_g: str
    wl_j: str
    yr_g: str
    yr_j: str


class OhangStrength(BaseModel):
    """P-0 오행 분포 (각 0~100)."""
    model_config = ConfigDict(populate_by_name=True)

    mok: int
    hwa: int
    to: int
    geum: int
    su: int


class IlganCardP0(BaseModel):
    """P-0 일간 카드 (value_object/ilgan_cards.py IlganCard와 매칭)."""
    model_config = ConfigDict(populate_by_name=True)

    name_kor: str
    name_han: str
    subtitle: str
    essence: str
    in_love: list[str]
    caution: str


# ═════════════════════════════════════════════════════════════════
# P-0 序 시작에 앞서
# ═════════════════════════════════════════════════════════════════


class PaidChapterP0(BaseModel):
    """P-0 — saju_pillars + ohang + ilgan_card + ai_intro."""
    model_config = ConfigDict(populate_by_name=True)

    saju_pillars: SajuPillarsP0
    ohang_strength: OhangStrength
    ohang_excess: OhangKey
    ohang_lack: OhangKey
    ilgan: str
    ilgan_card: IlganCardP0
    ai_intro: str


# ═════════════════════════════════════════════════════════════════
# P-1 一 너라는 사람 (1/2)
# ═════════════════════════════════════════════════════════════════


class CandleRow(BaseModel):
    """P-1 감정 폭발 패턴 — 단계별 촛불 row."""
    model_config = ConfigDict(populate_by_name=True)

    label: str  # "초반" / "중반" / "후반"
    flames: list[Literal["weak", "medium", "strong"]]
    desc: str
    is_peak: bool


class PaidChapterP1(BaseModel):
    """P-1 — 60갑자 + 트리거 3 + 감정 패턴."""
    model_config = ConfigDict(populate_by_name=True)

    ilgan: str  # "임수(壬水)"
    ilju: str   # "임술(壬戌)"
    love_type: str
    trigger_1: str
    trigger_2: str
    trigger_3: str
    trigger_desc_1: str
    trigger_desc_2: str
    trigger_desc_3: str
    candle_rows: list[CandleRow]
    emotion_bubble: str
    ai_opening: str
    ai_trigger: str
    ai_emotion: str


# ═════════════════════════════════════════════════════════════════
# P-2 一 너라는 사람 (2/2)
# ═════════════════════════════════════════════════════════════════


class RecoveryTimelineRow(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    time: str   # "직후" / "3개월 후" / "6개월 후"
    title: str
    desc: str


class RecoveryAccel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    value: str
    sub: str


class PaidChapterP2(BaseModel):
    """P-2 — 1-4 상처 + 1-5 회복."""
    model_config = ConfigDict(populate_by_name=True)

    # 1-4 상처받는 순간
    scenario_1_when: str
    scenario_1_desc: str
    scenario_2_when: str
    scenario_2_desc: str
    ai_hurt: str
    hurt_bubble: str
    # 1-5 이별 후 회복
    recovery_timeline: list[RecoveryTimelineRow]
    recovery_accel: RecoveryAccel
    ai_recovery: str


# ═════════════════════════════════════════════════════════════════
# P-3 二 연애를 막는 것 (1/2)
# ═════════════════════════════════════════════════════════════════


class ReverseCard(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    value: str
    sub: str


class PaidChapterP3(BaseModel):
    """P-3 — 2-1 명줄 + 2-2 반복 + 2-2-1 역이용."""
    model_config = ConfigDict(populate_by_name=True)

    ohang_excess: str  # "수(水)" 한자 포함
    blockade_card_sub: str
    ai_blockade: str
    pattern_body: str
    ai_pattern: str
    reverse_card_1: ReverseCard
    reverse_card_2: ReverseCard


# ═════════════════════════════════════════════════════════════════
# P-4 二 연애를 막는 것 (2/2)
# ═════════════════════════════════════════════════════════════════


class InfoRow(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    key: str
    val: str


class IllusionSignal(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    value: str
    sub: str


class IllusionGoodCard(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    value: str
    sub: str


class PaidChapterP4(BaseModel):
    """P-4 — 2-3 악연 + 2-4 착각 인연 식별."""
    model_config = ConfigDict(populate_by_name=True)

    # 2-3
    akyon_slot_id: str  # "m-water-yang"
    akyon_keyword_tags: list[str]
    akyon_info_rows: list[InfoRow]
    ai_akyon: str
    # 2-4
    illusion_stitle: str
    illusion_signals: list[IllusionSignal]
    illusion_good_card: IllusionGoodCard
    ai_illusion: str


# ═════════════════════════════════════════════════════════════════
# P-5 三 매력 분석
# ═════════════════════════════════════════════════════════════════


class CharmSalView(BaseModel):
    """P-5 매력살 카드 (보유한 것만)."""
    model_config = ConfigDict(populate_by_name=True)

    charm_key: str
    name_kor: str
    name_han: str
    trait: str


class StageCard(BaseModel):
    """P-5 3-2 이성이 끌리는 메커니즘 4 단계 카드."""
    model_config = ConfigDict(populate_by_name=True)

    label: str
    value: str
    sub: str


class PointCard(BaseModel):
    """P-5 3-3 감각적 매력 포인트 3 카드 (눈빛/목소리/분위기)."""
    model_config = ConfigDict(populate_by_name=True)

    label: str
    strength: Literal["weak", "medium", "strong"]
    flame_label: str
    sub: str


class PaidChapterP5(BaseModel):
    """P-5 — 매력 지수 + 매력살 카드 + 메커니즘 + 포인트."""
    model_config = ConfigDict(populate_by_name=True)

    charm_score: int
    charm_percentile: int  # 상위 N% (낮을수록 상위)
    charm_sals: list[CharmSalView]
    stage_cards: list[StageCard]
    point_cards: list[PointCard]
    ai_charm: str
    ai_mechanism: str
    ai_sense: str


# ═════════════════════════════════════════════════════════════════
# P-6 四 붉은 실이 이어진 사람 (1/2)
# ═════════════════════════════════════════════════════════════════


class InnerCard(BaseModel):
    """P-6 4-2 속마음 투시 카드 (실 상태 + 행동→심리 2)."""
    model_config = ConfigDict(populate_by_name=True)

    label: str
    value: str
    sub: str


class PaidChapterP6(BaseModel):
    """P-6 — 4-1 인연 외형/매칭/첫 만남 + 4-2 속마음 투시."""
    model_config = ConfigDict(populate_by_name=True)

    # 4-1 붉은 실이 이어진 사람
    match_slot_id: str  # "m-water-yang" 등 20 슬롯 (neutral은 caller가 None fallback)
    keyword_tags: list[str]   # 일간별 5
    info_rows: list[InfoRow]  # 일간별 8 (P-4 InfoRow 재사용)
    ai_looks: str             # 외형 묘사 (도입 + 슬롯 외형)
    ai_match: str             # 오행 매칭 + 일간 안정 짝
    ai_first_meeting: str     # 첫 만남 시나리오 (3 단락)
    bubble: str               # 강연우 멘트 (고정)
    # 4-2 속마음 투시
    inner_cards: list[InnerCard]  # 3 (실 상태 + 행동→심리 2개)
    ai_inner: str                 # 일간별 3 단락


# ═════════════════════════════════════════════════════════════════
# P-7 四 결말 예측 시나리오 (2/2)
# ═════════════════════════════════════════════════════════════════


class EndingCard(BaseModel):
    """P-7 4-3 결말 카드 (warn/good/amber 3종)."""
    model_config = ConfigDict(populate_by_name=True)

    label: str   # "지금 이대로" / "네가 먼저" / "상대가 먼저"
    value: str   # 한 줄 헤드 (일간별)
    sub: str     # 해설 (일간별)
    tone: Literal["warn", "good", "amber"]


class PaidChapterP7(BaseModel):
    """P-7 — 4-3 결말 예측 시나리오 (세 갈래 + AI 권유)."""
    model_config = ConfigDict(populate_by_name=True)

    ending_card_1: EndingCard  # warn
    ending_card_2: EndingCard  # good
    ending_card_3: EndingCard  # amber
    ai_ending: str             # 일간별 4 단락
    notice: str                # 🔮 안내문 (고정)
    bubble: str                # 강연우 멘트 (고정)


# ═════════════════════════════════════════════════════════════════
# P-8 五 12개월 운명선
# ═════════════════════════════════════════════════════════════════


class MonthRow(BaseModel):
    """P-8 5-1 타임라인 월별 row."""
    model_config = ConfigDict(populate_by_name=True)

    label: str   # "5월 (이번달)" / "6월" / "'27. 1월"
    hearts: int  # 1~5
    knot: Literal["loose", "tight", "glowing"]
    state: str   # 시작/진입/상승/피크/심화/안정/정체/재상승/2차 피크/신뢰/충전/1년차 마무리
    desc: str
    is_peak: bool = False


class PaidChapterP8(BaseModel):
    """P-8 — 5-1 12개월 운명선."""
    model_config = ConfigDict(populate_by_name=True)

    months: list[MonthRow]   # 12
    ai_intro: str            # 3 단락 (도입 + 피크 월 2개 + 일간 흐름)
    bubble: str              # 강연우 멘트 (고정)


# ═════════════════════════════════════════════════════════════════
# Chapters wrapper + Top-level response
# ═════════════════════════════════════════════════════════════════


class PaidChaptersResponse(BaseModel):
    """12 페이지 결과. 작성 완료된 P-0~P-5만 명시.

    P-6~P-11은 templates 작성 후 점진 확장. 현재는 응답에 없음 (None).
    프론트는 chapter가 undefined일 때 MOCK fallback으로 렌더.
    """
    model_config = ConfigDict(populate_by_name=True)

    p0: PaidChapterP0 | None = None
    p1: PaidChapterP1 | None = None
    p2: PaidChapterP2 | None = None
    p3: PaidChapterP3 | None = None
    p4: PaidChapterP4 | None = None
    p5: PaidChapterP5 | None = None
    p6: PaidChapterP6 | None = None
    p7: PaidChapterP7 | None = None
    p8: PaidChapterP8 | None = None
    # P-9~P-11 후속


class PaidReportStatusResponse(BaseModel):
    """`GET /api/saju/paid/{order_id}/status` 응답."""
    model_config = ConfigDict(populate_by_name=True)

    status: str  # "pending" | "ready" | "expired"


class PaidReportResponse(BaseModel):
    """`GET /api/saju/paid/{order_id}` 응답 — 12 페이지 결과."""
    model_config = ConfigDict(populate_by_name=True)

    order_id: str
    status: str
    chapters: PaidChaptersResponse  # ← dict[str, str]에서 명시 타입으로 변경
    expires_at: datetime
