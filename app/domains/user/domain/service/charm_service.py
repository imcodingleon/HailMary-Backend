"""매력(charm) 지표 산출 서비스.

dohwa-backend src/lib/charm.ts 의 calculateCharm + transformers/charmView.ts
의 toCharmView 를 합친 Python 포팅.

입력: FortuneTeller 응답 dict (SajuData 형태). 외부 I/O 없음, 순수 계산.
출력: 응답 DTO 가 그대로 받을 수 있는 dict (camelCase 키).
"""

from __future__ import annotations

from typing import Any, cast

from app.domains.user.domain.value_object.saju_constants import (
    BRANCH_ELEMENT,  # noqa: F401  — saju_constants 일관성 검증용 re-export
    EarthlyBranch,
    HeavenlyStem,
    PillarKey,
    TenGod,  # noqa: F401  — saju_constants 일관성 검증용 re-export (type alias)
    TwelvePhase,
    WuXing,  # noqa: F401  — saju_constants 일관성 검증용 re-export (type alias)
    get_twelve_phase,
)

PILLAR_KEYS: tuple[PillarKey, ...] = ("year", "month", "day", "hour")

YANG_STEMS: frozenset[HeavenlyStem] = frozenset({"갑", "병", "무", "경", "임"})

SCORE_STEM_BONUS: dict[HeavenlyStem, int] = {
    "병": 2, "정": 2, "임": 2, "경": -2, "신": -2,
}

# v2: mokyok 12 → 8 로 조정. 위치 가중치(MOKYOK_PILLAR_BONUS)와의 이중계산 회피.
TWELVE_PHASE_SCORE: dict[TwelvePhase, int] = {
    "mokyok": 8, "jewang": 8, "gwandae": 6, "geonrok": 4,
    "jangsaeng": 3, "yang": 2, "tae": 1, "soe": 0,
    "byeong": -2, "sa": -3, "myo": -4, "jeol": -4,
}

DOHWA_PILLAR_WEIGHT: dict[PillarKey, int] = {
    "day": 30, "month": 22, "hour": 18, "year": 14,
}

# v2: 매력 신호 Top 10 — 폴백 판정용 테이블
HONG_YEOM_TABLE: dict[HeavenlyStem, tuple[EarthlyBranch, ...]] = {
    "갑": ("오",), "을": ("오", "신"), "병": ("인",), "정": ("미",),
    "무": ("진",), "기": ("진",), "경": ("술",), "신": ("유",),
    "임": ("자",), "계": ("신",),
}

GEUM_YEO_ROK_TABLE: dict[HeavenlyStem, EarthlyBranch] = {
    "갑": "진", "을": "사", "병": "미", "정": "신", "무": "미",
    "기": "신", "경": "술", "신": "해", "임": "축", "계": "인",
}

JA_JWA_HONG_YEOM_ILJU: frozenset[tuple[HeavenlyStem, EarthlyBranch]] = frozenset({
    ("갑", "오"), ("정", "미"), ("무", "진"), ("기", "진"),
    ("경", "술"), ("신", "유"), ("임", "자"),
})

DOHWA_BRANCHES: frozenset[EarthlyBranch] = frozenset({"자", "묘", "오", "유"})

# 목욕 위치별 가중치 (도화 PILLAR_WEIGHT 비례 축소판)
MOKYOK_PILLAR_BONUS: dict[PillarKey, int] = {
    "day": 6, "hour": 3, "month": 2, "year": 1,
}

# 6충 페어 (sin_sal.ts:462 의 chungPairs 와 동일)
CHUNG_PAIRS: tuple[tuple[EarthlyBranch, EarthlyBranch], ...] = (
    ("자", "오"), ("축", "미"), ("인", "신"),
    ("묘", "유"), ("진", "술"), ("사", "해"),
)

# 화개 그룹 매핑 (sin_sal.ts checkHwaGaeSal 과 동일)
HWA_GAE_GROUPS: tuple[tuple[frozenset[EarthlyBranch], EarthlyBranch], ...] = (
    (frozenset({"인", "오", "술"}), "술"),
    (frozenset({"사", "유", "축"}), "축"),
    (frozenset({"신", "자", "진"}), "진"),
    (frozenset({"해", "묘", "미"}), "미"),
)

# 천을귀인 일간별 지지표 (sin_sal.ts CHEON_EUL_GWI_IN_TABLE 과 동일)
CHEON_EUL_TABLE: dict[HeavenlyStem, tuple[EarthlyBranch, ...]] = {
    "갑": ("축", "미"), "을": ("자", "신"),
    "병": ("해", "유"), "정": ("해", "유"),
    "무": ("축", "미"), "기": ("자", "신"),
    "경": ("축", "미"), "신": ("인", "오"),
    "임": ("사", "묘"), "계": ("사", "묘"),
}

V2_BONUS_CAP: int = 30

PERCENTILE_TABLE: tuple[tuple[int, int], ...] = (
    # 2026-05-14 결정: 결제 사용자 만족도 고려해 분포 후하게 조정.
    # 최저점도 상위 35% 부터 시작. 평균 점수(40~50)는 상위 70~80%대.
    (0, 35), (10, 42), (20, 50), (28, 57), (34, 63), (40, 70),
    (46, 76), (52, 82), (58, 87), (63, 91), (68, 94), (73, 96),
    (78, 97), (83, 98), (89, 99), (95, 99),
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


# ── v2 매력 신호 폴백 헬퍼 ──────────────────────────────────────────────────
# FortuneTeller가 sinSals/charmFlags 에 값을 안 보낸 경우 8자(stem/branch)에서
# 즉시 판정. FortuneTeller가 이미 보냈으면 그대로 신뢰(_augment_charm_signals
# 가 덮어쓰지 않음).


def _has_hong_yeom(saju: dict[str, Any]) -> bool:
    day_stem = cast(HeavenlyStem, saju["day"]["stem"])
    targets = HONG_YEOM_TABLE.get(day_stem, ())
    branches = _branch_map(saju).values()
    return any(b in targets for b in branches)


def _has_geum_yeo_rok(saju: dict[str, Any]) -> bool:
    day_stem = cast(HeavenlyStem, saju["day"]["stem"])
    target = GEUM_YEO_ROK_TABLE.get(day_stem)
    if target is None:
        return False
    return target in _branch_map(saju).values()


def _is_ja_jwa_hong_yeom(saju: dict[str, Any]) -> bool:
    day_stem = cast(HeavenlyStem, saju["day"]["stem"])
    day_branch = cast(EarthlyBranch, saju["day"]["branch"])
    return (day_stem, day_branch) in JA_JWA_HONG_YEOM_ILJU


def _is_dohwa_ilju(saju: dict[str, Any]) -> bool:
    day_branch = cast(EarthlyBranch, saju["day"]["branch"])
    return day_branch in DOHWA_BRANCHES


def _mokyok_pillars(saju: dict[str, Any]) -> list[PillarKey]:
    day_stem = cast(HeavenlyStem, saju["day"]["stem"])
    result: list[PillarKey] = []
    for k in PILLAR_KEYS:
        b = cast(EarthlyBranch, saju[k]["branch"])
        if get_twelve_phase(day_stem, b) == "mokyok":
            result.append(k)
    return result


def _dohwa_chung_pillars(
    saju: dict[str, Any], dohwa_pillars: list[PillarKey]
) -> list[PillarKey]:
    """도화 지지가 6충 페어의 한쪽으로 사주 안에 동시 존재 시 해당 도화 기둥 반환."""
    if not dohwa_pillars:
        return []
    branch_map = _branch_map(saju)
    all_branches = set(branch_map.values())
    result: list[PillarKey] = []
    for k in dohwa_pillars:
        b = branch_map[k]
        for a, c in CHUNG_PAIRS:
            partner: EarthlyBranch | None = None
            if b == a:
                partner = c
            elif b == c:
                partner = a
            if partner is not None and partner in all_branches:
                result.append(k)
                break
    return result


def _has_dohwa_via_groups(saju: dict[str, Any]) -> bool:
    """sin_sal.ts checkDoHwaSal 동등. sinSals 의존 없이 8자만으로 판정."""
    branch_map = _branch_map(saju)
    all_branches = set(branch_map.values())
    for group_set, dohwa in THREE_HARMONY_DOHWA:
        if any(b in all_branches for b in group_set) and dohwa in all_branches:
            return True
    return False


def _has_hwa_gae_via_groups(saju: dict[str, Any]) -> bool:
    """sin_sal.ts checkHwaGaeSal 동등."""
    branch_map = _branch_map(saju)
    all_branches = set(branch_map.values())
    for group_set, hwa_gae in HWA_GAE_GROUPS:
        if any(b in all_branches for b in group_set) and hwa_gae in all_branches:
            return True
    return False


def _has_gong_mang_via_table(saju: dict[str, Any]) -> bool:
    """sin_sal.ts checkGongMang 동등."""
    day_branch = cast(EarthlyBranch, saju["day"]["branch"])
    targets = set(GONG_MANG_TABLE.get(day_branch, ()))
    return any(b in targets for b in _branch_map(saju).values())


def _has_cheon_eul_via_table(saju: dict[str, Any]) -> bool:
    """sin_sal.ts CHEON_EUL_GWI_IN_TABLE 동등."""
    day_stem = cast(HeavenlyStem, saju["day"]["stem"])
    targets = CHEON_EUL_TABLE.get(day_stem, ())
    return any(b in targets for b in _branch_map(saju).values())


def _augment_charm_signals(saju: dict[str, Any]) -> dict[str, Any]:
    """FortuneTeller 응답에 v2 매력 신호가 누락된 경우 백엔드에서 폴백 보강.

    - FortuneTeller가 보낸 sinSals/charmFlags 는 신뢰(덮어쓰지 않음)
    - 입력 dict 는 변형하지 않음 (얕은 복사 후 반환)
    - 매력 점수에 영향 주는 신살 전부 폴백 처리하여 폴백 동등성 보장
    """
    out = dict(saju)
    sin_sals = list(out.get("sinSals") or [])
    sin_sals_set = set(sin_sals)
    # v1 신살 폴백 (기존 산식 영향 신호) — FortuneTeller 미제공 시에만 채움
    if "do_hwa_sal" not in sin_sals_set and _has_dohwa_via_groups(saju):
        sin_sals.append("do_hwa_sal")
        sin_sals_set.add("do_hwa_sal")
    if "hwa_gae_sal" not in sin_sals_set and _has_hwa_gae_via_groups(saju):
        sin_sals.append("hwa_gae_sal")
        sin_sals_set.add("hwa_gae_sal")
    if "gong_mang" not in sin_sals_set and _has_gong_mang_via_table(saju):
        sin_sals.append("gong_mang")
        sin_sals_set.add("gong_mang")
    if "cheon_eul_gwi_in" not in sin_sals_set and _has_cheon_eul_via_table(saju):
        sin_sals.append("cheon_eul_gwi_in")
        sin_sals_set.add("cheon_eul_gwi_in")
    # v2 신규 신살 폴백
    if "hong_yeom_sal" not in sin_sals_set and _has_hong_yeom(saju):
        sin_sals.append("hong_yeom_sal")
        sin_sals_set.add("hong_yeom_sal")
    if "geum_yeo_rok" not in sin_sals_set and _has_geum_yeo_rok(saju):
        sin_sals.append("geum_yeo_rok")
        sin_sals_set.add("geum_yeo_rok")
    if "ja_jwa_hong_yeom" not in sin_sals_set and _is_ja_jwa_hong_yeom(saju):
        sin_sals.append("ja_jwa_hong_yeom")
        sin_sals_set.add("ja_jwa_hong_yeom")
    out["sinSals"] = sin_sals

    charm_flags = dict(out.get("charmFlags") or {})
    charm_flags.setdefault("dohwaIlju", _is_dohwa_ilju(saju))
    charm_flags.setdefault("jaJwaHongYeom", _is_ja_jwa_hong_yeom(saju))
    has_dohwa = "do_hwa_sal" in sin_sals_set
    has_hong = "hong_yeom_sal" in sin_sals_set
    charm_flags.setdefault("hongYeomDohwaSynergy", has_dohwa and has_hong)
    charm_flags.setdefault("mokyokPillars", _mokyok_pillars(saju))
    out["charmFlags"] = charm_flags
    return out


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


def _calculate_v2_bonus(
    saju: dict[str, Any], dohwa_pillars: list[PillarKey]
) -> float:
    """Top 10 매력 신호 가산. _augment_charm_signals 통과 후 호출 가정."""
    bonus = 0.0
    sin_sals = saju.get("sinSals") or []
    charm_flags = saju.get("charmFlags") or {}

    # 1. 홍염살
    if "hong_yeom_sal" in sin_sals:
        bonus += 10

    # 2. 자좌홍염 일주 (홍염살에 누적되는 추가 가산 — 일주 자체가 매력)
    if charm_flags.get("jaJwaHongYeom"):
        bonus += 6

    # 3. 천을귀인 — 매력 가산은 약하게 (귀인성 ≠ 매력 그 자체)
    if "cheon_eul_gwi_in" in sin_sals:
        bonus += 4

    # 4. 도화일주 — 일지 자체가 도화 지지(자/묘/오/유). 기존 _find_dohwa_pillars
    # 의 삼합 그룹 판정에서 누락되는 케이스를 흡수.
    if charm_flags.get("dohwaIlju"):
        bonus += 8

    # 5. 홍염×도화 시너지
    if charm_flags.get("hongYeomDohwaSynergy"):
        bonus += 5

    # 6. 도화 충 페널티 (합은 도화 PILLAR_WEIGHT 자체에 반영되므로 별도 가산 X)
    if _dohwa_chung_pillars(saju, dohwa_pillars):
        bonus -= 3

    # 7. 목욕 위치 가중 (TWELVE_PHASE_SCORE['mokyok']=8 과 분리된 보너스)
    for k in charm_flags.get("mokyokPillars") or []:
        bonus += MOKYOK_PILLAR_BONUS.get(k, 0)

    # 8. 금여록
    if "geum_yeo_rok" in sin_sals:
        bonus += 3

    # 9. 편관·식상×도화 격국 (이성운 격국)
    dist = saju.get("tenGodsDistribution") or {}
    pyeongwan = dist.get("편관", 0)
    siksang = dist.get("식신", 0) + dist.get("상관", 0)
    if pyeongwan >= 2 and siksang >= 2 and dohwa_pillars:
        bonus += 6

    # 10. 공망 ∩ 매력살 페널티 확장 — 도화는 기존 -10 그대로, 홍염은 추가 -4
    if "gong_mang" in sin_sals and "hong_yeom_sal" in sin_sals:
        bonus -= 4

    return bonus


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

    # 도화 부재 시 차상위 매력살로 대체 가산 (2026-05-14 결정).
    # 도화 pillar 베이스 가산이 빠진 손실을 SAL_PRIORITY 최우선 살로 보충해서
    # "강렬한 매력" 같은 카피와 점수 라벨의 정합성을 맞춤. 둘 이상 보유 시 우선 살 하나만.
    if not dohwa_pillars:
        if "cheon_eul_gwi_in" in sin_sals:
            score += 25
        elif "hong_yeom_sal" in sin_sals:
            score += 25
        elif "geum_yeo_rok" in sin_sals:
            score += 20

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

    # v2: Top 10 매력 신호 가산 (cap +30 으로 인플레이션 방지)
    v2_bonus = _calculate_v2_bonus(saju, dohwa_pillars)
    score += min(V2_BONUS_CAP, v2_bonus)

    # 서비스 UX: 매우 낮은 매력 점수가 사용자에게 부정적으로 비춰지는 것을 방지하기 위해
    # 최저값을 20으로 floor 적용 (21점 이상 사용자는 자연 분포 유지).
    return max(20, min(100, round(score)))


# 일간(천간) → 매력 유형 슬러그 매핑.
# 사용자 결정 (2026-05-14): 무료/유료 결과지 매력 유형 라벨을 일간 10종으로 통일.
# 기존 사주 구조 분류 (active/passive/expressive/mystery/charisma/dignified/free/
# withdrawn/balanced 9종) 폐기. 인자는 saju 하나만 필요.
DAY_STEM_TO_TYPE_KEY: dict[HeavenlyStem, str] = {
    "갑": "gap",     "을": "eul",
    "병": "byeong",  "정": "jeong",
    "무": "mu",      "기": "gi",
    "경": "gyeong",  "신": "shin",
    "임": "im",      "계": "gye",
}


def _classify_type(saju: dict[str, Any]) -> str:
    day_stem = cast(HeavenlyStem, saju["day"]["stem"])
    return DAY_STEM_TO_TYPE_KEY[day_stem]


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

    # 매력살 보유 태그 — 도화 부재 시 우선순위(SAL_PRIORITY)에 따라 카피 선정용.
    # 천을귀인 > 홍염 > 도화 > 금여록 > 화개 > 공망.
    if "cheon_eul_gwi_in" in sin_sals:
        tags.append("cheoneul_present")
    if "hong_yeom_sal" in sin_sals:
        tags.append("hongyeom_present")
    if "geum_yeo_rok" in sin_sals:
        tags.append("geumyeo_present")
    if "hwa_gae_sal" in sin_sals:
        tags.append("hwagae_present")
    if "gong_mang" in sin_sals:
        tags.append("gongmang_present")

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
        # v2: FortuneTeller 미보유 매력 신호 폴백 보강.
        # FortuneTeller 가 이미 보낸 sinSals/charmFlags 값은 덮어쓰지 않음.
        saju = _augment_charm_signals(saju)
        dohwa_pillars = _find_dohwa_pillars(saju)
        groups = _count_ten_god_groups(saju)
        type_key = _classify_type(saju)
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

        dohwa: dict[str, Any]
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

    def get_user_charm_sals(self, saju: dict[str, Any]) -> list[str]:
        """사주에서 보유 매력살 키 리스트 반환 (P-5 유료 페이지 표시용).

        키는 `value_object/charm_sals.py` CHARM_SALS dict와 매칭:
          - do_hwa_sal / hong_yeom_sal / cheon_eul_gwi_in
          - hwa_gae_sal / geum_yeo_rok / gong_mang

        Returns: 보유한 매력살 키 list (0~6개). 우선순위 순서는 SAL_PRIORITY 따름.
        """
        saju = _augment_charm_signals(saju)

        present: list[str] = []
        # 우선순위 순서 (가장 귀한 매력살 먼저)
        if _has_cheon_eul_via_table(saju):
            present.append("cheon_eul_gwi_in")
        if _has_hong_yeom(saju):
            present.append("hong_yeom_sal")
        if _find_dohwa_pillars(saju) or _has_dohwa_via_groups(saju):
            present.append("do_hwa_sal")
        if _has_geum_yeo_rok(saju):
            present.append("geum_yeo_rok")
        if _has_hwa_gae_via_groups(saju):
            present.append("hwa_gae_sal")
        if _has_gong_mang_via_table(saju):
            present.append("gong_mang")

        return present


# BRANCH_ELEMENT / WuXing / TenGod 은 본 파일에서 직접 쓰지 않지만 saju_constants
# 의 일관성 검증 의도로 import 만 유지. F401 은 import 라인의 noqa 로 처리.
