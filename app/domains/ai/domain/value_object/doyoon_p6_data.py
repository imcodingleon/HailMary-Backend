"""도윤 P-6 데이터 풀 — 四 운명의 짝 (1/2).

원본 도윤_final.html data-page-idx=6 구조 정합.
- 4-1: match_slot_id × 20 매트릭스 (f-water-yang 정성 + fallback)
- 4-2: 일간 10셀 (행동 패턴 — 관심도/표현/지속 점수 + 행동→심리 카드)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InyonInfoRow:
    key: str
    val: str


@dataclass(frozen=True)
class DoyoonInyonData:
    """인연 프로파일 — match_slot_id 기반."""
    keyword_tags: tuple[str, str, str, str, str]
    info_rows: tuple[
        InyonInfoRow, InyonInfoRow, InyonInfoRow, InyonInfoRow, InyonInfoRow,
        InyonInfoRow, InyonInfoRow, InyonInfoRow, InyonInfoRow,
    ]
    height_distribution_pct: str          # "71%"
    profile_signal_pct: str               # "78%"
    emotional_stability_multiplier: str   # "0.6배"
    stability_high_multiplier: str        # "1.7배"
    compatibility_pct: str                # "82%"
    avg_compatibility_baseline: str       # "54%"
    compatibility_lift: str               # "1.5배"
    existing_path_multiplier: str         # "2.3배"
    low_impact_pct: str                   # "73%"
    second_contact_multiplier: str        # "2.4배"
    profile_bubble: str


@dataclass(frozen=True)
class BehaviorCard:
    label: str       # "행동 → 심리 1"
    keyword: str     # "먼저 연락 안 함"
    desc: str


@dataclass(frozen=True)
class DoyoonP6IlganData:
    """일간별 P-6 — 행동 패턴 + 심리 추정."""
    interest_score: int             # 78
    expression_score: int           # 52
    durability_score: int           # 88
    behavior_cards: tuple[BehaviorCard, BehaviorCard]
    answer_length_multiplier: str   # "3.2배"
    hesitation_pct: str             # "78%"
    cut_intent_pct: str             # "12%"
    resolution_pct: str             # "87%"
    initiative_multiplier: str      # "1.4배"


# 인연 SD spotlight (4-2)
P6_SD_BEHAVIOR_ASSET: str = "dy_07"


# ── 4-1 인연 프로파일 매트릭스 (f-water-yang fallback) ──────────


_FALLBACK_KEYWORDS: tuple[str, str, str, str, str] = (
    "따뜻한 인상",
    "조용한 사람",
    "표현 일관성",
    "감정 안정",
    "기다림 가능",
)

_FALLBACK_INFO_ROWS: tuple[
    InyonInfoRow, InyonInfoRow, InyonInfoRow, InyonInfoRow, InyonInfoRow,
    InyonInfoRow, InyonInfoRow, InyonInfoRow, InyonInfoRow,
] = (
    InyonInfoRow(key="키 분포", val="평균 ±5cm 범위 표본 71%"),
    InyonInfoRow(key="체형", val="균형 잡힌 골격 · 어깨선 단단"),
    InyonInfoRow(key="얼굴상", val="선이 부드러운 둥근형 · 이마 넓음"),
    InyonInfoRow(key="이목구비", val="눈매 길고 끝 부드러움 · 입꼬리 상향"),
    InyonInfoRow(key="손·실루엣", val="손가락 길고 단정 · 자세 차분"),
    InyonInfoRow(key="성격 데이터", val="감정 변동성 평균 대비 0.6배"),
    InyonInfoRow(key="직업군", val="기획·교육·창작 계열"),
    InyonInfoRow(key="접촉 시나리오", val="기존 동선 내 재접촉 확률 높음"),
    InyonInfoRow(key="궁합 지수", val="82%"),
)


def _build_default_inyon() -> DoyoonInyonData:
    return DoyoonInyonData(
        keyword_tags=_FALLBACK_KEYWORDS,
        info_rows=_FALLBACK_INFO_ROWS,
        height_distribution_pct="71%",
        profile_signal_pct="78%",
        emotional_stability_multiplier="0.6배",
        stability_high_multiplier="1.7배",
        compatibility_pct="82%",
        avg_compatibility_baseline="54%",
        compatibility_lift="1.5배",
        existing_path_multiplier="2.3배",
        low_impact_pct="73%",
        second_contact_multiplier="2.4배",
        profile_bubble="이 사람, {USER_NAME}님 주변에 이미 있을 확률이 높아요. 데이터가 그렇게 가리키고 있어요.",
    )


_ALL_INYON_SLOTS: tuple[str, ...] = tuple(
    f"{g}-{el}-{yy}"
    for g in ("m", "f")
    for el in ("wood", "fire", "earth", "metal", "water")
    for yy in ("yang", "yin")
)

DOYOON_INYON_BY_SLOT: dict[str, DoyoonInyonData] = {
    slot: _build_default_inyon() for slot in _ALL_INYON_SLOTS
}
DOYOON_INYON_BY_SLOT["m-neutral"] = _build_default_inyon()
DOYOON_INYON_BY_SLOT["f-neutral"] = _build_default_inyon()


# ── 4-2 행동 패턴 (일간 10셀) ──────────────────────────────────


_COMMON_BEHAVIOR_CARDS: tuple[BehaviorCard, BehaviorCard] = (
    BehaviorCard(
        label="행동 → 심리 1",
        keyword="먼저 연락 안 함",
        desc="관심 부재 신호 아닙니다. 표현 의지 점수가 낮아 망설이는 단계입니다.",
    ),
    BehaviorCard(
        label="행동 → 심리 2",
        keyword="대화는 길게 받음",
        desc="관심도와 지속 가능성이 일치하는 응답 패턴입니다.",
    ),
)


DOYOON_P6_DATA: dict[str, DoyoonP6IlganData] = {
    "임수": DoyoonP6IlganData(
        interest_score=78, expression_score=52, durability_score=88,
        behavior_cards=_COMMON_BEHAVIOR_CARDS,
        answer_length_multiplier="3.2배", hesitation_pct="78%",
        cut_intent_pct="12%", resolution_pct="87%",
        initiative_multiplier="1.4배",
    ),
    "갑목": DoyoonP6IlganData(
        interest_score=72, expression_score=68, durability_score=82,
        behavior_cards=_COMMON_BEHAVIOR_CARDS,
        answer_length_multiplier="2.8배", hesitation_pct="64%",
        cut_intent_pct="18%", resolution_pct="82%",
        initiative_multiplier="1.3배",
    ),
    "을목": DoyoonP6IlganData(
        interest_score=76, expression_score=58, durability_score=85,
        behavior_cards=_COMMON_BEHAVIOR_CARDS,
        answer_length_multiplier="3.0배", hesitation_pct="72%",
        cut_intent_pct="14%", resolution_pct="84%",
        initiative_multiplier="1.4배",
    ),
    "병화": DoyoonP6IlganData(
        interest_score=82, expression_score=74, durability_score=78,
        behavior_cards=_COMMON_BEHAVIOR_CARDS,
        answer_length_multiplier="2.6배", hesitation_pct="58%",
        cut_intent_pct="22%", resolution_pct="79%",
        initiative_multiplier="1.2배",
    ),
    "정화": DoyoonP6IlganData(
        interest_score=76, expression_score=54, durability_score=90,
        behavior_cards=_COMMON_BEHAVIOR_CARDS,
        answer_length_multiplier="3.4배", hesitation_pct="80%",
        cut_intent_pct="10%", resolution_pct="88%",
        initiative_multiplier="1.5배",
    ),
    "무토": DoyoonP6IlganData(
        interest_score=74, expression_score=56, durability_score=92,
        behavior_cards=_COMMON_BEHAVIOR_CARDS,
        answer_length_multiplier="3.0배", hesitation_pct="74%",
        cut_intent_pct="12%", resolution_pct="86%",
        initiative_multiplier="1.4배",
    ),
    "기토": DoyoonP6IlganData(
        interest_score=78, expression_score=58, durability_score=88,
        behavior_cards=_COMMON_BEHAVIOR_CARDS,
        answer_length_multiplier="3.1배", hesitation_pct="76%",
        cut_intent_pct="13%", resolution_pct="86%",
        initiative_multiplier="1.4배",
    ),
    "경금": DoyoonP6IlganData(
        interest_score=72, expression_score=66, durability_score=84,
        behavior_cards=_COMMON_BEHAVIOR_CARDS,
        answer_length_multiplier="2.7배", hesitation_pct="62%",
        cut_intent_pct="20%", resolution_pct="81%",
        initiative_multiplier="1.3배",
    ),
    "신금": DoyoonP6IlganData(
        interest_score=76, expression_score=54, durability_score=89,
        behavior_cards=_COMMON_BEHAVIOR_CARDS,
        answer_length_multiplier="3.3배", hesitation_pct="78%",
        cut_intent_pct="11%", resolution_pct="87%",
        initiative_multiplier="1.5배",
    ),
    "계수": DoyoonP6IlganData(
        interest_score=80, expression_score=50, durability_score=89,
        behavior_cards=_COMMON_BEHAVIOR_CARDS,
        answer_length_multiplier="3.4배", hesitation_pct="82%",
        cut_intent_pct="10%", resolution_pct="89%",
        initiative_multiplier="1.5배",
    ),
}


VALID_DOYOON_P6_ILGAN: frozenset[str] = frozenset(DOYOON_P6_DATA.keys())
