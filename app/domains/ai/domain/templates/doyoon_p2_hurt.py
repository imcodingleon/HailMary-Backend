"""도윤 P-2 1-4 약점 트리거 (취약 구간) — 풀 템플릿 합성 + facts 추출.

yeonwoo_p2_hurt와 동일 구조 (시나리오 2 + AI 박스 + 버블) — 톤만 도윤화.
AI 박스 = 두 시나리오 데이터 분석 + 일간 패턴 진단 + 처방 (300~350자).
"""

from __future__ import annotations

from app.domains.ai.domain.templates.doyoon_p0_intro import ILGAN_HANJA
from app.domains.ai.domain.value_object.doyoon_p2_data import (
    DOYOON_P2_DATA,
    VALID_DOYOON_P2_ILGAN,
)


def compose_doyoon_p2_hurt(
    *,
    user_name: str,
    ilgan: str,
) -> dict[str, str]:
    """1-4 약점 트리거 풀 합성.

    Returns:
        scenario_1_when/desc, scenario_2_when/desc, ai_hurt, bubble

    Raises:
        ValueError / KeyError
    """
    if not user_name:
        raise ValueError("doyoon P-2 hurt requires non-empty user_name")
    if ilgan not in VALID_DOYOON_P2_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")

    data = DOYOON_P2_DATA[ilgan]
    s1, s2 = data.scenarios
    ilgan_hanja = ILGAN_HANJA[ilgan]

    ai_hurt = (
        f"{user_name}님의 P-2 약점 트리거 분석입니다. "
        f"{ilgan}({ilgan_hanja}) 일간 표본에서 가장 빈번한 두 유형이 잡혔어요.\n\n"
        f"첫 번째 — {s1.when}. {s1.desc} 표본 발현률이 {data.vulnerability_pct}이고, "
        f"동일 패턴 케이스가 전체의 {data.common_pattern_pct}예요.\n\n"
        f"두 번째 — {s2.when}. {s2.desc}\n\n"
        f"{data.hurt_optimization}"
    )

    return {
        "scenario_1_when": s1.when,
        "scenario_1_desc": s1.desc,
        "scenario_2_when": s2.when,
        "scenario_2_desc": s2.desc,
        "ai_hurt": ai_hurt,
        "bubble": data.hurt_bubble,
    }


# ── AI prompt + 검증용 facts 추출 ────────────────────────────────


def get_doyoon_p2_hurt_facts(
    *,
    user_name: str,
    ilgan: str,
) -> dict[str, str]:
    """P-2 ai_hurt AI prompt에 박을 사실값 + 룰 합성 텍스트.

    Returns:
        사실값 dict + rule_text.

    Raises:
        ValueError / KeyError
    """
    if not user_name:
        raise ValueError("doyoon P-2 hurt facts require non-empty user_name")
    if ilgan not in VALID_DOYOON_P2_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")

    data = DOYOON_P2_DATA[ilgan]
    composed = compose_doyoon_p2_hurt(user_name=user_name, ilgan=ilgan)
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "ilgan_hanja": ILGAN_HANJA[ilgan],
        "scenario_1_when": data.scenarios[0].when,
        "scenario_2_when": data.scenarios[1].when,
        "vulnerability_pct": data.vulnerability_pct,
        "common_pattern_pct": data.common_pattern_pct,
        "hurt_optimization": data.hurt_optimization,
        "rule_text": composed["ai_hurt"],
    }
