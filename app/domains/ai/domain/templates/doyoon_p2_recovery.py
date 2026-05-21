"""도윤 P-2 1-5 회복 곡선 (Ch1 클로징) — 풀 템플릿 합성 + facts 추출.

yeonwoo_p2_recovery와 동일 구조 (3 타임라인 + 회복 가속 + AI 박스).
AI 박스 = 3 단계 회복 패턴 + 일간 지연성 + 처방 (350~400자).
"""

from __future__ import annotations

from app.domains.ai.domain.templates.doyoon_p0_intro import ILGAN_HANJA
from app.domains.ai.domain.value_object.doyoon_p2_data import (
    DOYOON_P2_DATA,
    TIME_LABELS_BY_SPEED,
    VALID_DOYOON_P2_ILGAN,
)


def compose_doyoon_p2_recovery(
    *,
    user_name: str,
    ilgan: str,
) -> dict[str, object]:
    """1-5 회복 풀 합성.

    Returns:
        timeline (list[dict] x 3), accel (dict), ai_recovery (str)

    Raises:
        ValueError / KeyError
    """
    if not user_name:
        raise ValueError("doyoon P-2 recovery requires non-empty user_name")
    if ilgan not in VALID_DOYOON_P2_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")

    data = DOYOON_P2_DATA[ilgan]
    ilgan_hanja = ILGAN_HANJA[ilgan]
    labels = TIME_LABELS_BY_SPEED[data.speed]

    timeline = [
        {"time": labels[i], "title": card.title, "desc": card.desc}
        for i, card in enumerate(data.timeline_cards)
    ]

    ai_recovery = (
        f"{user_name}님의 회복 곡선 분석입니다. "
        f"{ilgan}({ilgan_hanja}) 일간 표본 기준 회복 지연이 평균 대비 {data.recovery_lag_multiplier}예요.\n\n"
        f"{labels[0]} 구간 — {data.timeline_cards[0].desc}\n\n"
        f"{labels[1]} 구간 — {data.timeline_cards[1].desc} "
        f"{labels[2]} 구간 — {data.timeline_cards[2].desc}\n\n"
        f"{data.recovery_optimization}"
    )

    accel = {
        "value": data.recovery_accel_value,
        "sub": data.recovery_accel_sub,
    }

    return {
        "timeline": timeline,
        "accel": accel,
        "ai_recovery": ai_recovery,
    }


# ── AI prompt + 검증용 facts 추출 ────────────────────────────────


def get_doyoon_p2_recovery_facts(
    *,
    user_name: str,
    ilgan: str,
) -> dict[str, str]:
    """P-2 ai_recovery AI prompt에 박을 사실값 + 룰 합성 텍스트."""
    if not user_name:
        raise ValueError("doyoon P-2 recovery facts require non-empty user_name")
    if ilgan not in VALID_DOYOON_P2_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")

    data = DOYOON_P2_DATA[ilgan]
    composed = compose_doyoon_p2_recovery(user_name=user_name, ilgan=ilgan)
    labels = TIME_LABELS_BY_SPEED[data.speed]
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "ilgan_hanja": ILGAN_HANJA[ilgan],
        "recovery_lag_multiplier": data.recovery_lag_multiplier,
        "time_label_0": labels[0],
        "time_label_1": labels[1],
        "time_label_2": labels[2],
        "recovery_optimization": data.recovery_optimization,
        "rule_text": str(composed["ai_recovery"]),
    }
