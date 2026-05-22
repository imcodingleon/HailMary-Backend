"""도윤 P-9 6-1 오행 보완 — AI prompt + validate."""

from __future__ import annotations

_SYSTEM_PROMPT = """\
당신은 도화선 캐릭터 한도윤 — 사주 데이터 분석가.

[페르소나]
- 존댓말, "{user_name}님" 호명 (마지막 단락 1회)
- 어휘: 보완, 반응성, 상호작용, 누적 효과
- Ch6 오프닝 톤

[금지어]
- 신안, 기운, 살, 거머리, 결, 매듭, 명줄, 뿌리

[사실값 보존]
- {user_name}, {ilgan_full}({ilgan_hanja})
- 오행 보완 {ohang_lack}({ohang_lack_hanja})
- 보완 효율 {boost_pct} / 반응 배수 {response_multiplier} / 최대 부스트 {max_boost_pct}

[구성] 3 단락, 총 220~340자
1. 일간 반응성 분석
2. 30일 누적 효과
3. {user_name}님 시작 권장

[출력] 3단락만.
"""

_USER_PROMPT_TPL = """\
[사실값]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- ilgan_hanja: {ilgan_hanja}
- ohang_lack: {ohang_lack}
- ohang_lack_hanja: {ohang_lack_hanja}
- boost_pct: {boost_pct}
- response_multiplier: {response_multiplier}
- max_boost_pct: {max_boost_pct}

[기반]
{rule_text}

[요청] 3단락 220~340자.
"""

_REQUIRED_KEYS = {
    "user_name", "ilgan_full", "ilgan_hanja",
    "ohang_lack", "ohang_lack_hanja",
    "boost_pct", "response_multiplier", "max_boost_pct", "rule_text",
}


def build_p9_ohang_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(**{k: facts[k] for k in _REQUIRED_KEYS if k != "rule_text"})
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 200
_MAX_LENGTH = 400


def validate_p9_ohang(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    for k in ("user_name", "ohang_lack_hanja", "boost_pct",
              "response_multiplier", "max_boost_pct"):
        if facts[k] not in text:
            return False, f"{k} missing"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 2:
        return False, f"paragraph structure invalid: {paragraph_breaks}"
    return True, ""
