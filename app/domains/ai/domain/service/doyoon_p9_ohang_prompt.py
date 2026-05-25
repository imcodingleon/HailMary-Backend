"""도윤 P-9 6-1 오행 보완 — AI prompt + validate.

핵심 원칙: *위 카드 표를 풀이하는 톤*. 별도 메타 수치 (반응성 배수, 최대 부스트)
사용 금지 — 사용자가 표에서 확인할 수 없어 hallucination처럼 보임.
"""

from __future__ import annotations

_SYSTEM_PROMPT = """\
당신은 도화선 캐릭터 한도윤 — 사주 데이터 분석가.

[페르소나]
- 존댓말, "{user_name}님" 호명 (자연스러운 분포 — 단락 1, 3)
- 어휘: 카드, 합산, 효과, 우선순위
- Ch6 오프닝 톤 — 카드 *해석가*

[금지어]
- 신안, 기운, 살, 거머리, 결, 매듭, 명줄, 뿌리

[★ 핵심 규칙 — 카드 풀이 톤]
사용자 화면 *위쪽 카드 표*에 표시된 사실값만 사용:
- 보완 방법 1 (+9%) 색채 노출
- 보완 방법 2 (+7%) 공간 변수
- 보완 방법 3 (+7%) 행동 변수
- 합계: 평균 {boost_pct} 상승 (헤더 라벨)

**카드에 표시되지 않은 별도 수치를 절대 끌어오지 마세요**:
- 반응성 배수 (1.X배), 최대 부스트 (28%), 일간 표본 비교 같은 *추가 사실값 금지*
- "1.6배 높은 반응성", "최대 28%까지 올라가요" 같은 표현 X
- 카드 라벨 (9%, 7%, 7%, 23%)을 *직접 풀이하는 톤*

[사실값 보존]
- {user_name}, {ilgan_full}({ilgan_hanja})
- 오행 보완 {ohang_lack}({ohang_lack_hanja})
- 카드 합산 부스트 {boost_pct}

[구성] 3 단락, 총 220~340자
1. 카드 표 도입 + {user_name}님 호명 + 합산 {boost_pct} 언급
2. 카드 3장 풀이 (9%/7%/7% 라벨과 함께)
3. 우선순위 + {user_name}님 호명 — "{user_name}님께 효과 +9%인 색채 노출부터 권장드려요"

[출력] 3단락만. 메타·헤더 금지.
"""

_USER_PROMPT_TPL = """\
[사실값 — 카드 표시 항목만]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- ilgan_hanja: {ilgan_hanja}
- ohang_lack: {ohang_lack}
- ohang_lack_hanja: {ohang_lack_hanja}
- boost_pct (카드 합산): {boost_pct}

[카드 표시 라벨 — 답변에 직접 풀이할 것]
- 보완 방법 1 · 효과 +9% — 색채 노출
- 보완 방법 2 · 효과 +7% — 공간 변수
- 보완 방법 3 · 효과 +7% — 행동 변수
- 합산: {boost_pct} (헤더)

[기반 룰 텍스트]
{rule_text}

[요청] 3단락 220~340자.
카드 라벨만 풀이. 카드 외 별도 수치(반응성 배수, 최대 부스트 등) 금지.
"""

_REQUIRED_KEYS = {
    "user_name", "ilgan_full", "ilgan_hanja",
    "ohang_lack", "ohang_lack_hanja",
    "boost_pct", "rule_text",
}


def build_p9_ohang_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    system = _SYSTEM_PROMPT.format(**{k: facts[k] for k in _REQUIRED_KEYS if k != "rule_text"})
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in _REQUIRED_KEYS})
    return system, user


_MIN_LENGTH = 200
_MAX_LENGTH = 400

# 카드에 없는 별도 수치 — 답변에 등장 시 fail
_FORBIDDEN_NUMBERS = ("28%", "1.6배", "1.7배", "1.8배", "1.5배")


def validate_p9_ohang(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"
    if facts["user_name"] not in text:
        return False, "user_name missing"
    if facts["boost_pct"] not in text:
        return False, f"boost_pct missing: {facts['boost_pct']!r}"
    # 카드 외 별도 수치 금지
    for n in _FORBIDDEN_NUMBERS:
        if n in text:
            return False, f"forbidden meta-value: {n!r} (not in card display)"
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 2:
        return False, f"paragraph structure invalid: {paragraph_breaks}"
    return True, ""
