"""도윤 P-9 데이터 풀 — 六 연애 변수 최적화 가이드.

원본 도윤_final.html data-page-idx=9 구조 정합.
- 6-1: 오행 보완 방법 × 3 (색채/공간/행동) — 오행 5종 매트릭스
- 6-2: 리스크 카드 × 3 (즉시/단기/중기) — 일간 무관 공통
- 6-3: 매력 최적화 — 일간별 (현재/목표 + 부스트)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OhangMethodCard:
    label: str        # "보완 방법 1 · 효과 +9%"
    keyword: str      # "색채 노출 — 초록 계열"
    desc: str


@dataclass(frozen=True)
class RiskCard:
    label: str        # "즉시 · 위험도 81%"
    tone: str         # "warn" / "warn" / "amber"
    keyword: str      # "미정리 관계 변수"
    desc: str


@dataclass(frozen=True)
class DoyoonP9IlganData:
    """일간별 P-9 — 매력 최적화."""
    current_score: int       # 85
    target_score: int        # 92
    gap_per_action: str      # "1.3%"
    overall_boost_pct: str   # "21%"
    optimize_bubble: str
    sd_optimize_asset: str   # "dy_06"


# ── 6-1 오행 보완 매트릭스 (5 오행) ───────────────────────────────


_OHANG_METHODS_TEMPLATE = {
    "목": (
        OhangMethodCard(label="보완 방법 1 · 효과 +9%",
                        keyword="색채 노출 — 초록 계열",
                        desc="{ohang_lack} 기운을 시각 변수로 보완. 일상 노출량을 늘리는 것이 핵심."),
        OhangMethodCard(label="보완 방법 2 · 효과 +7%",
                        keyword="공간 변수 — 동쪽 배치",
                        desc="동쪽이 {ohang_lack}의 위치 변수. 책상·침대 머리 방향 조정."),
        OhangMethodCard(label="보완 방법 3 · 효과 +7%",
                        keyword="행동 변수 — 아침 산책 30분",
                        desc="생체 리듬 보완. 식물·자연광 노출이 효과 가속화."),
    ),
    "화": (
        OhangMethodCard(label="보완 방법 1 · 효과 +9%",
                        keyword="색채 노출 — 붉은 계열",
                        desc="{ohang_lack} 기운을 시각 변수로 보완. 액세서리·소품 활용."),
        OhangMethodCard(label="보완 방법 2 · 효과 +7%",
                        keyword="공간 변수 — 남쪽 배치",
                        desc="남쪽이 {ohang_lack}의 위치 변수. 조명·창문 방향 활용."),
        OhangMethodCard(label="보완 방법 3 · 효과 +7%",
                        keyword="행동 변수 — 햇볕 산책 20분",
                        desc="햇빛 노출이 {ohang_lack} 활성도 가속화 변수."),
    ),
    "토": (
        OhangMethodCard(label="보완 방법 1 · 효과 +9%",
                        keyword="색채 노출 — 황토·베이지",
                        desc="{ohang_lack} 기운을 시각 변수로 보완. 인테리어·옷차림 활용."),
        OhangMethodCard(label="보완 방법 2 · 효과 +7%",
                        keyword="공간 변수 — 중앙 배치",
                        desc="중심부가 {ohang_lack}의 위치 변수. 공간 정돈이 가속화."),
        OhangMethodCard(label="보완 방법 3 · 효과 +7%",
                        keyword="행동 변수 — 흙·도예 접촉",
                        desc="감각 변수 보완. 화분·정원 접촉이 효과 가속화."),
    ),
    "금": (
        OhangMethodCard(label="보완 방법 1 · 효과 +9%",
                        keyword="색채 노출 — 흰색·은색",
                        desc="{ohang_lack} 기운을 시각 변수로 보완. 메탈 액세서리 활용."),
        OhangMethodCard(label="보완 방법 2 · 효과 +7%",
                        keyword="공간 변수 — 서쪽 배치",
                        desc="서쪽이 {ohang_lack}의 위치 변수. 일출·일몰 활용."),
        OhangMethodCard(label="보완 방법 3 · 효과 +7%",
                        keyword="행동 변수 — 정리·운동 루틴",
                        desc="규칙성 변수 보완. 명확한 시간표가 효과 가속화."),
    ),
    "수": (
        OhangMethodCard(label="보완 방법 1 · 효과 +9%",
                        keyword="색채 노출 — 검정·짙은 청색",
                        desc="{ohang_lack} 기운을 시각 변수로 보완. 옷차림 비율 늘리기."),
        OhangMethodCard(label="보완 방법 2 · 효과 +7%",
                        keyword="공간 변수 — 북쪽 배치",
                        desc="북쪽이 {ohang_lack}의 위치 변수. 수공간 가시화 효과적."),
        OhangMethodCard(label="보완 방법 3 · 효과 +7%",
                        keyword="행동 변수 — 수영·반신욕",
                        desc="물 접촉 변수 보완. 주 2회 이상이 효과 가속화 임계점."),
    ),
}


def get_ohang_methods(ohang_lack: str) -> tuple[OhangMethodCard, OhangMethodCard, OhangMethodCard]:
    """ohang_lack ('목'/'화'/'토'/'금'/'수') → 보완 방법 카드 3개 (desc에 ohang_lack 치환)."""
    tmpl = _OHANG_METHODS_TEMPLATE.get(ohang_lack) or _OHANG_METHODS_TEMPLATE["목"]
    return tuple(  # type: ignore[return-value]
        OhangMethodCard(
            label=c.label,
            keyword=c.keyword,
            desc=c.desc.replace("{ohang_lack}", ohang_lack),
        )
        for c in tmpl
    )


# ── 6-2 리스크 카드 × 3 (일간 무관 공통) ──────────────────────────


RISK_CARDS: tuple[RiskCard, RiskCard, RiskCard] = (
    RiskCard(
        label="즉시 · 위험도 81%",
        tone="warn",
        keyword="미정리 관계 변수",
        desc="새 인연 진입 차단의 가장 큰 변수. 24시간 내 정리 권장.",
    ),
    RiskCard(
        label="단기 · 위험도 64%",
        tone="warn",
        keyword="충동 표현 빈도",
        desc="감정 폭발 빈도가 평균 대비 2.1배. 24시간 룰 적용 권장.",
    ),
    RiskCard(
        label="중기 · 위험도 47%",
        tone="amber",
        keyword="동선 단조로움",
        desc="접촉 노출 변수가 좁음. 월 1회 새 환경 진입이 효율적.",
    ),
)

# 리스크 사실값 (공통)
IMMEDIATE_IMPACT_PCT: str = "36%"
COMBINED_EFFECT_MULTIPLIER: str = "1.4배"
COMBINED_EFFECT_VALUE: str = "130"  # 81+64+47 = 192 → 1.4 수렴 ≈ 130


# ── 6-3 매력 최적화 (일간 10셀) ───────────────────────────────────


DOYOON_P9_DATA: dict[str, DoyoonP9IlganData] = {
    "갑목": DoyoonP9IlganData(
        current_score=83, target_score=90, gap_per_action="1.2%", overall_boost_pct="19%",
        optimize_bubble="분석은 다 끝났어요. 이제 {USER_NAME}님 결정만 남았어요.",
        sd_optimize_asset="dy_06",
    ),
    "을목": DoyoonP9IlganData(
        current_score=82, target_score=89, gap_per_action="1.2%", overall_boost_pct="20%",
        optimize_bubble="가벼운 신호 하나로 흐름이 움직여요. {USER_NAME}님이 먼저예요.",
        sd_optimize_asset="dy_06",
    ),
    "병화": DoyoonP9IlganData(
        current_score=86, target_score=93, gap_per_action="1.4%", overall_boost_pct="22%",
        optimize_bubble="발산 매력이 강점이에요. {USER_NAME}님이 한 번 빨리 표현하시면 됩니다.",
        sd_optimize_asset="dy_06",
    ),
    "정화": DoyoonP9IlganData(
        current_score=84, target_score=91, gap_per_action="1.3%", overall_boost_pct="21%",
        optimize_bubble="깊은 표현 한 번이 결정 변수예요. {USER_NAME}님 차례입니다.",
        sd_optimize_asset="dy_06",
    ),
    "무토": DoyoonP9IlganData(
        current_score=85, target_score=91, gap_per_action="1.2%", overall_boost_pct="19%",
        optimize_bubble="안정 케이스라 작은 변화도 누적 효과 커요. {USER_NAME}님이 시작이에요.",
        sd_optimize_asset="dy_06",
    ),
    "기토": DoyoonP9IlganData(
        current_score=83, target_score=90, gap_per_action="1.2%", overall_boost_pct="20%",
        optimize_bubble="배려가 강점이에요. {USER_NAME}님의 작은 신호가 결정적입니다.",
        sd_optimize_asset="dy_06",
    ),
    "경금": DoyoonP9IlganData(
        current_score=86, target_score=92, gap_per_action="1.3%", overall_boost_pct="20%",
        optimize_bubble="명확성이 무기예요. {USER_NAME}님이 직접적으로 전달하시면 됩니다.",
        sd_optimize_asset="dy_06",
    ),
    "신금": DoyoonP9IlganData(
        current_score=84, target_score=91, gap_per_action="1.3%", overall_boost_pct="21%",
        optimize_bubble="섬세한 신호가 결정 변수예요. {USER_NAME}님 차례입니다.",
        sd_optimize_asset="dy_06",
    ),
    "임수": DoyoonP9IlganData(
        current_score=85, target_score=92, gap_per_action="1.3%", overall_boost_pct="21%",
        optimize_bubble="분석은 다 끝났어요. 이제 공은 {USER_NAME}님한테 있어요.",
        sd_optimize_asset="dy_06",
    ),
    "계수": DoyoonP9IlganData(
        current_score=83, target_score=91, gap_per_action="1.4%", overall_boost_pct="23%",
        optimize_bubble="잠재 매력이 가장 큰 케이스예요. {USER_NAME}님이 시작만 하시면 돼요.",
        sd_optimize_asset="dy_06",
    ),
}


VALID_DOYOON_P9_ILGAN: frozenset[str] = frozenset(DOYOON_P9_DATA.keys())


# 6-1 공통 사실값
OHANG_BOOST_PCT: str = "23%"
OHANG_RESPONSE_MULTIPLIER: str = "1.6배"
OHANG_MAX_BOOST_PCT: str = "28%"
