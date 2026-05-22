"""도윤 P-9 6-2 리스크 변수 제거 — AI prompt + validate."""

from __future__ import annotations

_SYSTEM_PROMPT = """\
당신은 도화선 캐릭터 한도윤 — 사주 데이터 분석가.

[페르소나]
- 존댓말, "{user_name}님" 호명 (단락 2)
- 어휘: 리스크, 우선순위, 임팩트, 수렴
- 표준 톤

[금지어]
- 신안, 기운, 살, 거머리, 결, 매듭, 명줄, 뿌리

[사실값 보존]
- {user_name}, {ilgan_full}
- 즉시 변수 임팩트 {immediate_impact_pct}
- 합산 수렴 배수 {combined_multiplier} / 합산 값 {combined_value}

[구성] 2 단락, 총 170~330자
1. 즉시 변수 임팩트
2. 합산 효과 + {user_name}님 호명

[출력] 2단락만.
"""

_USER_PROMPT_TPL = """\
[사실값]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- immediate_impact_pct: {immediate_impact_pct}
- combined_multiplier: {combined_multiplier}
- combined_value: {combined_value}

[기반]
{rule_text}

[요청] 2단락 170~330자.
"""

_REQUIRED_KEYS = {
    "user_name", "ilgan_full",
    "immediate_impact_pct", "combined_multiplier", "combined_value",
    "rule_text",
}


def build_p9_risk_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(**{k: facts[k] for k in _REQUIRED_KEYS if k != "rule_text"})
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 150
_MAX_LENGTH = 400


def validate_p9_risk(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    for k in ("user_name", "immediate_impact_pct", "combined_multiplier", "combined_value"):
        if facts[k] not in text:
            return False, f"{k} missing"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 1:
        return False, f"paragraph structure invalid: {paragraph_breaks}"
    return True, ""
