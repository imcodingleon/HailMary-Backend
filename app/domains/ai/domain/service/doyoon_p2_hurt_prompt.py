"""도윤 P-2 1-4 약점 트리거 — AI prompt builder + validate.

3단락 300~350자. P-1 패턴 동일.
"""

from __future__ import annotations

_SYSTEM_PROMPT = """\
당신은 도화선 캐릭터 한도윤 — 사주 데이터 분석가.

[페르소나]
- 존댓말, "{user_name}님" 호명 (단락 1에서 1회)
- 어휘: 약점, 트리거, 위험 변수, 표본 발현률, 차단율, 케이스, 입력 — P-2 시그니처
- 따뜻함 절제, 숫자 뒤 한 줄 정리

[금지어]
- 신안, 기운, 살, 거머리, 결, 매듭, 명줄, 뿌리 (강연우 톤 X)
- P-1 시그니처(진폭/회복 곡선/자기조절)는 자제

[사실값 보존 — 절대 변경 금지]
- 사용자 이름 ({user_name})
- 일간 한글 + 한자 ({ilgan_full}, {ilgan_hanja})
- 표본 발현률 ({vulnerability_pct})
- 동일 패턴 비율 ({common_pattern_pct})

[구성] 3 단락, 단락 사이 빈 줄 1개, 총 270~400자
1. 호명 + 일간 약점 트리거 분석 도입 (1~2문장)
2. 첫 번째 시나리오 분석 + 표본 발현률 + 동일 패턴 비율 (2~3문장)
3. 두 번째 시나리오 분석 + 처방 (2~3문장)

[출력] 3단락 텍스트만. 메타·헤더 금지.
"""


_USER_PROMPT_TPL = """\
다음 사용자의 P-2 약점 트리거 분석을 작성해주세요.

[보존해야 하는 사실값 — 모두 출력에 포함]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- ilgan_hanja: {ilgan_hanja}
- vulnerability_pct: {vulnerability_pct}
- common_pattern_pct: {common_pattern_pct}

[참고 — 두 시나리오]
1. {scenario_1_when}
2. {scenario_2_when}

[참고 — 처방]
{hurt_optimization}

[룰 합성 기반 텍스트 — 기반으로 표현 다양화. 사실값 한 글자도 바꾸지 마세요.]

{rule_text}

[요청]
위 사실값 모두 포함하는 3단락 270~400자 텍스트를 작성하세요.
"""


_REQUIRED_KEYS = {
    "user_name",
    "ilgan_full",
    "ilgan_hanja",
    "scenario_1_when",
    "scenario_2_when",
    "vulnerability_pct",
    "common_pattern_pct",
    "hurt_optimization",
    "rule_text",
}


def build_p2_hurt_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(
        user_name=facts["user_name"],
        ilgan_full=facts["ilgan_full"],
        ilgan_hanja=facts["ilgan_hanja"],
        vulnerability_pct=facts["vulnerability_pct"],
        common_pattern_pct=facts["common_pattern_pct"],
    )
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 250
_MAX_LENGTH = 500


def validate_p2_hurt(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    if facts["user_name"] not in text:
        return False, "user_name missing"
    if facts["ilgan_full"] not in text:
        return False, f"ilgan_full missing: {facts['ilgan_full']!r}"
    if facts["ilgan_hanja"] not in text:
        return False, f"ilgan_hanja missing: {facts['ilgan_hanja']!r}"
    if facts["vulnerability_pct"] not in text:
        return False, f"vulnerability_pct missing: {facts['vulnerability_pct']!r}"
    if facts["common_pattern_pct"] not in text:
        return False, f"common_pattern_pct missing: {facts['common_pattern_pct']!r}"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 2:
        return False, f"paragraph structure invalid: {paragraph_breaks} (expected 2)"
    return True, ""
