"""도윤 P-2 1-5 회복 곡선 — AI prompt builder + validate.

3단락 350~400자. Ch1 클로징 톤.
"""

from __future__ import annotations

_SYSTEM_PROMPT = """\
당신은 도화선 캐릭터 한도윤 — 사주 데이터 분석가.

[페르소나]
- 존댓말, "{user_name}님" 호명 (단락 1에서 1회)
- 어휘: 회복 곡선, 인덱스, 가중치, 단계, 임계점, 케이스 — P-2 recovery 시그니처
- 따뜻함 절제, 숫자 뒤 한 줄 정리

[금지어]
- 신안, 기운, 살, 거머리, 결, 매듭, 명줄, 뿌리 (강연우 톤 X)
- P-1 시그니처(진폭/폭발 강도)는 자제

[사실값 보존 — 절대 변경 금지]
- 사용자 이름 ({user_name})
- 일간 한글 + 한자 ({ilgan_full}, {ilgan_hanja})
- 회복 지연 배수 ({recovery_lag_multiplier})
- 시간 라벨 3종 ({time_label_0} / {time_label_1} / {time_label_2})

[구성] 3 단락, 단락 사이 빈 줄 1개, 총 320~480자
1. 호명 + 일간 회복 곡선 도입 + 지연 배수 (2~3문장)
2. {time_label_0} ~ {time_label_2} 3단계 분석 (3~4문장)
3. 처방 + 마무리 (2~3문장)

[출력] 3단락 텍스트만. 메타·헤더 금지.
"""


_USER_PROMPT_TPL = """\
다음 사용자의 P-2 회복 곡선 분석을 작성해주세요.

[보존해야 하는 사실값 — 모두 출력에 포함]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- ilgan_hanja: {ilgan_hanja}
- recovery_lag_multiplier: {recovery_lag_multiplier}
- time_label_0: {time_label_0}
- time_label_1: {time_label_1}
- time_label_2: {time_label_2}

[참고 — 처방]
{recovery_optimization}

[룰 합성 기반 텍스트 — 기반으로 표현 다양화. 사실값 한 글자도 바꾸지 마세요.]

{rule_text}

[요청]
위 사실값 모두 포함하는 3단락 320~480자 텍스트를 작성하세요.
"""


_REQUIRED_KEYS = {
    "user_name",
    "ilgan_full",
    "ilgan_hanja",
    "recovery_lag_multiplier",
    "time_label_0",
    "time_label_1",
    "time_label_2",
    "recovery_optimization",
    "rule_text",
}


def build_p2_recovery_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(
        user_name=facts["user_name"],
        ilgan_full=facts["ilgan_full"],
        ilgan_hanja=facts["ilgan_hanja"],
        recovery_lag_multiplier=facts["recovery_lag_multiplier"],
        time_label_0=facts["time_label_0"],
        time_label_1=facts["time_label_1"],
        time_label_2=facts["time_label_2"],
    )
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 290
_MAX_LENGTH = 600


def validate_p2_recovery(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    if facts["user_name"] not in text:
        return False, "user_name missing"
    if facts["ilgan_full"] not in text:
        return False, f"ilgan_full missing: {facts['ilgan_full']!r}"
    if facts["ilgan_hanja"] not in text:
        return False, f"ilgan_hanja missing: {facts['ilgan_hanja']!r}"
    if facts["recovery_lag_multiplier"] not in text:
        return False, f"recovery_lag_multiplier missing: {facts['recovery_lag_multiplier']!r}"
    if facts["time_label_0"] not in text:
        return False, f"time_label_0 missing: {facts['time_label_0']!r}"
    if facts["time_label_1"] not in text:
        return False, f"time_label_1 missing: {facts['time_label_1']!r}"
    if facts["time_label_2"] not in text:
        return False, f"time_label_2 missing: {facts['time_label_2']!r}"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 2:
        return False, f"paragraph structure invalid: {paragraph_breaks} (expected 2)"
    return True, ""
