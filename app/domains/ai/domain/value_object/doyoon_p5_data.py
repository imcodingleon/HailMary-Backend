"""도윤 P-5 데이터 풀 — 三 매력 분석.

원본 도윤_final.html data-page-idx=5 구조 정합.
- 3-1: 6축 Radar (존재감/매력살/목소리/깊이감/분위기/눈빛) + 강점 2축
- 3-2: 4단계 전환율 (30→55→72→88) 고정
- 3-3: 4 변수 MeterBar (존재감/깊이감/표현/반응 점수)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RadarAxis:
    """레이더 축 1개 (6축 중)."""
    name: str        # "존재감"
    value: int       # 0~100 점수


@dataclass(frozen=True)
class AppealMeter:
    """3-3 호감 유발 4 변수 — meter bar."""
    name: str        # "존재감"
    value: int       # 0~100


@dataclass(frozen=True)
class DoyoonP5IlganData:
    """일간별 P-5 데이터."""
    # 3-1
    radar: tuple[RadarAxis, RadarAxis, RadarAxis, RadarAxis, RadarAxis, RadarAxis]
    strength_axis_1: str           # "존재감"
    strength_axis_2: str           # "깊이감"
    strength_multiplier: str       # "1.7배"
    conscious_gap_multiplier: str  # "2.4배"
    charm_bubble: str
    sd_charm_asset: str            # "dy_06"
    # 3-2 전환율 (모든 일간 공통 30/55/72/88)
    second_meeting_multiplier: str # "1.4배"
    final_gap_pct: str             # "38%p"
    # 3-3 호감 유발 4 변수
    appeal_meters: tuple[AppealMeter, AppealMeter, AppealMeter, AppealMeter]
    weakness_axis_1: str           # "표현 일관성"
    weakness_axis_2: str           # "반응 속도"
    appeal_boost_pct: str          # "26%"


# 4단계 전환율 (모든 일간 공통, 원본 고정)
CONVERSION_STEPS: tuple[tuple[str, int], ...] = (
    ("첫 인상", 30),
    ("반복 접촉", 55),
    ("익숙함", 72),
    ("끌림", 88),
)


DOYOON_P5_DATA: dict[str, DoyoonP5IlganData] = {
    # ── 임수 (원본 더미) ───────────────────────────────────────
    "임수": DoyoonP5IlganData(
        radar=(
            RadarAxis(name="존재감", value=92),
            RadarAxis(name="매력살", value=72),
            RadarAxis(name="목소리", value=68),
            RadarAxis(name="깊이감", value=88),
            RadarAxis(name="분위기", value=78),
            RadarAxis(name="눈빛", value=82),
        ),
        strength_axis_1="존재감",
        strength_axis_2="깊이감",
        strength_multiplier="1.7배",
        conscious_gap_multiplier="2.4배",
        charm_bubble="이거 그냥 놔두기엔 좀 아깝지 않아요?",
        sd_charm_asset="dy_06",
        second_meeting_multiplier="1.4배",
        final_gap_pct="38%p",
        appeal_meters=(
            AppealMeter(name="존재감", value=92),
            AppealMeter(name="깊이감", value=85),
            AppealMeter(name="표현 일관성", value=64),
            AppealMeter(name="반응 속도", value=71),
        ),
        weakness_axis_1="표현 일관성",
        weakness_axis_2="반응 속도",
        appeal_boost_pct="26%",
    ),
    # ── 갑목 ───────────────────────────────────────────────────
    "갑목": DoyoonP5IlganData(
        radar=(
            RadarAxis(name="존재감", value=88),
            RadarAxis(name="매력살", value=70),
            RadarAxis(name="목소리", value=75),
            RadarAxis(name="깊이감", value=72),
            RadarAxis(name="분위기", value=66),
            RadarAxis(name="눈빛", value=80),
        ),
        strength_axis_1="존재감",
        strength_axis_2="눈빛",
        strength_multiplier="1.6배",
        conscious_gap_multiplier="2.0배",
        charm_bubble="단호한 결단력이 매력의 핵심 변수예요.",
        sd_charm_asset="dy_06",
        second_meeting_multiplier="1.3배",
        final_gap_pct="34%p",
        appeal_meters=(
            AppealMeter(name="존재감", value=88),
            AppealMeter(name="눈빛", value=80),
            AppealMeter(name="부드러움", value=62),
            AppealMeter(name="유연성", value=68),
        ),
        weakness_axis_1="부드러움",
        weakness_axis_2="유연성",
        appeal_boost_pct="24%",
    ),
    # ── 을목 ───────────────────────────────────────────────────
    "을목": DoyoonP5IlganData(
        radar=(
            RadarAxis(name="존재감", value=72),
            RadarAxis(name="매력살", value=80),
            RadarAxis(name="목소리", value=76),
            RadarAxis(name="깊이감", value=78),
            RadarAxis(name="분위기", value=86),
            RadarAxis(name="눈빛", value=74),
        ),
        strength_axis_1="분위기",
        strength_axis_2="매력살",
        strength_multiplier="1.5배",
        conscious_gap_multiplier="1.9배",
        charm_bubble="적응형 매력이라 상대 환경에 맞춰 곡선이 다양해요.",
        sd_charm_asset="dy_06",
        second_meeting_multiplier="1.3배",
        final_gap_pct="32%p",
        appeal_meters=(
            AppealMeter(name="분위기", value=86),
            AppealMeter(name="매력살", value=80),
            AppealMeter(name="자기 표현", value=60),
            AppealMeter(name="단호함", value=58),
        ),
        weakness_axis_1="자기 표현",
        weakness_axis_2="단호함",
        appeal_boost_pct="28%",
    ),
    # ── 병화 ───────────────────────────────────────────────────
    "병화": DoyoonP5IlganData(
        radar=(
            RadarAxis(name="존재감", value=94),
            RadarAxis(name="매력살", value=82),
            RadarAxis(name="목소리", value=86),
            RadarAxis(name="깊이감", value=64),
            RadarAxis(name="분위기", value=70),
            RadarAxis(name="눈빛", value=88),
        ),
        strength_axis_1="존재감",
        strength_axis_2="눈빛",
        strength_multiplier="1.8배",
        conscious_gap_multiplier="1.7배",
        charm_bubble="발산 매력이 평균 대비 압도적으로 큰 케이스예요.",
        sd_charm_asset="dy_06",
        second_meeting_multiplier="1.2배",
        final_gap_pct="30%p",
        appeal_meters=(
            AppealMeter(name="존재감", value=94),
            AppealMeter(name="눈빛", value=88),
            AppealMeter(name="지속 집중", value=58),
            AppealMeter(name="페이스 조절", value=62),
        ),
        weakness_axis_1="지속 집중",
        weakness_axis_2="페이스 조절",
        appeal_boost_pct="25%",
    ),
    # ── 정화 ───────────────────────────────────────────────────
    "정화": DoyoonP5IlganData(
        radar=(
            RadarAxis(name="존재감", value=70),
            RadarAxis(name="매력살", value=76),
            RadarAxis(name="목소리", value=72),
            RadarAxis(name="깊이감", value=92),
            RadarAxis(name="분위기", value=84),
            RadarAxis(name="눈빛", value=80),
        ),
        strength_axis_1="깊이감",
        strength_axis_2="분위기",
        strength_multiplier="1.7배",
        conscious_gap_multiplier="2.3배",
        charm_bubble="잔잔한 깊이감이 핵심 변수예요. 발산보다 누적.",
        sd_charm_asset="dy_06",
        second_meeting_multiplier="1.5배",
        final_gap_pct="42%p",
        appeal_meters=(
            AppealMeter(name="깊이감", value=92),
            AppealMeter(name="분위기", value=84),
            AppealMeter(name="표현 빈도", value=60),
            AppealMeter(name="초반 가시성", value=58),
        ),
        weakness_axis_1="표현 빈도",
        weakness_axis_2="초반 가시성",
        appeal_boost_pct="32%",
    ),
    # ── 무토 ───────────────────────────────────────────────────
    "무토": DoyoonP5IlganData(
        radar=(
            RadarAxis(name="존재감", value=86),
            RadarAxis(name="매력살", value=68),
            RadarAxis(name="목소리", value=78),
            RadarAxis(name="깊이감", value=82),
            RadarAxis(name="분위기", value=80),
            RadarAxis(name="눈빛", value=72),
        ),
        strength_axis_1="존재감",
        strength_axis_2="깊이감",
        strength_multiplier="1.6배",
        conscious_gap_multiplier="1.8배",
        charm_bubble="안정형 매력 — 시간이 갈수록 강도가 오르는 케이스예요.",
        sd_charm_asset="dy_06",
        second_meeting_multiplier="1.5배",
        final_gap_pct="40%p",
        appeal_meters=(
            AppealMeter(name="존재감", value=86),
            AppealMeter(name="깊이감", value=82),
            AppealMeter(name="초반 임팩트", value=60),
            AppealMeter(name="변화 신호", value=62),
        ),
        weakness_axis_1="초반 임팩트",
        weakness_axis_2="변화 신호",
        appeal_boost_pct="29%",
    ),
    # ── 기토 ───────────────────────────────────────────────────
    "기토": DoyoonP5IlganData(
        radar=(
            RadarAxis(name="존재감", value=74),
            RadarAxis(name="매력살", value=78),
            RadarAxis(name="목소리", value=80),
            RadarAxis(name="깊이감", value=84),
            RadarAxis(name="분위기", value=88),
            RadarAxis(name="눈빛", value=76),
        ),
        strength_axis_1="분위기",
        strength_axis_2="깊이감",
        strength_multiplier="1.6배",
        conscious_gap_multiplier="2.0배",
        charm_bubble="포근한 분위기가 핵심 변수예요. 헌신형 매력.",
        sd_charm_asset="dy_06",
        second_meeting_multiplier="1.4배",
        final_gap_pct="36%p",
        appeal_meters=(
            AppealMeter(name="분위기", value=88),
            AppealMeter(name="깊이감", value=84),
            AppealMeter(name="자기 어필", value=58),
            AppealMeter(name="명시적 표현", value=62),
        ),
        weakness_axis_1="자기 어필",
        weakness_axis_2="명시적 표현",
        appeal_boost_pct="27%",
    ),
    # ── 경금 ───────────────────────────────────────────────────
    "경금": DoyoonP5IlganData(
        radar=(
            RadarAxis(name="존재감", value=90),
            RadarAxis(name="매력살", value=70),
            RadarAxis(name="목소리", value=82),
            RadarAxis(name="깊이감", value=72),
            RadarAxis(name="분위기", value=66),
            RadarAxis(name="눈빛", value=86),
        ),
        strength_axis_1="존재감",
        strength_axis_2="눈빛",
        strength_multiplier="1.7배",
        conscious_gap_multiplier="1.9배",
        charm_bubble="명확한 눈빛이 매력 변수의 정점이에요.",
        sd_charm_asset="dy_06",
        second_meeting_multiplier="1.3배",
        final_gap_pct="33%p",
        appeal_meters=(
            AppealMeter(name="존재감", value=90),
            AppealMeter(name="눈빛", value=86),
            AppealMeter(name="부드러움", value=60),
            AppealMeter(name="감정 표현", value=64),
        ),
        weakness_axis_1="부드러움",
        weakness_axis_2="감정 표현",
        appeal_boost_pct="25%",
    ),
    # ── 신금 ───────────────────────────────────────────────────
    "신금": DoyoonP5IlganData(
        radar=(
            RadarAxis(name="존재감", value=78),
            RadarAxis(name="매력살", value=88),
            RadarAxis(name="목소리", value=74),
            RadarAxis(name="깊이감", value=82),
            RadarAxis(name="분위기", value=86),
            RadarAxis(name="눈빛", value=80),
        ),
        strength_axis_1="매력살",
        strength_axis_2="분위기",
        strength_multiplier="1.6배",
        conscious_gap_multiplier="2.1배",
        charm_bubble="단정 매력이 측정값 최상위 케이스예요.",
        sd_charm_asset="dy_06",
        second_meeting_multiplier="1.4배",
        final_gap_pct="36%p",
        appeal_meters=(
            AppealMeter(name="매력살", value=88),
            AppealMeter(name="분위기", value=86),
            AppealMeter(name="자기 보호 완화", value=58),
            AppealMeter(name="진입 속도", value=60),
        ),
        weakness_axis_1="자기 보호 완화",
        weakness_axis_2="진입 속도",
        appeal_boost_pct="28%",
    ),
    # ── 계수 ───────────────────────────────────────────────────
    "계수": DoyoonP5IlganData(
        radar=(
            RadarAxis(name="존재감", value=68),
            RadarAxis(name="매력살", value=74),
            RadarAxis(name="목소리", value=72),
            RadarAxis(name="깊이감", value=90),
            RadarAxis(name="분위기", value=88),
            RadarAxis(name="눈빛", value=78),
        ),
        strength_axis_1="깊이감",
        strength_axis_2="분위기",
        strength_multiplier="1.8배",
        conscious_gap_multiplier="2.5배",
        charm_bubble="섬세 잠재 매력 — 의식화 시 변동성이 가장 큰 케이스예요.",
        sd_charm_asset="dy_06",
        second_meeting_multiplier="1.6배",
        final_gap_pct="44%p",
        appeal_meters=(
            AppealMeter(name="깊이감", value=90),
            AppealMeter(name="분위기", value=88),
            AppealMeter(name="명시 표현", value=56),
            AppealMeter(name="초반 가시성", value=60),
        ),
        weakness_axis_1="명시 표현",
        weakness_axis_2="초반 가시성",
        appeal_boost_pct="34%",
    ),
}


VALID_DOYOON_P5_ILGAN: frozenset[str] = frozenset(DOYOON_P5_DATA.keys())
