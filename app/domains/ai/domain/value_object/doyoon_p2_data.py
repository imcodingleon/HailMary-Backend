"""도윤 P-2 일간 10셀 데이터 풀 — 원본 도윤_final.html 구조 정합.

⚠️ 2026-05-21 재설계: yeonwoo 답습 폐기, 원본 도윤 HTML 구조 (P-2 data-page-idx=2)
정확히 매핑. 임수 셀은 원본 더미 그대로, 나머지 9 셀은 같은 구조 + 도윤 톤.

원본 구조:
- 1-4 약점: card-warn × 2 (짧은 keyword + risk_pct + 한 줄 desc)
- 1-5 회복: meter × 4 (직후/1개월/3개월/6개월 + 진행률 %)
- SD 아바타 + 한도윤 buble row
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HurtType:
    """약점 카드 — 원본 .card-warn 매핑."""
    keyword: str          # 짧은 핵심 키워드 (예: "무관심 신호 인지")
    risk_pct: str         # "78%"
    desc: str             # 한 줄 데이터 설명


@dataclass(frozen=True)
class RecoveryMeter:
    """회복 진행바 — 원본 .meter 매핑."""
    label: str            # "직후" / "1개월" / "3개월" / "6개월" (고정)
    pct: int              # 0~100 회복률


@dataclass(frozen=True)
class DoyoonP2IlganData:
    # 1-4 약점 트리거 (card-warn × 2)
    hurt_type_1: HurtType
    hurt_type_2: HurtType
    intervention_drop_pct: str    # "41%" — AI 박스 내 처방 효과 수치
    # 1-5 회복 곡선 (meter × 4 + SD + bubble)
    meters: tuple[RecoveryMeter, RecoveryMeter, RecoveryMeter, RecoveryMeter]
    recovery_lag_multiplier: str  # "1.4배" — 평균 대비 회복 지연
    sd_avatar_asset: str          # "dy_03" 등 (SD 슬롯 자산 키)
    recovery_bubble: str          # 한도윤 SD 옆 버블 멘트


# 시간 라벨 (원본 고정 4단계)
RECOVERY_LABELS: tuple[str, str, str, str] = ("직후", "1개월", "3개월", "6개월")


def _m(p0: int, p1: int, p2: int, p3: int) -> tuple[RecoveryMeter, RecoveryMeter, RecoveryMeter, RecoveryMeter]:
    return (
        RecoveryMeter(label=RECOVERY_LABELS[0], pct=p0),
        RecoveryMeter(label=RECOVERY_LABELS[1], pct=p1),
        RecoveryMeter(label=RECOVERY_LABELS[2], pct=p2),
        RecoveryMeter(label=RECOVERY_LABELS[3], pct=p3),
    )


DOYOON_P2_DATA: dict[str, DoyoonP2IlganData] = {
    # ── 임수 (원본 더미 그대로) ────────────────────────────────
    "임수": DoyoonP2IlganData(
        hurt_type_1=HurtType(
            keyword="무관심 신호 인지",
            risk_pct="78%",
            desc="동일 일간 표본 78%가 이 신호에서 가장 큰 감정 손실을 보고했습니다.",
        ),
        hurt_type_2=HurtType(
            keyword="의도 미독해",
            risk_pct="64%",
            desc="표현하지 않은 마음을 알아주길 기대하는 경향, 평균 대비 1.4배입니다.",
        ),
        intervention_drop_pct="41%",
        meters=_m(20, 40, 65, 90),
        recovery_lag_multiplier="1.4배",
        sd_avatar_asset="dy_03",
        recovery_bubble="3개월 지나고 한 달만 더 쉬세요. 그게 다음 사람한테 공평한 거예요.",
    ),
    # ── 갑목 ─────────────────────────────────────────────────
    "갑목": DoyoonP2IlganData(
        hurt_type_1=HurtType(
            keyword="결정 간섭 입력",
            risk_pct="72%",
            desc="독립 결정 패턴 표본 72%가 외부 간섭 입력에 가장 큰 손실을 보고합니다.",
        ),
        hurt_type_2=HurtType(
            keyword="성과 평가절하",
            risk_pct="68%",
            desc="자력 성취 가치 폄하 입력 시 회복 시간이 평균 1.5배로 측정됩니다.",
        ),
        intervention_drop_pct="38%",
        meters=_m(35, 60, 80, 95),
        recovery_lag_multiplier="0.7배",
        sd_avatar_asset="dy_03",
        recovery_bubble="끊은 결정을 의심하지 마세요. 그게 가장 빠른 회복 경로예요.",
    ),
    # ── 을목 ─────────────────────────────────────────────────
    "을목": DoyoonP2IlganData(
        hurt_type_1=HurtType(
            keyword="정성 미인지",
            risk_pct="74%",
            desc="작은 헌신 누적 케이스에서 미인지 발생률이 평균 1.5배 높게 잡힙니다.",
        ),
        hurt_type_2=HurtType(
            keyword="혼자 남겨짐",
            risk_pct="66%",
            desc="환경 의존도 1.3배 케이스라 단기 부재도 큰 변동성으로 해석됩니다.",
        ),
        intervention_drop_pct="35%",
        meters=_m(25, 50, 72, 90),
        recovery_lag_multiplier="1.1배",
        sd_avatar_asset="dy_03",
        recovery_bubble="혼자 있는 시간 길게 두지 마세요. 데이터가 흩어집니다.",
    ),
    # ── 병화 ─────────────────────────────────────────────────
    "병화": DoyoonP2IlganData(
        hurt_type_1=HurtType(
            keyword="저텐션 응답",
            risk_pct="70%",
            desc="표현 빈도 1.9배 케이스에서 응답 격차가 거절 신호로 해석되는 빈도가 높습니다.",
        ),
        hurt_type_2=HurtType(
            keyword="입출력 불균형",
            risk_pct="65%",
            desc="100 출력 대비 50 미만 입력 케이스가 위험 변수로 자동 분류됩니다.",
        ),
        intervention_drop_pct="36%",
        meters=_m(40, 65, 85, 95),
        recovery_lag_multiplier="0.8배",
        sd_avatar_asset="dy_03",
        recovery_bubble="새 환경 빨리 노출하세요. 그게 데이터상 가장 빠른 회복입니다.",
    ),
    # ── 정화 ─────────────────────────────────────────────────
    "정화": DoyoonP2IlganData(
        hurt_type_1=HurtType(
            keyword="조용한 정성 미인지",
            risk_pct="76%",
            desc="한 사람 집중도 1.7배 케이스에서 미인지 시 누적 손실이 평균보다 깊게 측정됩니다.",
        ),
        hurt_type_2=HurtType(
            keyword="시선 분산 감지",
            risk_pct="62%",
            desc="단일 집중 패턴이라 시선 이동 시 위험도가 평균 1.8배로 잡힙니다.",
        ),
        intervention_drop_pct="43%",
        meters=_m(18, 35, 55, 85),
        recovery_lag_multiplier="1.5배",
        sd_avatar_asset="dy_03",
        recovery_bubble="외부 채널 하나만 열어두세요. 일지든 대화든 출구가 필요해요.",
    ),
    # ── 무토 ─────────────────────────────────────────────────
    "무토": DoyoonP2IlganData(
        hurt_type_1=HurtType(
            keyword="일관성 결손",
            risk_pct="68%",
            desc="안정성 1.8배 케이스에서 변동성 입력이 가장 큰 위험 변수로 측정됩니다.",
        ),
        hurt_type_2=HurtType(
            keyword="강제 가속 입력",
            risk_pct="71%",
            desc="신중 진입 패턴이라 외부 가속 시 정지 응답이 자동 발화됩니다.",
        ),
        intervention_drop_pct="33%",
        meters=_m(22, 45, 68, 88),
        recovery_lag_multiplier="1.2배",
        sd_avatar_asset="dy_03",
        recovery_bubble="기존 루틴이 최고의 회복 도구입니다. 새 변수 도입은 나중에.",
    ),
    # ── 기토 ─────────────────────────────────────────────────
    "기토": DoyoonP2IlganData(
        hurt_type_1=HurtType(
            keyword="누적 헌신 미인지",
            risk_pct="73%",
            desc="수용도 1.7배 케이스에서 미인지 시 자기 소진 변수가 임계점에 도달합니다.",
        ),
        hurt_type_2=HurtType(
            keyword="상대 성장 정체",
            risk_pct="67%",
            desc="상대 성장 지원 패턴이라 정체 입력 시 헌신 출력이 자동 차단됩니다.",
        ),
        intervention_drop_pct="37%",
        meters=_m(25, 48, 70, 88),
        recovery_lag_multiplier="1.2배",
        sd_avatar_asset="dy_03",
        recovery_bubble="자기 우선순위 변수 한 줄만 매일 적어보세요. 회복이 정상화됩니다.",
    ),
    # ── 경금 ─────────────────────────────────────────────────
    "경금": DoyoonP2IlganData(
        hurt_type_1=HurtType(
            keyword="불확실 입력",
            risk_pct="69%",
            desc="판단 명확성 1.7배 케이스에서 모호한 응답 시 차단율이 평균보다 빠릅니다.",
        ),
        hurt_type_2=HurtType(
            keyword="우회 표현",
            risk_pct="64%",
            desc="직설 표현 패턴이라 우회 입력 시 신뢰 변수가 평균 1.5배 빠르게 감소합니다.",
        ),
        intervention_drop_pct="40%",
        meters=_m(38, 62, 82, 95),
        recovery_lag_multiplier="0.7배",
        sd_avatar_asset="dy_03",
        recovery_bubble="다음 기준만 명확히 잡으면 됩니다. 옛 데이터에 가중치 주지 마세요.",
    ),
    # ── 신금 ─────────────────────────────────────────────────
    "신금": DoyoonP2IlganData(
        hurt_type_1=HurtType(
            keyword="작은 약속 미준수",
            risk_pct="75%",
            desc="자기 보호 강도 1.7배 케이스에서 신뢰 위반 시 회복 임계점이 평균보다 깊습니다.",
        ),
        hurt_type_2=HurtType(
            keyword="섬세 변수 부주의 처리",
            risk_pct="63%",
            desc="정서 깊이 1.4배 케이스라 부주의 입력 시 차단율이 자동 발화됩니다.",
        ),
        intervention_drop_pct="39%",
        meters=_m(17, 33, 53, 82),
        recovery_lag_multiplier="1.6배",
        sd_avatar_asset="dy_03",
        recovery_bubble="옛 데이터 보존한 채로 새 매칭 받아도 됩니다. 강제 삭제는 권하지 않습니다.",
    ),
    # ── 계수 ─────────────────────────────────────────────────
    "계수": DoyoonP2IlganData(
        hurt_type_1=HurtType(
            keyword="가속 입력",
            risk_pct="71%",
            desc="섬세함 1.8배 케이스라 가속 입력 시 흩어짐 응답이 자동 발화됩니다.",
        ),
        hurt_type_2=HurtType(
            keyword="잠재 신호 미인지",
            risk_pct="65%",
            desc="명시 표현 0.5배 케이스에서 미인지 시 자기 가치 변수가 평균보다 빠르게 감소합니다.",
        ),
        intervention_drop_pct="35%",
        meters=_m(24, 47, 68, 88),
        recovery_lag_multiplier="1.2배",
        sd_avatar_asset="dy_03",
        recovery_bubble="잠재 신호를 명시로 옮기는 훈련 한 가지. 그게 회복 속도를 결정합니다.",
    ),
}


VALID_DOYOON_P2_ILGAN: frozenset[str] = frozenset(DOYOON_P2_DATA.keys())
