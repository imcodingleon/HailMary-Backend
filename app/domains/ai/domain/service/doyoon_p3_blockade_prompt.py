"""도윤 P-3 2-1 구조적 원인 — AI prompt builder + validate."""

from __future__ import annotations

_SYSTEM_PROMPT = """\
당신은 도화선 캐릭터 한도윤 — 사주 데이터 분석가.

[페르소나]
- 존댓말, "{user_name}님" 호명 (단락 1에서 1회)
- 어휘: 구조적 과다, 차단율, 변수 정리, 비움, 진입률, 케이스 — P-3 시그니처
- 따뜻함 절제, 숫자 뒤 한 줄 정리

[금지어]
- 신안, 기운, 살, 거머리, 결, 매듭, 명줄, 뿌리 (강연우 톤 X)

[사실값 보존 — 절대 변경 금지]
- 사용자 이름 ({user_name})
- 일간 ({ilgan_full})
- 오행 과다 ({ohang_excess}) + 한자 ({ohang_excess_hanja})
- 평균 대비 배수 ({blockade_multiplier})
- 차단율 ({blockage_rate_drop})
- 비움 회복률 ({recovery_after_clearing_pct})

[구성] 3 단락, 단락 사이 빈 줄 1개, 총 270~430자
1. 호명 + 오행 과다 측정 (1~2문장)
2. 차단율 데이터 (2~3문장)
3. 비움의 정량 효과 + 처방 (2~3문장)

[출력] 3단락 텍스트만. 메타·헤더 금지.
"""


_USER_PROMPT_TPL = """\
다음 사용자의 P-3 구조적 원인 분석을 작성해주세요.

[보존해야 하는 사실값 — 모두 출력에 포함]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- ohang_excess: {ohang_excess}
- ohang_excess_hanja: {ohang_excess_hanja}
- blockade_multiplier: {blockade_multiplier}
- blockage_rate_drop: {blockage_rate_drop}
- recovery_after_clearing_pct: {recovery_after_clearing_pct}

[룰 합성 기반 텍스트 — 기반으로 표현 다양화. 사실값 한 글자도 바꾸지 마세요.]

{rule_text}

[요청]
위 사실값 모두 포함하는 3단락 270~430자 텍스트를 작성하세요.
"""


_REQUIRED_KEYS = {
    "user_name",
    "ilgan_full",
    "ilgan_hanja",
    "ohang_excess",
    "ohang_excess_hanja",
    "blockade_pct",
    "blockade_multiplier",
    "blockage_rate_drop",
    "recovery_after_clearing_pct",
    "rule_text",
}


def build_p3_blockade_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(
        user_name=facts["user_name"],
        ilgan_full=facts["ilgan_full"],
        ohang_excess=facts["ohang_excess"],
        ohang_excess_hanja=facts["ohang_excess_hanja"],
        blockade_multiplier=facts["blockade_multiplier"],
        blockage_rate_drop=facts["blockage_rate_drop"],
        recovery_after_clearing_pct=facts["recovery_after_clearing_pct"],
    )
    user = _USER_PROMPT_TPL.format(
        user_name=facts["user_name"],
        ilgan_full=facts["ilgan_full"],
        ohang_excess=facts["ohang_excess"],
        ohang_excess_hanja=facts["ohang_excess_hanja"],
        blockade_multiplier=facts["blockade_multiplier"],
        blockage_rate_drop=facts["blockage_rate_drop"],
        recovery_after_clearing_pct=facts["recovery_after_clearing_pct"],
        rule_text=facts["rule_text"],
    )
    return system, user


_MIN_LENGTH = 240
_MAX_LENGTH = 500


def validate_p3_blockade(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    if facts["user_name"] not in text:
        return False, "user_name missing"
    if facts["ohang_excess_hanja"] not in text:
        return False, f"ohang_excess_hanja missing: {facts['ohang_excess_hanja']!r}"
    if facts["blockade_multiplier"] not in text:
        return False, f"blockade_multiplier missing: {facts['blockade_multiplier']!r}"
    if facts["blockage_rate_drop"] not in text:
        return False, f"blockage_rate_drop missing: {facts['blockage_rate_drop']!r}"
    if facts["recovery_after_clearing_pct"] not in text:
        return False, f"recovery_after_clearing_pct missing: {facts['recovery_after_clearing_pct']!r}"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 2:
        return False, f"paragraph structure invalid: {paragraph_breaks} (expected 2)"
    return True, ""
