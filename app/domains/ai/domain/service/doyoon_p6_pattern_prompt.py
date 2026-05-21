"""도윤 P-6 4-2 행동 패턴 — AI prompt + validate."""

from __future__ import annotations

_SYSTEM_PROMPT = """\
당신은 도화선 캐릭터 한도윤 — 사주 데이터 분석가.

[페르소나]
- 존댓말, "{user_name}님" 호명 (마지막 단락)
- 어휘: 행동 데이터, 심리 추정값, 망설임, 단절 의지, 매칭 효율

[금지어]
- 신안, 기운, 살, 거머리, 결, 매듭, 명줄, 뿌리

[사실값 보존]
- {user_name}, {ilgan_full}
- 답장 길이 {answer_length_multiplier}
- 망설임 {hesitation_pct}, 단절 의지 {cut_intent_pct}
- 해소 확률 {resolution_pct}
- 사용자 먼저 시 매칭 {initiative_multiplier}

[구성] 4단락, 총 280~440자
1. 도입
2. 연락 빈도 분석 + 답장 길이
3. 심리 추정값 (망설임/단절)
4. 매칭 전략 + {user_name}님 호명

[출력] 4단락만.
"""

_USER_PROMPT_TPL = """\
[사실값]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- answer_length_multiplier: {answer_length_multiplier}
- hesitation_pct: {hesitation_pct}
- cut_intent_pct: {cut_intent_pct}
- resolution_pct: {resolution_pct}
- initiative_multiplier: {initiative_multiplier}

[기반]
{rule_text}

[요청] 4단락 280~440자.
"""

_REQUIRED_KEYS = {
    "user_name", "ilgan_full",
    "answer_length_multiplier", "hesitation_pct", "cut_intent_pct",
    "resolution_pct", "initiative_multiplier", "rule_text",
}


def build_p6_pattern_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(**{k: facts[k] for k in _REQUIRED_KEYS if k != "rule_text"})
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 240
_MAX_LENGTH = 500


def validate_p6_pattern(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    for k in ("user_name", "answer_length_multiplier", "hesitation_pct",
              "cut_intent_pct", "resolution_pct", "initiative_multiplier"):
        if facts[k] not in text:
            return False, f"{k} missing"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks not in (2, 3):
        return False, f"paragraph structure invalid: {paragraph_breaks}"
    return True, ""
