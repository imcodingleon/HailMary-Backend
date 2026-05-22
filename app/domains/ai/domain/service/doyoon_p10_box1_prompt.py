"""도윤 P-10 box1 — 사용자 입력 상황 분석 AI prompt + validate."""

from __future__ import annotations

_SYSTEM_PROMPT = """\
당신은 도화선 캐릭터 한도윤 — 사주 데이터 분석가.

[페르소나]
- 존댓말, "{user_name}님" 호명 (단락 1, 3 자연스러운 분포)
- 어휘: 입력값, 변수, 활성도, 분류, 측정
- 짧고 분석적

[금지어]
- 신안, 기운, 살, 거머리, 결, 매듭, 명줄, 뿌리 (강연우 톤 X)
- "네가" 반말 금지 — 존댓말 일관

[사실값 보존]
- {user_name}, {ilgan_full}({ilgan_hanja})
- 입력 상황 라벨: {step1_labels}

[구성] 3 단락, 총 250~400자
1. 입력값 정리 + {user_name}님 호명
2. 일간 표본 분석 + 활성도 수치
3. 다음 행동 권장 + 클로징

[출력] 3단락만. 메타·헤더 금지.
"""

_USER_PROMPT_TPL = """\
[사실값]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- ilgan_hanja: {ilgan_hanja}
- step1_labels: {step1_labels}

[기반]
{rule_text}

[요청] 3단락 250~400자.
"""

_REQUIRED_KEYS = {
    "user_name", "ilgan_full", "ilgan_hanja", "step1_labels", "rule_text",
}


def build_p10_box1_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(**{k: facts[k] for k in _REQUIRED_KEYS if k != "rule_text"})
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 220
_MAX_LENGTH = 480


def validate_p10_box1(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    if facts["user_name"] not in text:
        return False, "user_name missing"
    if facts["ilgan_full"] not in text:
        return False, "ilgan_full missing"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 2:
        return False, f"paragraph structure invalid: {paragraph_breaks}"
    return True, ""
