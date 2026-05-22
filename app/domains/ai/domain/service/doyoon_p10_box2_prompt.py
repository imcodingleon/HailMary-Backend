"""도윤 P-10 box2 — 사용자 알고싶은 영역 분석 AI prompt + validate."""

from __future__ import annotations

_SYSTEM_PROMPT = """\
당신은 도화선 캐릭터 한도윤 — 사주 데이터 분석가.

[페르소나]
- 존댓말, "{user_name}님" 호명 (단락 1, 3)
- 어휘: 질문, 측정값, 변수, 답할 수 있는 영역
- 짧고 분석적

[금지어]
- 신안, 기운, 살, 거머리, 결, 매듭, 명줄, 뿌리
- "네가" 반말 금지

[사실값 보존]
- {user_name}, {ilgan_full}({ilgan_hanja})
- 질문 영역 라벨: {step2_labels}
- 오행 보완 {ohang_lack}({ohang_lack_hanja})

[구성] 3 단락, 총 280~430자
1. 질문 영역 분류
2. 일간 표본 + 측정 가능 영역
3. 데이터 한계 + {user_name}님 클로징

[출력] 3단락만.
"""

_USER_PROMPT_TPL = """\
[사실값]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- ilgan_hanja: {ilgan_hanja}
- step2_labels: {step2_labels}
- ohang_lack: {ohang_lack}
- ohang_lack_hanja: {ohang_lack_hanja}

[기반]
{rule_text}

[요청] 3단락 280~430자.
"""

_REQUIRED_KEYS = {
    "user_name", "ilgan_full", "ilgan_hanja",
    "step2_labels", "ohang_lack", "ohang_lack_hanja", "rule_text",
}


def build_p10_box2_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(**{k: facts[k] for k in _REQUIRED_KEYS if k != "rule_text"})
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 250
_MAX_LENGTH = 500


def validate_p10_box2(text: str, facts: dict[str, str]) -> tuple[bool, str]:
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
