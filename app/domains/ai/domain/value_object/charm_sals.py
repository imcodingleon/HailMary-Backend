"""매력살 6종 메타데이터.

charm_service.py의 판정 함수와 1:1 매칭. UI에 표시하는 한글/한자/특징/우선순위.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CharmSalMeta:
    """매력살 메타데이터 (UI 표시용)."""
    key: str           # "do_hwa_sal" — charm_service 키와 매칭
    name_kor: str      # "도화살"
    name_han: str      # "桃花煞"
    trait: str         # 특징 한 줄 (카드 표시용)


CHARM_SALS: dict[str, CharmSalMeta] = {
    "do_hwa_sal": CharmSalMeta(
        key="do_hwa_sal",
        name_kor="도화살",
        name_han="桃花煞",
        trait="사람을 끌어당기는 자기 매력",
    ),
    "gong_mang": CharmSalMeta(
        key="gong_mang",
        name_kor="공망",
        name_han="空亡",
        trait="신비롭게 비어있는 빈자리의 결",
    ),
    "hwa_gae_sal": CharmSalMeta(
        key="hwa_gae_sal",
        name_kor="화개살",
        name_han="華蓋煞",
        trait="예술·종교적 깊이가 매력으로",
    ),
    "geum_yeo_rok": CharmSalMeta(
        key="geum_yeo_rok",
        name_kor="금여록",
        name_han="金輿祿",
        trait="사랑과 풍요를 함께 부르는 결",
    ),
    "hong_yeom_sal": CharmSalMeta(
        key="hong_yeom_sal",
        name_kor="홍염살",
        name_han="紅艶煞",
        trait="한 번 보면 잊히지 않는 강렬한 매력",
    ),
    "cheon_eul_gwi_in": CharmSalMeta(
        key="cheon_eul_gwi_in",
        name_kor="천을귀인",
        name_han="天乙貴人",
        trait="귀인 중 최상 — 어디서든 사랑받는 결",
    ),
}


# Hero 자동 선택 우선순위 (강한 순)
SAL_PRIORITY: tuple[str, ...] = (
    "cheon_eul_gwi_in",
    "hong_yeom_sal",
    "do_hwa_sal",
    "geum_yeo_rok",
    "hwa_gae_sal",
    "gong_mang",
)


VALID_CHARM_KEYS: frozenset[str] = frozenset(CHARM_SALS.keys())


def get_charm_meta(key: str) -> CharmSalMeta:
    """매력살 키로 메타데이터 조회."""
    if key not in VALID_CHARM_KEYS:
        raise KeyError(f"unknown charm sal key: {key!r}")
    return CHARM_SALS[key]


def get_sal_hanja(key: str) -> str:
    """charm_service.py 키 → '도화살(桃花煞)' 형태로 표기."""
    if key not in VALID_CHARM_KEYS:
        return key
    m = CHARM_SALS[key]
    return f"{m.name_kor}({m.name_han})"
