"""P-8 5-1 12개월 운명선 — 일간 변형 + 월별 state/desc 합성.

설계:
- AI 박스 3단락: 고정 도입 + 피크 월 2개 삽입 + 일간별 흐름 결.
- 12 row: backend MonthlyRomanceFlowService.compute_full_months() 반환을 받아
  hearts/knot/state/desc 분류 + label 포맷.
- 피크 월 2개: 12개월 score 상위 2개 idx 추출, idx 순으로 "피크" / "2차 피크".
- 결제 월 고정: caller가 start_year/start_month를 명시하면 그 시점부터 12개월.

P-4 compose_p4_blocking2의 단락 join 패턴 차용. AI 호출 0.
"""

from typing import Any

# ═════════════════════════════════════════════════════════════════
# 고정 — AI 박스 도입/마무리 + 강연우 멘트
# ═════════════════════════════════════════════════════════════════

PARA_1_FIXED = (
    "한 해의 흐름이 보여. 일 년 내내 같은 결이 아니야. "
    "강하게 당겨지는 달이 있고, 비워야 하는 달이 있어."
)

PARA_2_TEMPLATE = (
    "이번 달부터 1년을 봐. 너의 명줄에서 실이 가장 강하게 당겨지는 건 "
    "{peak_1}과 {peak_2}이야. 그 두 달은 가만히 있어도 사람이 들어와. "
    "그 사이는 충전 구간이야. 조급해하지 마. 비우는 시간이 곧 채우는 시간이야."
)

BUBBLE = "이 시기에 붉은 실이 가장 강하게 당겨."


# ═════════════════════════════════════════════════════════════════
# 일간별 흐름 결 (AI 박스 3단락)
# ═════════════════════════════════════════════════════════════════
# `{ilgan_with_hanja}` placeholder 치환

ILGAN_FLOW_BY_ILGAN: dict[str, str] = {
    "갑목": (
        "{ilgan_with_hanja} 일간은 곧게 가는 결이야. "
        "흐름이 막혀도 직진해. 피크에 한 방향으로 가는 게 너에게 가장 잘 맞아."
    ),
    "을목": (
        "{ilgan_with_hanja} 일간은 휘어 살아남는 결이야. "
        "흐름에 맞춰 휘되, 한 번 감기면 끝까지. 그게 너에게 가장 잘 맞아."
    ),
    "병화": (
        "{ilgan_with_hanja} 일간은 빛으로 사람을 끄는 결이야. "
        "피크에 빨리 표현해. 식기 전에 닿는 게 너에게 가장 잘 맞아."
    ),
    "정화": (
        "{ilgan_with_hanja} 일간은 한 사람만 비추는 결이야. "
        "작게 오래 비추는 게 너에게 맞아. 피크엔 조용히 깊게 다가가."
    ),
    "무토": (
        "{ilgan_with_hanja} 일간은 묵직하게 받쳐주는 결이야. "
        "흔들리지 말고 자리에 있어. 피크엔 한 걸음 다가가는 게 너에게 잘 맞아."
    ),
    "기토": (
        "{ilgan_with_hanja} 일간은 다정하게 키워주는 결이야. "
        "피크엔 곁을 내주는 표현이 너에게 가장 잘 맞아."
    ),
    "경금": (
        "{ilgan_with_hanja} 일간은 결단력 있는 결이야. "
        "피크엔 분명하게 한마디 던져. 단호함이 너에게 가장 잘 맞아."
    ),
    "신금": (
        "{ilgan_with_hanja} 일간은 다듬어진 결이야. "
        "피크에도 결을 흩지 마. 정갈한 한마디가 너에게 가장 잘 맞아."
    ),
    "임수": (
        "{ilgan_with_hanja} 일간은 흐름을 거스르면 안 되는 결이야. "
        "피크에 움직이고, 정체기엔 멈춰. 그게 너에게 가장 잘 맞아."
    ),
    "계수": (
        "{ilgan_with_hanja} 일간은 분위기로 사랑하는 결이야. "
        "흐름 따라 스며들어. 피크엔 분위기로 신호를 주는 게 너에게 잘 맞아."
    ),
}


# ═════════════════════════════════════════════════════════════════
# state 12종 → desc 템플릿 (row별 멘트)
# ═════════════════════════════════════════════════════════════════

STATE_DESC_BY_STATE: dict[str, str] = {
    "시작":        "이번 달부터 흐름이 움직여. 큰 사건은 없어도 결이 바뀌는 시기야.",
    "진입":        "실이 한 가닥 새로 묶여. 익숙한 자리에서 새 사람 보일 수 있어.",
    "상승":        "흐름이 빠르게 차오르는 달. 다가오는 신호 놓치지 마.",
    "피크":        "실이 가장 강하게 당겨지는 달. 이때 움직이면 매듭이 단단히 묶여.",
    "심화":        "관계가 깊어지는 시기. 상대 페이스에 맞춰 움직여.",
    "안정":        "잔잔한 시기. 큰 변화보다 지금 흐름 유지가 좋아.",
    "정체":        "잠깐 흐름이 막혀. 조급하게 밀어붙이면 매듭이 엉켜.",
    "재상승":      "새 환경, 새 자리에 가봐. 거기서 실이 다시 움직여.",
    "2차 피크":    "실이 다시 한 번 강하게 당겨지는 달. 첫 피크 못 잡았어도 여기서 또 기회야. 표현을 분명히 해.",
    "신뢰":        "관계 단단해지는 시기. 약속 한 번이 천 마디보다 무거워.",
    "충전":        "속을 비우는 달. 다음 흐름에 쓸 기운을 모아.",
    "1년차 마무리": "1년이 한 바퀴 돌았어. 용기 있는 한마디가 다음 흐름을 바꿔.",
}


# ═════════════════════════════════════════════════════════════════
# 헬퍼
# ═════════════════════════════════════════════════════════════════

_STEM_HANJA: dict[str, str] = {
    "갑": "甲", "을": "乙", "병": "丙", "정": "丁", "무": "戊",
    "기": "己", "경": "庚", "신": "辛", "임": "壬", "계": "癸",
}
_OHANG_HANJA: dict[str, str] = {
    "목": "木", "화": "火", "토": "土", "금": "金", "수": "水",
}


def _ilgan_with_hanja(ilgan: str) -> str:
    if len(ilgan) != 2:
        return ilgan
    h = _STEM_HANJA.get(ilgan[0])
    o = _OHANG_HANJA.get(ilgan[1])
    if not h or not o:
        return ilgan
    return f"{ilgan}({h}{o})"


def _format_month_label(idx: int, start_year: int, start_month: int) -> str:
    """idx=0 → '5월 (이번달)' / 같은 해 → '6월' / 다음 해 → "'27. 1월"."""
    y = start_year
    m = start_month + idx
    if m > 12:
        m -= 12
        y += 1
    if idx == 0:
        return f"{m}월 (이번달)"
    if y == start_year:
        return f"{m}월"
    return f"'{str(y)[2:]}. {m}월"


def _peak_label_for_ai(idx: int, start_year: int, start_month: int) -> str:
    """AI 박스 안 '8월/`27. 1월' 같이 (이번달) 표기 없이 단순화."""
    y = start_year
    m = start_month + idx
    if m > 12:
        m -= 12
        y += 1
    if y == start_year:
        return f"{m}월"
    return f"'{str(y)[2:]}. {m}월"


def _pct_to_hearts_p8(pct: int) -> int:
    """P-8 전용 hearts 매핑. 실제 점수 분포(대부분 25~70대)에 맞춰 임계값 낮춤.

    무료 결과지 `_pct_to_hearts`(85+ = 5)는 hearts 5가 거의 안 뜨는 문제가 있어,
    P-8에서만 별도 분포 사용. hearts 5는 피크 강제로만 부여.
    """
    if pct <= 25:
        return 1
    if pct <= 40:
        return 2
    if pct <= 55:
        return 3
    return 4  # 5는 피크에서만 강제 부여


def _hearts_to_knot(hearts: int) -> str:
    if hearts >= 5:
        return "glowing"
    if hearts >= 3:
        return "tight"
    return "loose"


def _pick_top_two_peaks(raw_months: list[dict[str, Any]]) -> tuple[int, int]:
    """score 상위 2개 idx → idx 오름차순(시간순)으로 반환."""
    sorted_by_score = sorted(
        enumerate(raw_months), key=lambda x: -x[1]["romanceScore"]
    )
    top_two = [sorted_by_score[0][0], sorted_by_score[1][0]]
    top_two.sort()
    return top_two[0], top_two[1]


def _classify_state(
    idx: int,
    hearts: int,
    is_first_peak: bool,
    second_peak_idx: int,
    first_peak_idx: int,
) -> str:
    """row state 분류. hearts(=score) 기반 + 피크 전/후 위치로 분기.

    hearts가 라벨/desc와 일관되어야 사용자가 어색함 안 느낌:
    - hearts 5 = 피크
    - hearts 4 = 상승(피크 전) / 심화(피크 후)
    - hearts 3 = 진입(피크 전) / 안정(피크 후)
    - hearts 2 = 정체
    - hearts 1 = 충전
    - idx 0(이번달)과 11(마무리)은 hearts 무관 별도 라벨.
    """
    if is_first_peak:
        return "피크"
    if idx == second_peak_idx:
        return "2차 피크"
    if idx == 0:
        return "시작"
    if idx == 11:
        return "1년차 마무리"

    is_before_first_peak = idx < first_peak_idx
    if hearts >= 4:
        return "상승" if is_before_first_peak else "심화"
    if hearts == 3:
        return "진입" if is_before_first_peak else "안정"
    if hearts == 2:
        return "정체"
    return "충전"  # hearts <= 1


# ═════════════════════════════════════════════════════════════════
# 합성 함수
# ═════════════════════════════════════════════════════════════════

VALID_ILGAN: frozenset[str] = frozenset(ILGAN_FLOW_BY_ILGAN.keys())


def compose_p8_timing(
    *,
    ilgan: str,
    raw_months: list[dict[str, Any]],
    start_year: int,
    start_month: int,
) -> dict[str, object]:
    """P-8 5-1 12개월 운명선 풀 합성.

    Args:
        ilgan: 일간 한글 (10종)
        raw_months: MonthlyRomanceFlowService.compute_full_months() 결과 (12 row)
        start_year, start_month: 결제 시점 기준 (캐시된 사용자 시작 월)

    Returns:
        {
          months: [{label, hearts, knot, state, desc, is_peak}, ...] × 12,
          ai_intro: str (3단락),
          bubble: str (고정),
        }

    Raises:
        KeyError: 알 수 없는 일간.
        ValueError: raw_months 길이가 12 아님.
    """
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
        # 피크 2개는 score 절대값과 무관하게 hearts 5 강제 (그 사주에서 가장 강한 달).
        hearts = 5 if is_peak else _pct_to_hearts_p8(pct)
        knot = _hearts_to_knot(hearts)
        state = _classify_state(i, hearts, is_first, peak_2_idx, peak_1_idx)
        desc = STATE_DESC_BY_STATE.get(state, STATE_DESC_BY_STATE["상승"])
        label = _format_month_label(i, start_year, start_month)
        months_out.append({
            "label": label,
            "hearts": hearts,
            "knot": knot,
            "state": state,
            "desc": desc,
            "is_peak": is_peak,
        })

    peak_1_label = _peak_label_for_ai(peak_1_idx, start_year, start_month)
    peak_2_label = _peak_label_for_ai(peak_2_idx, start_year, start_month)

    ai_intro = "\n\n".join([
        PARA_1_FIXED,
        PARA_2_TEMPLATE.format(peak_1=peak_1_label, peak_2=peak_2_label),
        ILGAN_FLOW_BY_ILGAN[ilgan].format(ilgan_with_hanja=_ilgan_with_hanja(ilgan)),
    ])

    return {
        "months": months_out,
        "ai_intro": ai_intro,
        "bubble": BUBBLE,
    }
