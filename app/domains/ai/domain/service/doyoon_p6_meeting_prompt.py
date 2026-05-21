"""도윤 P-6 4-1 만남 시나리오 — AI prompt + validate."""

from __future__ import annotations

_SYSTEM_PROMPT = """\
당신은 도화선 캐릭터 한도윤 — 사주 데이터 분석가.

[페르소나]
- 존댓말, "{user_name}님" 호명 (마지막 단락)
- 어휘: 접촉 시나리오, 환경, 호감 전환율, 효율

[금지어]
- 신안, 기운, 살, 거머리, 결, 매듭, 명줄, 뿌리

[사실값 보존]
- {user_name}, {ilgan_full}
- 기존 동선 {existing_path_multiplier}
- 첫 만남 낮은 임팩트 {low_impact_pct}
- 두 번째 접촉 {second_contact_multiplier}

[구성] 3단락, 총 280~440자
1. 만남 환경 데이터
2. 첫 접촉 패턴
3. 두 번째 접촉 전략 + {user_name}님 호명

[출력] 3단락만.
"""

_USER_PROMPT_TPL = """\
[사실값]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- existing_path_multiplier: {existing_path_multiplier}
- low_impact_pct: {low_impact_pct}
- second_contact_multiplier: {second_contact_multiplier}

[기반]
{rule_text}

[요청] 3단락 280~440자.
"""

_REQUIRED_KEYS = {
    "user_name", "ilgan_full",
    "existing_path_multiplier", "low_impact_pct", "second_contact_multiplier",
    "rule_text",
}


def build_p6_meeting_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(**{k: facts[k] for k in _REQUIRED_KEYS if k != "rule_text"})
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 240
_MAX_LENGTH = 500


def validate_p6_meeting(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    for k in ("user_name", "existing_path_multiplier", "low_impact_pct",
              "second_contact_multiplier"):
        if facts[k] not in text:
            return False, f"{k} missing"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 2:
        return False, f"paragraph structure invalid: {paragraph_breaks}"
    return True, ""
