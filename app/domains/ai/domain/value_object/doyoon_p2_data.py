"""도윤 P-2 일간 10셀 데이터 풀.

yeonwoo_p2_hurt + yeonwoo_p2_recovery의 시나리오/회복 데이터를
도윤 톤(존댓말 + 통계 어휘)으로 변환. 시나리오 자체는 동일 (사용자 검수 완료).

회복 속도 3그룹 (FAST/MEDIUM/SLOW) — yeonwoo와 동일 분류.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

RecoverySpeed = Literal["fast", "medium", "slow"]


@dataclass(frozen=True)
class HurtScenario:
    """약점 트리거 시나리오 1개."""
    when: str   # 트리거 상황 라벨
    desc: str   # 데이터 분석 한 줄


@dataclass(frozen=True)
class RecoveryTimelineCard:
    """회복 단계 카드 1개."""
    time: str   # 시간 라벨 ("직후" 등)
    title: str  # 객관 라벨
    desc: str   # 도윤 톤 한 줄


@dataclass(frozen=True)
class DoyoonP2IlganData:
    # 1-4 상처
    scenarios: tuple[HurtScenario, HurtScenario]
    vulnerability_pct: str          # 약점 발현률 (60~85%)
    common_pattern_pct: str         # 동일 패턴 표본 비율 (60~80%)
    hurt_optimization: str          # 처방 한 줄 (도윤 톤)
    hurt_bubble: str                # 한도윤 클로징 (한 줄)
    # 1-5 회복
    speed: RecoverySpeed
    timeline_cards: tuple[RecoveryTimelineCard, RecoveryTimelineCard, RecoveryTimelineCard]
    recovery_lag_multiplier: str    # 평균 대비 회복 지연 (1.0~1.8배)
    recovery_accel_value: str       # 회복 가속 처방 (한 줄)
    recovery_accel_sub: str         # 가속 한도윤 멘트
    recovery_optimization: str      # 처방 한 줄


# 그룹별 시간 라벨 (yeonwoo와 동일)
TIME_LABELS_BY_SPEED: dict[RecoverySpeed, tuple[str, str, str]] = {
    "fast":   ("직후", "3일 후", "2주 후"),
    "medium": ("직후", "1개월 후", "3개월 후"),
    "slow":   ("직후", "3개월 후", "6개월 후"),
}


# ────────────────────────────────────────────────────────────────
# 10 일간 데이터 (임수 정성 작성 + 나머지 9 셀 도윤 톤 압축)
# ────────────────────────────────────────────────────────────────


def _t(speed: RecoverySpeed) -> tuple[str, str, str]:
    return TIME_LABELS_BY_SPEED[speed]


DOYOON_P2_DATA: dict[str, DoyoonP2IlganData] = {
    # ── 임수 (정성 작성 — 모범 셀, 사용자 P-1 텍스트 톤 추종) ──────
    "임수": DoyoonP2IlganData(
        scenarios=(
            HurtScenario(
                when="무시당했다고 느끼는 순간",
                desc="정보 처리량 많은 케이스라 무시 입력 시 외부 출력 대신 내부 침잠으로 잡혀요.",
            ),
            HurtScenario(
                when="속마음을 못 읽어줄 때",
                desc="명시적 표현 빈도가 평균의 0.4배라 상대가 신호 인지 실패 케이스가 누적돼요.",
            ),
        ),
        vulnerability_pct="78%",
        common_pattern_pct="64%",
        hurt_optimization="작은 신호 주 2회 의식적 노출 시 침잠 구간 강도가 평균 32% 감소합니다.",
        hurt_bubble="안 꺼내면 안에서 갇혀요. 표현 빈도가 데이터로 가장 빠른 처방입니다.",
        speed="slow",
        timeline_cards=(
            RecoveryTimelineCard(
                time=_t("slow")[0],
                title="일상 곳곳에서 흔적 감지",
                desc="정보 처리량이 많아 일상 모든 입력에 옛 데이터가 결합되는 구간이에요.",
            ),
            RecoveryTimelineCard(
                time=_t("slow")[1],
                title="표면 회복, 내면 미정리",
                desc="외부 출력은 정상화돼도 내부 처리량 잔여가 평균보다 1.4배 깁니다.",
            ),
            RecoveryTimelineCard(
                time=_t("slow")[2],
                title="새 입력 받을 준비 완료",
                desc="옛 데이터 인덱스가 충분히 흐려져 새 매칭 받을 임계점에 도달해요.",
            ),
        ),
        recovery_lag_multiplier="1.4배",
        recovery_accel_value="감정 일지 24시간 룰 + 표현 빈도 주 2회",
        recovery_accel_sub="내부 처리량을 외부로 출력하는 두 채널 — 회복 곡선이 평균보다 빨라집니다.",
        recovery_optimization="끊긴 입력은 끊긴 채로 인덱싱하세요. 재진입 시도는 회복 곡선을 평균 1.4배 늦춥니다.",
    ),
    # ── 갑목 (압축, fast 그룹) ─────────────────────────────────
    "갑목": DoyoonP2IlganData(
        scenarios=(
            HurtScenario(
                when="본인이 결정한 사안에 간섭이 들어오는 케이스",
                desc="독립적 의사결정 패턴 표본에서 외부 입력이 가장 큰 위험 변수로 잡혀요.",
            ),
            HurtScenario(
                when="자력으로 만든 성과를 가볍게 평가하는 입력",
                desc="신념 일관성 1.8배 케이스에서 평가절하 입력 시 회복 시간이 평균보다 길어요.",
            ),
        ),
        vulnerability_pct="72%",
        common_pattern_pct="68%",
        hurt_optimization="외부 평가 입력 필터링을 의식적으로 두 번 거치시면 변동성이 줄어들어요.",
        hurt_bubble="단호한 만큼 부서지기 쉽습니다. 한 번은 의식적으로 풀어두세요.",
        speed="fast",
        timeline_cards=(
            RecoveryTimelineCard(
                time=_t("fast")[0],
                title="즉시 정리 모드 진입",
                desc="의사결정 속도 평균 1.4배 케이스라 정리 진입도 즉시 발화돼요.",
            ),
            RecoveryTimelineCard(
                time=_t("fast")[1],
                title="본인 일에 즉시 몰입 재개",
                desc="옛 관계 데이터에 가중치를 빠르게 0으로 수렴시키는 패턴이에요.",
            ),
            RecoveryTimelineCard(
                time=_t("fast")[2],
                title="기억 인덱스 빠르게 흐려짐",
                desc="신념 일관성이 새 방향 추진력으로 전환된 상태입니다.",
            ),
        ),
        recovery_lag_multiplier="0.7배",
        recovery_accel_value="일정 재구조화 + 새 프로젝트 진입",
        recovery_accel_sub="결단 속도 케이스라 새 입력에 가중치 부여하는 게 가장 빠른 가속법입니다.",
        recovery_optimization="끊은 사람에게 재접촉 시도는 권하지 않습니다. 재진입 시 자기 신뢰 변수가 0.6배로 감소해요.",
    ),
    # ── 을목 (medium) ────────────────────────────────────────
    "을목": DoyoonP2IlganData(
        scenarios=(
            HurtScenario(
                when="정성 입력이 인지되지 않는 케이스",
                desc="적응 우선형이라 작은 헌신이 누적되는데 미인지 시 표본 위험도가 평균보다 높아요.",
            ),
            HurtScenario(
                when="혼자 남겨지는 입력 발생 순간",
                desc="환경 의존도 1.3배 케이스라 단기 부재도 큰 변동성으로 해석돼요.",
            ),
        ),
        vulnerability_pct="74%",
        common_pattern_pct="66%",
        hurt_optimization="상대 부재 시 짧은 안내 입력 한 번이면 변동성이 평균 28% 감소합니다.",
        hurt_bubble="혼자 두지 않는 사람만 옆에 두세요. 데이터가 그렇게 말합니다.",
        speed="medium",
        timeline_cards=(
            RecoveryTimelineCard(
                time=_t("medium")[0],
                title="혼자 시간 견디기 어려움",
                desc="환경 의존도 1.3배 케이스라 부재 입력이 가장 큰 변수로 잡혀요.",
            ),
            RecoveryTimelineCard(
                time=_t("medium")[1],
                title="사회 접촉 빈도 자가 회복",
                desc="옛 데이터 가중치를 새 접촉으로 분산하는 패턴이에요.",
            ),
            RecoveryTimelineCard(
                time=_t("medium")[2],
                title="새 매칭 입력 가능 임계점",
                desc="환경 적응 완료, 새 매칭 받을 안정 구간에 도달했어요.",
            ),
        ),
        recovery_lag_multiplier="1.1배",
        recovery_accel_value="사회 접촉 빈도 주 3회 이상 유지",
        recovery_accel_sub="환경 의존도 케이스라 접촉 빈도가 회복 곡선의 주 변수입니다.",
        recovery_optimization="자주 사라지는 입력원은 매칭에서 제외하세요. 안정성 변수가 0.5배로 떨어집니다.",
    ),
    # ── 병화 (fast) ──────────────────────────────────────────
    "병화": DoyoonP2IlganData(
        scenarios=(
            HurtScenario(
                when="고텐션 출력에 저텐션 응답이 들어올 때",
                desc="표현 빈도 1.9배 케이스라 응답 격차가 거절 신호로 해석되는 빈도가 높아요.",
            ),
            HurtScenario(
                when="입력 대비 출력 불균형 케이스",
                desc="100 출력 시 50 미만 입력이 들어오면 위험 변수로 자동 분류돼요.",
            ),
        ),
        vulnerability_pct="70%",
        common_pattern_pct="65%",
        hurt_optimization="상대 출력 능력을 사전 측정한 후 출력량 조절하시면 차단율이 평균 30% 감소해요.",
        hurt_bubble="비추기 전에 한 번 측정하세요. 받을 케이스인지 확인이 우선입니다.",
        speed="fast",
        timeline_cards=(
            RecoveryTimelineCard(
                time=_t("fast")[0],
                title="외부 출력 정상, 내부 무너짐",
                desc="공개 출력은 평소대로 유지되는데 사적 구간에서 변동성 폭증해요.",
            ),
            RecoveryTimelineCard(
                time=_t("fast")[1],
                title="관심 변수 이동 시작",
                desc="새 입력에 가중치 부여 패턴이 자가 발화돼요.",
            ),
            RecoveryTimelineCard(
                time=_t("fast")[2],
                title="새 대상에 들떠 있는 상태",
                desc="옛 데이터 인덱스 가중치가 빠르게 감소했어요.",
            ),
        ),
        recovery_lag_multiplier="0.8배",
        recovery_accel_value="새 환경 노출 + 출력 채널 다각화",
        recovery_accel_sub="에너지 회전 속도 케이스라 새 입력 다각화가 가장 빠른 회복 경로입니다.",
        recovery_optimization="옛 입력원과의 재접촉은 변동성을 평균 1.5배 증폭시켜요. 권하지 않습니다.",
    ),
    # ── 정화 (slow) ──────────────────────────────────────────
    "정화": DoyoonP2IlganData(
        scenarios=(
            HurtScenario(
                when="조용한 정성 입력 미인지 케이스",
                desc="한 사람 집중도 1.7배 케이스라 미인지 발생 시 누적 손실이 평균보다 깊어요.",
            ),
            HurtScenario(
                when="시선 분산 입력 감지 순간",
                desc="단일 대상 집중 패턴이라 시선 이동 시 위험도가 평균보다 1.8배 잡혀요.",
            ),
        ),
        vulnerability_pct="76%",
        common_pattern_pct="62%",
        hurt_optimization="미인지 케이스에는 표현 빈도를 늘리지 마시고, 인지 케이스에 집중력 재분배하세요.",
        hurt_bubble="작은 신호 한 번 알아주는 사람만 옆에 둡니다. 데이터가 그렇게 권합니다.",
        speed="slow",
        timeline_cards=(
            RecoveryTimelineCard(
                time=_t("slow")[0],
                title="외부 정상, 내부 잔불 지속",
                desc="공개 출력은 정상화되는데 야간 구간에 변동성이 가장 큽니다.",
            ),
            RecoveryTimelineCard(
                time=_t("slow")[1],
                title="표면 회복, 내면 데이터 잔존",
                desc="한 사람 집중 케이스라 인덱스 정리 시간이 평균 1.5배 길어요.",
            ),
            RecoveryTimelineCard(
                time=_t("slow")[2],
                title="새 매칭 가능 구간 진입",
                desc="옛 데이터 옆에 새 자리가 만들어진 상태입니다.",
            ),
        ),
        recovery_lag_multiplier="1.5배",
        recovery_accel_value="감정 외부화 채널 확보 (일지/대화)",
        recovery_accel_sub="내부 처리량 케이스라 외부 출력 채널이 회복 곡선의 주 변수입니다.",
        recovery_optimization="옛 데이터 잔존은 자연 현상입니다. 강제 삭제 시도 시 회복이 평균 1.6배 늦어져요.",
    ),
    # ── 무토 (medium) ────────────────────────────────────────
    "무토": DoyoonP2IlganData(
        scenarios=(
            HurtScenario(
                when="입력값 일관성 깨지는 케이스",
                desc="안정성 1.8배 케이스라 변동성 입력이 가장 큰 위험 변수로 잡혀요.",
            ),
            HurtScenario(
                when="고유 처리 속도를 무시한 가속 입력",
                desc="신중 진입 패턴이라 외부 가속 시 정지 응답이 자동 발화돼요.",
            ),
        ),
        vulnerability_pct="68%",
        common_pattern_pct="71%",
        hurt_optimization="입력 일관성 유지하는 매칭이 안정성 변수의 핵심입니다.",
        hurt_bubble="흔들리는 입력은 위험합니다. 한 자리 지켜주는 케이스만 옆에 두세요.",
        speed="medium",
        timeline_cards=(
            RecoveryTimelineCard(
                time=_t("medium")[0],
                title="방향 변수 일시 손실 상태",
                desc="안정성 케이스라 정리 진입까지 측정 시간이 필요해요.",
            ),
            RecoveryTimelineCard(
                time=_t("medium")[1],
                title="일상 루틴 자가 회복 시작",
                desc="기존 루틴에 가중치 재부여 패턴이 자동 발화돼요.",
            ),
            RecoveryTimelineCard(
                time=_t("medium")[2],
                title="안정 구간 재진입 완료",
                desc="변동성 변수가 평균 이하로 수렴한 상태입니다.",
            ),
        ),
        recovery_lag_multiplier="1.2배",
        recovery_accel_value="기존 루틴 강화 + 외부 변동 입력 차단",
        recovery_accel_sub="안정성 변수가 가장 빠른 회복 경로입니다.",
        recovery_optimization="새 매칭 시도는 안정 구간 진입 후로 권합니다. 조기 진입 시 변동성 1.4배로 증가해요.",
    ),
    # ── 기토 (medium) ────────────────────────────────────────
    "기토": DoyoonP2IlganData(
        scenarios=(
            HurtScenario(
                when="누적 헌신 입력 미인지 케이스",
                desc="수용도 1.7배 케이스라 미인지 발생 시 자기 소진 변수가 임계점에 도달해요.",
            ),
            HurtScenario(
                when="상대 성장 정체 감지",
                desc="상대 성장 지원 패턴이라 정체 입력 시 헌신 출력이 자동 차단돼요.",
            ),
        ),
        vulnerability_pct="73%",
        common_pattern_pct="67%",
        hurt_optimization="헌신 출력에 자기 우선순위 변수를 평균 0.4 비율로 같이 두세요.",
        hurt_bubble="다 주면 빈 흙이 됩니다. 자기 변수도 보존하세요.",
        speed="medium",
        timeline_cards=(
            RecoveryTimelineCard(
                time=_t("medium")[0],
                title="헌신 출력 임시 중단 상태",
                desc="수용도 케이스라 회복 진입까지 측정 시간이 필요해요.",
            ),
            RecoveryTimelineCard(
                time=_t("medium")[1],
                title="다른 대상에 헌신 변수 재배치",
                desc="가족·친구에 가중치 이동 패턴이 자동 발화돼요.",
            ),
            RecoveryTimelineCard(
                time=_t("medium")[2],
                title="새 매칭 받을 임계점",
                desc="자기 변수 보존 임계점에 도달한 상태입니다.",
            ),
        ),
        recovery_lag_multiplier="1.2배",
        recovery_accel_value="자기 우선순위 일지 + 헌신 시간 제한",
        recovery_accel_sub="자기 변수가 보존되는 매칭만 회복 곡선이 정상으로 잡혀요.",
        recovery_optimization="일방향 헌신 케이스에 재진입은 권하지 않습니다. 자기 변수가 평균 0.4배로 감소해요.",
    ),
    # ── 경금 (fast) ──────────────────────────────────────────
    "경금": DoyoonP2IlganData(
        scenarios=(
            HurtScenario(
                when="불확실 입력 케이스",
                desc="판단 명확성 1.7배 케이스라 모호한 응답 시 차단율이 평균보다 빠르게 발화돼요.",
            ),
            HurtScenario(
                when="우회 표현 감지 순간",
                desc="직설 표현 패턴이라 우회 입력 시 신뢰 변수가 평균보다 1.5배 빠르게 감소해요.",
            ),
        ),
        vulnerability_pct="69%",
        common_pattern_pct="64%",
        hurt_optimization="명확한 신호 주고받는 매칭이 신뢰 변수의 주 입력값입니다.",
        hurt_bubble="단호한 만큼 부서지기 쉽습니다. 한 번은 풀어두세요.",
        speed="fast",
        timeline_cards=(
            RecoveryTimelineCard(
                time=_t("fast")[0],
                title="즉시 결단 + 정리 진입",
                desc="결단 속도 케이스라 정리 발화도 즉시 완료돼요.",
            ),
            RecoveryTimelineCard(
                time=_t("fast")[1],
                title="다음 단계 즉시 진입",
                desc="옛 데이터에 가중치 0으로 수렴시키는 패턴이에요.",
            ),
            RecoveryTimelineCard(
                time=_t("fast")[2],
                title="재접촉 입력에도 무덤덤",
                desc="신뢰 변수가 새 대상에 이미 재배치된 상태입니다.",
            ),
        ),
        recovery_lag_multiplier="0.7배",
        recovery_accel_value="새 매칭 자가 탐색 + 명확한 기준 설정",
        recovery_accel_sub="명확성 케이스라 새 입력 기준 설정이 가장 빠른 가속법입니다.",
        recovery_optimization="끊은 매칭 재진입은 신뢰 변수를 평균 0.3배로 떨어뜨려요. 권하지 않습니다.",
    ),
    # ── 신금 (slow) ──────────────────────────────────────────
    "신금": DoyoonP2IlganData(
        scenarios=(
            HurtScenario(
                when="작은 약속 미준수 입력",
                desc="자기 보호 강도 1.7배 케이스라 신뢰 위반 시 회복 임계점이 평균보다 깊어요.",
            ),
            HurtScenario(
                when="섬세 변수를 거칠게 다루는 케이스",
                desc="정서 깊이 1.4배 케이스라 부주의 입력 시 차단율이 자동 발화돼요.",
            ),
        ),
        vulnerability_pct="75%",
        common_pattern_pct="63%",
        hurt_optimization="작은 신호 일관성이 신뢰 변수의 주 입력값입니다.",
        hurt_bubble="섬세함은 약점이 아닙니다. 함부로 다루는 케이스만 사전 차단하세요.",
        speed="slow",
        timeline_cards=(
            RecoveryTimelineCard(
                time=_t("slow")[0],
                title="외부 평소대로, 내면 변동성 폭증",
                desc="자존 변수 케이스라 외부 표현은 정상화되는데 내면 잔여가 큽니다.",
            ),
            RecoveryTimelineCard(
                time=_t("slow")[1],
                title="표면 회복, 기억 자주 재발화",
                desc="자기 보호 케이스라 인덱스 정리 시간이 평균 1.6배 길어요.",
            ),
            RecoveryTimelineCard(
                time=_t("slow")[2],
                title="기억 보존한 채 새 매칭 진입",
                desc="잔존 데이터와 새 입력을 병렬 처리할 임계점에 도달했어요.",
            ),
        ),
        recovery_lag_multiplier="1.6배",
        recovery_accel_value="감정 일지 + 신뢰 가능한 매칭 사전 검증",
        recovery_accel_sub="자기 보호 변수가 회복 곡선의 주 변수입니다.",
        recovery_optimization="옛 데이터 강제 삭제는 회복을 평균 1.7배 늦춰요. 보존한 채 새 매칭 받으세요.",
    ),
    # ── 계수 (medium) ────────────────────────────────────────
    "계수": DoyoonP2IlganData(
        scenarios=(
            HurtScenario(
                when="고유 처리 속도를 무시한 가속 입력",
                desc="섬세함 1.8배 케이스라 가속 입력 시 흩어짐 응답이 자동 발화돼요.",
            ),
            HurtScenario(
                when="잠재 신호 미인지 케이스",
                desc="명시 표현 0.5배 케이스라 미인지 발생 시 자기 가치 변수가 평균보다 빠르게 감소해요.",
            ),
        ),
        vulnerability_pct="71%",
        common_pattern_pct="65%",
        hurt_optimization="잠재 신호를 명시 표현으로 주 1회 옮기시면 인지율이 평균 35% 상승해요.",
        hurt_bubble="안개를 안개답게 봐주는 케이스만 옆에 둡니다. 데이터가 그렇게 권합니다.",
        speed="medium",
        timeline_cards=(
            RecoveryTimelineCard(
                time=_t("medium")[0],
                title="자기 가치 변수 급격 감소",
                desc="섬세 케이스라 자기 책임 변수가 일시적으로 과다 발화돼요.",
            ),
            RecoveryTimelineCard(
                time=_t("medium")[1],
                title="자기 가치 변수 회복 시작",
                desc="외부 입력 분석 통해 자기 책임 비율 재조정 패턴이 발화돼요.",
            ),
            RecoveryTimelineCard(
                time=_t("medium")[2],
                title="새 매칭 받을 자신감 회복",
                desc="자기 가치 변수가 평균 이상으로 재진입한 상태입니다.",
            ),
        ),
        recovery_lag_multiplier="1.2배",
        recovery_accel_value="자기 가치 객관 분석 + 잠재 신호 명시화 훈련",
        recovery_accel_sub="자기 가치 변수가 회복 곡선의 주 변수입니다.",
        recovery_optimization="속도 무시 케이스에 재진입은 권하지 않습니다. 흩어짐 변수가 1.5배로 증폭돼요.",
    ),
}


VALID_DOYOON_P2_ILGAN: frozenset[str] = frozenset(DOYOON_P2_DATA.keys())
