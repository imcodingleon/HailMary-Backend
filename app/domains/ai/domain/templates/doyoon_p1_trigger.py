"""도윤 P-1 1-2 트리거 발화 메커니즘 — 2단락 200~250자 합성.

HTML 도윤_final.html line 2042~2047 임수 더미 톤 미러:
- 단락 1 (~80자): 3 트리거 순차 88% 임계점 도달 의미
- 단락 2 (~140자): 처음 30일 + 트리거 1+2 결합 + 자기조절 N% + 진단

어휘: 발화, 도달 확률, 자기조절, 임계점 — P-1 시그니처. P-0의 "분포"와 다른 결.
"""

from __future__ import annotations

from app.domains.ai.domain.value_object.doyoon_p1_data import (
    DOYOON_P1_DATA,
    VALID_DOYOON_P1_ILGAN,
)

# 일간별 단락 2 추가 진단 (~50자) — 자기조절 어려운 이유 한 줄
ILGAN_CONTROL_REASON: dict[str, str] = {
    "갑목": "한 번 방향이 정해지면 점검 빈도가 떨어지는 패턴 때문이에요.",
    "을목": "환경에 맞추다 자기 신호가 흐려지는 케이스가 누적되거든요.",
    "병화": "한 번 텐션이 올라가면 페이스 조절이 어려운 구조예요.",
    "정화": "한 사람한테 들어가면 정보 처리량이 평균보다 1.6배라서요.",
    "무토": "안정적인데 초반 페이스 조절이 단단해서 한 번 진입하면 빠지기 어려워요.",
    "기토": "받쳐주는 모드에 들어가면 자기 우선순위가 0.6배로 떨어지는 패턴이에요.",
    "경금": "방향이 명확해지면 그쪽으로 단호하게 가는 구조라 그래요.",
    "신금": "감각적 신호가 들어오면 자기 보호 점검을 거치며 깊이 들어가요.",
    "임수": "정보 처리량이 많아서 빠져나오는 시간이 평균보다 1.4배 걸려요.",
    "계수": "잔잔한 신호가 누적되면 표면화 안 된 채로 깊어지는 구조예요.",
}


def compose_doyoon_p1_trigger(
    *,
    user_name: str,
    ilgan: str,
) -> str:
    """1-2 트리거 메커니즘 합성. 200~250자.

    Args:
        user_name: User.name
        ilgan: 일간 한글
    """
    if not user_name:
        raise ValueError("doyoon P-1 trigger requires non-empty user_name")
    if ilgan not in VALID_DOYOON_P1_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")

    data = DOYOON_P1_DATA[ilgan]

    para1 = (
        "흥미로운 부분이에요. 트리거 세 개가 순서대로 발화하면 임계점 도달 확률이 88%예요. "
        "사실상 거의 자동이라는 뜻이죠."
    )

    para2 = (
        f"특히 처음 30일 안에 '{data.trigger_1}'과 '{data.trigger_2}'가 같이 잡히면, "
        f"{user_name}님이 스스로 브레이크를 밟기가 어려워져요. "
        f"{ilgan} 일간 케이스에서 이 구간 자기조절 성공률이 {data.self_control_pct}%거든요. "
        f"{ILGAN_CONTROL_REASON[ilgan]} 알고 들어가시는 게 훨씬 나아요."
    )

    return "\n\n".join([para1, para2])
