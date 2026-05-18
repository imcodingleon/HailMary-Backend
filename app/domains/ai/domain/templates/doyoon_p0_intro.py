"""도윤 P-0 0-5 분석 진입 요약 — 4단락 템플릿 합성.

사용자 결정 (PAID_GUIDE_DOYOON.md): AI 호출 폐기 → 22조각 템플릿 합성.
- [1] 호명 + 데이터 정리 신호 (USER_NAME 변수, 50~70자)
- [2] 일간 강점 수치 (10종, 70~90자)
- [3a] 오행 과다 + 표본 영향 (5종, 90~120자, IMPACT 포함)
- [3b] 오행 부족 + 측정 한 줄 (5종, 30~50자)
- [4] 다음 장 예고 (1 고정, 30~40자)

총 22조각 → 250 조합. HTML 명세 분량: 220~300자.

톤: 존댓말 + 분석적 + 통계 어휘 ("평균 대비", "상위 N%", "표본"). HTML 임수+수+토
더미와 일관.
"""

from __future__ import annotations

PARA_1_OPENING_TPL = "{user_name}님, 데이터 정리 다 끝났어요."


ILGAN_PARA_2: dict[str, str] = {
    "갑목": (
        "일간은 갑목(甲木) — 의사결정 속도와 신념 일관성이 평균 대비 1.4~1.8배인 유형이에요. "
        "방향 통제력도 동일 일간 평균보다 높게 측정돼요."
    ),
    "을목": (
        "일간은 을목(乙木) — 적응 속도와 환경 수용도가 평균 대비 1.3~1.6배인 유형이에요. "
        "상대 맞춤 변화량도 동일 일간 평균보다 높게 측정돼요."
    ),
    "병화": (
        "일간은 병화(丙火) — 표현 빈도와 에너지 노출도가 평균 대비 1.5~1.9배인 유형이에요. "
        "첫인상 강도도 동일 일간 평균보다 높게 측정돼요."
    ),
    "정화": (
        "일간은 정화(丁火) — 한 사람 집중도와 깊이감이 평균 대비 1.6~1.7배인 유형이에요. "
        "장기 유지율도 동일 일간 평균보다 높게 측정돼요."
    ),
    "무토": (
        "일간은 무토(戊土) — 안정성과 신뢰 누적 속도가 평균 대비 1.5~1.8배인 유형이에요. "
        "관계 일관성도 동일 일간 평균보다 높게 측정돼요."
    ),
    "기토": (
        "일간은 기토(己土) — 수용도와 헌신 빈도가 평균 대비 1.6~1.7배인 유형이에요. "
        "상대 성장 지원 변수도 동일 일간 평균보다 높게 측정돼요."
    ),
    "경금": (
        "일간은 경금(庚金) — 판단 명확성과 결단 속도가 평균 대비 1.5~1.7배인 유형이에요. "
        "방향 정리력도 동일 일간 평균보다 높게 측정돼요."
    ),
    "신금": (
        "일간은 신금(辛金) — 매력 노출도와 정서 깊이가 평균 대비 1.4~1.7배인 유형이에요. "
        "매력 어필 변수도 동일 일간 평균보다 높게 측정돼요."
    ),
    "임수": (
        "일간은 임수(壬水) — 깊이감과 통찰력이 평균 대비 1.7배인 유형이에요. "
        "매력 변수도 동일 일간 평균보다 높게 측정돼요."
    ),
    "계수": (
        "일간은 계수(癸水) — 섬세함과 환경 적응이 평균 대비 1.5~1.8배인 유형이에요. "
        "디테일 캐치 변수도 동일 일간 평균보다 높게 측정돼요."
    ),
}


# 단락 3a: "다만 오행 분포에서 {OHANG_EXCESS}({한자}) 기운이 과다(상위 N%) 상태고,"
# {ohang_excess} 한글 key → 완성 문구 (한자 + 상위 N% 박힘)
OHANG_EXCESS_PARA_3A: dict[str, str] = {
    "목": "다만 오행 분포에서 목(木) 기운이 과다(상위 13%) 상태고,",
    "화": "다만 오행 분포에서 화(火) 기운이 과다(상위 12%) 상태고,",
    "토": "다만 오행 분포에서 토(土) 기운이 과다(상위 17%) 상태고,",
    "금": "다만 오행 분포에서 금(金) 기운이 과다(상위 14%) 상태고,",
    "수": "다만 오행 분포에서 수(水) 기운이 과다(상위 15%) 상태고,",
}

# 단락 3b: "{OHANG_LACK}({한자}) 기운이 부족(하위 N%)으로 측정돼요.
#          이 두 변수가 연애 영역에서 직접적인 영향을 주거든요.
#          실제로 동일 패턴 표본의 신규 인연 접촉률이 평균보다 N% 낮게 잡혀요."
# excess별 IMPACT 수치 다르게 박음 (excess가 인연 접촉률에 더 큰 영향).
OHANG_LACK_PARA_3B: dict[str, str] = {
    "목": (
        "목(木) 기운이 부족(하위 16%)으로 측정돼요. "
        "이 두 변수가 연애 영역에서 직접적인 영향을 주거든요."
    ),
    "화": (
        "화(火) 기운이 부족(하위 14%)으로 측정돼요. "
        "이 두 변수가 연애 영역에서 직접적인 영향을 주거든요."
    ),
    "토": (
        "토(土) 기운이 부족(하위 12%)으로 측정돼요. "
        "이 두 변수가 연애 영역에서 직접적인 영향을 주거든요."
    ),
    "금": (
        "금(金) 기운이 부족(하위 15%)으로 측정돼요. "
        "이 두 변수가 연애 영역에서 직접적인 영향을 주거든요."
    ),
    "수": (
        "수(水) 기운이 부족(하위 18%)으로 측정돼요. "
        "이 두 변수가 연애 영역에서 직접적인 영향을 주거든요."
    ),
}

# 단락 3 마지막 줄 (excess별 IMPACT %)
OHANG_EXCESS_IMPACT: dict[str, str] = {
    "목": "실제로 동일 패턴 표본의 신규 인연 접촉률이 평균보다 28% 낮게 잡혀요.",
    "화": "실제로 동일 패턴 표본의 신규 인연 접촉률이 평균보다 32% 낮게 잡혀요.",
    "토": "실제로 동일 패턴 표본의 신규 인연 접촉률이 평균보다 24% 낮게 잡혀요.",
    "금": "실제로 동일 패턴 표본의 신규 인연 접촉률이 평균보다 30% 낮게 잡혀요.",
    "수": "실제로 동일 패턴 표본의 신규 인연 접촉률이 평균보다 36% 낮게 잡혀요.",
}


PARA_4_CLOSING = "다음 장부터 이 변수들을 하나씩 분석해드릴게요. 그냥 따라오시면 돼요."


VALID_DOYOON_P0_ILGAN: frozenset[str] = frozenset(ILGAN_PARA_2.keys())
VALID_DOYOON_P0_OHANG: frozenset[str] = frozenset(OHANG_EXCESS_PARA_3A.keys())


def compose_doyoon_p0_intro(
    *,
    user_name: str,
    ilgan: str,
    ohang_excess: str,
    ohang_lack: str,
) -> str:
    """4단락 도윤 톤 합성. 220~300자 범위 출력.

    Args:
        user_name: 사용자 이름 (User.name). 단락 1 호명에 박힘.
        ilgan: 일간 한글 (갑목/을목/.../계수 10종)
        ohang_excess: 과다 오행 한글 (목/화/토/금/수)
        ohang_lack: 부족 오행 한글

    Returns:
        4단락 합성 텍스트 (단락 사이 \\n\\n).

    Raises:
        ValueError: user_name 빈 문자열
        KeyError: 알 수 없는 일간 또는 오행
    """
    if not user_name:
        raise ValueError("doyoon P-0 requires non-empty user_name")
    if ilgan not in VALID_DOYOON_P0_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")
    if ohang_excess not in VALID_DOYOON_P0_OHANG:
        raise KeyError(f"unknown ohang_excess: {ohang_excess!r}")
    if ohang_lack not in VALID_DOYOON_P0_OHANG:
        raise KeyError(f"unknown ohang_lack: {ohang_lack!r}")

    para_3 = " ".join([
        OHANG_EXCESS_PARA_3A[ohang_excess],
        OHANG_LACK_PARA_3B[ohang_lack],
        OHANG_EXCESS_IMPACT[ohang_excess],
    ])

    return "\n\n".join([
        PARA_1_OPENING_TPL.format(user_name=user_name),
        ILGAN_PARA_2[ilgan],
        para_3,
        PARA_4_CLOSING,
    ])
