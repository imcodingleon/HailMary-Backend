"""매력(charm) 지표 산출 서비스.

dohwa-backend src/lib/charm.ts 의 calculateCharm + transformers/charmView.ts
의 toCharmView 를 합친 Python 포팅.

입력: FortuneTeller 응답 dict (SajuData 형태). 외부 I/O 없음, 순수 계산.
출력: 응답 DTO 가 그대로 받을 수 있는 dict (camelCase 키).
"""

from __future__ import annotations

from typing import Any, cast

from app.domains.user.domain.value_object.saju_constants import (
    BRANCH_ELEMENT,
    EarthlyBranch,
    HeavenlyStem,
    PillarKey,
    TenGod,
    TwelvePhase,
    WuXing,
    get_twelve_phase,
)

PILLAR_KEYS: tuple[PillarKey, ...] = ("year", "month", "day", "hour")

YANG_STEMS: frozenset[HeavenlyStem] = frozenset({"갑", "병", "무", "경", "임"})

SCORE_STEM_BONUS: dict[HeavenlyStem, int] = {
    "병": 2, "정": 2, "임": 2, "경": -2, "신": -2,
}

TWELVE_PHASE_SCORE: dict[TwelvePhase, int] = {
    "mokyok": 12, "jewang": 8, "gwandae": 6, "geonrok": 4,
    "jangsaeng": 3, "yang": 2, "tae": 1, "soe": 0,
    "byeong": -2, "sa": -3, "myo": -4, "jeol": -4,
}

DOHWA_PILLAR_WEIGHT: dict[PillarKey, int] = {
    "day": 30, "month": 22, "hour": 18, "year": 14,
}

PERCENTILE_TABLE: tuple[tuple[int, int], ...] = (
    (0, 0), (10, 5), (20, 10), (28, 15), (34, 20), (40, 28),
    (46, 36), (52, 45), (58, 54), (63, 62), (68, 70), (73, 77),
    (78, 83), (83, 88), (89, 93), (95, 97),
)

GONG_MANG_TABLE: dict[EarthlyBranch, tuple[EarthlyBranch, ...]] = {
    "자": ("술", "해"), "축": ("술", "해"),
    "인": ("자", "축"), "묘": ("자", "축"),
    "진": ("인", "묘"), "사": ("인", "묘"),
    "오": ("진", "사"), "미": ("진", "사"),
    "신": ("오", "미"), "유": ("오", "미"),
    "술": ("신", "유"), "해": ("신", "유"),
}

THREE_HARMONY_DOHWA: tuple[tuple[frozenset[EarthlyBranch], EarthlyBranch], ...] = (
    (frozenset({"인", "오", "술"}), "묘"),
    (frozenset({"사", "유", "축"}), "오"),
    (frozenset({"신", "자", "진"}), "유"),
    (frozenset({"해", "묘", "미"}), "자"),
)

DOHWA_PRIORITY: tuple[PillarKey, ...] = ("day", "month", "hour", "year")


def _branch_map(saju: dict[str, Any]) -> dict[PillarKey, EarthlyBranch]:
    return {k: cast(EarthlyBranch, saju[k]["branch"]) for k in PILLAR_KEYS}


def _find_dohwa_pillars(saju: dict[str, Any]) -> list[PillarKey]:
    sin_sals = saju.get("sinSals") or []
    if "do_hwa_sal" not in sin_sals:
        return []

    branch_map = _branch_map(saju)
    all_branches = set(branch_map.values())
    result: list[PillarKey] = []

    for group_set, dohwa in THREE_HARMONY_DOHWA:
        if not any(b in all_branches for b in group_set):
            continue
        for k in PILLAR_KEYS:
            if branch_map[k] == dohwa and k not in result:
                result.append(k)

    return result


def _count_ten_god_groups(saju: dict[str, Any]) -> dict[str, int]:
    dist = saju.get("tenGodsDistribution") or {}
    return {
        "siksang": (dist.get("식신", 0) + dist.get("상관", 0)),
        "gwangwan": (dist.get("정관", 0) + dist.get("편관", 0)),
        "jaeseong": (dist.get("정재", 0) + dist.get("편재", 0)),
        "inseong": (dist.get("정인", 0) + dist.get("편인", 0)),
        "bigyeop": (dist.get("비견", 0) + dist.get("겁재", 0)),
    }


def _sum_twelve_phase_bonus(saju: dict[str, Any]) -> int:
    day_stem = cast(HeavenlyStem, saju["day"]["stem"])
    total = 0
    for k in PILLAR_KEYS:
        b = cast(EarthlyBranch, saju[k]["branch"])
        total += TWELVE_PHASE_SCORE[get_twelve_phase(day_stem, b)]
    return total


def _is_dohwa_in_gong_mang(
    saju: dict[str, Any], dohwa_pillars: list[PillarKey]
) -> bool:
    if not dohwa_pillars:
        return False
    sin_sals = saju.get("sinSals") or []
    if "gong_mang" not in sin_sals:
        return False
    day_branch = cast(EarthlyBranch, saju["day"]["branch"])
    targets = set(GONG_MANG_TABLE.get(day_branch, ()))
    branch_map = _branch_map(saju)
    return any(branch_map[k] in targets for k in dohwa_pillars)


def _lookup_percentile(score: int) -> int:
    clamped = max(0, min(100, score))
    pct = 0
    for score_min, p in PERCENTILE_TABLE:
        if clamped >= score_min:
            pct = p
    return pct


def _calculate_score(saju: dict[str, Any], dohwa_pillars: list[PillarKey]) -> int:
    score = 0.0

    if len(dohwa_pillars) == 1:
        score += DOHWA_PILLAR_WEIGHT[dohwa_pillars[0]]
    elif len(dohwa_pillars) >= 2:
        weights = sorted((DOHWA_PILLAR_WEIGHT[k] for k in dohwa_pillars), reverse=True)
        score += weights[0] + sum(w * 0.4 for w in weights[1:])

    sin_sals = saju.get("sinSals") or []
    has_hwa_gae = "hwa_gae_sal" in sin_sals
    if has_hwa_gae:
        score += 12 if not dohwa_pillars else 8

    score += _sum_twelve_phase_bonus(saju)

    dist = saju.get("tenGodsDistribution") or {}
    if dist:
        ten_god_bonus = (
            (dist.get("식신", 0) + dist.get("상관", 0)) * 4
            + dist.get("편재", 0) * 3
            + dist.get("정관", 0) * 2
            + dist.get("편인", 0) * 2
        )
        score += min(18, ten_god_bonus)

    day_stem = cast(HeavenlyStem, saju["day"]["stem"])
    score += SCORE_STEM_BONUS.get(day_stem, 0)

    if _is_dohwa_in_gong_mang(saju, dohwa_pillars):
        score -= 10

    return max(0, min(100, round(score)))


def _classify_type(
    saju: dict[str, Any], dohwa_pillars: list[PillarKey], groups: dict[str, int]
) -> str:
    sin_sals = saju.get("sinSals") or []
    day_stem = cast(HeavenlyStem, saju["day"]["stem"])
    is_yang_stem = day_stem in YANG_STEMS
    has_day_or_hour = ("day" in dohwa_pillars) or ("hour" in dohwa_pillars)
    has_year_or_month = ("year" in dohwa_pillars) or ("month" in dohwa_pillars)

    if has_day_or_hour and is_yang_stem and groups["siksang"] >= 2:
        return "active"

    if has_year_or_month and not is_yang_stem and (
        groups["gwangwan"] >= 2 or groups["jaeseong"] >= 2
    ):
        return "passive"

    if groups["siksang"] >= 3:
        return "expressive"

    if (
        "hwa_gae_sal" in sin_sals
        and groups["inseong"] >= 2
        and len(dohwa_pillars) <= 1
    ):
        return "mystery"

    if "day" in dohwa_pillars:
        day_branch = cast(EarthlyBranch, saju["day"]["branch"])
        day_phase = get_twelve_phase(day_stem, day_branch)
        if day_phase in ("jewang", "gwandae"):
            return "charisma"

    if (
        not dohwa_pillars
        and groups["gwangwan"] >= 2
        and groups["jaeseong"] >= 1
    ):
        return "dignified"

    if (
        "yeok_ma_sal" in sin_sals
        and groups["siksang"] >= 2
        and len(dohwa_pillars) == 1
    ):
        return "free"

    if not dohwa_pillars and "hwa_gae_sal" not in sin_sals:
        myo_jeol = 0
        for k in PILLAR_KEYS:
            b = cast(EarthlyBranch, saju[k]["branch"])
            p = get_twelve_phase(day_stem, b)
            if p == "myo" or p == "jeol":
                myo_jeol += 1
        if myo_jeol >= 2:
            return "withdrawn"

    return "balanced"


def _classify_manifestation(
    saju: dict[str, Any], dohwa_pillars: list[PillarKey]
) -> str:
    sin_sals = saju.get("sinSals") or []
    day_stem = cast(HeavenlyStem, saju["day"]["stem"])

    if len(dohwa_pillars) >= 2:
        return "oscillating"

    if "day" in dohwa_pillars:
        day_branch = cast(EarthlyBranch, saju["day"]["branch"])
        day_phase = get_twelve_phase(day_stem, day_branch)
        groups = _count_ten_god_groups(saju)
        if day_phase in ("gwandae", "jewang") and groups["siksang"] >= 1:
            return "stable"

    if dohwa_pillars:
        for k in PILLAR_KEYS:
            b = cast(EarthlyBranch, saju[k]["branch"])
            p = get_twelve_phase(day_stem, b)
            if p == "myo" or p == "jeol":
                return "peakFade"

    if "hour" in dohwa_pillars:
        return "crescendo"

    year_phase = get_twelve_phase(
        day_stem, cast(EarthlyBranch, saju["year"]["branch"])
    )
    if year_phase in ("myo", "tae", "yang"):
        return "crescendo"

    if not dohwa_pillars and "hwa_gae_sal" in sin_sals:
        dist = saju.get("tenGodsDistribution") or {}
        if dist.get("편인", 0) >= 2:
            return "latent"

    return "stable"


def _collect_variant_tags(
    saju: dict[str, Any], dohwa_pillars: list[PillarKey]
) -> list[str]:
    tags: list[str] = []
    sin_sals = saju.get("sinSals") or []

    if dohwa_pillars:
        tags.append("dohwa_active")
        if len(dohwa_pillars) >= 2:
            tags.append("dohwa_multi")
        for k in dohwa_pillars:
            tags.append(f"dohwa_pillar_{k}")

    if "hwa_gae_sal" in sin_sals:
        tags.append("hwagae_present")

    yong_sin = saju.get("yongSin") or {}
    day_stem_element = saju["day"].get("stemElement")
    if yong_sin.get("primaryYongSin") == day_stem_element:
        tags.append("yongsin_aligned")

    wuxing_count = saju.get("wuxingCount") or {}
    day_count = wuxing_count.get(day_stem_element, 0) if day_stem_element else 0
    if day_count >= 3:
        tags.append("wuxing_dominant")
    elif day_count == 0:
        tags.append("wuxing_rare")

    return tags


class CharmService:
    """SajuData(dict) → CharmView(dict, camelCase)."""

    def calculate(self, saju: dict[str, Any]) -> dict[str, Any]:
        dohwa_pillars = _find_dohwa_pillars(saju)
        groups = _count_ten_god_groups(saju)
        type_key = _classify_type(saju, dohwa_pillars, groups)
        manifestation_key = _classify_manifestation(saju, dohwa_pillars)
        variant_tags = _collect_variant_tags(saju, dohwa_pillars)
        charm_strength = _calculate_score(saju, dohwa_pillars)
        charm_percentile = _lookup_percentile(charm_strength)

        primary_pillar: PillarKey | None = None
        if dohwa_pillars:
            for k in DOHWA_PRIORITY:
                if k in dohwa_pillars:
                    primary_pillar = k
                    break
            if primary_pillar is None:
                primary_pillar = dohwa_pillars[0]

        if primary_pillar is None:
            dohwa = {"present": False, "pillar": None, "hanja": None}
        else:
            dohwa = {"present": True, "pillar": primary_pillar, "hanja": "桃花殺"}

        return {
            "typeKey": type_key,
            "manifestationKey": manifestation_key,
            "variantTags": variant_tags,
            "charmStrength": charm_strength,
            "charmPercentile": charm_percentile,
            "showPercent": charm_percentile >= 15,
            "label": type_key,
            "dohwa": dohwa,
        }


# BRANCH_ELEMENT 는 이 파일에서 직접 쓰지 않지만 saju_constants 의 일관성 검증을
# 위해 import 하여 lint pass — type checker 가 남아있는 import 를 검출하면 유지.
_ = BRANCH_ELEMENT
_ = WuXing
_ = TenGod
