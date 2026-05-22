"""도윤 P-8 5-1 ai_intro — AI prompt + validate."""

from __future__ import annotations

_SYSTEM_PROMPT = """\
당신은 도화선 캐릭터 한도윤 — 사주 데이터 분석가.

[페르소나]
- 존댓말, "{user_name}님" 호명은 사용하지 않음 (P-8은 타임라인 보조 톤)
- 어휘: 접촉 확률, 피크 구간, ROI, 충전 구간
- 12개월 타임라인 보조 — 짧고 분석적

[금지어]
- 신안, 기운, 살, 거머리, 결, 매듭, 명줄, 뿌리

[사실값 보존]
- 일간 {ilgan_full}({ilgan_hanja})
- 피크 라벨 2개 {peak_1_label} / {peak_2_label}

[구성] 3단락, 총 200~340자
1. 도입 (1~2문장)
2. 피크 구간 2곳 + 2.3배 배수
3. 일간 흐름 결 (ROI)

[출력] 3단락만.
"""

_USER_PROMPT_TPL = """\
[사실값]
- ilgan_full: {ilgan_full}
- ilgan_hanja: {ilgan_hanja}
- peak_1_label: {peak_1_label}
- peak_2_label: {peak_2_label}
- user_name: {user_name}

[기반]
{rule_text}

[요청] 3단락 200~340자.
"""

_REQUIRED_KEYS = {
    "user_name", "ilgan_full", "ilgan_hanja",
    "peak_1_label", "peak_2_label", "rule_text",
}


def build_p8_intro_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(**{k: facts[k] for k in _REQUIRED_KEYS if k != "rule_text"})
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 170
_MAX_LENGTH = 400


def validate_p8_intro(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    for k in ("peak_1_label", "peak_2_label"):
        if facts[k] not in text:
            return False, f"{k} missing: {facts[k]!r}"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 2:
        return False, f"paragraph structure invalid: {paragraph_breaks}"
    return True, ""
