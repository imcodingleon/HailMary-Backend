"""도윤 P-8 五 인연이 오는 시간 — 룰 합성 + facts.

원본 도윤_final.html data-page-idx=8 구조 정합.
연우 P-8 헬퍼 재사용 (_pct_to_hearts_p8 / _pick_top_two_peaks /
_classify_state / _format_month_label / _peak_label_for_ai).
도윤 톤 텍스트만 신규.
"""

from __future__ import annotations

from typing import Any

from app.domains.ai.domain.templates.doyoon_p0_intro import ILGAN_HANJA
from app.domains.ai.domain.templates.yeonwoo_p8_timing import (
    VALID_ILGAN,
    _classify_state,
    _format_month_label,
    _peak_label_for_ai,
    _pct_to_hearts_p8,
    _pick_top_two_peaks,
)

# ── 도윤 톤 텍스트 ────────────────────────────────────────────


PARA_1_FIXED_DOYOON = (
    "향후 12개월 접촉 확률 분포 정리해드릴게요. 이번 달부터 1년이에요."
)

PARA_2_TEMPLATE_DOYOON = (
    "연간 평균 대비 피크 구간이 두 곳이에요. {peak_1}과 {peak_2}. "
    "이 두 달은 신규 인연 접촉 확률이 평균 대비 2.3배까지 올라가요. "
    "그 사이 구간은 변수 정리·매력 변수 보완에 효율적인 충전 구간이에요."
)

BUBBLE_DOYOON = "이 시기에 접촉 확률이 가장 높게 잡혀요."

# 일간별 흐름 결 (3단락 마지막 단락)
ILGAN_FLOW_BY_ILGAN_DOYOON: dict[str, str] = {
    "갑목": (
        "{ilgan_with_hanja} 일간 표본에서 직진형 움직임의 ROI가 가장 높게 측정돼요. "
        "피크에 한 방향으로 가시는 게 효율적이에요."
    ),
    "을목": (
        "{ilgan_with_hanja} 일간 표본에서 환경 적응형 움직임의 ROI가 가장 높아요. "
        "피크에 흐름 맞춰 휘되, 한 번 잡힌 신호 끝까지 가시는 게 효율적이에요."
    ),
    "병화": (
        "{ilgan_with_hanja} 일간 표본에서 빠른 표현의 ROI가 가장 높게 잡혀요. "
        "피크에 즉시 신호 전달하시는 게 효율적이에요."
    ),
    "정화": (
        "{ilgan_with_hanja} 일간 표본에서 단일 집중의 ROI가 가장 높아요. "
        "피크에 한 사람만 조용히 깊게 다가가시는 게 효율적이에요."
    ),
    "무토": (
        "{ilgan_with_hanja} 일간 표본에서 흐름 거스르는 행동의 ROI가 가장 낮게 측정돼요. "
        "피크에 한 걸음씩 다가가시는 게 효율적이에요. 데이터가 그렇게 가리키고 있어요."
    ),
    "기토": (
        "{ilgan_with_hanja} 일간 표본에서 다정한 신호의 ROI가 가장 높아요. "
        "피크에 작은 배려 한 번이 결정 변수예요."
    ),
    "경금": (
        "{ilgan_with_hanja} 일간 표본에서 명확성 기반 움직임의 ROI가 가장 높게 잡혀요. "
        "피크에 직접적으로 의도 전달하시는 게 효율적이에요."
    ),
    "신금": (
        "{ilgan_with_hanja} 일간 표본에서 디테일 신호의 ROI가 가장 높아요. "
        "피크에 섬세한 표현 한 번이 결정적이에요."
    ),
    "임수": (
        "{ilgan_with_hanja} 일간 표본에서 흐름 거스르는 행동의 ROI가 가장 낮게 측정돼요. "
        "피크에 적극 움직이고, 정체기엔 변수 정리에 집중하시는 게 가장 효율적이에요. "
        "데이터가 그렇게 가리키고 있어요."
    ),
    "계수": (
        "{ilgan_with_hanja} 일간 표본에서 잠재 신호 활용의 ROI가 가장 높게 측정돼요. "
        "피크에 미세 끌림을 명확한 신호로 전환하시는 게 효율적이에요."
    ),
}

# 월별 코멘트 풀 (state 기반 매핑 — 연우와 동일 키 사용, 도윤 톤으로 재작성)
STATE_DESC_BY_STATE_DOYOON: dict[str, str] = {
    "시작": "이번 달부터 흐름 진입 구간이에요. 큰 변동은 없지만 변수가 움직이기 시작해요.",
    "상승": "신규 접촉 확률 상승. 반복 접촉이 인연으로 발전하는 사례가 많아요.",
    "진입": "접촉 확률이 빠르게 차오르는 구간이에요. 신호 인지율 높이세요.",
    "피크": "피크 구간. 적극적 감정 표현 효율이 평균 대비 2.3배예요.",
    "심화": "관계 심화 국면. 상대 페이스 존중이 효율적이에요.",
    "안정": "안정 전환. 현 상태 유지 전략이 가장 효과적이에요.",
    "정체": "변수 최소화 구간. 조급한 밀어붙임은 역효과예요.",
    "충전": "신규 환경 진입 권장. 동선 변화로 접촉 변수 재가동돼요.",
    "2차 피크": "연도 전환과 함께 2차 피크. 표현 명확성이 결정적 변수예요.",
    "1년차 마무리": "1년 사이클 마무리. 명확한 표현이 다음 흐름 변수를 결정해요.",
}


def _ilgan_with_hanja_doyoon(ilgan: str) -> str:
    return f"{ilgan}({ILGAN_HANJA[ilgan]})"


def compose_doyoon_p8_timing(
    *,
    user_name: str,
    ilgan: str,
    raw_months: list[dict[str, Any]],
    start_year: int,
    start_month: int,
) -> dict[str, object]:
    """도윤 P-8 5-1 12개월 합성. 연우 P-8과 동일 데이터 + 도윤 텍스트."""
    if not user_name:
        raise ValueError("doyoon P-8 requires non-empty user_name")
    if ilgan not in VALID_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")
    if len(raw_months) != 12:
        raise ValueError(f"raw_months 길이 12 필요. got {len(raw_months)}")

    peak_1_idx, peak_2_idx = _pick_top_two_peaks(raw_months)

    months_out: list[dict[str, object]] = []
    for i, m in enumerate(raw_months):
        pct = int(m["romanceScore"])
        is_first = i == peak_1_idx
        is_second = i == peak_2_idx
        is_peak = is_first or is_second
        hearts = 5 if is_peak else _pct_to_hearts_p8(pct)
        state = _classify_state(i, hearts, is_first, peak_2_idx, peak_1_idx)
        desc = STATE_DESC_BY_STATE_DOYOON.get(state, STATE_DESC_BY_STATE_DOYOON["상승"])
        label = _format_month_label(i, start_year, start_month)
        months_out.append({
            "label": label,
            "hearts": hearts,
            "pct": pct,
            "state": state,
            "desc": desc,
            "is_peak": is_peak,
        })

    peak_1_label = _peak_label_for_ai(peak_1_idx, start_year, start_month)
    peak_2_label = _peak_label_for_ai(peak_2_idx, start_year, start_month)

    ai_intro = "\n\n".join([
        PARA_1_FIXED_DOYOON,
        PARA_2_TEMPLATE_DOYOON.format(peak_1=peak_1_label, peak_2=peak_2_label),
        ILGAN_FLOW_BY_ILGAN_DOYOON[ilgan].format(
            ilgan_with_hanja=_ilgan_with_hanja_doyoon(ilgan)
        ),
    ])

    return {
        "months": months_out,
        "ai_intro": ai_intro,
        "bubble": BUBBLE_DOYOON,
        "peak_1_label": peak_1_label,
        "peak_2_label": peak_2_label,
    }


def get_doyoon_p8_facts(
    *,
    user_name: str,
    ilgan: str,
    raw_months: list[dict[str, Any]],
    start_year: int,
    start_month: int,
) -> dict[str, str]:
    """AI prompt용 facts."""
    composed = compose_doyoon_p8_timing(
        user_name=user_name, ilgan=ilgan,
        raw_months=raw_months,
        start_year=start_year, start_month=start_month,
    )
    return {
        "user_name": user_name,
        "ilgan_full": ilgan,
        "ilgan_hanja": ILGAN_HANJA[ilgan],
        "peak_1_label": str(composed["peak_1_label"]),
        "peak_2_label": str(composed["peak_2_label"]),
        "rule_text": str(composed["ai_intro"]),
    }
