"""도윤 P-7 데이터 풀 — 四 운명의 짝 · 결말 (2/2).

원본 도윤_final.html data-page-idx=7 구조 정합.
- 4-3: 3 시나리오 카드 + AI ai_ending (1 슬롯)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScenarioCard:
    prob_label: str    # "소멸 65%"
    prob_tone: str     # "low" / "high" / "best"
    title: str         # "지금 이대로" / "{USER_NAME}님이 먼저" / "상대가 먼저"
    desc: str


@dataclass(frozen=True)
class DoyoonP7IlganData:
    """일간별 P-7 — 결말 시나리오."""
    scenarios: tuple[ScenarioCard, ScenarioCard, ScenarioCard]
    sc1_six_month_pct: str       # "22%" — 6개월 후 관계 성립
    sc2_six_month_pct: str       # "71%"
    sc3_six_month_pct: str       # "38%"
    initiative_multiplier: str   # "1.4배"
    wait_cost_multiplier: str    # "2.7배"
    expected_value_ratio: str    # "3배" — 71% vs 22%
    sd_ending_asset: str         # "dy_05"
    ending_bubble: str


def _build_scenarios() -> tuple[ScenarioCard, ScenarioCard, ScenarioCard]:
    return (
        ScenarioCard(
            prob_label="소멸 65%",
            prob_tone="low",
            title="지금 이대로",
            desc="둘 다 기다리다 흐지부지됩니다.",
        ),
        ScenarioCard(
            prob_label="좋은 결말 78%",
            prob_tone="high",
            title="{USER_NAME}님이 먼저",
            desc="작은 신호 하나로 상대가 반응할 가능성이 높습니다.",
        ),
        ScenarioCard(
            prob_label="좋은 결말 91%",
            prob_tone="best",
            title="상대가 먼저",
            desc="그 신호 놓치지 마세요.",
        ),
    )


DOYOON_P7_DATA: dict[str, DoyoonP7IlganData] = {
    "임수": DoyoonP7IlganData(
        scenarios=_build_scenarios(),
        sc1_six_month_pct="22%",
        sc2_six_month_pct="71%",
        sc3_six_month_pct="38%",
        initiative_multiplier="1.4배",
        wait_cost_multiplier="2.7배",
        expected_value_ratio="3배",
        sd_ending_asset="dy_05",
        ending_bubble="{USER_NAME}님이 먼저 움직이는 게 제일 안전한 선택이에요. 데이터가 그렇게 나왔어요.",
    ),
    "갑목": DoyoonP7IlganData(
        scenarios=_build_scenarios(),
        sc1_six_month_pct="24%", sc2_six_month_pct="68%", sc3_six_month_pct="40%",
        initiative_multiplier="1.3배", wait_cost_multiplier="2.4배",
        expected_value_ratio="2.8배", sd_ending_asset="dy_05",
        ending_bubble="결단력이 핵심 변수예요. 망설이지 마시고 한 번 보내세요.",
    ),
    "을목": DoyoonP7IlganData(
        scenarios=_build_scenarios(),
        sc1_six_month_pct="26%", sc2_six_month_pct="66%", sc3_six_month_pct="42%",
        initiative_multiplier="1.4배", wait_cost_multiplier="2.5배",
        expected_value_ratio="2.5배", sd_ending_asset="dy_05",
        ending_bubble="유연성이 강점이에요. 작은 신호 한 번이면 흐름 바뀝니다.",
    ),
    "병화": DoyoonP7IlganData(
        scenarios=_build_scenarios(),
        sc1_six_month_pct="20%", sc2_six_month_pct="73%", sc3_six_month_pct="35%",
        initiative_multiplier="1.2배", wait_cost_multiplier="3.0배",
        expected_value_ratio="3.6배", sd_ending_asset="dy_05",
        ending_bubble="발산형 매력 케이스라 먼저 움직일 때 효율이 가장 높아요.",
    ),
    "정화": DoyoonP7IlganData(
        scenarios=_build_scenarios(),
        sc1_six_month_pct="25%", sc2_six_month_pct="74%", sc3_six_month_pct="40%",
        initiative_multiplier="1.5배", wait_cost_multiplier="2.8배",
        expected_value_ratio="3배", sd_ending_asset="dy_05",
        ending_bubble="잔잔한 표현이 무기예요. 한 번이면 충분합니다.",
    ),
    "무토": DoyoonP7IlganData(
        scenarios=_build_scenarios(),
        sc1_six_month_pct="23%", sc2_six_month_pct="69%", sc3_six_month_pct="42%",
        initiative_multiplier="1.4배", wait_cost_multiplier="2.6배",
        expected_value_ratio="3배", sd_ending_asset="dy_05",
        ending_bubble="안정 케이스라 신호 보내면 받는 쪽이 안정감을 느껴요.",
    ),
    "기토": DoyoonP7IlganData(
        scenarios=_build_scenarios(),
        sc1_six_month_pct="22%", sc2_six_month_pct="70%", sc3_six_month_pct="40%",
        initiative_multiplier="1.4배", wait_cost_multiplier="2.7배",
        expected_value_ratio="3.2배", sd_ending_asset="dy_05",
        ending_bubble="배려가 강점이에요. 그 배려를 신호로 바꿔 보내세요.",
    ),
    "경금": DoyoonP7IlganData(
        scenarios=_build_scenarios(),
        sc1_six_month_pct="25%", sc2_six_month_pct="68%", sc3_six_month_pct="38%",
        initiative_multiplier="1.3배", wait_cost_multiplier="2.5배",
        expected_value_ratio="2.7배", sd_ending_asset="dy_05",
        ending_bubble="명확함이 강점입니다. 직접적으로 전달하시면 됩니다.",
    ),
    "신금": DoyoonP7IlganData(
        scenarios=_build_scenarios(),
        sc1_six_month_pct="20%", sc2_six_month_pct="72%", sc3_six_month_pct="36%",
        initiative_multiplier="1.5배", wait_cost_multiplier="2.9배",
        expected_value_ratio="3.6배", sd_ending_asset="dy_05",
        ending_bubble="섬세한 표현이 강점이에요. 그 디테일 그대로 보내세요.",
    ),
    "계수": DoyoonP7IlganData(
        scenarios=_build_scenarios(),
        sc1_six_month_pct="18%", sc2_six_month_pct="74%", sc3_six_month_pct="34%",
        initiative_multiplier="1.5배", wait_cost_multiplier="3.0배",
        expected_value_ratio="4배", sd_ending_asset="dy_05",
        ending_bubble="잠재력이 큰 케이스예요. 한 신호로 모든 게 움직입니다.",
    ),
}


VALID_DOYOON_P7_ILGAN: frozenset[str] = frozenset(DOYOON_P7_DATA.keys())
