"""월별 연애운 흐름(monthlyRomanceFlow) 지표 산출 서비스.

dohwa-backend src/lib/monthlyRomanceFlow.ts + transformers/monthlyRomanceFlowView.ts
포팅. 무료 응답에는 visibleMonths(현재달+다음달) + lockedSlots 메타만 노출.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol, cast

from app.domains.user.domain.value_object.saju_constants import (
    BRANCH_ELEMENT,
    HEAVENLY_STEMS,
    WUXING_DESTRUCTION,
    EarthlyBranch,
    HeavenlyStem,
    WuXing,
    calculate_ten_god,
)


class _Clock(Protocol):
    def now(self) -> datetime: ...


class _SystemClock:
    def now(self) -> datetime:
        return datetime.now()


# 양력 월 → 월지 (절기 기준 근사)
MONTH_TO_BRANCH: dict[int, EarthlyBranch] = {
    1: "축", 2: "인", 3: "묘", 4: "진", 5: "사", 6: "오",
    7: "미", 8: "신", 9: "유", 10: "술", 11: "해", 12: "자",
}

FIRST_MONTH_STEMS: dict[HeavenlyStem, HeavenlyStem] = {
    "갑": "병", "을": "무", "병": "경", "정": "임", "무": "갑",
    "기": "병", "경": "무", "신": "경", "임": "임", "계": "갑",
}

YUK_HAP_PAIRS: tuple[tuple[EarthlyBranch, EarthlyBranch], ...] = (
    ("자", "축"), ("인", "해"), ("묘", "술"),
    ("진", "유"), ("사", "신"), ("오", "미"),
)

SAM_HAP_GROUPS: tuple[tuple[EarthlyBranch, ...], ...] = (
    ("신", "자", "진"), ("해", "묘", "미"),
    ("인", "오", "술"), ("사", "유", "축"),
)

CHUNG_PAIRS: tuple[tuple[EarthlyBranch, EarthlyBranch], ...] = (
    ("자", "오"), ("축", "미"), ("인", "신"),
    ("묘", "유"), ("진", "술"), ("사", "해"),
)

YUK_HAE_PAIRS: tuple[tuple[EarthlyBranch, EarthlyBranch], ...] = (
    ("자", "미"), ("축", "오"), ("인", "사"),
    ("묘", "진"), ("신", "해"), ("유", "술"),
)

SAM_HYEONG: tuple[tuple[EarthlyBranch, ...], ...] = (
    ("인", "사", "신"),
    ("축", "술", "미"),
    ("자", "묘"),
)

DOHWA_GROUPS: tuple[tuple[frozenset[EarthlyBranch], EarthlyBranch], ...] = (
    (frozenset({"인", "오", "술"}), "묘"),
    (frozenset({"사", "유", "축"}), "오"),
    (frozenset({"신", "자", "진"}), "유"),
    (frozenset({"해", "묘", "미"}), "자"),
)

TEN_GOD_BONUS: dict[str, int] = {
    "정관": 18, "정재": 15, "편재": 12, "식신": 10,
    "상관": 6, "편관": 6, "정인": 2, "편인": 2,
    "비견": -3, "겁재": -3,
}

STEM_ELEMENTS_ORDERED: tuple[WuXing, ...] = (
    "목", "목", "화", "화", "토", "토", "금", "금", "수", "수",
)


def _get_year_stem(year: int) -> HeavenlyStem:
    base = 1984  # 갑자년
    diff = ((year - base) % 10 + 10) % 10
    return HEAVENLY_STEMS[diff]


def _get_month_stem(year_stem: HeavenlyStem, month_branch: EarthlyBranch) -> HeavenlyStem:
    first_stem = FIRST_MONTH_STEMS[year_stem]
    first_idx = HEAVENLY_STEMS.index(first_stem)
    branch_order: tuple[EarthlyBranch, ...] = (
        "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해", "자", "축",
    )
    month_offset = branch_order.index(month_branch)
    return HEAVENLY_STEMS[(first_idx + month_offset) % 10]


def _branch_relation_score(
    month_branch: EarthlyBranch, day_branch: EarthlyBranch
) -> int:
    for a, b in YUK_HAP_PAIRS:
        if (month_branch == a and day_branch == b) or (month_branch == b and day_branch == a):
            return 18
    for group in SAM_HAP_GROUPS:
        if month_branch in group and day_branch in group and month_branch != day_branch:
            return 12
    for a, b in CHUNG_PAIRS:
        if (month_branch == a and day_branch == b) or (month_branch == b and day_branch == a):
            return -12
    for a, b in YUK_HAE_PAIRS:
        if (month_branch == a and day_branch == b) or (month_branch == b and day_branch == a):
            return -8
    for group in SAM_HYEONG:
        if month_branch in group and day_branch in group and month_branch != day_branch:
            return -8
    return 0


def _dohwa_score(month_branch: EarthlyBranch, saju: dict[str, Any]) -> int:
    all_branches: set[EarthlyBranch] = {
        cast(EarthlyBranch, saju["year"]["branch"]),
        cast(EarthlyBranch, saju["month"]["branch"]),
        cast(EarthlyBranch, saju["day"]["branch"]),
        cast(EarthlyBranch, saju["hour"]["branch"]),
    }
    sin_sals = saju.get("sinSals") or []
    has_dohwa = "do_hwa_sal" in sin_sals

    for group_set, dohwa in DOHWA_GROUPS:
        if not any(b in all_branches for b in group_set):
            continue
        if month_branch == dohwa:
            return 20 if has_dohwa else 10
    return 0


def _calc_month_score(
    saju: dict[str, Any],
    month_stem: HeavenlyStem,
    month_branch: EarthlyBranch,
) -> int:
    score: float = 30  # base

    day_stem = cast(HeavenlyStem, saju["day"]["stem"])
    ten_god = calculate_ten_god(day_stem, month_stem)
    score += TEN_GOD_BONUS.get(ten_god, 0)

    score += _branch_relation_score(
        month_branch, cast(EarthlyBranch, saju["day"]["branch"])
    )

    score += _dohwa_score(month_branch, saju)

    yong_sin = saju.get("yongSin") or {}
    primary_yong_sin = yong_sin.get("primaryYongSin")
    if primary_yong_sin:
        primary_ys = cast(WuXing, primary_yong_sin)
        branch_element = BRANCH_ELEMENT[month_branch]
        if branch_element == primary_ys:
            score += 8
        kishin = WUXING_DESTRUCTION[primary_ys]
        if branch_element == kishin:
            score -= 6

        stem_idx = HEAVENLY_STEMS.index(month_stem)
        stem_element = STEM_ELEMENTS_ORDERED[stem_idx]
        if stem_element == primary_ys:
            score += 8
        if stem_element == kishin:
            score -= 6

    return max(0, min(100, round(score)))


def _pct_to_hearts(pct: int) -> int:
    if pct <= 20:
        return 1
    if pct <= 40:
        return 2
    if pct <= 65:
        return 3
    if pct <= 85:
        return 4
    return 5


class MonthlyRomanceFlowService:
    """SajuData(dict) → MonthlyRomanceFlowView(dict, camelCase).

    내부적으로 12개월을 산출한 뒤 무료 응답 형태(visibleMonths 2개 + lockedSlots
    메타)로 잘라 반환한다.

    유료 P-8 (12개월 운명선)에서는 `compute_full_months()`로 12 raw months를 받아
    직접 합성한다.
    """

    def __init__(self, clock: _Clock | None = None) -> None:
        self._clock = clock or _SystemClock()

    def compute_full_months(
        self,
        saju: dict[str, Any],
        start_year: int | None = None,
        start_month: int | None = None,
    ) -> list[dict[str, Any]]:
        """12 raw months 반환. P-8 합성용.

        Args:
            saju: 사주 raw dict
            start_year, start_month: 시작 시점. 둘 다 None이면 now 사용.

        Returns:
            [{year, month, stem, branch, romanceScore, isPeak}, ...] × 12.
            isPeak는 12개월 중 score 최대 1개에만 True.
        """
        if start_year is None or start_month is None:
            now = self._clock.now()
            start_year = now.year
            start_month = now.month

        months: list[dict[str, Any]] = []
        for i in range(12):
            y = start_year
            m = start_month + i
            if m > 12:
                m -= 12
                y += 1
            year_stem = _get_year_stem(y)
            month_branch = MONTH_TO_BRANCH[m]
            month_stem = _get_month_stem(year_stem, month_branch)
            romance_score = _calc_month_score(saju, month_stem, month_branch)
            months.append({
                "year": y, "month": m, "stem": month_stem,
                "branch": month_branch, "romanceScore": romance_score,
                "isPeak": False,
            })

        peak_index = 0
        for i in range(1, len(months)):
            if months[i]["romanceScore"] > months[peak_index]["romanceScore"]:
                peak_index = i
        months[peak_index]["isPeak"] = True
        return months

    def calculate(self, saju: dict[str, Any]) -> dict[str, Any]:
        months = self.compute_full_months(saju)

        # peak_index 재추출 (compute_full_months에서 isPeak True인 row 위치)
        peak_index = next(
            (i for i, m in enumerate(months) if m["isPeak"]), 0
        )

        first = months[0]
        second = months[1]

        v0 = {
            "monthLabel": f"{first['month']}월",
            "percentage": first["romanceScore"],
            "hearts": _pct_to_hearts(first["romanceScore"]),
            "isPeak": first["isPeak"],
        }
        v1 = {
            "monthLabel": f"{second['month']}월",
            "percentage": second["romanceScore"],
            "hearts": _pct_to_hearts(second["romanceScore"]),
            "isPeak": second["isPeak"],
        }

        peak_offset = 0 if peak_index in (0, 1) else peak_index - 1

        return {
            "visibleMonths": [v0, v1],
            "lockedSlots": {
                "totalCount": 10,
                "peakOffsetFromVisible": peak_offset,
            },
        }
