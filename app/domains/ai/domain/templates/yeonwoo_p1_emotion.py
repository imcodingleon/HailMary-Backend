"""P-1 1-3 연애 중 감정 패턴 — 풀 템플릿 합성.

명리학 도메인 활용:
- 일간 10 × 촛불 차트 (3 row: 초반/중반/위기, 각 row의 강도/개수 다름)
- 일간 10 × row별 desc (30 조각)
- 일간 10 × ai_emotion 3단락 (30 조각)
- peak 위치 (분홍 강조 row) 일간별 다름

핵심 패턴:
- 갑목 (직진 단단): 초반부터 강 → 위기 단호 끊음 (위기 peak)
- 을목 (감김): 천천히 감김 → 위기 오래 끔 (위기 peak)
- 병화 (빛 → 식음): 초반 가장 강 → 위기 사라짐 (역행, 초반 peak)
- 정화 (은근 집중): 변동 X, 한 사람만 (peak X)
- 무토 (한결같음): 일관 (peak X)
- 기토 (다정 키움): 점점 키움 (위기 peak)
- 경금 (결단): 강함 유지 → 위기 단호 끊음 (위기 peak)
- 신금 (자존): 거리 → 들임 → 자존심 상함 (위기 peak)
- 임수 (깊이 빠짐): 누진 (위기 peak, HTML 더미)
- 계수 (스며듦): 천천히 → 위기 멈출 수 없음 (위기 peak)

AI 호출 0.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CandleStage:
    label: str
    flames: tuple[str, ...]
    desc: str
    is_peak: bool


# ── 일간별 촛불 차트 패턴 (3 row) + row별 desc ──
CANDLE_PATTERN_BY_ILGAN: dict[str, tuple[CandleStage, CandleStage, CandleStage]] = {
    "갑목": (
        CandleStage("초반", ("weak", "medium"),
                    "망설임 없이 표현해. 원하는 거 분명히 말해.", False),
        CandleStage("중반", ("weak", "medium", "strong"),
                    "점점 더 단단하게 가. 흔들림 없이.", False),
        CandleStage("후반", ("weak",),
                    "안 맞다 싶으면 단호하게 끊어. 미련 없어.", True),
    ),
    "을목": (
        CandleStage("초반", ("weak",),
                    "살살 감기기 시작해. 자신도 모르게.", False),
        CandleStage("중반", ("weak", "medium"),
                    "점점 깊이 들어가. 빠져나오기 어려워져.", False),
        CandleStage("후반", ("weak", "medium", "medium"),
                    "떠나고도 오래 끌어. 회복이 느려.", True),
    ),
    "병화": (
        CandleStage("초반", ("strong", "strong", "strong"),
                    "한 번에 환하게 비춰. 거리낌 없어.", True),
        CandleStage("중반", ("weak", "medium"),
                    "조금씩 식어가. 익숙해진 듯.", False),
        CandleStage("후반", ("weak",),
                    "한꺼번에 사라져. 차가워져.", False),
    ),
    "정화": (
        CandleStage("초반", ("weak",),
                    "작은 불꽃이지만 깊어. 한 사람만 봐.", False),
        CandleStage("중반", ("weak", "weak"),
                    "그 사람만 데우는 결. 흔들림 없어.", False),
        CandleStage("후반", ("weak", "weak", "weak"),
                    "한 사람한테 집중. 안 바꿔.", False),
    ),
    "무토": (
        CandleStage("초반", ("medium",),
                    "묵묵히 자리 잡아. 변동 없어.", False),
        CandleStage("중반", ("medium", "medium"),
                    "한결같이 곁에 있어. 행동으로 증명해.", False),
        CandleStage("후반", ("medium", "medium", "medium"),
                    "한 번 결정하면 안 흔들려. 묵직하게.", False),
    ),
    "기토": (
        CandleStage("초반", ("weak",),
                    "살살 챙겨주기 시작해.", False),
        CandleStage("중반", ("weak", "medium"),
                    "점점 더 깊이 키워줘. 진심이 쌓여.", False),
        CandleStage("후반", ("strong", "strong", "strong"),
                    "너 자신을 잊을 만큼 줘. 그러다 무너져.", True),
    ),
    "경금": (
        CandleStage("초반", ("strong",),
                    "강하게 다가가. 분명하게.", False),
        CandleStage("중반", ("strong", "medium"),
                    "단단하게 가. 흔들림 없어.", False),
        CandleStage("후반", ("strong",),
                    "단호하게 끊어내. 미련 없어.", True),
    ),
    "신금": (
        CandleStage("초반", ("weak",),
                    "거리를 두고 살펴. 단정하게.", False),
        CandleStage("중반", ("weak", "medium"),
                    "점점 들이게 돼. 그래도 단단함 유지.", False),
        CandleStage("후반", ("weak",),
                    "자존심 상하면 한 번에 끊어. 깊이 새겨.", True),
    ),
    "임수": (
        CandleStage("초반", ("weak",),
                    "잔잔해. 아직 불꽃이 작아.", False),
        CandleStage("중반", ("weak", "medium"),
                    "타오르기 시작해. 걷잡기 어려워.", False),
        CandleStage("후반", ("weak", "medium", "strong"),
                    "걷잡을 수 없어. 한꺼번에 터져.", True),
    ),
    "계수": (
        CandleStage("초반", ("weak",),
                    "거의 없는 듯 시작해. 천천히.", False),
        CandleStage("중반", ("weak", "weak"),
                    "천천히 스며들어. 멈출 수 없어.", False),
        CandleStage("후반", ("weak", "medium", "medium"),
                    "깊이 들어가서 멈출 수 없어. 모든 틈을 채워.", True),
    ),
}


# ── AI 박스 ai_emotion 일간별 3단락 ──
PARA_1_INTRO_BY_ILGAN: dict[str, str] = {
    "갑목": "초에 불을 붙이면 갑목은 처음부터 환해. 망설임 없이 직진해. 그게 매력이지만 위험해.",
    "을목": "초에 불을 붙여도 을목은 천천히 타. 감김이 느린데, 한 번 감기면 풀기 어려워.",
    "병화": "초에 불을 붙이면 병화는 한낮의 해처럼 환해. 처음이 가장 뜨거워. 근데 식으면 한꺼번에 사라져.",
    "정화": "초에 작은 불꽃을 켜면 정화는 한 사람만 데워. 안 흔들리고, 안 꺼져.",
    "무토": "초에 불을 붙여도 무토는 한결같아. 변동 없이, 묵직하게.",
    "기토": "초에 불을 붙이면 기토는 옆 사람을 키우려 해. 진심을 쌓아가는 결이야.",
    "경금": "초에 불을 붙이면 경금은 단단해. 옳고 그름이 분명한 결이야.",
    "신금": "초에 불을 붙이면 신금은 거리를 둬. 단정하게 살피는 결이야.",
    "임수": (
        "초에 불을 붙여 놓고 가만히 있으면 처음엔 작아. 손바닥만 한 불꽃이야. "
        "근데 어느 순간부터 멈출 수가 없어. 네 사랑이 그래."
    ),
    "계수": "초에 불을 붙이면 계수는 거의 없는 듯 시작해. 그러다 천천히 스며들어.",
}

PARA_2_ANALYSIS_BY_ILGAN: dict[str, str] = {
    "갑목": (
        "{ilgan_with_hanja} 일간은 분명한 사람이야. 좋다는 표현도 빠르고 아니라는 표현도 빠르지. "
        "근데 그 직진이 상대를 짓누를 때가 와."
    ),
    "을목": (
        "{ilgan_with_hanja} 일간은 깊이 빠지는 결이야. 한 사람한테 다 줘버려. "
        "너 자신이 먼저 닳을 만큼."
    ),
    "병화": (
        "{ilgan_with_hanja} 일간은 표현이 빠르고 숨김없어. 빛나는 결인데, "
        "식는 순간 차가워져. 그게 약점이야."
    ),
    "정화": (
        "{ilgan_with_hanja} 일간은 집중형이야. 한 사람한테 정성을 끝까지 쏟아. "
        "바람 한 번에 흔들리는 예민함도 있어."
    ),
    "무토": (
        "{ilgan_with_hanja} 일간은 다 받아주는 결이야. 표현은 적은데 행동으로 증명해. "
        "흔들림 없는 산처럼."
    ),
    "기토": (
        "{ilgan_with_hanja} 일간은 받기보다 주는 데 익숙해. "
        "그러다 자기를 잊는 게 약점이야."
    ),
    "경금": (
        "{ilgan_with_hanja} 일간은 결단력 있어. 아닌 관계는 잘라내. "
        "그러다 사람을 다치게 하기도 해."
    ),
    "신금": (
        "{ilgan_with_hanja} 일간은 은근한 자존감이 매력이야. "
        "감정을 들키지 않으려는 단정함도 있어."
    ),
    "임수": (
        "{ilgan_with_hanja} 일간은 표현이 늦어. 속에선 이미 활활 타고 있는데 밖에 안 보여. "
        "그러다 위기가 오면 한꺼번에 터져. 네 자신도 놀랄 만큼."
    ),
    "계수": (
        "{ilgan_with_hanja} 일간은 분위기와 감정을 먼저 읽는 결이야. "
        "느리게 자리잡아서 멈출 수 없게 돼."
    ),
}

# ── 강연우 클로징 멘트 (1-3 섹션 끝 YeonwooBubble) ──
BUBBLE_BY_ILGAN: dict[str, str] = {
    "갑목": "네 직진이 너무 빨라서 상대가 따라오기 전에 부담돼.",
    "을목": "너만 깊어지고 상대는 아직 미적지근해.",
    "병화": "네 빛이 한꺼번에 식으면, 상대는 이유도 모르고 차가워졌다고 느껴.",
    "정화": "네 작은 불꽃을 알아주는 사람한테만 가. 흔들리는 바람한테 데이지 마.",
    "무토": "표현 적은 게 너의 결인데, 상대는 그걸 무관심으로 오해해.",
    "기토": "너 자신부터 챙겨야 오래 가. 다 줘버리고 무너지지 마.",
    "경금": "끊어낼 땐 상대 마음도 같이 끊어진다는 걸 잊지 마.",
    "신금": "자존심에 한 번 상처 입으면 너는 다시 안 돌아봐. 그러니까 처음부터 잘 보여.",
    "임수": "속에서 다 끓는데 밖으로 안 내보내잖아. 상대는 네가 관심 없는 줄 알아.",
    "계수": "천천히 스며들면서 너부터 잃지 마. 흐른다고 다 받아들이지 마.",
}


def get_emotion_bubble(ilgan: str) -> str:
    """1-3 섹션 끝 강연우 멘트 (일간별)."""
    if ilgan not in VALID_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")
    return BUBBLE_BY_ILGAN[ilgan]


PARA_3_ADVICE_BY_ILGAN: dict[str, str] = {
    "갑목": "한 번쯤은 휘어줘. 곧음만으론 사람이 못 견뎌. 너의 감정도 가끔은 천천히 가.",
    "을목": "감기다 너부터 챙겨. 끝까지 갈 수 있는 결이니까 자신을 믿어.",
    "병화": "그늘도 같이 줘야 사람이 머물러. 빛만 너무 세면 상대가 눈을 돌려.",
    "정화": "네 불꽃을 알아주는 사람한테만 가. 거센 바람은 너를 꺼버려.",
    "무토": "다 받아주다 네가 무너지지 마. 산도 가끔은 비를 흘려보내야 해.",
    "기토": "네가 키운 마음에 네 자리도 꼭 남겨둬. 너부터 챙겨야 오래 가.",
    "경금": "갈고 다듬어서 써. 날카로움이 사람을 다치게 해.",
    "신금": "네 빛을 알아보는 사람한테만 곁을 줘. 험하게 다루는 손은 끊어내.",
    "임수": (
        "그 전에 작은 불꽃이라도 보여줘. 한 줄, 한 마디면 돼. "
        "안 그러면 상대는 영영 못 알아. 너는 또 혼자 끓다가 혼자 무너질 거야."
    ),
    "계수": "흐른다고 다 받아들이지 마. 멈춰야 할 자리는 멈춰. 너부터 지켜야 해.",
}


VALID_ILGAN: frozenset[str] = frozenset(CANDLE_PATTERN_BY_ILGAN.keys())


# ── 한자 병기 헬퍼 (yeonwoo_p1_chapter_opening / yeonwoo_p1_trigger와 동일) ──
_HEAVEN_HANJA: dict[str, str] = {
    "갑": "甲", "을": "乙", "병": "丙", "정": "丁", "무": "戊",
    "기": "己", "경": "庚", "신": "辛", "임": "壬", "계": "癸",
}

_OHANG_HANJA: dict[str, str] = {
    "목": "木", "화": "火", "토": "土", "금": "金", "수": "水",
}


def _ilgan_with_hanja(ilgan: str) -> str:
    if len(ilgan) != 2:
        return ilgan
    h = _HEAVEN_HANJA.get(ilgan[0])
    o = _OHANG_HANJA.get(ilgan[1])
    if not h or not o:
        return ilgan
    return f"{ilgan}({h}{o})"


def get_candle_pattern(
    ilgan: str,
) -> tuple[CandleStage, CandleStage, CandleStage]:
    """일간별 감정 차트 3 row (초반/중반/위기) 반환."""
    if ilgan not in VALID_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")
    return CANDLE_PATTERN_BY_ILGAN[ilgan]


def compose_p1_emotion(*, ilgan: str) -> str:
    """1-3 AI 박스 ai_emotion 합성 — 250~300자.

    3단락: 도입 + 일간 분석 + 조언.
    """
    if ilgan not in VALID_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")

    para1 = PARA_1_INTRO_BY_ILGAN[ilgan]
    para2 = PARA_2_ANALYSIS_BY_ILGAN[ilgan].format(
        ilgan_with_hanja=_ilgan_with_hanja(ilgan)
    )
    para3 = PARA_3_ADVICE_BY_ILGAN[ilgan]

    return "\n\n".join([para1, para2, para3])
