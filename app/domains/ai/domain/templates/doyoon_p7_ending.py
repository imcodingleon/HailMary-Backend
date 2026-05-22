"""도윤 P-7 四 운명의 짝 · 결말 (2/2) — 룰 합성 + facts (1 박스)."""

from __future__ import annotations

from app.domains.ai.domain.templates.doyoon_p0_intro import ILGAN_HANJA
from app.domains.ai.domain.value_object.doyoon_p7_data import (
    DOYOON_P7_DATA,
    VALID_DOYOON_P7_ILGAN,
)


def _validate(user_name: str, ilgan: str) -> None:
    if not user_name:
        raise ValueError("doyoon P-7 requires non-empty user_name")
    if ilgan not in VALID_DOYOON_P7_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")


def compose_doyoon_p7_ending(*, user_name: str, ilgan: str) -> str:
    """4-3 결말 시나리오 ai_ending 합성 (400~450자, 5단락)."""
    _validate(user_name, ilgan)
    d = DOYOON_P7_DATA[ilgan]
    ilgan_hanja = ILGAN_HANJA[ilgan]

    return (
        "세 시나리오 각각 성공 확률과 기대값 정리해드릴게요.\n\n"
        f"시나리오 1 — 지금 이대로 유지. 6개월 후 관계 성립 확률 {d.sc1_six_month_pct}. "
        "양쪽 모두 정체된 채로 흐름이 약해지는 패턴이에요. "
        "가장 흔한 결말이지만 기대값은 가장 낮아요.\n\n"
        f"시나리오 2 — {user_name}님이 먼저 움직임. 6개월 후 관계 성립 확률 {d.sc2_six_month_pct}. "
        f"데이터상 가장 권장되는 분기예요. {ilgan}({ilgan_hanja}) 일간이 먼저 신호를 보냈을 때 "
        f"상대 호응률이 평균보다 {d.initiative_multiplier} 높게 측정되거든요. "
        "깊은 사람이 먼저 표현했을 때의 무게가 데이터로도 잡혀요.\n\n"
        f"시나리오 3 — 상대가 먼저 움직이기를 기다림. 6개월 후 관계 성립 확률 {d.sc3_six_month_pct}. "
        f"가능성은 있지만 시간 비용이 평균 {d.wait_cost_multiplier} 더 들어요.\n\n"
        f"{user_name}님 결정이에요. 다만 분석가로서 한 가지만 말씀드리면, "
        f"시나리오 2가 기대값 기준 압도적이에요. "
        f"{d.sc2_six_month_pct} vs {d.sc1_six_month_pct} — {d.expected_value_ratio} 차이예요."
    )


def get_doyoon_p7_ending_facts(*, user_name: str, ilgan: str) -> dict[str, str]:
    _validate(user_name, ilgan)
    d = DOYOON_P7_DATA[ilgan]
    rule_text = compose_doyoon_p7_ending(user_name=user_name, ilgan=ilgan)
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "sc1_six_month_pct": d.sc1_six_month_pct,
        "sc2_six_month_pct": d.sc2_six_month_pct,
        "sc3_six_month_pct": d.sc3_six_month_pct,
        "initiative_multiplier": d.initiative_multiplier,
        "wait_cost_multiplier": d.wait_cost_multiplier,
        "expected_value_ratio": d.expected_value_ratio,
        "rule_text": rule_text,
    }
