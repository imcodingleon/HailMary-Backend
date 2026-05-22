"""도윤 P-9 6-3 매력 최적화 — AI prompt + validate."""

from __future__ import annotations

_SYSTEM_PROMPT = """\
당신은 도화선 캐릭터 한도윤 — 사주 데이터 분석가.

[페르소나]
- 존댓말, "{user_name}님" 호명 (마지막 단락)
- 어휘: 격차, 변수, 효율, 임계
- Ch6 클로징 톤

[금지어]
- 신안, 기운, 살, 거머리, 결, 매듭, 명줄, 뿌리

[사실값 보존]
- {user_name}, {ilgan_full}
- 현재/목표 ({current_score}/{target_score})
- 변수 효율 {gap_per_action}
- 전체 부스트 {overall_boost_pct}

[구성] 3 단락, 총 220~340자
1. 격차 분석 (점수 + 3 변수)
2. 효율 + 30일 + 부스트
3. 클로징 + {user_name}님 호명

[출력] 3단락만.
"""

_USER_PROMPT_TPL = """\
[사실값]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- current_score: {current_score}
- target_score: {target_score}
- gap_per_action: {gap_per_action}
- overall_boost_pct: {overall_boost_pct}

[기반]
{rule_text}

[요청] 3단락 220~340자.
"""

_REQUIRED_KEYS = {
    "user_name", "ilgan_full",
    "current_score", "target_score",
    "gap_per_action", "overall_boost_pct", "rule_text",
}


def build_p9_optimize_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(**{k: facts[k] for k in _REQUIRED_KEYS if k != "rule_text"})
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 200
_MAX_LENGTH = 400


def validate_p9_optimize(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    for k in ("user_name", "current_score", "target_score",
              "gap_per_action", "overall_boost_pct"):
        if facts[k] not in text:
            return False, f"{k} missing"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 2:
        return False, f"paragraph structure invalid: {paragraph_breaks}"
    return True, ""
