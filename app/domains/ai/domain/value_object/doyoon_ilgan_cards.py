"""도윤 일간 10종 정적 카드 풀.

HTML line 1846~1887 (P-0 0-3 일간 분석 카드) 도윤 패널 양식:
- 헤더: {USER_NAME}님의 일간 — 한글(한자)
- 부제: 데이터형 한 줄 (예: "큰 물 / 깊은 바다 유형")
- 데이터 특성: 3 bullet (통계 수치 — "평균 대비 N배" 형식)
- 연애 특화 변수: 3 bullet (관계 outcome — "↑ / ↓ / ↑↑" 화살표 표기)
- 주요 변수 충돌: 1줄 (어떤 매칭에서 충돌하는지)

톤: 존댓말 안 들어감 (카드는 객관 데이터). 통계 어휘 + 화살표.
LLM 호출 비용 0. 사용자 일간 정해지면 dict 조회로 즉시 반환.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class DoyoonIlganCard:
    name_kor: str
    name_han: str
    subtitle: str
    data_traits: tuple[str, str, str]
    love_variables: tuple[str, str, str]
    main_conflict: str


DOYOON_ILGAN_CARDS: dict[str, DoyoonIlganCard] = {
    "갑목": DoyoonIlganCard(
        name_kor="갑목",
        name_han="甲木",
        subtitle="큰 나무 / 직선 추진 유형",
        data_traits=(
            "의사결정 속도 평균 대비 1.4배",
            "방향 전환 빈도 0.5배",
            "신념 일관성 1.8배",
        ),
        love_variables=(
            "첫 접근 추진력 ↑",
            "관계 방향 통제력 ↑",
            "의견 충돌 임계점 ↓",
        ),
        main_conflict="우회와 타협을 요구하는 상대와 매칭 시 충돌.",
    ),
    "을목": DoyoonIlganCard(
        name_kor="을목",
        name_han="乙木",
        subtitle="풀·덩굴 / 적응 생존 유형",
        data_traits=(
            "적응 속도 평균 대비 1.6배",
            "환경 의존도 1.3배",
            "자기 표현 빈도 0.7배",
        ),
        love_variables=(
            "상대 맞춤 적응력 ↑",
            "관계 감김 깊이 ↑",
            "단호한 끊음 ↓",
        ),
        main_conflict="결단 빠른 상대와 장기 매칭 시 자기 소진.",
    ),
    "병화": DoyoonIlganCard(
        name_kor="병화",
        name_han="丙火",
        subtitle="태양 / 광범위 발산 유형",
        data_traits=(
            "표현 빈도 평균 대비 1.9배",
            "에너지 노출도 1.5배",
            "감정 회복 속도 1.3배",
        ),
        love_variables=(
            "첫인상 강도 ↑",
            "관계 페이스 빠름",
            "지속 집중도 ↓",
        ),
        main_conflict="느린 페이스 선호 상대와 매칭 시 흥미 저하 가속.",
    ),
    "정화": DoyoonIlganCard(
        name_kor="정화",
        name_han="丁火",
        subtitle="등불 / 한 점 집중 유형",
        data_traits=(
            "깊이감 평균 대비 1.6배",
            "표현 폭 0.8배",
            "한 사람 집중도 1.7배",
        ),
        love_variables=(
            "장기 관계 유지율 ↑",
            "일관성 ↑",
            "첫 진입 속도 ↓",
        ),
        main_conflict="즉각 반응 요구하는 상대와 매칭 시 피로 누적.",
    ),
    "무토": DoyoonIlganCard(
        name_kor="무토",
        name_han="戊土",
        subtitle="산 / 묵직한 안정 유형",
        data_traits=(
            "안정성 평균 대비 1.8배",
            "변화 수용 0.6배",
            "신뢰 누적 속도 1.5배",
        ),
        love_variables=(
            "관계 안정감 ↑",
            "결정 후 변경 빈도 ↓",
            "첫 진입 신중함 ↑",
        ),
        main_conflict="변동성 큰 상대와 매칭 시 답답함 누적.",
    ),
    "기토": DoyoonIlganCard(
        name_kor="기토",
        name_han="己土",
        subtitle="옥토 / 받쳐주는 유형",
        data_traits=(
            "수용도 평균 대비 1.7배",
            "자기 우선순위 0.6배",
            "헌신 빈도 1.6배",
        ),
        love_variables=(
            "상대 성장 지원 ↑",
            "자기 표현 ↓",
            "소진 위험 ↑",
        ),
        main_conflict="받기만 하는 상대와 매칭 시 일방향 소진.",
    ),
    "경금": DoyoonIlganCard(
        name_kor="경금",
        name_han="庚金",
        subtitle="단단한 금속 / 명확 판단 유형",
        data_traits=(
            "판단 명확성 평균 대비 1.7배",
            "모호함 수용도 0.4배",
            "결단 속도 1.5배",
        ),
        love_variables=(
            "옳고 그름 정리 ↑",
            "부드러운 표현 ↓",
            "갈등 임계점 ↓",
        ),
        main_conflict="감정적 모호함을 즐기는 상대와 매칭 시 충돌.",
    ),
    "신금": DoyoonIlganCard(
        name_kor="신금",
        name_han="辛金",
        subtitle="보석 / 단정 매력 유형",
        data_traits=(
            "매력 노출도 평균 대비 1.6배",
            "정서 깊이 1.4배",
            "자기 보호 강도 1.7배",
        ),
        love_variables=(
            "매력 어필 ↑",
            "첫 마음 열기 ↓",
            "상처 누적 시간 ↑",
        ),
        main_conflict="갈무리 못 하는 상대와 매칭 시 상처 오래 새김.",
    ),
    "임수": DoyoonIlganCard(
        name_kor="임수",
        name_han="壬水",
        subtitle="큰 물 / 깊은 바다 유형",
        data_traits=(
            "깊이감 평균 대비 1.7배",
            "표현 빈도 0.4배",
            "감정 회복 속도 1.4배 느림",
        ),
        love_variables=(
            "장기 관계 유지율 ↑",
            "첫 진입 속도 ↓",
            "깊이 호환 매칭 시 안정성 ↑↑",
        ),
        main_conflict="표현 따라잡기 못하는 상대와 매칭 시 충돌.",
    ),
    "계수": DoyoonIlganCard(
        name_kor="계수",
        name_han="癸水",
        subtitle="실개천 / 스며듦 유형",
        data_traits=(
            "섬세함 평균 대비 1.8배",
            "자기 주장 0.5배",
            "환경 적응 1.5배",
        ),
        love_variables=(
            "디테일 캐치 ↑",
            "명시적 표현 ↓",
            "잠재 욕구 누적 ↑",
        ),
        main_conflict="큰 흐름만 보는 상대와 매칭 시 자기 사라짐.",
    ),
}


VALID_DOYOON_ILGAN: frozenset[str] = frozenset(DOYOON_ILGAN_CARDS.keys())
