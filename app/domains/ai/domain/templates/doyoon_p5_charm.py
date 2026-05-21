"""도윤 P-5 三 매력 분석 — 룰 합성 + facts (3 박스).

3-1 매력 지수 (charm_index) + 3-2 전환율 (conversion) + 3-3 호감 유발 (appeal).
"""

from __future__ import annotations

from app.domains.ai.domain.templates.doyoon_p0_intro import ILGAN_HANJA
from app.domains.ai.domain.value_object.doyoon_p5_data import (
    CONVERSION_STEPS,
    DOYOON_P5_DATA,
    VALID_DOYOON_P5_ILGAN,
)


def _validate(user_name: str, ilgan: str) -> None:
    if not user_name:
        raise ValueError("doyoon P-5 requires non-empty user_name")
    if ilgan not in VALID_DOYOON_P5_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")


def compose_doyoon_p5_charm_index(
    *,
    user_name: str,
    ilgan: str,
    charm_pct: int,
) -> str:
    """3-1 매력 지수 ai_charm_index 합성 (300~350자, 3단락).

    Args:
        charm_pct: 상위 N% (정수, 1~99)
    """
    _validate(user_name, ilgan)
    d = DOYOON_P5_DATA[ilgan]

    return (
        f"상위 {charm_pct}%예요. 이거 그냥 숫자가 아니에요.\n\n"
        f"6개 축 중에서 강점이 두 개예요. {d.strength_axis_1}과 {d.strength_axis_2} — "
        f"둘 다 평균의 {d.strength_multiplier}예요. 동일 일간 표본에서도 이 두 축에서 "
        "이만큼 나오는 분이 흔하지 않아요. 나머지 4개 축은 평균~약상위 구간이에요. "
        "약점이 있는 게 아니라, 강점이 두드러지는 구조예요.\n\n"
        f"다만 {user_name}님은 이걸 아직 제대로 안 쓰고 있어요. "
        f"무의식적으로 발현될 때랑 의식적으로 쓸 때 차이가 {d.conscious_gap_multiplier}예요. "
        "잠재력이 이 정도면, 조금만 의식해도 주변 반응이 꽤 달라질 거예요."
    )


def compose_doyoon_p5_conversion(
    *,
    user_name: str,
    ilgan: str,
) -> str:
    """3-2 전환율 ai_conversion 합성 (200~250자, 3단락)."""
    _validate(user_name, ilgan)
    d = DOYOON_P5_DATA[ilgan]
    s1, s2, s3, s4 = CONVERSION_STEPS

    return (
        f"첫 인상 {s1[1]}%에서 시작해서 끌림 {s4[1]}%까지 올라가는 구조예요. "
        "4단계 전환율(다음 단계로 넘어가는 비율)이에요.\n\n"
        f"근데 재미있는 건, {user_name}님은 두 번째 만남에서 전환율이 "
        f"평균의 {d.second_meeting_multiplier}로 뛰어요. "
        "즉 한 번 만나고 끝내면 진짜 매력의 절반도 못 보여주는 거예요. "
        f"첫 만남에서 끝내는 분과 두 번째까지 가는 분의 최종 호감도 차이가 {d.final_gap_pct} 벌어져요.\n\n"
        f"첫 만남에서 두 번째 약속을 자연스럽게 만들어두세요. 그게 {user_name}님한테 가장 효율적인 전략이에요."
    )


def compose_doyoon_p5_appeal(
    *,
    user_name: str,
    ilgan: str,
) -> str:
    """3-3 호감 유발 ai_appeal 합성 (250~300자, 3단락)."""
    _validate(user_name, ilgan)
    d = DOYOON_P5_DATA[ilgan]
    m1, m2, m3, m4 = d.appeal_meters

    return (
        "4개 변수 점수 정리해드릴게요.\n\n"
        f"{m1.name} {m1.value}, {m2.name} {m2.value}, {m3.name} {m3.value}, {m4.name} {m4.value}. "
        "강점 두 개와 약점 두 개가 명확해요.\n\n"
        f"{d.weakness_axis_1}과 {d.weakness_axis_2}가 약점이에요. "
        f"이게 {user_name}님이 통제하기 가장 쉬운 영역이기도 해요. "
        f"두 변수만 끌어올리면 전체 호감 유발 효율이 {d.appeal_boost_pct} 상승해요. "
        "강점 보완보다 약점 보완이 효율이 높아요."
    )


# ── facts 추출 ────────────────────────────────────────────────────


def get_doyoon_p5_charm_index_facts(
    *,
    user_name: str,
    ilgan: str,
    charm_pct: int,
) -> dict[str, str]:
    _validate(user_name, ilgan)
    d = DOYOON_P5_DATA[ilgan]
    rule_text = compose_doyoon_p5_charm_index(
        user_name=user_name, ilgan=ilgan, charm_pct=charm_pct
    )
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "charm_pct": f"{charm_pct}%",
        "strength_axis_1": d.strength_axis_1,
        "strength_axis_2": d.strength_axis_2,
        "strength_multiplier": d.strength_multiplier,
        "conscious_gap_multiplier": d.conscious_gap_multiplier,
        "rule_text": rule_text,
    }


def get_doyoon_p5_conversion_facts(
    *,
    user_name: str,
    ilgan: str,
) -> dict[str, str]:
    _validate(user_name, ilgan)
    d = DOYOON_P5_DATA[ilgan]
    rule_text = compose_doyoon_p5_conversion(user_name=user_name, ilgan=ilgan)
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "step_1_pct": f"{CONVERSION_STEPS[0][1]}%",
        "step_2_pct": f"{CONVERSION_STEPS[1][1]}%",
        "step_3_pct": f"{CONVERSION_STEPS[2][1]}%",
        "step_4_pct": f"{CONVERSION_STEPS[3][1]}%",
        "second_meeting_multiplier": d.second_meeting_multiplier,
        "final_gap_pct": d.final_gap_pct,
        "rule_text": rule_text,
    }


def get_doyoon_p5_appeal_facts(
    *,
    user_name: str,
    ilgan: str,
) -> dict[str, str]:
    _validate(user_name, ilgan)
    d = DOYOON_P5_DATA[ilgan]
    m1, m2, m3, m4 = d.appeal_meters
    rule_text = compose_doyoon_p5_appeal(user_name=user_name, ilgan=ilgan)
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "meter_1_name": m1.name,
        "meter_1_value": str(m1.value),
        "meter_2_name": m2.name,
        "meter_2_value": str(m2.value),
        "meter_3_name": m3.name,
        "meter_3_value": str(m3.value),
        "meter_4_name": m4.name,
        "meter_4_value": str(m4.value),
        "weakness_axis_1": d.weakness_axis_1,
        "weakness_axis_2": d.weakness_axis_2,
        "appeal_boost_pct": d.appeal_boost_pct,
        "rule_text": rule_text,
    }


# ILGAN_HANJA re-export for downstream
__all__ = [
    "compose_doyoon_p5_charm_index",
    "compose_doyoon_p5_conversion",
    "compose_doyoon_p5_appeal",
    "get_doyoon_p5_charm_index_facts",
    "get_doyoon_p5_conversion_facts",
    "get_doyoon_p5_appeal_facts",
    "ILGAN_HANJA",
]
