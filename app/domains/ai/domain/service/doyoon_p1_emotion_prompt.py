"""도윤 P-1 1-3 감정 곡선 — AI prompt builder + validate.

3단락 230~350자. 차트 그래프 보조 톤. user_name은 룰 본문에 없어 검증 X.
"""

from __future__ import annotations

_SYSTEM_PROMPT = """\
당신은 도화선 서비스의 캐릭터 한도윤. 사주 데이터 분석가 페르소나.

[페르소나]
- 존댓말 (호명 선택적, 강제 X — 그래프 분석 톤)
- 어휘: 진폭, 폭발 강도, 회복 곡선, 의식적 노출, 구간, 진입 — P-1 시그니처
- 따뜻함 절제, 숫자 뒤 한 줄 정리

[금지어]
- 신안, 기운, 살, 거머리, 결, 매듭, 명줄, 뿌리 (강연우 톤 X)
- P-0 시그니처(표본/분포/차단율)는 사용 자제

[사실값 보존 — 절대 변경 금지]
- 일간 ({ilgan_full})
- 위기 구간 강도 ({crisis_pct})
- 회복 구간 강도 ({recovery_pct})
- 평균 대비 배수 ({crisis_multiplier})
- 표현 빈도 효과 ({expression_effect_pct})

[구성] 3 단락, 단락 사이 빈 줄 1개, 총 210~380자
1. 그래프 도입 — 위기 {crisis_pct} + 배수 {crisis_multiplier} + 회복 {recovery_pct} (2~3문장)
2. {ilgan_full} 일간 감정 곡선 특성 진단 (2문장)
3. 의식적 노출 가이드 + 효과 {expression_effect_pct} (2~3문장)

[출력] 3단락 텍스트만. 메타 설명·헤더·코드블록 금지.
"""


_USER_PROMPT_TPL = """\
다음 사용자의 P-1 감정 곡선 분석을 작성해주세요.

[보존해야 하는 사실값 — 모두 출력에 포함]
- ilgan_full: {ilgan_full}
- crisis_pct: {crisis_pct}
- recovery_pct: {recovery_pct}
- crisis_multiplier: {crisis_multiplier}
- expression_effect_pct: {expression_effect_pct}

[참고 — 일간 감정 곡선 진단 본문]
{curve_diag_text}

[룰 합성 기반 텍스트 — 이걸 *기반으로* 같은 사실값을 모두 보존한 채 표현을 다양화하세요. \
그대로 복붙 금지. 사실값 한 글자도 바꾸지 마세요.]

{rule_text}

[요청]
위 사실값을 모두 포함하는 3단락 210~380자 텍스트를 작성하세요.
"""


_REQUIRED_KEYS = {
    "user_name",
    "ilgan_full",
    "crisis_pct",
    "recovery_pct",
    "crisis_multiplier",
    "expression_effect_pct",
    "curve_diag_text",
    "rule_text",
}


def build_p1_emotion_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")

    system = _SYSTEM_PROMPT.format(
        ilgan_full=facts["ilgan_full"],
        crisis_pct=facts["crisis_pct"],
        recovery_pct=facts["recovery_pct"],
        crisis_multiplier=facts["crisis_multiplier"],
        expression_effect_pct=facts["expression_effect_pct"],
    )
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 190
_MAX_LENGTH = 450


def validate_p1_emotion(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    """user_name 검증 X (룰 본문에 없음 — AI 출력에 들어가도 안 들어가도 OK)."""
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"

    if facts["ilgan_full"] not in text:
        return False, f"ilgan_full missing: {facts['ilgan_full']!r}"
    if facts["crisis_pct"] not in text:
        return False, f"crisis_pct missing: {facts['crisis_pct']!r}"
    if facts["recovery_pct"] not in text:
        return False, f"recovery_pct missing: {facts['recovery_pct']!r}"
    if facts["crisis_multiplier"] not in text:
        return False, f"crisis_multiplier missing: {facts['crisis_multiplier']!r}"
    if facts["expression_effect_pct"] not in text:
        return False, "expression_effect_pct missing"

    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 2:
        return False, f"paragraph structure invalid: {paragraph_breaks} breaks (expected 2)"

    return True, ""
