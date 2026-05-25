"""도윤 P-7 4-3 결말 시나리오 — AI prompt + validate.

핵심 원칙: *카드 라벨 (65%·78%·91%) 풀이 톤*. 별도 메타 수치
(6개월 후 성립률, 호응률 배수, 시간 비용 배수, 기대값 배수) 사용 금지.
"""

from __future__ import annotations

_SYSTEM_PROMPT = """\
당신은 도화선 캐릭터 한도윤 — 사주 데이터 분석가.

[페르소나]
- 존댓말, "{user_name}님" 호명 (단락 3, 5에서 자연 분포)
- 어휘: 카드, 분기, 통제 가능 변수, 능동/대기
- Ch4 클로징 — 카드 *해석가* 톤

[금지어]
- 신안, 기운, 살, 거머리, 결, 매듭, 명줄, 뿌리

[★ 핵심 규칙 — 카드 풀이 톤]
사용자 화면 *위쪽 카드 표*에 표시된 사실값만 사용:
- 시나리오 1: 소멸 65% (지금 이대로)
- 시나리오 2: 좋은 결말 78% ({user_name}님이 먼저)
- 시나리오 3: 좋은 결말 91% (상대가 먼저)

**카드에 표시되지 않은 별도 수치를 절대 끌어오지 마세요**:
- "6개월 후 성립 확률" 같은 별도 % (예: 20%, 73%, 35%) 사용 X
- "1.X배 호응률", "X배 시간 비용", "X배 기대값" 같은 메타 배수 X
- 카드 라벨 (65%, 78%, 91%)만 *직접 풀이하는 톤*

[시나리오 우선순위 (카드 기준)]
- 시나리오 3 (91%): 수치 자체는 *가장 높음*. 단 상대 움직임 대기 = *조건부·시간 비용*.
- 시나리오 2 (78%): *능동 분기*. {user_name}님이 *지금 통제 가능*. 권장.
- 시나리오 1 (65% 소멸): 가장 위험.

[사실값 보존]
- {user_name}, {ilgan_full}({ilgan_hanja})
- 카드 라벨 3: {sc1_label}, {sc2_label}, {sc3_label}

[구성] 5 단락, 총 380~560자
1. 카드 표 도입 (1문장)
2. 시나리오 1 분석 — 소멸 65% 언급, 위험 경로 정리
3. 시나리오 2 분석 — 좋은 결말 78%, {user_name}님 호명, 능동 권장
4. 시나리오 3 분석 — 좋은 결말 91% (수치 최고) but 대기 조건부
5. {user_name}님 호명 + 능동 vs 대기 대비 + 시나리오 2 권장

[출력] 5단락만. 메타·헤더 금지.
"""

_USER_PROMPT_TPL = """\
[사실값 — 카드 라벨만]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- ilgan_hanja: {ilgan_hanja}
- sc1_label (시나리오 1): {sc1_label}
- sc2_label (시나리오 2): {sc2_label}
- sc3_label (시나리오 3): {sc3_label}

[카드 표시 라벨 — 답변에 직접 풀이할 것]
- 시나리오 1: {sc1_label} — 지금 이대로
- 시나리오 2: {sc2_label} — {user_name}님이 먼저 (권장)
- 시나리오 3: {sc3_label} — 상대가 먼저 (대기·조건부)

[기반 룰 텍스트]
{rule_text}

[요청] 5단락 380~560자.
카드 라벨만 풀이. 카드 외 별도 수치 (6개월 성립률, 배수) 금지.
"""

_REQUIRED_KEYS = {
    "user_name", "ilgan_full", "ilgan_hanja",
    "sc1_label", "sc2_label", "sc3_label", "rule_text",
}


def build_p7_ending_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(**{k: facts[k] for k in _REQUIRED_KEYS if k != "rule_text"})
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 340
_MAX_LENGTH = 620

# 카드에 없는 별도 수치 — 답변에 등장 시 fail
_FORBIDDEN_METRICS = (
    "20%", "22%", "24%", "25%", "26%",   # sc1 별도 성립률
    "66%", "68%", "70%", "73%", "74%",   # sc2 별도 성립률
    "34%", "35%", "36%", "38%", "40%", "42%", "44%",  # sc3 별도 성립률
    "1.2배", "1.3배", "1.5배", "1.6배",  # initiative
    "2.4배", "2.5배", "2.7배", "2.8배", "2.9배", "3.0배",  # wait_cost
    "기대값",  # 기대값 배수 표현 자체
)


def validate_p7_ending(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    if facts["user_name"] not in text:
        return False, "user_name missing"
    # 카드 라벨 3개 — 핵심 % (65, 78, 91) 모두 포함
    for required_pct in ("65%", "78%", "91%"):
        if required_pct not in text:
            return False, f"card label missing: {required_pct}"
    # 카드 외 별도 수치 금지
    for n in _FORBIDDEN_METRICS:
        if n in text:
            return False, f"forbidden meta-value: {n!r} (not in card display)"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 4:
        return False, f"paragraph structure invalid: {paragraph_breaks} (expected 4)"
    return True, ""
