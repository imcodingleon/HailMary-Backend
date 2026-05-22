"""도윤 P-7 4-3 결말 시나리오 — AI prompt + validate."""

from __future__ import annotations

_SYSTEM_PROMPT = """\
당신은 도화선 캐릭터 한도윤 — 사주 데이터 분석가.

[페르소나]
- 존댓말, "{user_name}님" 호명 (단락 3, 5에서)
- 어휘: 시나리오, 기대값, 권장 분기, 시간 비용
- Ch4 클로징 — 정서적 클라이맥스 톤

[금지어]
- 신안, 기운, 살, 거머리, 결, 매듭, 명줄, 뿌리

[사실값 보존]
- {user_name}, {ilgan_full}
- 3 시나리오 6개월 후 % ({sc1_six_month_pct} / {sc2_six_month_pct} / {sc3_six_month_pct})
- initiative_multiplier {initiative_multiplier}
- wait_cost_multiplier {wait_cost_multiplier}
- expected_value_ratio {expected_value_ratio}

[구성] 5 단락, 총 380~520자
1. 도입 (1문장)
2. 시나리오 1 분석
3. 시나리오 2 분석 (권장 분기 + {user_name}님 호명)
4. 시나리오 3 분석
5. 클로징 + {user_name}님 호명 + 기대값 비교

[출력] 5단락만.
"""

_USER_PROMPT_TPL = """\
[사실값]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- sc1_six_month_pct: {sc1_six_month_pct}
- sc2_six_month_pct: {sc2_six_month_pct}
- sc3_six_month_pct: {sc3_six_month_pct}
- initiative_multiplier: {initiative_multiplier}
- wait_cost_multiplier: {wait_cost_multiplier}
- expected_value_ratio: {expected_value_ratio}

[기반]
{rule_text}

[요청] 5단락 380~520자.
"""

_REQUIRED_KEYS = {
    "user_name", "ilgan_full",
    "sc1_six_month_pct", "sc2_six_month_pct", "sc3_six_month_pct",
    "initiative_multiplier", "wait_cost_multiplier", "expected_value_ratio",
    "rule_text",
}


def build_p7_ending_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(**{k: facts[k] for k in _REQUIRED_KEYS if k != "rule_text"})
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 340
_MAX_LENGTH = 600


def validate_p7_ending(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    for k in ("user_name",
              "sc1_six_month_pct", "sc2_six_month_pct", "sc3_six_month_pct",
              "initiative_multiplier", "wait_cost_multiplier", "expected_value_ratio"):
        if facts[k] not in text:
            return False, f"{k} missing: {facts[k]!r}"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 4:
        return False, f"paragraph structure invalid: {paragraph_breaks} (expected 4)"
    return True, ""
