"""도윤 P-6 四 운명의 짝 (1/2) — 룰 합성 + facts (3 박스)."""

from __future__ import annotations

from app.domains.ai.domain.templates.doyoon_p0_intro import (
    ILGAN_HANJA,
    OHANG_HANJA,
)
from app.domains.ai.domain.value_object.doyoon_p6_data import (
    DOYOON_INYON_BY_SLOT,
    DOYOON_P6_DATA,
    VALID_DOYOON_P6_ILGAN,
)


def _validate(user_name: str, ilgan: str) -> None:
    if not user_name:
        raise ValueError("doyoon P-6 requires non-empty user_name")
    if ilgan not in VALID_DOYOON_P6_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")


def _resolve_inyon(match_slot_id: str):
    return DOYOON_INYON_BY_SLOT.get(match_slot_id) or DOYOON_INYON_BY_SLOT["f-water-yang"]


def compose_doyoon_p6_profile(
    *,
    user_name: str,
    ilgan: str,
    match_slot_id: str,
    pct_value: int,
    ohang_lack: str,
) -> str:
    """4-1 인연 프로파일 합성 (400~500자, 4단락)."""
    _validate(user_name, ilgan)
    i = _resolve_inyon(match_slot_id)
    ilgan_hanja = ILGAN_HANJA[ilgan]
    lack_hanja = OHANG_HANJA.get(ohang_lack, ohang_lack)

    return (
        f"궁합 지수 상위 {pct_value}%예요. 데이터가 분류한 최적 인연의 모습부터 보여드릴게요.\n\n"
        f"외형 데이터 — 키 분포는 평균 ±5cm 범위 표본이 {i.height_distribution_pct}로 가장 많아요. "
        "체형은 균형 잡힌 골격에 어깨선이 단단한 편이에요. "
        "얼굴 데이터는 선이 부드러운 둥근형, 이마가 넓은 비율이 64%. "
        f"눈매가 길고 끝이 부드럽게 떨어지는 패턴이 동일 호환 사례의 {i.profile_signal_pct}를 차지해요.\n\n"
        f"성격 변수도 봐드릴게요. 감정 변동성이 평균 대비 {i.emotional_stability_multiplier}예요. "
        f"즉 안정성이 {i.stability_high_multiplier} 높다는 뜻이에요. "
        "직업군은 기획·교육·창작 계열에서 매칭률이 가장 높게 나와요.\n\n"
        f"{ohang_lack}({lack_hanja}) 보완 효율이 결정적이에요. "
        f"{user_name}님 사주에서 비어 있는 변수를 이 프로파일이 정확히 채워주거든요. "
        f"{ilgan}({ilgan_hanja}) 일간과의 궁합 지수가 {i.compatibility_pct}까지 올라가는 이유예요. "
        f"평균 궁합 지수 {i.avg_compatibility_baseline} 대비 {i.compatibility_lift} 수치예요."
    )


def compose_doyoon_p6_meeting(
    *,
    user_name: str,
    ilgan: str,
    match_slot_id: str,
) -> str:
    """4-1 만남 시나리오 합성 (300~400자, 3단락)."""
    _validate(user_name, ilgan)
    i = _resolve_inyon(match_slot_id)
    ilgan_hanja = ILGAN_HANJA[ilgan]

    return (
        f"만남 발생 확률이 가장 높은 환경부터 짚어드릴게요. "
        f"신규 환경보다 기존 동선 내 재접촉 확률이 {i.existing_path_multiplier} 높아요. "
        "즉 새로운 곳보다 이미 가는 곳에서 만날 가능성이 높다는 뜻이에요.\n\n"
        f"첫 접촉 패턴 — 짧고 평이한 대화로 시작해요. 인상에 강하게 남지 않는 케이스가 {i.low_impact_pct}예요. "
        "그래서 첫 만남에서 알아채지 못할 가능성이 커요. "
        "의도적으로 못 알아보시는 게 아니라, 데이터 자체가 그렇게 분포돼요.\n\n"
        f"결정적인 건 두 번째 접촉이에요. 두 번째 마주칠 때 호감 전환율이 첫 번째 대비 {i.second_contact_multiplier}로 급상승해요. "
        f"{ilgan}({ilgan_hanja}) 일간 표본에서도 이 패턴이 일관되게 나타나요. "
        f"{user_name}님, 첫 만남에서 두 번째 약속을 자연스럽게 만들어두시면 효율이 가장 높아요."
    )


def compose_doyoon_p6_pattern(
    *,
    user_name: str,
    ilgan: str,
) -> str:
    """4-2 행동 패턴 합성 (300~350자, 4단락)."""
    _validate(user_name, ilgan)
    d = DOYOON_P6_DATA[ilgan]
    ilgan_hanja = ILGAN_HANJA[ilgan]

    return (
        "상대의 행동 데이터를 분석해드릴게요.\n\n"
        "연락 빈도 — 답장은 길게 받는데 먼저 연락하지 않는 패턴이에요. "
        f"이게 보통 '관심 없음'으로 해석되는데, 데이터상 관심 없는 케이스의 답장 길이는 평균 {d.answer_length_multiplier} 짧아요. "
        "길게 받는다는 건 시간을 들이고 있다는 뜻이에요. 그냥 먼저 움직이는 사람이 아닌 거예요.\n\n"
        f"심리 추정값 — 망설임 지수 {d.hesitation_pct}, 단절 의지 {d.cut_intent_pct}. "
        "끊을 마음은 거의 없어요. 다만 시작할 결정도 안 내린 상태예요.\n\n"
        f"{ilgan}({ilgan_hanja}) 일간 표본에서 이런 교착 상태는 둘 중 한 명이 작은 신호를 보내면 {d.resolution_pct} 확률로 해소돼요. "
        f"통계적으로 {user_name}님 쪽에서 먼저 보내는 게 더 효율적이에요. "
        f"먼저 움직였을 때 매칭 성공률이 {d.initiative_multiplier} 높거든요."
    )


# ── facts 추출 ────────────────────────────────────────────────────


def get_doyoon_p6_profile_facts(
    *,
    user_name: str,
    ilgan: str,
    match_slot_id: str,
    pct_value: int,
    ohang_lack: str,
) -> dict[str, str]:
    _validate(user_name, ilgan)
    i = _resolve_inyon(match_slot_id)
    rule_text = compose_doyoon_p6_profile(
        user_name=user_name, ilgan=ilgan, match_slot_id=match_slot_id,
        pct_value=pct_value, ohang_lack=ohang_lack,
    )
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "ilgan_hanja": ILGAN_HANJA[ilgan],
        "ohang_lack": ohang_lack,
        "ohang_lack_hanja": OHANG_HANJA.get(ohang_lack, ohang_lack),
        "pct_value": f"{pct_value}%",
        "height_distribution_pct": i.height_distribution_pct,
        "profile_signal_pct": i.profile_signal_pct,
        "emotional_stability_multiplier": i.emotional_stability_multiplier,
        "stability_high_multiplier": i.stability_high_multiplier,
        "compatibility_pct": i.compatibility_pct,
        "avg_compatibility_baseline": i.avg_compatibility_baseline,
        "compatibility_lift": i.compatibility_lift,
        "rule_text": rule_text,
    }


def get_doyoon_p6_meeting_facts(
    *,
    user_name: str,
    ilgan: str,
    match_slot_id: str,
) -> dict[str, str]:
    _validate(user_name, ilgan)
    i = _resolve_inyon(match_slot_id)
    rule_text = compose_doyoon_p6_meeting(
        user_name=user_name, ilgan=ilgan, match_slot_id=match_slot_id
    )
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "existing_path_multiplier": i.existing_path_multiplier,
        "low_impact_pct": i.low_impact_pct,
        "second_contact_multiplier": i.second_contact_multiplier,
        "rule_text": rule_text,
    }


def get_doyoon_p6_pattern_facts(
    *,
    user_name: str,
    ilgan: str,
) -> dict[str, str]:
    _validate(user_name, ilgan)
    d = DOYOON_P6_DATA[ilgan]
    rule_text = compose_doyoon_p6_pattern(user_name=user_name, ilgan=ilgan)
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "answer_length_multiplier": d.answer_length_multiplier,
        "hesitation_pct": d.hesitation_pct,
        "cut_intent_pct": d.cut_intent_pct,
        "resolution_pct": d.resolution_pct,
        "initiative_multiplier": d.initiative_multiplier,
        "rule_text": rule_text,
    }
