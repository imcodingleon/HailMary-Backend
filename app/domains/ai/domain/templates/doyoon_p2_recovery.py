"""도윤 P-2 1-5 회복 곡선 — 풀 템플릿 합성 + facts 추출 (원본 도윤 구조).

원본 meter × 4 (직후/1개월/3개월/6개월) + SD + 한도윤 버블.
AI 박스 = 평균 회복 곡선 분석 (감정 강도 잔여 기준) + 처방 (350~400자).
"""

from __future__ import annotations

from app.domains.ai.domain.templates.doyoon_p0_intro import ILGAN_HANJA
from app.domains.ai.domain.value_object.doyoon_p2_data import (
    DOYOON_P2_DATA,
    VALID_DOYOON_P2_ILGAN,
)


def compose_doyoon_p2_recovery(
    *,
    user_name: str,
    ilgan: str,
) -> dict[str, str]:
    """1-5 회복 곡선 합성 — ai_recovery만 반환 (meters/bubble는 facts 노출)."""
    if not user_name:
        raise ValueError("doyoon P-2 recovery requires non-empty user_name")
    if ilgan not in VALID_DOYOON_P2_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")

    data = DOYOON_P2_DATA[ilgan]
    ilgan_hanja = ILGAN_HANJA[ilgan]
    # 회복률 → 잔여 감정 강도 변환 (100 - pct)
    residual = [100 - m.pct for m in data.meters]

    ai_recovery = (
        f"회복 데이터도 정리해 드릴게요. {ilgan}({ilgan_hanja}) 일간 표본의 평균 회복 곡선이에요.\n\n"
        f"직후 — 감정 강도 {residual[0]}% 유지. 1개월 차 — {residual[1]}%까지 내려와요. "
        f"3개월 차 — {residual[2]}% 수준. 6개월 차 — {residual[3]}%까지 감소합니다.\n\n"
        f"평균 대비 회복 지연이 {data.recovery_lag_multiplier}로 측정돼요. "
        f"{user_name}님 케이스에서는 자연 인덱스 감소를 기다리는 게 가장 안전한 경로입니다. "
        "강제 삭제 시도는 곡선을 오히려 늦춥니다.\n\n"
        "회복 구간 내 새 매칭 시도는 충돌 확률이 높아져요. 기존 데이터가 정리된 후에 새 변수를 받으세요."
    )

    return {
        "ai_recovery": ai_recovery,
    }


# ── AI prompt + 검증용 facts 추출 ────────────────────────────────


def get_doyoon_p2_recovery_facts(
    *,
    user_name: str,
    ilgan: str,
) -> dict[str, str]:
    if not user_name:
        raise ValueError("doyoon P-2 recovery facts require non-empty user_name")
    if ilgan not in VALID_DOYOON_P2_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")

    data = DOYOON_P2_DATA[ilgan]
    composed = compose_doyoon_p2_recovery(user_name=user_name, ilgan=ilgan)
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "ilgan_hanja": ILGAN_HANJA[ilgan],
        "meter_pct_0": f"{data.meters[0].pct}%",
        "meter_pct_1": f"{data.meters[1].pct}%",
        "meter_pct_2": f"{data.meters[2].pct}%",
        "meter_pct_3": f"{data.meters[3].pct}%",
        "recovery_lag_multiplier": data.recovery_lag_multiplier,
        "rule_text": composed["ai_recovery"],
    }
