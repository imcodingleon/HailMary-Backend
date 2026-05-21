"""도윤 P-5 3-3 호감 유발 — AI prompt + validate."""

from __future__ import annotations

_SYSTEM_PROMPT = """\
당신은 도화선 캐릭터 한도윤 — 사주 데이터 분석가.

[페르소나]
- 존댓말, "{user_name}님" 호명 (단락 2~3에서)
- 어휘: 변수 점수, 강점/약점, 통제 영역, 효율
- 압축적 클로징 톤

[금지어]
- 신안, 기운, 살, 거머리, 결, 매듭, 명줄, 뿌리

[사실값 보존]
- {user_name}, {ilgan_full}
- 4 변수 점수 ({meter_1_name} {meter_1_value} / {meter_2_name} {meter_2_value} /
  {meter_3_name} {meter_3_value} / {meter_4_name} {meter_4_value})
- 약점 축 2개 ({weakness_axis_1} / {weakness_axis_2})
- 호감 부스트 ({appeal_boost_pct})

[구성] 3 단락, 총 220~380자
1. 4 변수 점수 정리
2. 강점/약점 명시
3. 약점 보완 효율 + 처방

[출력] 3단락만.
"""

_USER_PROMPT_TPL = """\
[사실값]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- meter_1: {meter_1_name} {meter_1_value}
- meter_2: {meter_2_name} {meter_2_value}
- meter_3: {meter_3_name} {meter_3_value}
- meter_4: {meter_4_name} {meter_4_value}
- weakness_axis_1: {weakness_axis_1}
- weakness_axis_2: {weakness_axis_2}
- appeal_boost_pct: {appeal_boost_pct}

[기반]
{rule_text}

[요청] 3단락 220~380자.
"""

_REQUIRED_KEYS = {
    "user_name", "ilgan_full",
    "meter_1_name", "meter_1_value",
    "meter_2_name", "meter_2_value",
    "meter_3_name", "meter_3_value",
    "meter_4_name", "meter_4_value",
    "weakness_axis_1", "weakness_axis_2", "appeal_boost_pct", "rule_text",
}


def build_p5_appeal_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(**{k: facts[k] for k in _REQUIRED_KEYS if k != "rule_text"})
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 200
_MAX_LENGTH = 450


def validate_p5_appeal(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    if facts["user_name"] not in text:
        return False, "user_name missing"
    # 4 변수 이름 + 점수 모두 포함
    for k in ("meter_1_name", "meter_2_name", "meter_3_name", "meter_4_name",
              "meter_1_value", "meter_2_value", "meter_3_value", "meter_4_value",
              "weakness_axis_1", "weakness_axis_2", "appeal_boost_pct"):
        if facts[k] not in text:
            return False, f"{k} missing: {facts[k]!r}"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 2:
        return False, f"paragraph structure invalid: {paragraph_breaks}"
    return True, ""
