"""도윤 P-4 2-4 착각 인연 — AI prompt builder + validate."""

from __future__ import annotations

_SYSTEM_PROMPT = """\
당신은 도화선 캐릭터 한도윤 — 사주 데이터 분석가.

[페르소나]
- 존댓말, "{user_name}님" 호명 (마지막 단락 1회)
- 어휘: 착각 인연, 기울기, 검증, 오인 신호 — P-4 시그니처
- 따뜻함 절제, 숫자 뒤 한 줄 정리

[금지어]
- 신안, 기운, 살, 거머리, 결, 매듭, 명줄, 뿌리 (강연우 톤 X)

[사실값 보존 — 절대 변경 금지]
- 사용자 이름 ({user_name})
- 일간 ({ilgan_full})
- 착각 발생률 배수 ({illusion_multiplier})
- 오인 신호 키워드 3종 ({sign_1_keyword} / {sign_2_keyword} / {sign_3_keyword})
- 오인 신호 발생률 3종 ({sign_1_pct} / {sign_2_pct} / {sign_3_pct})
- 진짜 인연 성장률 ({real_growth_pct}) + 착각 인연 하락률 ({fake_drop_pct})
- 정확도 배수 ({accuracy_multiplier})

[구성] 4 단락, 총 290~500자
1. 일간 착각 발생률 + 통계 유의성
2. 3개월차 기울기 + 진짜/착각 변화율 + 정확도 배수
3. 오인 신호 3종 요약
4. {user_name}님 호명 + 마지막 한 줄

[출력] 4단락 텍스트만. 메타·헤더 금지.
"""


_USER_PROMPT_TPL = """\
다음 사용자의 P-4 착각 인연 분석을 작성해주세요.

[보존해야 하는 사실값 — 모두 출력에 포함]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- illusion_multiplier: {illusion_multiplier}
- sign_1_keyword: {sign_1_keyword}
- sign_1_pct: {sign_1_pct}
- sign_2_keyword: {sign_2_keyword}
- sign_2_pct: {sign_2_pct}
- sign_3_keyword: {sign_3_keyword}
- sign_3_pct: {sign_3_pct}
- real_growth_pct: {real_growth_pct}
- fake_drop_pct: {fake_drop_pct}
- accuracy_multiplier: {accuracy_multiplier}

[룰 합성 기반 텍스트 — 기반으로 표현 다양화. 사실값 한 글자도 바꾸지 마세요.]

{rule_text}

[요청]
위 사실값 모두 포함하는 4단락 290~500자 텍스트를 작성하세요.
"""


_REQUIRED_KEYS = {
    "user_name",
    "ilgan_full",
    "illusion_multiplier",
    "sign_1_keyword",
    "sign_1_pct",
    "sign_2_keyword",
    "sign_2_pct",
    "sign_3_keyword",
    "sign_3_pct",
    "real_growth_pct",
    "fake_drop_pct",
    "accuracy_multiplier",
    "rule_text",
}


def build_p4_illusion_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(**{k: facts[k] for k in _REQUIRED_KEYS if k != "rule_text"})
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 260
_MAX_LENGTH = 600


def validate_p4_illusion(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    if facts["user_name"] not in text:
        return False, "user_name missing"
    if facts["ilgan_full"] not in text:
        return False, f"ilgan_full missing"
    for k in ("illusion_multiplier", "real_growth_pct", "fake_drop_pct",
              "accuracy_multiplier",
              "sign_1_keyword", "sign_1_pct",
              "sign_2_keyword", "sign_2_pct",
              "sign_3_keyword", "sign_3_pct"):
        if facts[k] not in text:
            return False, f"{k} missing: {facts[k]!r}"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks not in (2, 3):
        return False, f"paragraph structure invalid: {paragraph_breaks} (expected 2 or 3)"
    return True, ""
