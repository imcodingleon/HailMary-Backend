"""도윤 P-2 1-4 약점 트리거 — 풀 템플릿 합성 + facts 추출 (원본 도윤 구조).

원본 .card-warn × 2 패턴: 짧은 keyword + risk_pct + desc.
AI 박스 = 두 유형 분석 + 처방 (300~350자).
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
        ai_hurt 텍스트만 (카드 데이터는 facts로 노출).

    Raises:
        ValueError / KeyError
    """
    if not user_name:
        raise ValueError("doyoon P-2 hurt requires non-empty user_name")
    if ilgan not in VALID_DOYOON_P2_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")

    data = DOYOON_P2_DATA[ilgan]
    ilgan_hanja = ILGAN_HANJA[ilgan]
    h1, h2 = data.hurt_type_1, data.hurt_type_2

    ai_hurt = (
        f"두 유형이 {ilgan}({ilgan_hanja}) 일간 표본에서 가장 자주 나와요. 하나씩 보여드릴게요.\n\n"
        f"첫 번째는 {h1.keyword}예요. 위험도 {h1.risk_pct}. {h1.desc} "
        f"{user_name}님 케이스에서 가장 빈번한 변수입니다.\n\n"
        f"두 번째는 {h2.keyword}예요. 위험도 {h2.risk_pct}. {h2.desc}\n\n"
        f"둘 다 통제 가능한 영역이에요. 신호 해석 전에 24시간 텀을 두시면 두 패턴 모두 "
        f"발생률이 {data.intervention_drop_pct} 떨어져요. 조금만 의식해보세요."
    )

    return {
        "ai_hurt": ai_hurt,
    }


# ── AI prompt + 검증용 facts 추출 ────────────────────────────────


def get_doyoon_p2_hurt_facts(
    *,
    user_name: str,
    ilgan: str,
) -> dict[str, str]:
    """P-2 ai_hurt AI prompt facts + 룰 합성 텍스트."""
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
        "hurt_type_1_keyword": data.hurt_type_1.keyword,
        "hurt_type_1_risk_pct": data.hurt_type_1.risk_pct,
        "hurt_type_2_keyword": data.hurt_type_2.keyword,
        "hurt_type_2_risk_pct": data.hurt_type_2.risk_pct,
        "intervention_drop_pct": data.intervention_drop_pct,
        "rule_text": composed["ai_hurt"],
    }
