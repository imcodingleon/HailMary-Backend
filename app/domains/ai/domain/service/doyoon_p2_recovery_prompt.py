"""도윤 P-2 1-5 회복 곡선 — AI prompt builder + validate.

원본 도윤 구조 정합 (2026-05-21 재설계). 진행바 4단계 % + 평균 회복 곡선 분석.
3~4 단락 280~500자.
"""

from __future__ import annotations

_SYSTEM_PROMPT = """\
당신은 도화선 캐릭터 한도윤 — 사주 데이터 분석가.

[페르소나]
- 존댓말, "{user_name}님" 호명 (단락 2 이후 1회)
- 어휘: 회복 곡선, 인덱스, 가중치, 단계, 임계점, 케이스, 잔여 — P-2 recovery 시그니처
- 따뜻함 절제, 숫자 뒤 한 줄 정리

[금지어]
- 신안, 기운, 살, 거머리, 결, 매듭, 명줄, 뿌리 (강연우 톤 X)

[사실값 보존 — 절대 변경 금지]
- 사용자 이름 ({user_name})
- 일간 한글 + 한자 ({ilgan_full}, {ilgan_hanja})
- 평균 대비 회복 지연 ({recovery_lag_multiplier})
- 4단계 회복률 ({meter_pct_0} / {meter_pct_1} / {meter_pct_2} / {meter_pct_3})

[구성] 3~4 단락, 총 260~500자
1. 도입 — 평균 회복 곡선 소개 (1~2문장)
2. 4단계 분석 — 직후/1개월/3개월/6개월 회복률 또는 잔여 강도 (2~3문장)
3. 평균 대비 지연 평가 + 처방 (2~3문장)

[출력] 텍스트만. 메타·헤더 금지.
"""


_USER_PROMPT_TPL = """\
다음 사용자의 P-2 회복 곡선 분석을 작성해주세요.

[보존해야 하는 사실값 — 모두 출력에 포함]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- ilgan_hanja: {ilgan_hanja}
- recovery_lag_multiplier: {recovery_lag_multiplier}
- meter_pct_0: {meter_pct_0}
- meter_pct_1: {meter_pct_1}
- meter_pct_2: {meter_pct_2}
- meter_pct_3: {meter_pct_3}

[룰 합성 기반 텍스트 — 기반으로 표현 다양화. 사실값 한 글자도 바꾸지 마세요.]

{rule_text}

[요청]
위 사실값 모두 포함하는 3~4단락 260~500자 텍스트를 작성하세요.
"""


_REQUIRED_KEYS = {
    "user_name",
    "ilgan_full",
    "ilgan_hanja",
    "recovery_lag_multiplier",
    "meter_pct_0",
    "meter_pct_1",
    "meter_pct_2",
    "meter_pct_3",
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
        meter_pct_0=facts["meter_pct_0"],
        meter_pct_1=facts["meter_pct_1"],
        meter_pct_2=facts["meter_pct_2"],
        meter_pct_3=facts["meter_pct_3"],
    )
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 230
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
    # 4 단계 회복률 중 *최소 2개* 포함 — 잔여 강도 표현(100-pct)으로 갈 수 있어 완화
    pcts_found = sum(
        1 for k in ("meter_pct_0", "meter_pct_1", "meter_pct_2", "meter_pct_3")
        if facts[k] in text
    )
    if pcts_found < 2:
        return False, f"meter pcts insufficient: {pcts_found}/4"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks not in (2, 3):
        return False, f"paragraph structure invalid: {paragraph_breaks} (expected 2 or 3)"
    return True, ""
