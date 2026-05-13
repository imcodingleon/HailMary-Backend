"""P-9 6-2 매력살 활용 — 매력살 7(6+am_rok 폴백) × 보유 수 인식 × 일간 10 변형 풀 템플릿.

설계:
- P-5 = 매력살 진단(64조합), P-9 6-2 = 매력살 활용(Primary 1점 집중) — 페이지 역할 분리.
- 카드 3개 (감각/태도/언어) × 매력살 7 매트릭스 → label/value/sub 일간 무관 변동.
- AI 박스 3단락:
  1. {보유 수 인식, n>=1만} + {매력살별 헤더}
  2. {매력살별 본문} (카드 3가지 요약 + 단계 변화)
  3. {매력살(한자)} × {일간(한자)} 마무리 + 고정 꼬리.

폴백 (매력살 보유 0개):
- primary_charm_key = "am_rok" (암록)
- 보유 인식 멘트 생략, 헤더가 곧 암록 소개
- 단계는 微 → 弱 (잠재→살짝 깸)

명리학 7매력살 발현 룰:
- 도화살(桃花煞): 외향 발산 — 시선·표현·꾸밈
- 홍염살(紅艶煞): 정적 매력 — 인상·자기 색
- 화개살(華蓋煞): 내적 깊이 — 예술·고독한 결
- 금여록(金輿祿): 여유·풍요감
- 공망(空亡): 절제·미스터리
- 천을귀인(天乙貴人): 정중함·단정함
- 암록(暗祿) [폴백]: 숨은 록 — 드러나지 않는 결

AI 호출 0.
"""

from dataclasses import dataclass
from typing import Literal

# ═════════════════════════════════════════════════════════════════
# 5단계 한자 스케일
# ═════════════════════════════════════════════════════════════════

CharmStage = Literal["微", "弱", "中", "強", "極"]

STAGE_KOR: dict[CharmStage, str] = {
    "微": "미", "弱": "약", "中": "중", "強": "강", "極": "극",
}
STAGE_DESC: dict[CharmStage, str] = {
    "微": "잠재 상태",
    "弱": "살짝 깸",
    "中": "현재 자리",
    "強": "목표 단계",
    "極": "완전 발동",
}


def score_to_stage(score: int) -> CharmStage:
    """charm_service.charmStrength (0~100) → current 단계.

    current 최대치는 強 (4단계). 極(5단계)은 시각적 목표 단계로만 존재 —
    어떤 점수든 항상 위에 한 칸이 있어야 "{current}에서 {target}으로 한 칸 올라가"
    멘트가 자연스럽게 성립.

    임계값은 실측 후 조정 가능.
    """
    if score <= 20:
        return "微"
    if score <= 45:
        return "弱"
    if score <= 70:
        return "中"
    return "強"


def next_stage(stage: CharmStage) -> CharmStage:
    """한 칸 위 (極은 자기 자신)."""
    order: tuple[CharmStage, ...] = ("微", "弱", "中", "強", "極")
    idx = order.index(stage)
    return order[min(idx + 1, len(order) - 1)]


# ═════════════════════════════════════════════════════════════════
# 매력살 키 → 한자 표기 (charm_sals.py CHARM_SALS와 동기화 + am_rok 추가)
# ═════════════════════════════════════════════════════════════════

CHARM_KEY_WITH_HANJA: dict[str, str] = {
    "do_hwa_sal": "도화살(桃花煞)",
    "hong_yeom_sal": "홍염살(紅艶煞)",
    "hwa_gae_sal": "화개살(華蓋煞)",
    "geum_yeo_rok": "금여록(金輿祿)",
    "gong_mang": "공망(空亡)",
    "cheon_eul_gwi_in": "천을귀인(天乙貴人)",
    "am_rok": "암록(暗祿)",
}


# ═════════════════════════════════════════════════════════════════
# 카드 3종 — 매력살 7 × {감각/태도/언어}
# ═════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class CharmCard:
    label: str
    value: str
    sub: str


_CARD_LABELS: tuple[str, str, str] = (
    "방법 1 · 감각",
    "방법 2 · 태도",
    "방법 3 · 언어",
)


CHARM_PRACTICE_CARDS_BY_KEY: dict[str, tuple[CharmCard, CharmCard, CharmCard]] = {
    "do_hwa_sal": (
        CharmCard(_CARD_LABELS[0], "자기 향 하나 고정",
                  "향수 한 방울이면 돼. 매번 같은 결로 박혀야 사람이 기억해."),
        CharmCard(_CARD_LABELS[1], "한 박자 머무는 눈빛",
                  "스쳐 보지 말고 잠깐 잡아. 도화는 시선에서 켜져."),
        CharmCard(_CARD_LABELS[2], "한 박자 늦게 답하기",
                  "바로 답하지 말고 한 호흡 쉬어. 그 빈 자리에 끌림이 와."),
    ),
    "hong_yeom_sal": (
        CharmCard(_CARD_LABELS[0], "자기 색 하나 정해",
                  "옷·립·헤어 시그니처 컬러 하나만. 흩어지면 강렬함이 묻혀."),
        CharmCard(_CARD_LABELS[1], "어깨 펴고 천천히",
                  "빠른 동작 줄여. 정적인 결이 홍염을 살려."),
        CharmCard(_CARD_LABELS[2], "첫 한마디 짧게",
                  "인사를 길게 끌지 마. 한 단어로 박히는 게 홍염이야."),
    ),
    "hwa_gae_sal": (
        CharmCard(_CARD_LABELS[0], "취향 큐레이션",
                  "영화·책·음악 자기 결로 큐레이션. 화개는 깊이로 끌어."),
        CharmCard(_CARD_LABELS[1], "혼자 있는 시간 확보",
                  "의식적으로 비워. 군중 속에 섞이면 화개가 닫혀."),
        CharmCard(_CARD_LABELS[2], "깊은 말 한 줄",
                  "가벼운 잡담 줄이고 한 문장 무게 있게. 짧고 깊게."),
    ),
    "geum_yeo_rok": (
        CharmCard(_CARD_LABELS[0], "공간 정돈",
                  "책상·가방·방 정리. 풍요는 정돈된 결에서 풀려."),
        CharmCard(_CARD_LABELS[1], "조급함 빼기",
                  "빨리 대답 안 해도 돼. 여유가 곧 금여록이야."),
        CharmCard(_CARD_LABELS[2], "감사·칭찬 자주",
                  "작은 거 자주 표현해. 베푸는 결이 풍요를 부르거든."),
    ),
    "gong_mang": (
        CharmCard(_CARD_LABELS[0], "다 보여주지 않기",
                  "옷·SNS 절반만. 채우지 말고 비워."),
        CharmCard(_CARD_LABELS[1], "반응 한 박자 줄이기",
                  "다 받아치지 마. 비어있는 자리가 매력이야."),
        CharmCard(_CARD_LABELS[2], "다 답하지 않기",
                  "받은 질문 골라서 답해. 침묵의 무게."),
    ),
    "cheon_eul_gwi_in": (
        CharmCard(_CARD_LABELS[0], "단정함 유지",
                  "옷·머리·자세 깔끔하게. 흐트러지면 귀인기가 흐려져."),
        CharmCard(_CARD_LABELS[1], "먼저 인사",
                  "정중함 한 박자 빠르게. 천을귀인은 태도에서 켜져."),
        CharmCard(_CARD_LABELS[2], "약속 가볍게 안 하기",
                  "한 마디에 책임 실어. 신뢰가 곧 귀인이야."),
    ),
    "am_rok": (
        CharmCard(_CARD_LABELS[0], "잔향만 남기기",
                  "옷·향·소품 다 빼고 한 가지만. 비어 있어야 암록이 켜져."),
        CharmCard(_CARD_LABELS[1], "한 발 물러서기",
                  "적극적으로 어필하지 마. 물러설 때 끌어와."),
        CharmCard(_CARD_LABELS[2], "말 한 마디에 의미 싣기",
                  "많이 말하지 말고 한 문장에 담아. 침묵의 무게."),
    ),
}


# ═════════════════════════════════════════════════════════════════
# AI 단락 1a — 보유 수 인식 (n=0은 헤더에 흡수, 별도 셀 X)
# ═════════════════════════════════════════════════════════════════
# `{primary_with_hanja}` placeholder 치환

COUNT_RECOGNITION_BY_N: dict[int, str] = {
    1: "너에겐 매력살이 하나 있어. 이거만 잘 깨우면 돼.",
    2: "너에겐 매력살이 두 개 박혀 있어. 그 중 {primary_with_hanja}부터 깨워.",
    3: (
        "너에겐 매력살이 세 개 박혀 있는 결이야. 흔치 않아. "
        "{primary_with_hanja}부터 시작하면 나머지가 따라 와."
    ),
    4: (
        "너에겐 매력살이 네 개 박혀 있어. 명리적으로 풍부한 결이야. "
        "{primary_with_hanja}부터 깨우는 게 빨라."
    ),
    5: (
        "너에겐 매력살이 다섯 개 박혀 있어. 거의 다 갖춘 결이야. "
        "{primary_with_hanja}만 의식하면 충분해."
    ),
    6: (
        "너에겐 매력살 여섯 종이 다 박혀 있어. 매우 드문 결. "
        "{primary_with_hanja} 하나만 의식적으로 깨우면 나머지가 자동으로 켜져."
    ),
}


# ═════════════════════════════════════════════════════════════════
# AI 단락 1b — 매력살별 헤더
# ═════════════════════════════════════════════════════════════════

CHARM_HEADER_BY_KEY: dict[str, str] = {
    "do_hwa_sal": "도화살(桃花煞)은 살아 있어야 켜져. 잠재워 두면 그대로 잠들어.",
    "hong_yeom_sal": "홍염살(紅艶煞)은 한 번에 박히는 결이야. 안 드러내면 그대로 묻혀.",
    "hwa_gae_sal": "화개살(華蓋煞)은 깊이로 사람을 끌어. 가볍게 흩어지면 닫혀.",
    "geum_yeo_rok": "금여록(金輿祿)은 여유에서 풀려나와. 조급하면 가두는 결이야.",
    "gong_mang": "공망(空亡)은 비어있어야 끌려. 다 채우면 사라져.",
    "cheon_eul_gwi_in": "천을귀인(天乙貴人)은 단정함 위에 켜져. 흐트러지면 흐려져.",
    "am_rok": (
        "두드러진 매력살은 안 보여. 그런데 너에겐 암록(暗祿)이 있어. "
        "드러나지 않는 결인데, 깨우면 사람이 이유 없이 끌려와."
    ),
}


# ═════════════════════════════════════════════════════════════════
# AI 단락 2 — 매력살별 본문 (카드 3가지 요약 + 단계 변화)
# ═════════════════════════════════════════════════════════════════
# `{current_kor}` / `{target_kor}` placeholder 치환 (예: "中"/"強")

CHARM_PRACTICE_BODY_BY_KEY: dict[str, str] = {
    "do_hwa_sal": (
        "향 한 방울. 한 박자 머무는 눈빛. 한 박자 늦게 답하기. "
        "이 셋만 일주일 해봐. {current}에서 {target}으로 한 칸 올라가."
    ),
    "hong_yeom_sal": (
        "자기 색 하나 고정. 어깨 펴고 천천히. 첫 한마디 짧게. "
        "이 셋만 일주일 해봐. {current}에서 {target}으로 한 칸 올라가."
    ),
    "hwa_gae_sal": (
        "취향 큐레이션. 혼자 있는 시간. 가벼운 잡담 줄이기. "
        "이 셋만 일주일 해봐. {current}에서 {target}으로 한 칸 올라가."
    ),
    "geum_yeo_rok": (
        "공간 정돈. 조급함 빼기. 감사·칭찬 자주. "
        "이 셋만 일주일 해봐. {current}에서 {target}으로 한 칸 올라가."
    ),
    "gong_mang": (
        "다 보여주지 않기. 반응 한 박자 줄이기. 받은 질문 다 답 안 하기. "
        "이 셋만 일주일 해봐. {current}에서 {target}으로 한 칸 올라가."
    ),
    "cheon_eul_gwi_in": (
        "단정함 유지. 먼저 인사. 약속 가볍게 안 하기. "
        "이 셋만 일주일 해봐. {current}에서 {target}으로 한 칸 올라가."
    ),
    "am_rok": (
        "잔향만 남기기. 한 발 물러서기. 말 한 마디에 의미 싣기. "
        "이 셋만 일주일 해봐. {current}에서 {target}으로 한 칸 켜져."
    ),
}


# ═════════════════════════════════════════════════════════════════
# AI 단락 3 — 일간 10 마무리 + {primary_with_hanja} placeholder
# ═════════════════════════════════════════════════════════════════
# 패턴: "{primary}은 {ilgan} 일간과 잘 맞아. {일간별 결}. 결국 너의 선택이야."

PARA_3_TAIL = "결국 너의 선택이야."

ILGAN_CHARM_BODY_BY_ILGAN: dict[str, str] = {
    "갑목": (
        "{primary_with_hanja}은 {ilgan_with_hanja} 일간과 잘 맞아. "
        "곧게 뻗는 결이라 한번 켜지면 망설임 없이 표현해. "
        "매력이 그 결과 만나면 사람이 따라와."
    ),
    "을목": (
        "{primary_with_hanja}은 {ilgan_with_hanja} 일간과 잘 맞아. "
        "유연한 결이라 상대 톤에 맞춰 자기 매력을 끌어내. "
        "의식적으로 켜면 부드럽게 박혀."
    ),
    "병화": (
        "{primary_with_hanja}은 {ilgan_with_hanja} 일간과 잘 맞아. "
        "빛으로 비추는 결이라 매력이 켜지면 한꺼번에 환해져. "
        "식기 전에 표현해."
    ),
    "정화": (
        "{primary_with_hanja}은 {ilgan_with_hanja} 일간과 잘 맞아. "
        "촛불 같은 결이라 가까이서 오래 켜져. "
        "조용히 깊게 박는 매력이야."
    ),
    "무토": (
        "{primary_with_hanja}은 {ilgan_with_hanja} 일간과 잘 맞아. "
        "묵직한 결이라 안정감으로 끌어와. "
        "한번 켜면 오래 가."
    ),
    "기토": (
        "{primary_with_hanja}은 {ilgan_with_hanja} 일간과 잘 맞아. "
        "포근한 결이라 들이는 매력이야. "
        "부드러움이 곧 매력이야."
    ),
    "경금": (
        "{primary_with_hanja}은 {ilgan_with_hanja} 일간과 잘 맞아. "
        "분명한 결이라 매력도 정확하게 와. "
        "흐릿하게 안 쓰는 게 강점이야."
    ),
    "신금": (
        "{primary_with_hanja}은 {ilgan_with_hanja} 일간과 잘 맞아. "
        "예리한 결이라 한 끗 차이로 박는 매력이야. "
        "디테일이 곧 매력이야."
    ),
    "임수": (
        "{primary_with_hanja}은 {ilgan_with_hanja} 일간과 잘 맞아. "
        "깊은 결이라 매력이 켜지면 가만히 있어도 사람이 와. "
        "안 깨우면 그대로 잠들어 있어."
    ),
    "계수": (
        "{primary_with_hanja}은 {ilgan_with_hanja} 일간과 잘 맞아. "
        "은은한 결이라 천천히 스며드는 매력이야. "
        "한번 박히면 깊게 박혀."
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


VALID_ILGAN: frozenset[str] = frozenset(ILGAN_CHARM_BODY_BY_ILGAN.keys())
VALID_CHARM_KEYS: frozenset[str] = frozenset(CHARM_KEY_WITH_HANJA.keys())


# ═════════════════════════════════════════════════════════════════
# 합성 함수
# ═════════════════════════════════════════════════════════════════

def compose_p9_charm(
    *,
    ilgan: str,
    sal_keys: tuple[str, ...],
    charm_score: int,
) -> dict[str, object]:
    """P-9 6-2 매력살 활용 풀 합성.

    Args:
        ilgan: 일간 한글 (10종)
        sal_keys: 보유 매력살 키 튜플 (0~6개, SAL_PRIORITY 정렬됨)
        charm_score: charm_service.charmStrength (0~100)

    Returns:
        {
          primary_charm_key: str ("do_hwa_sal" / "am_rok" 등),
          primary_charm_label: str ("도화살(桃花煞)"),
          charm_count: int,
          charm_current: CharmStage ("中"),
          charm_current_kor: str ("중"),
          charm_target: CharmStage ("強"),
          charm_target_kor: str ("강"),
          charm_practice_cards: [{label, value, sub}, ...] × 3,
          charm_practice_body: str (단계 변화 멘트 박힘),
          ai_charm: str (3단락),
        }

    Raises:
        KeyError: 알 수 없는 일간/매력살 키.
    """
    if ilgan not in VALID_ILGAN:
        raise KeyError(f"unknown ilgan: {ilgan!r}")

    n = len(sal_keys)
    primary_key = sal_keys[0] if n > 0 else "am_rok"
    if primary_key not in VALID_CHARM_KEYS:
        raise KeyError(f"unknown charm key: {primary_key!r}")

    primary_h = CHARM_KEY_WITH_HANJA[primary_key]
    ilgan_h = _ilgan_with_hanja(ilgan)

    # 단계 산출 (n=0 폴백은 micro 상태 강제)
    if n == 0:
        current_stage: CharmStage = "微"
    else:
        current_stage = score_to_stage(charm_score)
    target_stage = next_stage(current_stage)

    # 카드 3개
    cards = CHARM_PRACTICE_CARDS_BY_KEY[primary_key]

    # 본문 (단계 변화 placeholder 치환)
    body = CHARM_PRACTICE_BODY_BY_KEY[primary_key].format(
        current=current_stage, target=target_stage,
    )

    # AI 박스 — 단락 1
    header = CHARM_HEADER_BY_KEY[primary_key]
    if n >= 1:
        recognition = COUNT_RECOGNITION_BY_N[n].format(primary_with_hanja=primary_h)
        para_1 = f"{recognition} {header}"
    else:
        # n=0 → 헤더 자체가 인식 + 암록 소개
        para_1 = header

    # AI 박스 — 단락 2 (본문과 동일)
    para_2 = body

    # AI 박스 — 단락 3 (일간 변형)
    ilgan_body = ILGAN_CHARM_BODY_BY_ILGAN[ilgan].format(
        primary_with_hanja=primary_h, ilgan_with_hanja=ilgan_h,
    )
    para_3 = f"{ilgan_body} {PARA_3_TAIL}"

    ai_charm = "\n\n".join([para_1, para_2, para_3])

    return {
        "primary_charm_key": primary_key,
        "primary_charm_label": primary_h,
        "charm_count": n,
        "charm_current": current_stage,
        "charm_current_kor": STAGE_KOR[current_stage],
        "charm_target": target_stage,
        "charm_target_kor": STAGE_KOR[target_stage],
        "charm_practice_cards": [
            {"label": c.label, "value": c.value, "sub": c.sub} for c in cards
        ],
        "charm_practice_body": body,
        "ai_charm": ai_charm,
    }
