"""일간 10종 정적 카드 풀.

HTML line 1572~1596 (P-0 0-3 일간 카드) 양식을 따른다:
- 헤더: 한글(한자)
- 부제: 짧은 비유
- 결: 1~2문장 본질
- 연애에서: 3개 불릿
- 주의: 1문장

톤: 반말, 시적, 무속적 — HTML 임수(壬水) 더미와 일관.
LLM 호출 비용 0. 사용자 일간이 정해지면 dict 조회로 즉시 반환.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class IlganCard:
    name_kor: str
    name_han: str
    subtitle: str
    essence: str
    in_love: tuple[str, ...]
    caution: str

    def total_length(self) -> int:
        """결 + 연애 3불릿 + 주의 합산 글자 수 (공백 포함)."""
        return (
            len(self.essence)
            + sum(len(b) for b in self.in_love)
            + len(self.caution)
        )


ILGAN_CARDS: dict[str, IlganCard] = {
    "갑목": IlganCard(
        name_kor="갑목",
        name_han="甲木",
        subtitle="큰 나무 · 곧게 뻗은 결",
        essence="하늘로 곧게 뻗는 큰 나무. 굽히기보다 부러지는 결을 가진 사람.",
        in_love=(
            "한 번 정하면 끝까지 밀고 가는 직진형",
            "지키고 싶은 사람 앞에선 더 단단해짐",
            "굽히지 못해 사소한 데서 부딪히는 결",
        ),
        caution="네 곧음이 상대를 짓누를 수 있어. 가끔은 휘어줘.",
    ),
    "을목": IlganCard(
        name_kor="을목",
        name_han="乙木",
        subtitle="풀·덩굴 · 휘어 살아남는 결",
        essence="바위 틈에서도 자라는 덩굴. 부드러운데 끝까지 살아남는 사람.",
        in_love=(
            "상대에 맞춰 결을 휘는 적응력",
            "기대고 싶은 사람한테 깊이 감기는 결",
            "버려질까 두려워 먼저 놓아버리는 경향",
        ),
        caution="휘어주는 게 네 매력인데, 너무 감기면 네가 먼저 닳아.",
    ),
    "병화": IlganCard(
        name_kor="병화",
        name_han="丙火",
        subtitle="태양 · 환하게 비추는 결",
        essence="모두를 비추는 한낮의 해. 들어오는 사람마다 따뜻해지는 사람.",
        in_love=(
            "먼저 다가가 온도를 올리는 결",
            "표현이 빠르고 숨김없는 직관형",
            "관심이 식으면 빛이 한꺼번에 사라짐",
        ),
        caution="네 빛이 너무 세면 상대가 눈을 돌려. 그늘도 같이 줘야 해.",
    ),
    "정화": IlganCard(
        name_kor="정화",
        name_han="丁火",
        subtitle="촛불 · 작게 오래 타는 결",
        essence="작은 불꽃인데 밤새 꺼지지 않는 촛불. 고요한 정성으로 사랑하는 사람.",
        in_love=(
            "조용히 곁을 지키는 은근한 결",
            "한 사람만 깊게 데우는 집중형",
            "바람 한 번에 흔들리는 예민함",
        ),
        caution="네 불꽃을 알아주는 사람한테만 가. 거센 바람은 너를 꺼버려.",
    ),
    "무토": IlganCard(
        name_kor="무토",
        name_han="戊土",
        subtitle="큰 산 · 흔들리지 않는 결",
        essence="우뚝 선 산처럼 묵직한 사람. 누구라도 기댈 수 있는 자리를 가진 결.",
        in_love=(
            "상대를 다 받아주는 너른 품",
            "표현은 적어도 행동으로 증명하는 결",
            "한 번 등 돌리면 다시 오르기 어려움",
        ),
        caution="다 받아주다 네가 무너져. 산도 가끔은 비를 흘려보내야 해.",
    ),
    "기토": IlganCard(
        name_kor="기토",
        name_han="己土",
        subtitle="밭 · 묵묵히 키워내는 결",
        essence="씨를 받아 가만히 길러내는 부드러운 흙. 옆 사람을 자라게 하는 따뜻한 사람.",
        in_love=(
            "상대의 결점까지 품어 키워주는 너른 결",
            "조심스럽고 세심해서 오래 가는 다정함",
            "받기보다 주는 데 익숙해 자기를 잊는 경향",
        ),
        caution="네가 키운 마음에 네 자리도 꼭 남겨둬.",
    ),
    "경금": IlganCard(
        name_kor="경금",
        name_han="庚金",
        subtitle="도끼·바위 · 베고 가는 결",
        essence="단단하고 거친 쇠. 옳고 그름이 분명한, 잘라낼 줄 아는 사람.",
        in_love=(
            "할 말은 하는 직설적인 결",
            "결심이 서면 흔들리지 않는 단단함",
            "상처 줄까 봐 먼저 거리를 두는 습관",
        ),
        caution="네 날카로움이 사람을 다치게 해. 갈고 다듬어서 써.",
    ),
    "신금": IlganCard(
        name_kor="신금",
        name_han="辛金",
        subtitle="보석 · 다듬어진 결",
        essence="잘 닦인 보석처럼 빛나는 사람. 눈에 띄는데 쉽게 잡히지 않는 결.",
        in_love=(
            "은근한 자존감이 매력으로 도는 결",
            "감정을 들키지 않으려는 단정함",
            "상처를 오래 마음에 새기는 예민함",
        ),
        caution="네 빛을 알아보는 사람한테만 곁을 줘. 험하게 다루는 손은 끊어내.",
    ),
    "임수": IlganCard(
        name_kor="임수",
        name_han="壬水",
        subtitle="큰 물 · 깊은 바다",
        essence="깊고 잔잔한데 안에서 끊임없이 도는 물. 보이는 것보다 훨씬 큰 사람.",
        in_love=(
            "한 번 빠지면 끝까지 가는 결",
            "표현이 늦지만 한 번 하면 깊음",
            "침묵으로 사랑을 증명하려는 경향",
        ),
        caution="네 깊이를 못 받는 사람한테 가지 마.",
    ),
    "계수": IlganCard(
        name_kor="계수",
        name_han="癸水",
        subtitle="이슬·시냇물 · 스며드는 결",
        essence="가만히 흐르고 조용히 적시는 물. 작아 보이는데 결국 모든 틈을 채우는 사람.",
        in_love=(
            "분위기와 감정을 먼저 읽는 섬세함",
            "느리게 스며들어 깊게 자리잡는 결",
            "상대 기분에 너무 맞추다 자기를 잃음",
        ),
        caution="흐른다고 다 받아들이지 마. 멈춰야 할 자리는 멈춰.",
    ),
}


VALID_ILGAN_NAMES: frozenset[str] = frozenset(ILGAN_CARDS.keys())


def get_ilgan_card(ilgan: str) -> IlganCard:
    """일간 한글로 카드 조회. 알 수 없는 이름은 KeyError."""
    return ILGAN_CARDS[ilgan]
