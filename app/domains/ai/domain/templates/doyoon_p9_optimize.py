"""도윤 P-9 六 연애 변수 최적화 가이드 — 룰 합성 + facts (3 박스)."""

from __future__ import annotations

from app.domains.ai.domain.templates.doyoon_p0_intro import (
    ILGAN_HANJA,
    OHANG_HANJA,
)
from app.domains.ai.domain.value_object.doyoon_p9_data import (
    COMBINED_EFFECT_MULTIPLIER,
    COMBINED_EFFECT_VALUE,
    DOYOON_P9_DATA,
    IMMEDIATE_IMPACT_PCT,
    OHANG_BOOST_PCT,
    OHANG_MAX_BOOST_PCT,
    OHANG_RESPONSE_MULTIPLIER,
    VALID_DOYOON_P9_ILGAN,
)


def _validate(user_name: str, ilgan: str) -> None:
    if not user_name:
        raise ValueError("doyoon P-9 requires non-empty user_name")
    if ilgan not in VALID_DOYOON_P9_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")


def compose_doyoon_p9_ohang(*, user_name: str, ilgan: str, ohang_lack: str) -> str:
    """6-1 오행 보완 ai_ohang 합성 (250~300자, 3단락)."""
    _validate(user_name, ilgan)
    ilgan_hanja = ILGAN_HANJA[ilgan]
    lack_hanja = OHANG_HANJA.get(ohang_lack, ohang_lack)

    return (
        f"{ilgan}({ilgan_hanja}) 일간은 {ohang_lack}({lack_hanja}) 보완에 유독 민감하게 반응해요. "
        f"동일 일간 표본에서 보완 적용 전후 인연 접촉률이 평균 {OHANG_BOOST_PCT} 차이가 나요. "
        f"일반 케이스보다 {OHANG_RESPONSE_MULTIPLIER} 높은 반응성이에요.\n\n"
        "세 가지를 30일간 유지하시면 효과가 누적돼요. 단순 합산이 아니라 상호작용 효과까지 포함하면 "
        f"최대 {OHANG_MAX_BOOST_PCT}까지 올라가요. 그냥 생활 패턴 조금 바꾸는 것뿐인데 꽤 큰 변화예요.\n\n"
        f"뭐부터 할지 모르겠으면 제일 가벼운 것부터 시작하세요. {user_name}님께 가장 진입 장벽이 낮은 색채 노출부터 권장드려요."
    )


def compose_doyoon_p9_risk(*, user_name: str, ilgan: str) -> str:
    """6-2 리스크 제거 ai_risk 합성 (200~250자, 2단락)."""
    _validate(user_name, ilgan)
    return (
        "세 개 중에 즉시 변수가 임팩트가 가장 커요. "
        f"이것 하나만 정리해도 새 인연 진입률이 {IMMEDIATE_IMPACT_PCT} 올라가거든요. "
        "단기랑 중기는 차차 하셔도 되는데, 즉시는 말 그대로 지금 바로예요.\n\n"
        f"{user_name}님께서 동시에 셋 다 진행하시면 좋긴 한데, 효과가 단순 합산이 아니라 "
        f"{COMBINED_EFFECT_MULTIPLIER} 수준으로 수렴해요. 즉 81+64+47 = 192가 아니라 약 {COMBINED_EFFECT_VALUE} 수준이에요. "
        "그래도 충분히 의미 있는 수치예요. 다만 우선순위는 분명히 잡고 가시는 게 효율적이에요."
    )


def compose_doyoon_p9_optimize(*, user_name: str, ilgan: str) -> str:
    """6-3 매력 최적화 ai_optimize 합성 (250~300자, 3단락)."""
    _validate(user_name, ilgan)
    d = DOYOON_P9_DATA[ilgan]
    ilgan_hanja = ILGAN_HANJA[ilgan]
    gap = d.target_score - d.current_score

    return (
        f"{d.current_score}에서 {d.target_score}까지 딱 {gap}점 남았어요. "
        "이 격차는 세 가지 변수에서 발생해요 — 침묵 활용, 시선 안정, 표현 빈도.\n\n"
        f"{ilgan}({ilgan_hanja}) 일간은 침묵 활용 하나만 올려도 매력 발현 효율이 {d.gap_per_action}씩 오르거든요. "
        "30일 의식적으로 해보시면 6~8점은 올라요. "
        f"{d.target_score}점을 넘기면 전체 호감 유발 효율이 {d.overall_boost_pct} 상승해요.\n\n"
        f"별거 없어요. 그냥 시작하시면 돼요. 분석은 다 끝났어요. 이제 공은 {user_name}님한테 있어요."
    )


# ── facts ─────────────────────────────────────────────────────────


def get_doyoon_p9_ohang_facts(*, user_name: str, ilgan: str, ohang_lack: str) -> dict[str, str]:
    _validate(user_name, ilgan)
    rule_text = compose_doyoon_p9_ohang(user_name=user_name, ilgan=ilgan, ohang_lack=ohang_lack)
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "ilgan_hanja": ILGAN_HANJA[ilgan],
        "ohang_lack": ohang_lack,
        "ohang_lack_hanja": OHANG_HANJA.get(ohang_lack, ohang_lack),
        "boost_pct": OHANG_BOOST_PCT,
        "response_multiplier": OHANG_RESPONSE_MULTIPLIER,
        "max_boost_pct": OHANG_MAX_BOOST_PCT,
        "rule_text": rule_text,
    }


def get_doyoon_p9_risk_facts(*, user_name: str, ilgan: str) -> dict[str, str]:
    _validate(user_name, ilgan)
    rule_text = compose_doyoon_p9_risk(user_name=user_name, ilgan=ilgan)
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "immediate_impact_pct": IMMEDIATE_IMPACT_PCT,
        "combined_multiplier": COMBINED_EFFECT_MULTIPLIER,
        "combined_value": COMBINED_EFFECT_VALUE,
        "rule_text": rule_text,
    }


def get_doyoon_p9_optimize_facts(*, user_name: str, ilgan: str) -> dict[str, str]:
    _validate(user_name, ilgan)
    d = DOYOON_P9_DATA[ilgan]
    rule_text = compose_doyoon_p9_optimize(user_name=user_name, ilgan=ilgan)
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "current_score": str(d.current_score),
        "target_score": str(d.target_score),
        "gap_per_action": d.gap_per_action,
        "overall_boost_pct": d.overall_boost_pct,
        "rule_text": rule_text,
    }
