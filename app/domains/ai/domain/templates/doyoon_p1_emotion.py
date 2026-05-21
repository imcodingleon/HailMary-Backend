"""도윤 P-1 1-3 감정 강도 분석 — 3단락 250~300자 합성.

HTML 도윤_final.html line 2085~2089 임수 더미 톤 미러:
- 단락 1 (~70자): 위기 % + 평균 대비 1.X배 + 회복 % 평이성
- 단락 2 (~100자): {ILGAN} 일간 특성 — 초반 차분 → 폭발 패턴
- 단락 3 (~80자): 작은 표현 효과 N% + 마무리

어휘: 진폭, 폭발 강도, 회복 곡선, 의식적 노출 — P-1 시그니처. 차트 보조 톤.
"""

from __future__ import annotations

from app.domains.ai.domain.value_object.doyoon_p1_data import (
    DOYOON_P1_DATA,
    VALID_DOYOON_P1_ILGAN,
)

# 일간별 단락 2 진단 (~80~100자) — 감정 곡선 특성
ILGAN_CURVE_DIAG: dict[str, str] = {
    "갑목": (
        "{ILGAN} 일간이 원래 이런 구조예요. 한 번 방향 정하면 끝까지 밀고 가는데, "
        "위기 구간에 다른 사람 의견을 받기가 평균보다 어려워지는 패턴이에요."
    ),
    "을목": (
        "{ILGAN} 일간이 그래요. 상대 환경에 맞춰 결을 휘다가 위기 구간에 자기 신호가 한꺼번에 터지는 형이에요. "
        "회복 구간에 또 환경에 맞춰 휘어 들어가는 사이클이 누적돼요."
    ),
    "병화": (
        "{ILGAN} 일간이 원래 이래요. 텐션이 빨리 올라가서 위기 구간 진입도 빠른 편이고, "
        "다행히 회복도 다른 일간보다 빠른 편이긴 해요."
    ),
    "정화": (
        "{ILGAN} 일간이 그래요. 한 사람한테 깊이 집중하다가 위기 구간에 한꺼번에 진폭이 커지는 패턴이죠. "
        "회복도 한참 깊은 곳에서 시작하는 편이라 시간이 걸려요."
    ),
    "무토": (
        "{ILGAN} 일간이 원래 안정적이에요. 진폭이 작은 편이라 위기 강도도 평균 대비 낮은데, "
        "회복도 빠르지 않아서 한 구간에 오래 머무는 형이에요."
    ),
    "기토": (
        "{ILGAN} 일간이 그래요. 받쳐주는 모드라 평소엔 잔잔한데, "
        "위기 구간에 한 번 자기 신호가 터지면 회복 시간이 평균보다 더 걸려요."
    ),
    "경금": (
        "{ILGAN} 일간이 원래 이래요. 명확한 판단 구조라 위기 구간에 진폭이 날카로워지고, "
        "회복은 비교적 빠른데 그 사이 관계 단절 결정이 빠르게 나오는 편이에요."
    ),
    "신금": (
        "{ILGAN} 일간이 그래요. 자기 보호 강도가 높아서 위기 구간 진폭이 크게 잡히고, "
        "회복은 빠른 편인데 마음을 다시 여는 데까지 시간이 더 걸려요."
    ),
    "임수": (
        "{ILGAN} 일간이 원래 이래요. 초반엔 되게 차분한 것처럼 보이다가 어느 순간 한꺼번에 쏟아지는 패턴이죠. "
        "회복 구간도 평균보다 깊고 길어요."
    ),
    "계수": (
        "{ILGAN} 일간이 그래요. 잔잔한 진폭이 누적되다 위기 구간에 한꺼번에 표면화되는 형이에요. "
        "회복은 다시 스며들듯 천천히 진행되고요."
    ),
}


def compose_doyoon_p1_emotion(
    *,
    user_name: str,
    ilgan: str,
) -> str:
    """1-3 감정 곡선 분석 합성. 250~300자.

    Args:
        user_name: User.name
        ilgan: 일간 한글
    """
    if not user_name:
        raise ValueError("doyoon P-1 emotion requires non-empty user_name")
    if ilgan not in VALID_DOYOON_P1_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")

    data = DOYOON_P1_DATA[ilgan]
    crisis_pct = data.emotion_curve[2]  # 위기 %
    recovery_pct = data.emotion_curve[3]  # 회복 %

    para1 = (
        f"그래프 보시면 느끼시겠지만, 위기 구간에서 감정이 {crisis_pct}%까지 튀어요. "
        f"평균의 {data.crisis_multiplier}예요. 회복 구간도 {recovery_pct}% 수준에서 한참 머물러요."
    )

    para2 = ILGAN_CURVE_DIAG[ilgan].replace("{ILGAN}", ilgan)

    para3 = (
        f"미리 조금씩 꺼내두면 폭발 강도가 줄어요. 작은 표현을 주 2회 이상 의식적으로 노출하시면 "
        f"위기 구간 강도가 평균 {data.expression_effect_pct}% 떨어져요. 어렵게 생각하지 마시고, "
        f"그냥 작은 표현을 자주 하시면 돼요."
    )

    return "\n\n".join([para1, para2, para3])


# ── AI prompt + 검증용 facts 추출 ────────────────────────────────


def get_doyoon_p1_emotion_facts(
    *,
    user_name: str,
    ilgan: str,
) -> dict[str, str]:
    """P-1 ai_emotion AI prompt에 박을 사실값 + 룰 합성 텍스트.

    Returns:
        사실값 dict + rule_text. AI가 모두 보존해야 함.
        검증 핵심: ilgan, crisis_pct, recovery_pct, crisis_multiplier, expression_effect_pct.
        user_name은 본 박스 룰에 안 들어가서 검증 생략 (선택적 포함).

    Raises:
        ValueError / KeyError: 입력 가드 실패.
    """
    if not user_name:
        raise ValueError("doyoon P-1 emotion facts require non-empty user_name")
    if ilgan not in VALID_DOYOON_P1_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")

    data = DOYOON_P1_DATA[ilgan]
    rule_text = compose_doyoon_p1_emotion(user_name=user_name, ilgan=ilgan)
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "crisis_pct": f"{data.emotion_curve[2]}%",
        "recovery_pct": f"{data.emotion_curve[3]}%",
        "crisis_multiplier": data.crisis_multiplier,
        "expression_effect_pct": f"{data.expression_effect_pct}%",
        "curve_diag_text": ILGAN_CURVE_DIAG[ilgan].replace("{ILGAN}", ilgan),
        "rule_text": rule_text,
    }
