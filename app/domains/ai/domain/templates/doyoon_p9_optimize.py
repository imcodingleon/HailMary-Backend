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
    """6-1 오행 보완 ai_ohang 합성 — 카드 풀이 톤.

    별도 메타 수치 (반응성 배수·최대 부스트) 인용 X. 카드 라벨 (9%+7%+7%=23%)만 풀이.
    """
    _validate(user_name, ilgan)
    ilgan_hanja = ILGAN_HANJA[ilgan]
    lack_hanja = OHANG_HANJA.get(ohang_lack, ohang_lack)

    return (
        f"{ilgan}({ilgan_hanja}) 일간 {user_name}님께 {ohang_lack}({lack_hanja}) 보완 효과를 카드로 정리해드렸어요. "
        f"세 가지 방법의 효과를 합하면 평균 {OHANG_BOOST_PCT} 인연 접촉 확률이 올라가요.\n\n"
        "보완 방법 1(+9%) 색채 노출이 가장 진입 장벽이 낮아요. 옷차림 비율 늘리시는 정도로도 시작 가능해요. "
        "방법 2(+7%) 공간 변수와 방법 3(+7%) 행동 변수는 누적 시간이 필요한 변수예요.\n\n"
        f"세 가지를 30일간 유지하시면 23% 효과가 안정적으로 잡혀요. "
        f"{user_name}님께 우선순위는 효과 +9%인 색채 노출부터 권장드려요."
    )


def compose_doyoon_p9_risk(*, user_name: str, ilgan: str) -> str:
    """6-2 리스크 제거 ai_risk 합성 — 카드 풀이 톤.

    별도 메타 수치 (36% 임팩트) 인용 X. 카드 라벨 (81%·64%·47% = 192)과
    실제 합산 수렴 (1.4배 → 130) 패턴만 풀이.
    """
    _validate(user_name, ilgan)
    return (
        "리스크 카드 세 장 정리해드렸어요. 즉시 변수 81%가 가장 위험도 높고, 단기 64%, 중기 47% 순서예요. "
        "위험도 라벨 자체가 우선순위를 그대로 가리켜요.\n\n"
        f"{user_name}님께서 셋 다 진행하실 때 단순 합산은 81+64+47 = 192로 잡혀요. "
        f"하지만 실제는 변수 간 상호작용 효과로 {COMBINED_EFFECT_MULTIPLIER} 수준으로 수렴해 약 {COMBINED_EFFECT_VALUE} 정도가 측정값이에요. "
        "192라는 단순 합산을 그대로 받지 마시고, 130이 실제 임팩트라고 보시면 됩니다.\n\n"
        "다만 즉시(81%)부터 우선 처리하시는 게 효율적이에요. 위험도 라벨이 그 자체로 진행 순서를 가리키니까요."
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
    """6-1 facts — *카드에 표시되는 사실값만* prompt에 노출.

    응답성 배수 (1.6배) / 최대 부스트 (28%) 같은 별도 메타 수치는 제외 —
    사용자가 표에서 확인할 수 없어 hallucination처럼 보임.
    """
    _validate(user_name, ilgan)
    rule_text = compose_doyoon_p9_ohang(user_name=user_name, ilgan=ilgan, ohang_lack=ohang_lack)
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "ilgan_hanja": ILGAN_HANJA[ilgan],
        "ohang_lack": ohang_lack,
        "ohang_lack_hanja": OHANG_HANJA.get(ohang_lack, ohang_lack),
        "boost_pct": OHANG_BOOST_PCT,    # 카드 합산 (9+7+7)
        "rule_text": rule_text,
    }


def get_doyoon_p9_risk_facts(*, user_name: str, ilgan: str) -> dict[str, str]:
    """6-2 facts — *카드에 표시되는 사실값 + 합산 패턴만* prompt에 노출.

    즉시 변수 단독 임팩트 (36%) 같은 별도 메타 수치는 제외.
    192 (단순 합산) / 130 (1.4배 수렴)은 카드 라벨로부터 유도 가능해서 유지.
    """
    _validate(user_name, ilgan)
    rule_text = compose_doyoon_p9_risk(user_name=user_name, ilgan=ilgan)
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "combined_multiplier": COMBINED_EFFECT_MULTIPLIER,   # 1.4배
        "combined_value": COMBINED_EFFECT_VALUE,             # 130
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
