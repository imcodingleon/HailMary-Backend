"""도윤 P-4 2-3 비호환 — AI prompt builder + validate."""

from __future__ import annotations

_SYSTEM_PROMPT = """\
당신은 도화선 캐릭터 한도윤 — 사주 데이터 분석가.

[페르소나]
- 존댓말, "{user_name}님" 호명 (마지막 단락에서 1회)
- 어휘: 비호환 프로파일, 인상 점수, 감정 주파수, 격차, 케이스 — P-4 시그니처
- 따뜻함 절제, 숫자 뒤 한 줄 정리

[금지어]
- 신안, 기운, 살, 거머리, 결, 매듭, 명줄, 뿌리 (강연우 톤 X)

[사실값 보존 — 절대 변경 금지]
- 사용자 이름 ({user_name})
- 일간 ({ilgan_full})
- 키 분포 ({height_distribution_pct})
- 첫인상 / 6개월 / 격차 ({impression_first} / {impression_6m} / {impression_gap})
- 동일 비호환 사례 비율 ({common_signal_pct})

[구성] 4 단락, 단락 사이 빈 줄 1개, 총 320~520자
1. 데이터 도입 (1문장)
2. 외형 데이터 — 키 분포, 체형, 얼굴상, 이목구비 (2~3문장)
3. 인상 점수 격차 분석 (2~3문장)
4. {ilgan_full} 일간 주파수 불일치 + 거리 두기 + {user_name}님 호명 (3문장)

[출력] 4단락 텍스트만. 메타·헤더 금지.
"""


_USER_PROMPT_TPL = """\
다음 사용자의 P-4 비호환 프로파일 분석을 작성해주세요.

[보존해야 하는 사실값 — 모두 출력에 포함]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- height_distribution_pct: {height_distribution_pct}
- impression_first: {impression_first}
- impression_6m: {impression_6m}
- impression_gap: {impression_gap}
- common_signal_pct: {common_signal_pct}

[룰 합성 기반 텍스트 — 기반으로 표현 다양화. 사실값 한 글자도 바꾸지 마세요.]

{rule_text}

[요청]
위 사실값 모두 포함하는 4단락 320~520자 텍스트를 작성하세요.
"""


_REQUIRED_KEYS = {
    "user_name",
    "ilgan_full",
    "ilgan_hanja",
    "height_distribution_pct",
    "impression_first",
    "impression_6m",
    "impression_gap",
    "emotional_volatility_multiplier",
    "common_signal_pct",
    "rule_text",
}


def build_p4_akyon_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(**{k: facts[k] for k in (
        "user_name", "ilgan_full", "height_distribution_pct",
        "impression_first", "impression_6m", "impression_gap", "common_signal_pct",
    )})
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in (
        "user_name", "ilgan_full", "height_distribution_pct",
        "impression_first", "impression_6m", "impression_gap",
        "common_signal_pct", "rule_text",
    )})
    return system, user


_MIN_LENGTH = 290
_MAX_LENGTH = 600


def validate_p4_akyon(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    if facts["user_name"] not in text:
        return False, "user_name missing"
    if facts["ilgan_full"] not in text:
        return False, "ilgan_full missing"
    for k in ("height_distribution_pct", "impression_first", "impression_6m",
              "impression_gap", "common_signal_pct"):
        if facts[k] not in text:
            return False, f"{k} missing: {facts[k]!r}"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 3:
        return False, f"paragraph structure invalid: {paragraph_breaks} (expected 3)"
    return True, ""
