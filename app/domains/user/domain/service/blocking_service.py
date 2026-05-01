"""연애 장애물(blocking) 지표 산출 서비스.

dohwa-backend src/lib/blockingProfile.ts + transformers/blockingView.ts 포팅.
출력은 십성 카운트 수치 미노출 — 라벨 키만 반환.
"""

from __future__ import annotations

from typing import Any, cast

from app.domains.user.domain.value_object.saju_constants import (
    BRANCH_PRIMARY_STEM,
    EarthlyBranch,
    HeavenlyStem,
    PillarKey,
    WuXing,
    calculate_ten_god,
)

WUXING_PRIORITY: tuple[WuXing, ...] = ("목", "화", "토", "금", "수")


def _resolve_element_overload(saju: dict[str, Any]) -> WuXing | None:
    counts = saju.get("wuxingCount") or {}
    max_count = 0
    result: WuXing | None = None
    for el in WUXING_PRIORITY:
        count = counts.get(el, 0)
        if count >= 3 and count > max_count:
            max_count = count
            result = el
    return result


def _count_ten_gods(
    saju: dict[str, Any], time_unknown: bool
) -> dict[str, float]:
    counts: dict[str, float] = {
        "비견": 0, "겁재": 0, "식신": 0, "상관": 0,
        "편재": 0, "정재": 0, "편관": 0, "정관": 0,
        "편인": 0, "정인": 0,
    }
    day_stem = cast(HeavenlyStem, saju["day"]["stem"])
    keys: list[PillarKey] = (
        ["year", "month", "day"]
        if time_unknown
        else ["year", "month", "day", "hour"]
    )
    ji_jang_gan = saju.get("jiJangGan") or {}

    for key in keys:
        pillar = saju[key]
        heaven_god = calculate_ten_god(day_stem, cast(HeavenlyStem, pillar["stem"]))
        counts[heaven_god] += 1

        primary = (ji_jang_gan.get(key) or {}).get("primary") or {}
        branch_stem = (
            primary.get("stem")
            if primary.get("stem")
            else BRANCH_PRIMARY_STEM[cast(EarthlyBranch, pillar["branch"])]
        )
        earth_god = calculate_ten_god(day_stem, cast(HeavenlyStem, branch_stem))
        counts[earth_god] += 1

    return counts


def _resolve_ten_god_pattern(counts: dict[str, float]) -> str | None:
    bigyeop = counts["비견"] + counts["겁재"]
    siksang = counts["식신"] + counts["상관"]
    gwanseong = counts["편관"] + counts["정관"]
    jaeseong = counts["편재"] + counts["정재"]
    inseong = counts["편인"] + counts["정인"]

    if bigyeop >= 3:
        return "stubborn_rivalry"
    if siksang >= 4 or counts["상관"] >= 3:
        return "expression_surplus"
    if gwanseong >= 4 or counts["편관"] >= 3:
        return "officer_pressure"
    if jaeseong >= 4 or counts["편재"] >= 3:
        return "wealth_scattered"
    if inseong >= 4 or counts["편인"] >= 3:
        return "resource_dependent"
    if siksang == 0:
        return "expression_absent"
    if gwanseong == 0:
        return "officer_absent"
    if jaeseong == 0:
        return "wealth_absent"
    return None


class BlockingService:
    """SajuData(dict) → BlockingView(dict, camelCase)."""

    def calculate(self, saju: dict[str, Any], time_unknown: bool = False) -> dict[str, Any]:
        return {
            "elementOverloadKey": _resolve_element_overload(saju),
            "tenGodPatternKey": _resolve_ten_god_pattern(_count_ten_gods(saju, time_unknown)),
        }
