"""도윤 P-5 3-1 매력 지수 — AI prompt + validate."""

from __future__ import annotations

_SYSTEM_PROMPT = """\
당신은 도화선 캐릭터 한도윤 — 사주 데이터 분석가.

[페르소나]
- 존댓말, "{user_name}님" 호명 (마지막 단락 1회)
- 어휘: 측정값, 강점 축, 의식/무의식 발현, 잠재력
- 따뜻함 절제

[금지어]
- 신안, 기운, 살, 거머리, 결, 매듭, 명줄, 뿌리

[사실값 보존]
- {user_name}, {ilgan_full}
- 상위 {charm_pct}, 강점 축 {strength_axis_1}/{strength_axis_2} (평균 대비 {strength_multiplier})
- 의식 vs 무의식 차이 {conscious_gap_multiplier}

[구성] 3 단락, 총 280~430자
1. 상위 % + 가치 부각
2. 강점 2축 + 배수
3. 의식 발현 차이 + 잠재력 호명

[출력] 3단락만.
"""

_USER_PROMPT_TPL = """\
[사실값]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- charm_pct: {charm_pct}
- strength_axis_1: {strength_axis_1}
- strength_axis_2: {strength_axis_2}
- strength_multiplier: {strength_multiplier}
- conscious_gap_multiplier: {conscious_gap_multiplier}

[기반]
{rule_text}

[요청] 3단락 280~430자.
"""

_REQUIRED_KEYS = {
    "user_name", "ilgan_full", "charm_pct",
    "strength_axis_1", "strength_axis_2", "strength_multiplier",
    "conscious_gap_multiplier", "rule_text",
}


def build_p5_charm_index_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(**{k: facts[k] for k in _REQUIRED_KEYS if k != "rule_text"})
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 250
_MAX_LENGTH = 500


def validate_p5_charm_index(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    for k in ("user_name", "charm_pct", "strength_axis_1", "strength_axis_2",
              "strength_multiplier", "conscious_gap_multiplier"):
        if facts[k] not in text:
            return False, f"{k} missing: {facts[k]!r}"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 2:
        return False, f"paragraph structure invalid: {paragraph_breaks}"
    return True, ""
