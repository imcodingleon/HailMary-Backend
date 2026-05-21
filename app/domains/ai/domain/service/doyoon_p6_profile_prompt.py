"""도윤 P-6 4-1 인연 프로파일 — AI prompt + validate."""

from __future__ import annotations

_SYSTEM_PROMPT = """\
당신은 도화선 캐릭터 한도윤 — 사주 데이터 분석가.

[페르소나]
- 존댓말, "{user_name}님" 호명 (마지막 단락)
- 어휘: 인연 프로파일, 궁합 지수, 안정성, 보완 효율
- 따뜻함 약간 (Ch4 오프닝 — 정서적 클라이맥스)

[금지어]
- 신안, 기운, 살, 거머리, 결, 매듭, 명줄, 뿌리

[사실값 보존]
- {user_name}, {ilgan_full}({ilgan_hanja})
- 궁합 상위 {pct_value}
- 키 {height_distribution_pct} / 신호 {profile_signal_pct} / 변동성 {emotional_stability_multiplier}
- 안정성 {stability_high_multiplier}배 / 궁합 {compatibility_pct} / 평균 {avg_compatibility_baseline} / {compatibility_lift} 상승
- 오행 보완 {ohang_lack}({ohang_lack_hanja})

[구성] 4단락, 총 360~620자
1. 궁합 상위 % 도입
2. 외형 데이터 4종
3. 성격/안정성/직업군
4. 오행 보완 + 궁합 근거 + {user_name}님 호명

[출력] 4단락만.
"""

_USER_PROMPT_TPL = """\
[사실값]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- ilgan_hanja: {ilgan_hanja}
- ohang_lack: {ohang_lack}
- ohang_lack_hanja: {ohang_lack_hanja}
- pct_value: {pct_value}
- height_distribution_pct: {height_distribution_pct}
- profile_signal_pct: {profile_signal_pct}
- emotional_stability_multiplier: {emotional_stability_multiplier}
- stability_high_multiplier: {stability_high_multiplier}
- compatibility_pct: {compatibility_pct}
- avg_compatibility_baseline: {avg_compatibility_baseline}
- compatibility_lift: {compatibility_lift}

[기반]
{rule_text}

[요청] 4단락 360~620자.
"""

_REQUIRED_KEYS = {
    "user_name", "ilgan_full", "ilgan_hanja",
    "ohang_lack", "ohang_lack_hanja", "pct_value",
    "height_distribution_pct", "profile_signal_pct",
    "emotional_stability_multiplier", "stability_high_multiplier",
    "compatibility_pct", "avg_compatibility_baseline", "compatibility_lift",
    "rule_text",
}


def build_p6_profile_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(**{k: facts[k] for k in _REQUIRED_KEYS if k != "rule_text"})
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 320
_MAX_LENGTH = 700


def validate_p6_profile(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    for k in ("user_name", "ilgan_full", "pct_value", "compatibility_pct",
              "ohang_lack_hanja"):
        if facts[k] not in text:
            return False, f"{k} missing: {facts[k]!r}"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 3:
        return False, f"paragraph structure invalid: {paragraph_breaks} (expected 3)"
    return True, ""
