"""도윤 P-3 데이터 풀 — 원본 도윤_final.html data-page-idx=3 구조 정합.

오행 5셀 (BlockadeOhangData) + 일간 10셀 (DoyoonP3IlganData) 매트릭스.
- 2-1 구조적 원인: 오행 dimension (ohang_excess 기반)
- 2-2 반복 패턴: 일간 dimension (3 패턴 × 10 일간)
- 2-2-1 변수 통제: 일간 dimension (2 strategies × 10 일간)

임수 일간 + 수 과다 셀은 원본 더미 그대로, 나머지는 도윤 톤 압축.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BlockadeOhangData:
    """오행 과다 구조적 원인 — 큰 card-warn 1 매핑."""
    ohang_hanja: str               # "水"
    blockade_pct: str              # "상위 15%"
    blockade_multiplier: str       # "1.7배"
    blockage_rate_drop: str        # "36%"
    recovery_after_clearing_pct: str  # "24%"


@dataclass(frozen=True)
class PatternEntry:
    """반복 실수 패턴 — card-warn × 3 매핑."""
    keyword: str                   # "초기 과진입"
    pct: str                       # "81%"
    multiplier: str                # "1.8배" 또는 "47%"
    desc: str


@dataclass(frozen=True)
class ControlStrategy:
    """변수 통제 전략 — card-good × 2 매핑."""
    keyword: str                   # "표현 빈도 상한선 설정"
    desc: str
    effect_pct: str                # "47%"


@dataclass(frozen=True)
class DoyoonP3IlganData:
    """일간별 P-3 데이터 (패턴 + 통제 + 안정성 + 버블 3종)."""
    patterns: tuple[PatternEntry, PatternEntry, PatternEntry]
    strategies: tuple[ControlStrategy, ControlStrategy]
    stability_boost_pct: str       # "41%"
    blockade_bubble: str
    pattern_bubble: str
    strategy_bubble: str


# 도윤_final.html 원본 SD asset (2-2-1 spotlight 고정)
P3_SD_ASSET: str = "dy_10"


# ────────────────────────────────────────────────────────────────
# 오행 5셀 — BlockadeOhangData
# ────────────────────────────────────────────────────────────────

# 임수+수 과다 케이스는 원본 더미. 나머지 4 오행은 정량 정책 §2 범위로 작성.
BLOCKADE_BY_OHANG: dict[str, BlockadeOhangData] = {
    "수": BlockadeOhangData(
        ohang_hanja="水",
        blockade_pct="상위 15%",
        blockade_multiplier="1.7배",
        blockage_rate_drop="36%",
        recovery_after_clearing_pct="24%",
    ),
    "목": BlockadeOhangData(
        ohang_hanja="木",
        blockade_pct="상위 13%",
        blockade_multiplier="1.6배",
        blockage_rate_drop="28%",
        recovery_after_clearing_pct="22%",
    ),
    "화": BlockadeOhangData(
        ohang_hanja="火",
        blockade_pct="상위 12%",
        blockade_multiplier="1.8배",
        blockage_rate_drop="32%",
        recovery_after_clearing_pct="26%",
    ),
    "토": BlockadeOhangData(
        ohang_hanja="土",
        blockade_pct="상위 17%",
        blockade_multiplier="1.5배",
        blockage_rate_drop="24%",
        recovery_after_clearing_pct="20%",
    ),
    "금": BlockadeOhangData(
        ohang_hanja="金",
        blockade_pct="상위 14%",
        blockade_multiplier="1.7배",
        blockage_rate_drop="30%",
        recovery_after_clearing_pct="23%",
    ),
}


# ────────────────────────────────────────────────────────────────
# 일간 10셀 — DoyoonP3IlganData
# ────────────────────────────────────────────────────────────────

DOYOON_P3_DATA: dict[str, DoyoonP3IlganData] = {
    # ── 임수 (원본 더미) ───────────────────────────────────────
    "임수": DoyoonP3IlganData(
        patterns=(
            PatternEntry(keyword="초기 과진입", pct="81%", multiplier="1.8배",
                         desc="첫 30일 내 감정 투입량이 평균 대비 1.8배입니다."),
            PatternEntry(keyword="중반 무표현", pct="67%", multiplier="47%",
                         desc="감정 투입은 유지되는데 표현 빈도가 47% 떨어집니다."),
            PatternEntry(keyword="위기 일괄 폭발", pct="54%", multiplier="2.1배",
                         desc="누적된 감정이 한 번에 표출되는 빈도가 평균 대비 2.1배입니다."),
        ),
        strategies=(
            ControlStrategy(keyword="표현 빈도 상한선 설정",
                            desc="주 단위 표현 횟수에 상한·하한 명시. 데이터상 이 한 가지만 적용해도 폭발 빈도가 47% 감소해요.",
                            effect_pct="47%"),
            ControlStrategy(keyword="감정 일지 24시간 룰",
                            desc="감정 발생 직후가 아니라 24시간 후에 표현. 충동 표현 비율이 평균 38% 감소합니다.",
                            effect_pct="38%"),
        ),
        stability_boost_pct="41%",
        blockade_bubble="분류 끝났어요. {USER_NAME}님 사주는 {OHANG_EXCESS} 과다 구조예요.",
        pattern_bubble="사람은 바뀌어도 패턴은 안 바뀌어요. 그래서 데이터가 의미가 있는 거예요.",
        strategy_bubble="지금 이걸 읽고 계신다는 것 자체가 이미 다음 연애가 달라진다는 신호예요.",
    ),
    # ── 갑목 ───────────────────────────────────────────────────
    "갑목": DoyoonP3IlganData(
        patterns=(
            PatternEntry(keyword="단방향 추진", pct="76%", multiplier="1.6배",
                         desc="결정 후 점검 빈도가 평균의 0.6배로 떨어지는 패턴입니다."),
            PatternEntry(keyword="협상 회피", pct="62%", multiplier="43%",
                         desc="합의 요구 입력 시 응답률이 43% 떨어집니다."),
            PatternEntry(keyword="끊고 떠남", pct="58%", multiplier="2.0배",
                         desc="신뢰 깨지면 재진입 거부 빈도가 평균 대비 2.0배입니다."),
        ),
        strategies=(
            ControlStrategy(keyword="결정 전 30초 점검 룰",
                            desc="결정 직전 30초 점검만 추가해도 후속 충돌 빈도가 38% 감소합니다.",
                            effect_pct="38%"),
            ControlStrategy(keyword="협상 입력 1회 수용",
                            desc="대안 제시 1건만 의식적으로 수용하면 관계 안정성이 평균 32% 향상됩니다.",
                            effect_pct="32%"),
        ),
        stability_boost_pct="36%",
        blockade_bubble="분류 끝났어요. {USER_NAME}님 사주는 {OHANG_EXCESS} 과다 구조예요.",
        pattern_bubble="단호한 게 강점이지만, 단호함만으로는 관계가 누적 안 돼요.",
        strategy_bubble="점검 한 번이 결정 자체를 흔드는 게 아니에요. 결정 품질을 높이는 거예요.",
    ),
    # ── 을목 ───────────────────────────────────────────────────
    "을목": DoyoonP3IlganData(
        patterns=(
            PatternEntry(keyword="환경 과적응", pct="78%", multiplier="1.5배",
                         desc="상대 환경 맞추다 자기 신호 강도가 평균 0.6배로 떨어집니다."),
            PatternEntry(keyword="자기 표현 누락", pct="71%", multiplier="38%",
                         desc="자기 의사 명시 빈도가 평균 38% 적게 측정됩니다."),
            PatternEntry(keyword="끊임없는 흡수", pct="56%", multiplier="1.7배",
                         desc="갈등 흡수량이 평균 1.7배로 누적 임계점 도달 빈도가 높습니다."),
        ),
        strategies=(
            ControlStrategy(keyword="자기 신호 주 1회 표명",
                            desc="자기 의사 한 줄 명시화 주 1회. 자기 위치 인식률이 평균 35% 회복됩니다.",
                            effect_pct="35%"),
            ControlStrategy(keyword="흡수량 한계 설정",
                            desc="감정 흡수 임계점 사전 설정. 누적 폭발 빈도가 31% 감소합니다.",
                            effect_pct="31%"),
        ),
        stability_boost_pct="33%",
        blockade_bubble="분류 끝났어요. {USER_NAME}님 사주는 {OHANG_EXCESS} 과다 구조예요.",
        pattern_bubble="휘어 들어가는 게 능력인데, 휘어만 있으면 본인이 없어져요.",
        strategy_bubble="자기 한 줄이 매주 들어가야 관계 안에서 본인이 보입니다.",
    ),
    # ── 병화 ───────────────────────────────────────────────────
    "병화": DoyoonP3IlganData(
        patterns=(
            PatternEntry(keyword="고출력 즉시 발산", pct="83%", multiplier="1.9배",
                         desc="첫 만남 출력 강도가 평균 1.9배로 측정됩니다."),
            PatternEntry(keyword="응답 격차 감지", pct="69%", multiplier="42%",
                         desc="출력 대비 응답 비율이 42% 미달 시 차단율이 급증합니다."),
            PatternEntry(keyword="페이스 변동", pct="51%", multiplier="2.2배",
                         desc="고텐션 → 저텐션 전환 빈도가 평균 2.2배입니다."),
        ),
        strategies=(
            ControlStrategy(keyword="출력 단계 분산",
                            desc="첫 3주 출력 강도를 평균선까지 낮추면 지속률이 39% 향상됩니다.",
                            effect_pct="39%"),
            ControlStrategy(keyword="응답 측정 후 매칭",
                            desc="상대 응답 능력 사전 측정 후 출력 조정. 차단율이 평균 34% 감소합니다.",
                            effect_pct="34%"),
        ),
        stability_boost_pct="38%",
        blockade_bubble="분류 끝났어요. {USER_NAME}님 사주는 {OHANG_EXCESS} 과다 구조예요.",
        pattern_bubble="빛을 비추기 전에 받을 사람인지 측정하세요.",
        strategy_bubble="출력 강도는 통제 가능한 변수예요. 데이터가 그렇게 말합니다.",
    ),
    # ── 정화 ───────────────────────────────────────────────────
    "정화": DoyoonP3IlganData(
        patterns=(
            PatternEntry(keyword="한 사람 깊이 침잠", pct="74%", multiplier="1.7배",
                         desc="단일 대상 집중도가 평균 1.7배로 잠재 손실이 큽니다."),
            PatternEntry(keyword="조용한 정성 누적", pct="68%", multiplier="33%",
                         desc="비공개 헌신 빈도가 평균 대비 33% 더 많이 측정됩니다."),
            PatternEntry(keyword="시선 분산 시 단절", pct="52%", multiplier="1.9배",
                         desc="시선 이동 감지 시 차단율이 평균 1.9배로 급증합니다."),
        ),
        strategies=(
            ControlStrategy(keyword="정성 명시화 룰",
                            desc="조용한 헌신을 명시 신호로 옮기는 주 2회 룰. 인지율이 평균 42% 향상됩니다.",
                            effect_pct="42%"),
            ControlStrategy(keyword="집중 분산 임계 설정",
                            desc="한 대상 집중도 임계점 설정. 차단 발화 시 회복 속도가 36% 빨라집니다.",
                            effect_pct="36%"),
        ),
        stability_boost_pct="44%",
        blockade_bubble="분류 끝났어요. {USER_NAME}님 사주는 {OHANG_EXCESS} 과다 구조예요.",
        pattern_bubble="등불은 봐주는 사람이 있을 때 의미가 있어요.",
        strategy_bubble="작은 명시 하나가 인지율을 결정합니다.",
    ),
    # ── 무토 ───────────────────────────────────────────────────
    "무토": DoyoonP3IlganData(
        patterns=(
            PatternEntry(keyword="안정 변수 과집착", pct="72%", multiplier="1.5배",
                         desc="변동성 입력 시 응답 거부 빈도가 평균 1.5배입니다."),
            PatternEntry(keyword="속도 차이 정지", pct="65%", multiplier="36%",
                         desc="가속 입력 시 응답 정지 빈도가 평균 36% 높습니다."),
            PatternEntry(keyword="신뢰 검증 장기화", pct="59%", multiplier="1.7배",
                         desc="신뢰 누적 임계점 도달 시간이 평균 1.7배입니다."),
        ),
        strategies=(
            ControlStrategy(keyword="작은 변화 신호 허용",
                            desc="주 1회 작은 변화 입력 수용. 매칭 인지 속도가 평균 40% 빨라집니다.",
                            effect_pct="40%"),
            ControlStrategy(keyword="신뢰 검증 단계 압축",
                            desc="신뢰 검증 단계 2개 축소. 진입 속도가 평균 33% 향상됩니다.",
                            effect_pct="33%"),
        ),
        stability_boost_pct="35%",
        blockade_bubble="분류 끝났어요. {USER_NAME}님 사주는 {OHANG_EXCESS} 과다 구조예요.",
        pattern_bubble="안정은 강점이지만 외부 입력 차단 신호로도 작동해요.",
        strategy_bubble="작은 변화 한 가지가 안정 변수를 깨지 않습니다.",
    ),
    # ── 기토 ───────────────────────────────────────────────────
    "기토": DoyoonP3IlganData(
        patterns=(
            PatternEntry(keyword="일방향 헌신", pct="79%", multiplier="1.6배",
                         desc="상대 우선 빈도가 자기 우선의 1.6배로 누적 소진이 큽니다."),
            PatternEntry(keyword="자기 우선순위 누락", pct="73%", multiplier="40%",
                         desc="자기 의사 표현 빈도가 평균 40% 적게 측정됩니다."),
            PatternEntry(keyword="누적 후 일괄 정지", pct="55%", multiplier="2.0배",
                         desc="자기 소진 임계점 도달 시 응답 정지 빈도가 평균 2.0배입니다."),
        ),
        strategies=(
            ControlStrategy(keyword="자기 우선순위 명시화",
                            desc="자기 욕구 한 가지 명시 표현 주 1회. 균형 회복률이 평균 38% 향상됩니다.",
                            effect_pct="38%"),
            ControlStrategy(keyword="헌신 시간 상한 설정",
                            desc="주 단위 헌신 시간 상한 설정. 자기 소진 임계점 도달 시간이 45% 늦춰집니다.",
                            effect_pct="45%"),
        ),
        stability_boost_pct="40%",
        blockade_bubble="분류 끝났어요. {USER_NAME}님 사주는 {OHANG_EXCESS} 과다 구조예요.",
        pattern_bubble="다 주는 게 사랑이 아니에요. 자기 변수가 보존돼야 관계가 누적돼요.",
        strategy_bubble="자기 한 줄이 매주 들어가야 매칭이 균형 잡힙니다.",
    ),
    # ── 경금 ───────────────────────────────────────────────────
    "경금": DoyoonP3IlganData(
        patterns=(
            PatternEntry(keyword="이분법적 판단", pct="77%", multiplier="1.7배",
                         desc="모호 입력 시 차단 결정 빈도가 평균 1.7배입니다."),
            PatternEntry(keyword="감정 우회 표현", pct="64%", multiplier="37%",
                         desc="간접 표현 입력 시 신뢰 변수가 평균 37% 빠르게 감소합니다."),
            PatternEntry(keyword="단호한 단절", pct="57%", multiplier="2.1배",
                         desc="신뢰 위반 감지 시 재진입 거부 빈도가 평균 2.1배입니다."),
        ),
        strategies=(
            ControlStrategy(keyword="모호 입력 24시간 유보",
                            desc="모호 신호 즉시 판단 X, 24시간 유보. 오판 빈도가 평균 41% 감소합니다.",
                            effect_pct="41%"),
            ControlStrategy(keyword="감정 단계 명시 표현",
                            desc="감정 단계를 직설 표현으로 명시화. 신뢰 변수 안정성이 평균 35% 향상됩니다.",
                            effect_pct="35%"),
        ),
        stability_boost_pct="37%",
        blockade_bubble="분류 끝났어요. {USER_NAME}님 사주는 {OHANG_EXCESS} 과다 구조예요.",
        pattern_bubble="명확함이 강점이지만, 명확함만으로는 모호 신호를 못 읽어요.",
        strategy_bubble="24시간 유보가 결정을 약하게 만드는 게 아니에요. 결정 정확도를 높이는 거예요.",
    ),
    # ── 신금 ───────────────────────────────────────────────────
    "신금": DoyoonP3IlganData(
        patterns=(
            PatternEntry(keyword="작은 약속 과중량", pct="75%", multiplier="1.6배",
                         desc="작은 신뢰 위반 시 누적 손실이 평균 1.6배로 측정됩니다."),
            PatternEntry(keyword="자기 보호 장기화", pct="70%", multiplier="34%",
                         desc="첫 마음 열기까지 시간이 평균 34% 더 걸립니다."),
            PatternEntry(keyword="흠집 인덱스 보존", pct="53%", multiplier="1.9배",
                         desc="옛 손실 데이터 잔존 시간이 평균 1.9배로 깁니다."),
        ),
        strategies=(
            ControlStrategy(keyword="작은 신뢰 위반 분류",
                            desc="신뢰 위반 강도 사전 분류 후 응답. 과민 반응 빈도가 평균 39% 감소합니다.",
                            effect_pct="39%"),
            ControlStrategy(keyword="자기 보호 단계 축소",
                            desc="자기 보호 검증 단계 1개 축소. 진입 속도가 평균 32% 향상됩니다.",
                            effect_pct="32%"),
        ),
        stability_boost_pct="36%",
        blockade_bubble="분류 끝났어요. {USER_NAME}님 사주는 {OHANG_EXCESS} 과다 구조예요.",
        pattern_bubble="섬세함이 강점이지만, 잔여 인덱스가 새 입력을 막아요.",
        strategy_bubble="작은 신뢰 위반에 모두 같은 강도로 응답하지 마세요.",
    ),
    # ── 계수 ───────────────────────────────────────────────────
    "계수": DoyoonP3IlganData(
        patterns=(
            PatternEntry(keyword="잠재 신호 누적", pct="76%", multiplier="1.8배",
                         desc="명시 표현 빈도가 평균 0.5배로 누적 잠재 신호량이 큽니다."),
            PatternEntry(keyword="속도 무시 감지 시 흩어짐", pct="68%", multiplier="35%",
                         desc="가속 입력 시 응답 흐려짐 빈도가 평균 35% 높습니다."),
            PatternEntry(keyword="자기 가치 감소", pct="54%", multiplier="2.0배",
                         desc="미인지 누적 시 자기 가치 변수 감소 속도가 평균 2.0배입니다."),
        ),
        strategies=(
            ControlStrategy(keyword="잠재 신호 명시화",
                            desc="잠재 신호 한 가지를 명시 표현으로 옮기는 주 1회 룰. 인지율이 평균 43% 향상됩니다.",
                            effect_pct="43%"),
            ControlStrategy(keyword="자기 가치 객관 분석",
                            desc="외부 평가 분석 후 자기 가치 변수 재조정. 안정성이 평균 37% 향상됩니다.",
                            effect_pct="37%"),
        ),
        stability_boost_pct="39%",
        blockade_bubble="분류 끝났어요. {USER_NAME}님 사주는 {OHANG_EXCESS} 과다 구조예요.",
        pattern_bubble="잠재 신호는 본인 안에서만 보여요. 외부로 옮겨야 인지됩니다.",
        strategy_bubble="명시화 한 가지가 인지율을 결정합니다.",
    ),
}


VALID_DOYOON_P3_ILGAN: frozenset[str] = frozenset(DOYOON_P3_DATA.keys())
VALID_DOYOON_P3_OHANG: frozenset[str] = frozenset(BLOCKADE_BY_OHANG.keys())
