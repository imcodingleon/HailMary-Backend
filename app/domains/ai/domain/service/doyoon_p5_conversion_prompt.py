"""도윤 P-5 3-2 전환율 — AI prompt + validate."""

from __future__ import annotations

_SYSTEM_PROMPT = """\
당신은 도화선 캐릭터 한도윤 — 사주 데이터 분석가.

[페르소나]
- 존댓말, "{user_name}님" 호명 (단락 2 또는 3에서)
- 어휘: 전환율, 단계, 격차, 효율
- 시각화 보조 톤

[금지어]
- 신안, 기운, 살, 거머리, 결, 매듭, 명줄, 뿌리

[사실값 보존]
- {user_name}, {ilgan_full}
- 4단계 % ({step_1_pct} → {step_2_pct} → {step_3_pct} → {step_4_pct})
- 두 번째 만남 배수 ({second_meeting_multiplier})
- 최종 호감도 격차 ({final_gap_pct})

[구성] 3 단락, 총 180~330자
1. 4단계 전환율 도입
2. 두 번째 만남 효율 + 격차
3. 처방 + {user_name}님 호명

[출력] 3단락만.
"""

_USER_PROMPT_TPL = """\
[사실값]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- step_1_pct: {step_1_pct}
- step_2_pct: {step_2_pct}
- step_3_pct: {step_3_pct}
- step_4_pct: {step_4_pct}
- second_meeting_multiplier: {second_meeting_multiplier}
- final_gap_pct: {final_gap_pct}

[기반]
{rule_text}

[요청] 3단락 180~330자.
"""

_REQUIRED_KEYS = {
    "user_name", "ilgan_full",
    "step_1_pct", "step_2_pct", "step_3_pct", "step_4_pct",
    "second_meeting_multiplier", "final_gap_pct", "rule_text",
}


def build_p5_conversion_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(**{k: facts[k] for k in _REQUIRED_KEYS if k != "rule_text"})
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 160
_MAX_LENGTH = 400


def validate_p5_conversion(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    if facts["user_name"] not in text:
        return False, "user_name missing"
    # 4단계 % 중 최소 3개 포함
    pcts_found = sum(1 for k in ("step_1_pct", "step_2_pct", "step_3_pct", "step_4_pct") if facts[k] in text)
    if pcts_found < 3:
        return False, f"conversion steps insufficient: {pcts_found}/4"
    if facts["second_meeting_multiplier"] not in text:
        return False, "second_meeting_multiplier missing"
    if facts["final_gap_pct"] not in text:
        return False, "final_gap_pct missing"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 2:
        return False, f"paragraph structure invalid: {paragraph_breaks}"
    return True, ""
