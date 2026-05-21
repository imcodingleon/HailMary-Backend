"""도윤 P-3 2-2 반복 패턴 — AI prompt builder + validate."""

from __future__ import annotations

_SYSTEM_PROMPT = """\
당신은 도화선 캐릭터 한도윤 — 사주 데이터 분석가.

[페르소나]
- 존댓말, "{user_name}님" 호명 (단락 1에서 1회)
- 어휘: 패턴, 발생률, 단계, 안정성, 통제 — P-3 패턴 시그니처
- 따뜻함 절제, 숫자 뒤 한 줄 정리

[금지어]
- 신안, 기운, 살, 거머리, 결, 매듭, 명줄, 뿌리 (강연우 톤 X)

[사실값 보존 — 절대 변경 금지]
- 사용자 이름 ({user_name})
- 일간 ({ilgan_full})
- 패턴 키워드 3종 ({pattern_1_keyword} / {pattern_2_keyword} / {pattern_3_keyword})
- 패턴 발생률 3종 ({pattern_1_pct} / {pattern_2_pct} / {pattern_3_pct})
- 안정성 부스트 ({stability_boost_pct})

[구성] 4 단락, 총 230~400자
1. 도입 (1문장)
2. 1단계 패턴 분석
3. 2단계 + 3단계 패턴 분석
4. {ilgan_full} 일간 특유 + 안정성 부스트

[출력] 4단락 텍스트만. 메타·헤더 금지.
"""


_USER_PROMPT_TPL = """\
다음 사용자의 P-3 반복 실수 패턴 분석을 작성해주세요.

[보존해야 하는 사실값 — 모두 출력에 포함]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- pattern_1_keyword: {pattern_1_keyword}
- pattern_1_pct: {pattern_1_pct}
- pattern_2_keyword: {pattern_2_keyword}
- pattern_2_pct: {pattern_2_pct}
- pattern_3_keyword: {pattern_3_keyword}
- pattern_3_pct: {pattern_3_pct}
- stability_boost_pct: {stability_boost_pct}

[룰 합성 기반 텍스트 — 기반으로 표현 다양화. 사실값 한 글자도 바꾸지 마세요.]

{rule_text}

[요청]
위 사실값 모두 포함하는 4단락 230~400자 텍스트를 작성하세요.
"""


_REQUIRED_KEYS = {
    "user_name",
    "ilgan_full",
    "pattern_1_keyword",
    "pattern_1_pct",
    "pattern_2_keyword",
    "pattern_2_pct",
    "pattern_3_keyword",
    "pattern_3_pct",
    "stability_boost_pct",
    "rule_text",
}


def build_p3_pattern_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(**{k: facts[k] for k in _REQUIRED_KEYS if k != "rule_text"})
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 200
_MAX_LENGTH = 500


def validate_p3_pattern(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    if facts["user_name"] not in text:
        return False, "user_name missing"
    if facts["ilgan_full"] not in text:
        return False, f"ilgan_full missing: {facts['ilgan_full']!r}"
    for k in ("pattern_1_keyword", "pattern_2_keyword", "pattern_3_keyword",
              "pattern_1_pct", "pattern_2_pct", "pattern_3_pct",
              "stability_boost_pct"):
        if facts[k] not in text:
            return False, f"{k} missing: {facts[k]!r}"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks not in (2, 3):
        return False, f"paragraph structure invalid: {paragraph_breaks} (expected 2 or 3)"
    return True, ""
