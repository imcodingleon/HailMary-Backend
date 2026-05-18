"""도윤 P-1 일간 10셀 데이터 풀.

HTML 도윤_final.html line 1974~2096 (P-1 1-1/1-2/1-3) 변수 매핑:
- love_type: 일간별 연애 유형 한 줄 (도윤 톤, 분석적)
- pct_value: 상위 N% — {ILGAN} 일간 표본 안에서 동일 유형 분포의 상위 위치
- distribution_pct: 전체 표본 대비 {ILGAN} 일간 비율 (예: 12.4%)
- trigger_1/2/3: 감정 발화 트리거 3종 (30% → 62% → 88% flow)
- emotion_curve: 4 데이터 포인트 (초반/중반/위기/회복 강도 %)
- crisis_multiplier: 위기 구간 평균 대비 배수 (예: "1.8배")
- self_control_pct: 처음 30일 자기조절 성공률
- expression_effect_pct: 표현 빈도 ↑ 시 위기 강도 감소 폭

톤: 도윤 — 존댓말 + 분석적 + 통계 어휘.
어휘 다양화 (`feedback_template_word_diversity`): P-0 시그니처 어휘(표본/분포/임계점/전환율)는
유지하되, 페이지별 다른 변형 어휘 추가 — "분류", "케이스", "구간", "발화", "도달 확률".
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DoyoonP1IlganData:
    love_type: str
    pct_value: int                       # 상위 N% (1~30)
    distribution_pct: float              # 전체 표본 분포 (8.0~15.0)
    trigger_1: str
    trigger_2: str
    trigger_3: str
    emotion_curve: tuple[int, int, int, int]   # (초반, 중반, 위기, 회복) %
    crisis_multiplier: str               # "1.7배" / "1.8배" / "2.0배"
    self_control_pct: int                # 자기조절 (12~38)
    expression_effect_pct: int           # 표현 효과 (24~38)


DOYOON_P1_DATA: dict[str, DoyoonP1IlganData] = {
    "갑목": DoyoonP1IlganData(
        love_type="직진 추진형 명확 의사결정자",
        pct_value=11,
        distribution_pct=10.8,
        trigger_1="공통 신념 발견",
        trigger_2="분명한 의사 표시",
        trigger_3="직접적인 거리 좁힘",
        emotion_curve=(50, 80, 90, 65),
        crisis_multiplier="1.6배",
        self_control_pct=34,
        expression_effect_pct=28,
    ),
    "을목": DoyoonP1IlganData(
        love_type="적응 우선형 점진 진입자",
        pct_value=18,
        distribution_pct=11.5,
        trigger_1="안전한 분위기 형성",
        trigger_2="일관된 관심 신호",
        trigger_3="깊은 이해 표명",
        emotion_curve=(35, 70, 85, 55),
        crisis_multiplier="1.7배",
        self_control_pct=22,
        expression_effect_pct=30,
    ),
    "병화": DoyoonP1IlganData(
        love_type="고텐션 즉시 발산자",
        pct_value=9,
        distribution_pct=11.1,
        trigger_1="호응하는 리액션",
        trigger_2="같은 텐션의 대화",
        trigger_3="즉각 답신 빈도",
        emotion_curve=(60, 88, 92, 78),
        crisis_multiplier="1.7배",
        self_control_pct=20,
        expression_effect_pct=26,
    ),
    "정화": DoyoonP1IlganData(
        love_type="한 사람 집중형 깊이 케이스",
        pct_value=7,
        distribution_pct=8.6,
        trigger_1="사적 관심사 공유",
        trigger_2="차분한 시선 누적",
        trigger_3="한 주제 깊은 몰입",
        emotion_curve=(30, 65, 88, 45),
        crisis_multiplier="1.9배",
        self_control_pct=18,
        expression_effect_pct=34,
    ),
    "무토": DoyoonP1IlganData(
        love_type="안정 추구형 신중 진입자",
        pct_value=14,
        distribution_pct=12.0,
        trigger_1="시간 약속 지킴 반복",
        trigger_2="큰 변화 없는 일관성",
        trigger_3="점진적 신뢰 누적",
        emotion_curve=(25, 55, 75, 50),
        crisis_multiplier="1.5배",
        self_control_pct=38,
        expression_effect_pct=24,
    ),
    "기토": DoyoonP1IlganData(
        love_type="받쳐주기 우선형 헌신 케이스",
        pct_value=15,
        distribution_pct=10.3,
        trigger_1="도움이 필요한 신호",
        trigger_2="약점 노출 순간",
        trigger_3="의지하는 분위기",
        emotion_curve=(40, 72, 85, 52),
        crisis_multiplier="1.7배",
        self_control_pct=23,
        expression_effect_pct=29,
    ),
    "경금": DoyoonP1IlganData(
        love_type="명확 판단형 직설 표현자",
        pct_value=12,
        distribution_pct=9.7,
        trigger_1="명확한 선호 표명",
        trigger_2="솔직한 피드백 교환",
        trigger_3="단호한 거리 좁힘",
        emotion_curve=(45, 78, 92, 70),
        crisis_multiplier="1.7배",
        self_control_pct=32,
        expression_effect_pct=27,
    ),
    "신금": DoyoonP1IlganData(
        love_type="단정 매력 노출형 보호 케이스",
        pct_value=10,
        distribution_pct=9.4,
        trigger_1="디테일 알아채는 시선",
        trigger_2="감각적 인정 신호",
        trigger_3="보호 의지 표명",
        emotion_curve=(32, 68, 90, 48),
        crisis_multiplier="1.8배",
        self_control_pct=26,
        expression_effect_pct=31,
    ),
    "임수": DoyoonP1IlganData(
        love_type="정보 처리형 신중 진입자",
        pct_value=8,
        distribution_pct=12.4,
        trigger_1="공유된 지적 발견",
        trigger_2="답 빠른 메시지 응답",
        trigger_3="의식적인 거리 좁힘",
        emotion_curve=(45, 85, 95, 60),
        crisis_multiplier="1.8배",
        self_control_pct=17,
        expression_effect_pct=32,
    ),
    "계수": DoyoonP1IlganData(
        love_type="스며들기 우선형 섬세 케이스",
        pct_value=13,
        distribution_pct=10.1,
        trigger_1="잔잔한 디테일 캐치",
        trigger_2="침묵 공유의 편안함",
        trigger_3="작은 변화 알아챔",
        emotion_curve=(28, 60, 82, 45),
        crisis_multiplier="1.6배",
        self_control_pct=19,
        expression_effect_pct=35,
    ),
}


VALID_DOYOON_P1_ILGAN: frozenset[str] = frozenset(DOYOON_P1_DATA.keys())
