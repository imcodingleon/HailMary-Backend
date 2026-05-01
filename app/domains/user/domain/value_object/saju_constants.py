"""사주 분석 공통 상수/순수 헬퍼.

dohwa-backend의 lib/twelve_phases.ts, lib/ten_gods.ts, data/wuxing.ts,
data/heavenly_stems.ts 를 hailmary 도메인 레이어로 포팅한 것.
순수 Python — 외부 라이브러리 import 없음.
"""

from __future__ import annotations

from typing import Literal

HeavenlyStem = Literal["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"]
EarthlyBranch = Literal["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]
WuXing = Literal["목", "화", "토", "금", "수"]
YinYang = Literal["음", "양"]
TenGod = Literal[
    "비견", "겁재", "식신", "상관", "편재", "정재", "편관", "정관", "편인", "정인"
]
TwelvePhase = Literal[
    "jangsaeng", "mokyok", "gwandae", "geonrok", "jewang", "soe",
    "byeong", "sa", "myo", "jeol", "tae", "yang",
]
PillarKey = Literal["year", "month", "day", "hour"]


HEAVENLY_STEMS: tuple[HeavenlyStem, ...] = (
    "갑", "을", "병", "정", "무", "기", "경", "신", "임", "계",
)


STEM_ELEMENT: dict[HeavenlyStem, WuXing] = {
    "갑": "목", "을": "목",
    "병": "화", "정": "화",
    "무": "토", "기": "토",
    "경": "금", "신": "금",
    "임": "수", "계": "수",
}

STEM_YIN_YANG: dict[HeavenlyStem, YinYang] = {
    "갑": "양", "을": "음",
    "병": "양", "정": "음",
    "무": "양", "기": "음",
    "경": "양", "신": "음",
    "임": "양", "계": "음",
}


WUXING_GENERATION: dict[WuXing, WuXing] = {
    "목": "화", "화": "토", "토": "금", "금": "수", "수": "목",
}

WUXING_DESTRUCTION: dict[WuXing, WuXing] = {
    "목": "토", "화": "금", "토": "수", "금": "목", "수": "화",
}


# ── 십이운성 테이블 (장생 기준 양간 순행 / 음간 역행) ────────────────────────────

_JANGSAENG_BRANCH: dict[HeavenlyStem, EarthlyBranch] = {
    "갑": "해", "을": "오",
    "병": "인", "정": "유",
    "무": "인", "기": "유",
    "경": "사", "신": "자",
    "임": "신", "계": "묘",
}

_STEM_IS_YANG: dict[HeavenlyStem, bool] = {
    s: (yy == "양") for s, yy in STEM_YIN_YANG.items()
}

_BRANCH_ORDER: tuple[EarthlyBranch, ...] = (
    "자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해",
)

_TWELVE_PHASE_SEQUENCE: tuple[TwelvePhase, ...] = (
    "jangsaeng", "mokyok", "gwandae", "geonrok", "jewang", "soe",
    "byeong", "sa", "myo", "jeol", "tae", "yang",
)


def _build_twelve_phase_table() -> dict[HeavenlyStem, dict[EarthlyBranch, TwelvePhase]]:
    table: dict[HeavenlyStem, dict[EarthlyBranch, TwelvePhase]] = {}
    for stem in HEAVENLY_STEMS:
        start_branch = _JANGSAENG_BRANCH[stem]
        start_idx = _BRANCH_ORDER.index(start_branch)
        direction = 1 if _STEM_IS_YANG[stem] else -1
        row: dict[EarthlyBranch, TwelvePhase] = {}
        for step in range(12):
            branch_idx = ((start_idx + direction * step) % 12 + 12) % 12
            branch = _BRANCH_ORDER[branch_idx]
            row[branch] = _TWELVE_PHASE_SEQUENCE[step]
        table[stem] = row
    return table


TWELVE_PHASES_TABLE: dict[HeavenlyStem, dict[EarthlyBranch, TwelvePhase]] = (
    _build_twelve_phase_table()
)


def get_twelve_phase(day_stem: HeavenlyStem, branch: EarthlyBranch) -> TwelvePhase:
    return TWELVE_PHASES_TABLE[day_stem][branch]


# ── 십성 계산 ───────────────────────────────────────────────────────────────

def calculate_ten_god(day_stem: HeavenlyStem, target_stem: HeavenlyStem) -> TenGod:
    day_el = STEM_ELEMENT[day_stem]
    day_yy = STEM_YIN_YANG[day_stem]
    tgt_el = STEM_ELEMENT[target_stem]
    tgt_yy = STEM_YIN_YANG[target_stem]

    if day_el == tgt_el:
        return "비견" if day_yy == tgt_yy else "겁재"

    if WUXING_GENERATION[day_el] == tgt_el:
        return "식신" if day_yy == tgt_yy else "상관"

    if WUXING_DESTRUCTION[day_el] == tgt_el:
        return "편재" if day_yy == tgt_yy else "정재"

    if WUXING_DESTRUCTION[tgt_el] == day_el:
        return "편관" if day_yy == tgt_yy else "정관"

    if WUXING_GENERATION[tgt_el] == day_el:
        return "편인" if day_yy == tgt_yy else "정인"

    raise ValueError(f"십성 계산 오류: {day_stem}({day_el}) - {target_stem}({tgt_el})")


# 지지 → 정기(正氣) 대표 천간 폴백
BRANCH_PRIMARY_STEM: dict[EarthlyBranch, HeavenlyStem] = {
    "자": "계", "축": "기", "인": "갑", "묘": "을", "진": "무", "사": "병",
    "오": "정", "미": "기", "신": "경", "유": "신", "술": "무", "해": "임",
}

# 지지 → 오행 매핑 (간이)
BRANCH_ELEMENT: dict[EarthlyBranch, WuXing] = {
    "자": "수", "축": "토", "인": "목", "묘": "목", "진": "토", "사": "화",
    "오": "화", "미": "토", "신": "금", "유": "금", "술": "토", "해": "수",
}
