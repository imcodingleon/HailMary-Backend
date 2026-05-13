"""P-9 6-1 오행 보완 — 부족 오행 5 + 일간 10 변형 풀 템플릿.

설계:
- 카드 3개 (색/공간/행동) × 부족 오행 5 매트릭스 → label/value/sub 일간 무관 변동
- AI 박스 3단락:
  1. 부족 오행별 헤더 ("토(土)가 비어 있어. 채워야 흐름이 도네...")
  2. 부족 오행별 본문 ("색은 X. 자리는 Y. 행동은 Z.")
  3. 고정 도입 + 일간 10 × 부족 오행 placeholder + 고정 마무리

명리학 5행 보완 룰:
- 木 부족: 초록·청록 / 동쪽 / 산책·식물
- 火 부족: 빨강·주황 / 남쪽 / 활동·운동
- 土 부족: 노랑·갈색(사용자 자료는 초록·동쪽 톤 차용 — 사용자 케이스 임수+토 부족 기준)
- 金 부족: 흰색·금속 / 서쪽 / 정리·단단함
- 水 부족: 짙은 파랑·검정 / 북쪽 / 물·차분함

AI 호출 0.
"""

from dataclasses import dataclass

# ═════════════════════════════════════════════════════════════════
# 고정 — AI 박스 3단락 도입/마무리
# ═════════════════════════════════════════════════════════════════

PARA_3_LEAD = "이 셋을 한 달만 의식해. 명줄의 매듭이 풀리기 시작해."
PARA_3_TAIL = "작은 거 하나부터 시작하면 돼. 다 안 해도 돼. 하나씩 해."


# ═════════════════════════════════════════════════════════════════
# 카드 3종 — 부족 오행 5 × {색/공간/행동}
# ═════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class MethodCard:
    label: str
    value: str
    sub: str


METHOD_CARDS_BY_LACK: dict[str, tuple[MethodCard, MethodCard, MethodCard]] = {
    "목": (
        MethodCard("방법 1 · 색", "초록 계열 가까이 둬",
                   "목(木) 기운을 색으로 끌어와. 옷, 소품, 화면 다 좋아."),
        MethodCard("방법 2 · 공간", "동쪽 자리 의식해",
                   "동쪽이 목(木)의 자리야. 책상이든 침대 머리든 그 방향으로."),
        MethodCard("방법 3 · 행동", "아침 산책 30분",
                   "살아있는 기운을 몸에 채워. 식물, 나무, 흙 가까이."),
    ),
    "화": (
        MethodCard("방법 1 · 색", "빨강·주황 들여놔",
                   "화(火) 기운을 색으로 끌어와. 액세서리든 포인트 컬러로든 일상에."),
        MethodCard("방법 2 · 공간", "남쪽 자리 의식해",
                   "남쪽이 화(火)의 자리야. 햇볕 잘 드는 자리에 머물러."),
        MethodCard("방법 3 · 행동", "오후 운동 30분",
                   "땀 나는 활동으로 기운을 데워. 차가운 결을 식히지 마."),
    ),
    "토": (
        MethodCard("방법 1 · 색", "초록 계열 가까이 둬",
                   "토(土) 기운을 색으로 끌어와. 옷, 소품, 화면 다 좋아."),
        MethodCard("방법 2 · 공간", "동쪽 자리 의식해",
                   "동쪽이 토(土)의 자리야. 책상이든 침대 머리든 그 방향으로."),
        MethodCard("방법 3 · 행동", "아침 산책 30분",
                   "살아있는 기운을 몸에 채워. 식물, 나무, 흙 가까이."),
    ),
    "금": (
        MethodCard("방법 1 · 색", "흰색·금속 톤 들여놔",
                   "금(金) 기운을 색으로 끌어와. 단정한 흰옷, 금색 소품이 좋아."),
        MethodCard("방법 2 · 공간", "서쪽 자리 의식해",
                   "서쪽이 금(金)의 자리야. 책상이든 침대 머리든 그 방향으로."),
        MethodCard("방법 3 · 행동", "공간 정리 30분",
                   "물건 줄이고 결을 다듬어. 금속 소품·도구 가까이 둬."),
    ),
    "수": (
        MethodCard("방법 1 · 색", "짙은 파랑·검정 가까이 둬",
                   "수(水) 기운을 색으로 끌어와. 옷, 소품, 화면 다 좋아."),
        MethodCard("방법 2 · 공간", "북쪽 자리 의식해",
                   "북쪽이 수(水)의 자리야. 책상이든 침대 머리든 그 방향으로."),
        MethodCard("방법 3 · 행동", "저녁 차 한 잔",
                   "차분한 결을 몸에 채워. 물 가까이·고요한 자리에 머물러."),
    ),
}


# ═════════════════════════════════════════════════════════════════
# AI 단락 1 — 부족 오행별 헤더
# ═════════════════════════════════════════════════════════════════
# `{ohang_with_hanja}` placeholder 치환

LACK_HEADER_BY_LACK: dict[str, str] = {
    "목": (
        "{ohang_with_hanja}가 비어 있어. 채워야 결이 자라네. "
        "빈 채로 두면 인연이 들어와도 뿌리 내릴 자리가 없어."
    ),
    "화": (
        "{ohang_with_hanja}가 비어 있어. 채워야 결이 따뜻해지네. "
        "빈 채로 두면 인연이 와도 식어버려."
    ),
    "토": (
        "{ohang_with_hanja}가 비어 있어. 채워야 흐름이 도네. "
        "빈 채로 두면 인연이 들어와도 머물 자리가 없어."
    ),
    "금": (
        "{ohang_with_hanja}가 비어 있어. 채워야 결이 분명해지네. "
        "빈 채로 두면 인연이 와도 흐릿하게 흘러."
    ),
    "수": (
        "{ohang_with_hanja}가 비어 있어. 채워야 결이 깊어지네. "
        "빈 채로 두면 인연이 와도 깊이가 안 생겨."
    ),
}


# ═════════════════════════════════════════════════════════════════
# AI 단락 2 — 부족 오행별 본문 (카드 셋 요약)
# ═════════════════════════════════════════════════════════════════

METHOD_BODY_BY_LACK: dict[str, str] = {
    "목": (
        "색은 초록. 옷이든 소품이든 화면이든 일상에 들여놔. "
        "자리는 동쪽. 책상이든 침대 머리든 동쪽으로 돌려. "
        "행동은 아침 산책. 30분이면 돼. 식물, 나무, 흙 — 목(木) 기운이 사는 자리 가까이 가."
    ),
    "화": (
        "색은 빨강·주황. 포인트 컬러로 일상에 들여놔. "
        "자리는 남쪽. 햇볕 잘 드는 자리에 머물러. "
        "행동은 오후 운동. 30분이면 돼. 땀 나는 결로 차가운 자리를 데워."
    ),
    "토": (
        "색은 초록. 옷이든 소품이든 화면이든 일상에 들여놔. "
        "자리는 동쪽. 책상이든 침대 머리든 동쪽으로 돌려. "
        "행동은 아침 산책. 30분이면 돼. 식물, 나무, 흙 — 토(土) 기운이 사는 자리 가까이 가."
    ),
    "금": (
        "색은 흰색·금속 톤. 단정한 옷·금색 소품으로 들여놔. "
        "자리는 서쪽. 책상이든 침대 머리든 서쪽으로 돌려. "
        "행동은 공간 정리. 30분이면 돼. 물건 줄이고 결을 다듬는 자리에 머물러."
    ),
    "수": (
        "색은 짙은 파랑·검정. 옷이든 소품이든 화면이든 일상에 들여놔. "
        "자리는 북쪽. 책상이든 침대 머리든 북쪽으로 돌려. "
        "행동은 저녁 차 한 잔. 30분이면 돼. 물 가까이·고요한 자리에 머물러."
    ),
}


# ═════════════════════════════════════════════════════════════════
# AI 단락 3 — 일간별 변형 + 부족 오행 placeholder
# ═════════════════════════════════════════════════════════════════
# `{ilgan_with_hanja}` + `{ohang_with_hanja}` 둘 다 치환
# 일간 결 + "거기에 [부족 오행] 기운이 들어가야 인연이 움직여" 형태

ILGAN_PRACTICE_BY_ILGAN: dict[str, str] = {
    "갑목": (
        "{ilgan_with_hanja} 일간은 곧게 뻗는 결인데, "
        "거기에 {ohang_with_hanja} 기운이 들어가야 비로소 인연이 움직여."
    ),
    "을목": (
        "{ilgan_with_hanja} 일간은 휘어 살아남는 결인데, "
        "거기에 {ohang_with_hanja} 기운이 들어가야 비로소 인연이 움직여."
    ),
    "병화": (
        "{ilgan_with_hanja} 일간은 환하게 비추는 결인데, "
        "거기에 {ohang_with_hanja} 기운이 들어가야 비로소 인연이 움직여."
    ),
    "정화": (
        "{ilgan_with_hanja} 일간은 작게 오래 비추는 결인데, "
        "거기에 {ohang_with_hanja} 기운이 들어가야 비로소 인연이 움직여."
    ),
    "무토": (
        "{ilgan_with_hanja} 일간은 묵직하게 받쳐주는 결인데, "
        "거기에 {ohang_with_hanja} 기운이 들어가야 비로소 인연이 움직여."
    ),
    "기토": (
        "{ilgan_with_hanja} 일간은 다정하게 키워주는 결인데, "
        "거기에 {ohang_with_hanja} 기운이 들어가야 비로소 인연이 움직여."
    ),
    "경금": (
        "{ilgan_with_hanja} 일간은 단단하고 분명한 결인데, "
        "거기에 {ohang_with_hanja} 기운이 들어가야 비로소 인연이 움직여."
    ),
    "신금": (
        "{ilgan_with_hanja} 일간은 다듬어진 정갈한 결인데, "
        "거기에 {ohang_with_hanja} 기운이 들어가야 비로소 인연이 움직여."
    ),
    "임수": (
        "{ilgan_with_hanja} 일간은 원래 깊은데 "
        "거기에 살아있는 {ohang_with_hanja} 기운이 들어가야 비로소 인연이 움직여."
    ),
    "계수": (
        "{ilgan_with_hanja} 일간은 분위기로 스며드는 결인데, "
        "거기에 {ohang_with_hanja} 기운이 들어가야 비로소 인연이 움직여."
    ),
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


def _ohang_with_hanja(ohang: str) -> str:
    o = _OHANG_HANJA.get(ohang)
    return f"{ohang}({o})" if o else ohang


VALID_ILGAN: frozenset[str] = frozenset(ILGAN_PRACTICE_BY_ILGAN.keys())
VALID_OHANG: frozenset[str] = frozenset(METHOD_CARDS_BY_LACK.keys())


def compose_p9_practice(
    *, ilgan: str, ohang_lack: str
) -> dict[str, object]:
    """P-9 6-1 오행 보완 풀 합성.

    Args:
        ilgan: 일간 한글 (10종)
        ohang_lack: 부족 오행 한글 1글자 (5종)

    Returns:
        {
          ohang_lack: str ("토(土)" 한자 포함),
          ohang_method_cards: [{label, value, sub}, ...] × 3,
          ai_ohang: str (3단락),
        }

    Raises:
        KeyError: 알 수 없는 일간/오행.
    """
    if ilgan not in VALID_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")
    if ohang_lack not in VALID_OHANG:
        raise KeyError(f"unknown ohang_lack: {ohang_lack!r}")

    ilgan_h = _ilgan_with_hanja(ilgan)
    ohang_h = _ohang_with_hanja(ohang_lack)

    cards = METHOD_CARDS_BY_LACK[ohang_lack]
    para_1 = LACK_HEADER_BY_LACK[ohang_lack].format(ohang_with_hanja=ohang_h)
    para_2 = METHOD_BODY_BY_LACK[ohang_lack]
    ilgan_line = ILGAN_PRACTICE_BY_ILGAN[ilgan].format(
        ilgan_with_hanja=ilgan_h, ohang_with_hanja=ohang_h
    )
    para_3 = f"{PARA_3_LEAD} {ilgan_line} {PARA_3_TAIL}"

    return {
        "ohang_lack": ohang_h,
        "ohang_method_cards": [
            {"label": c.label, "value": c.value, "sub": c.sub} for c in cards
        ],
        "ai_ohang": "\n\n".join([para_1, para_2, para_3]),
    }
