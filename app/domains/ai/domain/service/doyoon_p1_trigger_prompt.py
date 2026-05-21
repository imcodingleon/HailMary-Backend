"""도윤 P-1 1-2 트리거 메커니즘 — AI prompt builder + validate.

2단락 200~280자. P-0/P-1 opening 패턴 동일.
"""

from __future__ import annotations

_SYSTEM_PROMPT = """\
당신은 도화선 서비스의 캐릭터 한도윤. 사주 데이터 분석가 페르소나.

[페르소나]
- 존댓말, "{user_name}님" 호명 (단락 2에서 1회)
- 어휘: 발화, 도달 확률, 자기조절, 임계점, 처리량, 구간 — P-1 시그니처
- 따뜻함 절제, 숫자 뒤 한 줄 정리

[금지어]
- 신안, 기운, 살, 거머리, 결, 매듭, 명줄, 뿌리 (강연우 톤 X)
- P-0 시그니처(표본/분포/차단율)는 사용 자제

[사실값 보존 — 절대 변경 금지]
- 사용자 이름 ({user_name})
- 일간 ({ilgan_full})
- 트리거 임계점 ({trigger_completion_pct})
- 초기 진입 시간 ({peak_window_days})
- 자기조절 성공률 ({self_control_pct})

[구성] 2 단락, 단락 사이 빈 줄 1개, 총 180~310자
1. 트리거 3개 순차 발화 시 임계점 도달 ({trigger_completion_pct}) 의미 (1~2문장)
2. {peak_window_days} 초기 + 트리거 1+2 결합 + 자기조절 {self_control_pct} (3~4문장)

[출력] 2단락 텍스트만. 메타 설명·헤더·코드블록 금지.
"""


_USER_PROMPT_TPL = """\
다음 사용자의 P-1 트리거 메커니즘 분석을 작성해주세요.

[보존해야 하는 사실값 — 모두 출력에 포함]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- trigger_1: {trigger_1}
- trigger_2: {trigger_2}
- trigger_completion_pct: {trigger_completion_pct}
- peak_window_days: {peak_window_days}
- self_control_pct: {self_control_pct}

[참고 — 자기조절 어려운 이유 본문]
{control_reason_text}

[룰 합성 기반 텍스트 — 이걸 *기반으로* 같은 사실값을 모두 보존한 채 표현을 다양화하세요. \
그대로 복붙 금지. 사실값 한 글자도 바꾸지 마세요.]

{rule_text}

[요청]
위 사실값을 모두 포함하는 2단락 180~310자 텍스트를 작성하세요.
"""


_REQUIRED_KEYS = {
    "user_name",
    "ilgan_full",
    "trigger_1",
    "trigger_2",
    "trigger_3",
    "trigger_completion_pct",
    "peak_window_days",
    "self_control_pct",
    "control_reason_text",
    "rule_text",
}


def build_p1_trigger_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")

    system = _SYSTEM_PROMPT.format(
        user_name=facts["user_name"],
        ilgan_full=facts["ilgan_full"],
        trigger_completion_pct=facts["trigger_completion_pct"],
        peak_window_days=facts["peak_window_days"],
        self_control_pct=facts["self_control_pct"],
    )
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 160
_MAX_LENGTH = 380


def validate_p1_trigger(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"

    if facts["user_name"] not in text:
        return False, "user_name missing"
    if facts["ilgan_full"] not in text:
        return False, f"ilgan_full missing: {facts['ilgan_full']!r}"
    if facts["trigger_completion_pct"] not in text:
        return False, "trigger_completion_pct missing"
    if facts["peak_window_days"] not in text:
        return False, "peak_window_days missing"
    if facts["self_control_pct"] not in text:
        return False, "self_control_pct missing"
    # trigger_1, trigger_2 중 적어도 둘은 포함 (룰 본문에 둘 다 박혀있음)
    if facts["trigger_1"] not in text:
        return False, "trigger_1 missing"
    if facts["trigger_2"] not in text:
        return False, "trigger_2 missing"

    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 1:
        return False, f"paragraph structure invalid: {paragraph_breaks} breaks (expected 1)"

    return True, ""
