"""도윤 P-0 0-5 분석 진입 요약 — 4단락 템플릿 합성 + AI facts 추출.

사용자 결정 (PAID_GUIDE_DOYOON.md):
- 룰 합성은 **AI 호출 fallback** 역할로 유지 (이전엔 메인 합성 경로).
- 메인 경로는 generate_p0_diagnosis_usecase가 AI 호출 → 검증 실패 시 본 모듈로 fallback.

데이터 구조 (단일 진실원):
- ILGAN_HANJA: 일간 한글 → 한자 매핑 (10셀)
- OHANG_HANJA: 오행 한글 → 한자 (5셀)
- OHANG_EXCESS_PERCENTILE: 과다 백분위 (5셀, "상위 N%")
- OHANG_LACK_PERCENTILE: 부족 백분위 (5셀, "하위 N%")
- OHANG_CONTACT_RATE_DROP: excess별 신규 인연 접촉률 감소 (5셀, "N%")

기존 PARA_3A/3B/IMPACT는 위 dict 4종에서 *합성*돼 생성 — 동일 텍스트 출력 보장
(테스트 호환). 정량 정책 §정량 표현 기준 §2와 정합 (퍼센트 12~17%, contact 24~36%).
"""

from __future__ import annotations

PARA_1_OPENING_TPL = "{user_name}님, 데이터 정리 다 끝났어요."


# ── 매핑 dict (단일 진실원) ──────────────────────────────────────

ILGAN_HANJA: dict[str, str] = {
    "갑목": "甲木", "을목": "乙木",
    "병화": "丙火", "정화": "丁火",
    "무토": "戊土", "기토": "己土",
    "경금": "庚金", "신금": "辛金",
    "임수": "壬水", "계수": "癸水",
}

OHANG_HANJA: dict[str, str] = {
    "목": "木", "화": "火", "토": "土", "금": "金", "수": "水",
}

# 정량 정책 §2 "위험도/차단율 자유, 상위 12~20% / 하위 12~15%" 정합.
# 과다 백분위: 사주 분포상 상위에 잡히는 정도 (5종).
OHANG_EXCESS_PERCENTILE: dict[str, str] = {
    "목": "상위 13%",
    "화": "상위 12%",
    "토": "상위 17%",
    "금": "상위 14%",
    "수": "상위 15%",
}

# 부족 백분위: 사주 분포상 하위에 잡히는 정도 (5종).
OHANG_LACK_PERCENTILE: dict[str, str] = {
    "목": "하위 16%",
    "화": "하위 14%",
    "토": "하위 12%",
    "금": "하위 15%",
    "수": "하위 18%",
}

# 과다 오행별 신규 인연 접촉률 감소율. 정량 정책 §2 "차단율 60~88% 자유"의 작은 값
# (전체 차단이 아니라 *접촉률 저하*라 24~36% 범위).
OHANG_CONTACT_RATE_DROP: dict[str, str] = {
    "목": "28%",
    "화": "32%",
    "토": "24%",
    "금": "30%",
    "수": "36%",
}


# ── 일간 강점 문구 (단락 2) ─────────────────────────────────────

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


# ── 단락 3 합성 (위 dict에서 생성, 단일 진실원) ──────────────────

OHANG_EXCESS_PARA_3A: dict[str, str] = {
    oh: f"다만 오행 분포에서 {oh}({OHANG_HANJA[oh]}) 기운이 과다({OHANG_EXCESS_PERCENTILE[oh]}) 상태고,"
    for oh in OHANG_HANJA
}

OHANG_LACK_PARA_3B: dict[str, str] = {
    oh: (
        f"{oh}({OHANG_HANJA[oh]}) 기운이 부족({OHANG_LACK_PERCENTILE[oh]})으로 측정돼요. "
        "이 두 변수가 연애 영역에서 직접적인 영향을 주거든요."
    )
    for oh in OHANG_HANJA
}

OHANG_EXCESS_IMPACT: dict[str, str] = {
    oh: f"실제로 동일 패턴 표본의 신규 인연 접촉률이 평균보다 {OHANG_CONTACT_RATE_DROP[oh]} 낮게 잡혀요."
    for oh in OHANG_HANJA
}


PARA_4_CLOSING = "다음 장부터 이 변수들을 하나씩 분석해드릴게요. 그냥 따라오시면 돼요."


VALID_DOYOON_P0_ILGAN: frozenset[str] = frozenset(ILGAN_PARA_2.keys())
VALID_DOYOON_P0_OHANG: frozenset[str] = frozenset(OHANG_HANJA.keys())


# ── 합성 함수 (룰 fallback) ──────────────────────────────────────


def compose_doyoon_p0_intro(
    *,
    user_name: str,
    ilgan: str,
    ohang_excess: str,
    ohang_lack: str,
) -> str:
    """4단락 도윤 톤 합성. 220~300자 범위 출력.

    AI 호출 실패·검증 실패 시 fallback 경로로 호출됨.

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


# ── AI prompt + 검증용 facts 추출 ────────────────────────────────


def get_doyoon_p0_facts(
    *,
    user_name: str,
    ilgan: str,
    ohang_excess: str,
    ohang_lack: str,
) -> dict[str, str]:
    """AI prompt에 substituted 박을 사실값 + 출력 검증에 쓸 keys.

    AI는 이 사실값들을 *변경/누락 없이* 그대로 출력에 포함해야 함.
    검증 함수가 각 값이 AI 출력에 포함됐는지 verify.

    Returns:
        키 12개:
            user_name, ilgan_full, ilgan_hanja,
            excess_ohang, excess_ohang_hanja, excess_percentile,
            lack_ohang, lack_ohang_hanja, lack_percentile,
            contact_rate_drop,
            ilgan_para_2 (참고용 룰 합성 일간 강점 문구),
            rule_text (전체 룰 합성 결과 — AI variation 기반)

    Raises:
        ValueError / KeyError: compose와 동일 가드.
    """
    if not user_name:
        raise ValueError("doyoon P-0 facts require non-empty user_name")
    if ilgan not in VALID_DOYOON_P0_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")
    if ohang_excess not in VALID_DOYOON_P0_OHANG:
        raise KeyError(f"unknown ohang_excess: {ohang_excess!r}")
    if ohang_lack not in VALID_DOYOON_P0_OHANG:
        raise KeyError(f"unknown ohang_lack: {ohang_lack!r}")

    rule_text = compose_doyoon_p0_intro(
        user_name=user_name,
        ilgan=ilgan,
        ohang_excess=ohang_excess,
        ohang_lack=ohang_lack,
    )
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "ilgan_hanja": ILGAN_HANJA[ilgan],
        "excess_ohang": ohang_excess,
        "excess_ohang_hanja": OHANG_HANJA[ohang_excess],
        "excess_percentile": OHANG_EXCESS_PERCENTILE[ohang_excess],
        "lack_ohang": ohang_lack,
        "lack_ohang_hanja": OHANG_HANJA[ohang_lack],
        "lack_percentile": OHANG_LACK_PERCENTILE[ohang_lack],
        "contact_rate_drop": OHANG_CONTACT_RATE_DROP[ohang_excess],
        "ilgan_para_2": ILGAN_PARA_2[ilgan],
        "rule_text": rule_text,
    }
