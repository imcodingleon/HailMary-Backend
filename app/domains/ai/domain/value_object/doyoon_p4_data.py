"""도윤 P-4 데이터 풀 — 二 연애를 막는 것 (2/2).

원본 도윤_final.html data-page-idx=4 구조 정합.

- 2-3 비호환: akyon_slot_id (20 slot) 매트릭스. 본 세션은 m-water-yang 정성 +
  나머지 19 slot fallback (사용자 검수 후 점진 확대).
- 2-4 착각 인연: 일간 10셀 (착각 신호 3종)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AkyonInfoRow:
    key: str
    val: str


@dataclass(frozen=True)
class DoyoonAkyonData:
    """비호환 프로파일 — akyon_slot_id 기반."""
    keyword_tags: tuple[str, str, str, str, str]   # 5 태그
    info_rows: tuple[
        AkyonInfoRow, AkyonInfoRow, AkyonInfoRow, AkyonInfoRow, AkyonInfoRow,
        AkyonInfoRow, AkyonInfoRow, AkyonInfoRow, AkyonInfoRow, AkyonInfoRow,
    ]                                              # 10 row
    height_distribution_pct: str                   # "64%"
    impression_first: str                          # "91"
    impression_6m: str                             # "14"
    impression_gap: str                            # "77"
    emotional_volatility_multiplier: str           # "1.9배"
    common_signal_pct: str                         # "71%"
    sd_avatar_asset: str                           # "dy_08"
    akyon_bubble: str


@dataclass(frozen=True)
class IllusionSign:
    """착각 인연 오인 신호 — card-warn × 3."""
    keyword: str          # "첫 만남 점수 90+"
    pct: str              # "78%"
    desc: str


@dataclass(frozen=True)
class DoyoonP4IlganData:
    """일간별 P-4 데이터 — 착각 인연."""
    illusion_multiplier: str          # "1.3배" — 평균 대비 착각 발생률
    illusion_signs: tuple[IllusionSign, IllusionSign, IllusionSign]
    illusion_bubble: str              # 클로징 멘트


# ── 2-3 비호환 매트릭스 (m-water-yang 정성 + fallback 동일) ──────


_FALLBACK_KEYWORDS: tuple[str, str, str, str, str] = (
    "차가운 인상",
    "감정 변동 큼",
    "약속 일관성 낮음",
    "자기중심 응답",
    "반응 속도 빠름",
)

_FALLBACK_INFO_ROWS: tuple[
    AkyonInfoRow, AkyonInfoRow, AkyonInfoRow, AkyonInfoRow, AkyonInfoRow,
    AkyonInfoRow, AkyonInfoRow, AkyonInfoRow, AkyonInfoRow, AkyonInfoRow,
] = (
    AkyonInfoRow(key="키 분포", val="평균보다 +5cm 이상 표본 64%"),
    AkyonInfoRow(key="체형", val="마른 골격 · 어깨 좁은 편"),
    AkyonInfoRow(key="얼굴상", val="광대 도드라짐 · 턱선 각짐"),
    AkyonInfoRow(key="이목구비", val="얇은 입술 · 눈꼬리 상향"),
    AkyonInfoRow(key="스타일 특성", val="시즌 트렌드 추종도 높음"),
    AkyonInfoRow(key="인상 점수", val="첫인상 강도 91 / 6개월 호감 14"),
    AkyonInfoRow(key="감정 변동성", val="평균 대비 1.9배"),
    AkyonInfoRow(key="행동 신호", val="초기 과접근, 중반 급랭각"),
    AkyonInfoRow(key="비호환 이유", val="감정 주파수 불일치 87%"),
    AkyonInfoRow(key="대응 전략", val="초기 신호 2개 이상 시 즉시 거리 조정"),
)


def _build_default_akyon() -> DoyoonAkyonData:
    return DoyoonAkyonData(
        keyword_tags=_FALLBACK_KEYWORDS,
        info_rows=_FALLBACK_INFO_ROWS,
        height_distribution_pct="64%",
        impression_first="91",
        impression_6m="14",
        impression_gap="77",
        emotional_volatility_multiplier="1.9배",
        common_signal_pct="71%",
        sd_avatar_asset="dy_08",
        akyon_bubble="이 신호 두 개 이상 보이면 그냥 다음으로 넘어가세요. 시간이 아까워요.",
    )


# 20 slot 모두 동일 fallback (사용자 검수 후 slot별 다양화)
_ALL_AKYON_SLOTS: tuple[str, ...] = tuple(
    f"{g}-{el}-{yy}"
    for g in ("m", "f")
    for el in ("wood", "fire", "earth", "metal", "water")
    for yy in ("yang", "yin")
)

DOYOON_AKYON_BY_SLOT: dict[str, DoyoonAkyonData] = {
    slot: _build_default_akyon() for slot in _ALL_AKYON_SLOTS
}
# m-neutral / f-neutral fallback (spouse_avoid가 둘 다 반환 가능)
DOYOON_AKYON_BY_SLOT["m-neutral"] = _build_default_akyon()
DOYOON_AKYON_BY_SLOT["f-neutral"] = _build_default_akyon()


# ── 2-4 착각 인연 (일간 10셀) ────────────────────────────────────

# 임수 정성 + 나머지 9셀 압축. 모든 일간 공통: 오인 신호 3종 (78/64/71)
_COMMON_SIGNS: tuple[IllusionSign, IllusionSign, IllusionSign] = (
    IllusionSign(
        keyword="첫 만남 점수 90+",
        pct="78%",
        desc="초기 호감도가 비정상적으로 높음. 평균 사례는 65~75 분포.",
    ),
    IllusionSign(
        keyword="2주차 연락 빈도 급감",
        pct="64%",
        desc="초반 폭발적 접촉 후 2주 안에 빈도 60% 이상 감소.",
    ),
    IllusionSign(
        keyword="3개월차 대화 온도 -38%",
        pct="71%",
        desc="대화 길이·답장 속도가 같은 시점 평균 대비 38% 하락.",
    ),
)


DOYOON_P4_DATA: dict[str, DoyoonP4IlganData] = {
    "임수": DoyoonP4IlganData(
        illusion_multiplier="1.3배",
        illusion_signs=_COMMON_SIGNS,
        illusion_bubble="첫 만남 점수에 속지 마세요. 3개월차 기울기가 진짜 지표예요.",
    ),
    "갑목": DoyoonP4IlganData(
        illusion_multiplier="1.1배",
        illusion_signs=_COMMON_SIGNS,
        illusion_bubble="단호함이 강점이지만, 첫 인상 강도에 가중치 주지 마세요.",
    ),
    "을목": DoyoonP4IlganData(
        illusion_multiplier="1.2배",
        illusion_signs=_COMMON_SIGNS,
        illusion_bubble="환경 적응 케이스라 초기 끌림 보존 시간이 길어요. 객관 지표 우선.",
    ),
    "병화": DoyoonP4IlganData(
        illusion_multiplier="1.4배",
        illusion_signs=_COMMON_SIGNS,
        illusion_bubble="고텐션 케이스라 첫 만남 점수에 휘둘리기 가장 쉬워요.",
    ),
    "정화": DoyoonP4IlganData(
        illusion_multiplier="1.3배",
        illusion_signs=_COMMON_SIGNS,
        illusion_bubble="한 사람 집중 케이스라 초기 강한 끌림을 운명으로 오인하기 쉬워요.",
    ),
    "무토": DoyoonP4IlganData(
        illusion_multiplier="1.0배",
        illusion_signs=_COMMON_SIGNS,
        illusion_bubble="안정 케이스라 평균 수준 오인률이지만, 3개월차 검증은 필수.",
    ),
    "기토": DoyoonP4IlganData(
        illusion_multiplier="1.2배",
        illusion_signs=_COMMON_SIGNS,
        illusion_bubble="헌신 케이스라 초기 도움 신호를 운명으로 인지하기 쉬워요.",
    ),
    "경금": DoyoonP4IlganData(
        illusion_multiplier="1.0배",
        illusion_signs=_COMMON_SIGNS,
        illusion_bubble="명확성 케이스라 오인률 낮지만, 첫 만남 강도에 한 번은 흔들려요.",
    ),
    "신금": DoyoonP4IlganData(
        illusion_multiplier="1.3배",
        illusion_signs=_COMMON_SIGNS,
        illusion_bubble="섬세 케이스라 디테일 신호 한 가지가 운명 인식 트리거가 돼요.",
    ),
    "계수": DoyoonP4IlganData(
        illusion_multiplier="1.4배",
        illusion_signs=_COMMON_SIGNS,
        illusion_bubble="섬세 잠재 신호 케이스라 미세 끌림이 누적되어 오인되기 쉬워요.",
    ),
}


# 결정 분기점 (모든 일간 공통)
DECISIVE_GRADIENT_LABEL: str = "3개월차 호감 곡선의 기울기"
REAL_GROWTH_PCT: str = "+18%"
FAKE_DROP_PCT: str = "-38%"
ACCURACY_MULTIPLIER: str = "9배"


VALID_DOYOON_P4_ILGAN: frozenset[str] = frozenset(DOYOON_P4_DATA.keys())
