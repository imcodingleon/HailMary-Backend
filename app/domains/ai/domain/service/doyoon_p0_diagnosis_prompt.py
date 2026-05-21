"""도윤 P-0 0-5 분석 진입 요약 — AI prompt builder.

호출자: generate_p0_diagnosis_usecase. 입력 facts는 doyoon_p0_intro.get_doyoon_p0_facts.

전략: 룰 합성 결과를 *기반 텍스트*로 AI에 전달 → AI가 같은 사실값을 보존하면서
표현·연결사·문장 길이를 다양화. 환각 위험 최소 (수치를 만들 필요 없음, 보존만).

순수 도메인 — 외부 라이브러리 import 금지 (CLAUDE.md Domain 규칙).
"""

from __future__ import annotations

_SYSTEM_PROMPT = """\
당신은 도화선 서비스의 캐릭터 한도윤입니다. 한도윤은 사주 데이터 분석가 페르소나입니다.

[페르소나]
- 존댓말 사용, "{user_name}님" 호명 (단락 1에서 1회)
- 데이터/통계 어휘로만 분석: 표본, 분포, 임계점, 차단율, 측정값, 입력 데이터, 변수, 인풋
- 따뜻함은 절제 — 숫자 뒤 한 줄 정리. 감상적·형이상학적 표현 금지

[금지어]
- 신안, 기운, 살, 거머리, 결, 매듭, 명줄, 뿌리 (강연우 톤 어휘 사용 X)
- "운명", "인연이 ~한다" 같은 비결정론적 표현 X

[어휘 다양화]
- P-1 시그니처 어휘는 사용 자제: 분류, 케이스, 구간, 발화, 도달 확률, 자기조절, 진폭, 폭발 강도, 회복 곡선
- P-0 시그니처에 집중: 표본, 분포, 임계점, 차단율, 측정값, 입력 데이터

[사실값 보존 — 절대 변경 금지]
참조 데이터에 박힌 다음 값들은 *변경, 누락, 풀어쓰기, 약어화* 모두 금지:
- 사용자 이름 ({user_name})
- 일간 한글 + 한자 ({ilgan_full}, {ilgan_hanja})
- 오행 한자 ({excess_ohang_hanja}, {lack_ohang_hanja})
- 백분위 ({excess_percentile}, {lack_percentile})
- 접촉률 감소 ({contact_rate_drop})
출력 텍스트에 위 문자열들이 그대로 포함돼야 합니다.

[구성] 4 단락, 단락 사이 빈 줄 1개, 총 220~340자
1. 호명 + 데이터 정리 완료 신호 (1문장)
2. 일간 진단 + 강점 변수 (2문장)
3. 핵심 리스크 변수 2개(과다·부족 오행) + 정량 영향 (3문장)
4. 다음 장 안내 (1문장)

[출력]
4단락 텍스트만 출력. 메타 설명·주석·헤더·코드블록 금지.
"""


_USER_PROMPT_TPL = """\
다음 사용자의 P-0 분석 진입 요약을 작성해주세요.

[보존해야 하는 사실값 — 모두 출력에 포함]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- ilgan_hanja: {ilgan_hanja}
- excess_ohang_hanja: {excess_ohang_hanja}
- excess_percentile: {excess_percentile}
- lack_ohang_hanja: {lack_ohang_hanja}
- lack_percentile: {lack_percentile}
- contact_rate_drop: {contact_rate_drop}

[참고 문구 — 일간 강점 설명]
{ilgan_para_2}

[룰 합성 기반 텍스트 — 이걸 *기반으로* 같은 사실값을 모두 보존한 채 표현을 다양화하세요. \
그대로 복붙은 금지 (연결사·문장 길이·구성 다양화). 사실값 한 글자도 바꾸지 마세요.]

{rule_text}

[요청]
위 사실값을 모두 포함하는 4단락 220~340자 텍스트를 작성하세요.
"""


def build_p0_diagnosis_prompt(facts: dict[str, str]) -> tuple[str, str]:
    """facts dict → (system_prompt, user_prompt) 튜플 반환.

    Args:
        facts: doyoon_p0_intro.get_doyoon_p0_facts() 반환 dict.
               필수 키 12개. 누락 시 KeyError.

    Returns:
        (system_prompt, user_prompt). system 안에 user_name도 박힘 (호명 인지용).

    Raises:
        KeyError: facts에 필수 키 누락.
    """
    required_keys = {
        "user_name",
        "ilgan_full",
        "ilgan_hanja",
        "excess_ohang_hanja",
        "excess_percentile",
        "lack_ohang_hanja",
        "lack_percentile",
        "contact_rate_drop",
        "ilgan_para_2",
        "rule_text",
    }
    missing = required_keys - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")

    system = _SYSTEM_PROMPT.format(
        user_name=facts["user_name"],
        ilgan_full=facts["ilgan_full"],
        ilgan_hanja=facts["ilgan_hanja"],
        excess_ohang_hanja=facts["excess_ohang_hanja"],
        lack_ohang_hanja=facts["lack_ohang_hanja"],
        excess_percentile=facts["excess_percentile"],
        lack_percentile=facts["lack_percentile"],
        contact_rate_drop=facts["contact_rate_drop"],
    )
    user = _USER_PROMPT_TPL.format(**{k: facts[k] for k in required_keys})
    return system, user


# ── 출력 검증 ─────────────────────────────────────────────────────


_MIN_LENGTH = 180
_MAX_LENGTH = 500


def validate_p0_diagnosis(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    """AI 출력 텍스트가 facts의 사실값을 모두 보존했는지 검증.

    실패 시 (False, 사유) — 사유는 로그용 (사용자 이름 마스킹).
    성공 시 (True, "").

    검증 단계 (CLAUDE.md 마스킹 룰 — user_name은 로그에 평문 X):
        1. 길이 _MIN_LENGTH~_MAX_LENGTH
        2. user_name 포함
        3. ilgan_full + ilgan_hanja 포함
        4. excess_ohang_hanja 포함
        5. lack_ohang_hanja 포함
        6. excess_percentile 정확 문자열 포함
        7. lack_percentile 정확 문자열 포함
        8. contact_rate_drop 정확 문자열 포함
        9. 4단락 구조 (\\n\\n 정확히 3회)
    """
    length = len(text)
    if length < _MIN_LENGTH or length > _MAX_LENGTH:
        return False, f"length out of range: {length}"

    user_name = facts["user_name"]
    if user_name not in text:
        return False, "user_name missing"

    for key in ("ilgan_full", "ilgan_hanja"):
        if facts[key] not in text:
            return False, f"{key} missing: {facts[key]!r}"

    if facts["excess_ohang_hanja"] not in text:
        return False, f"excess_ohang_hanja missing: {facts['excess_ohang_hanja']!r}"
    if facts["lack_ohang_hanja"] not in text:
        return False, f"lack_ohang_hanja missing: {facts['lack_ohang_hanja']!r}"

    for key in ("excess_percentile", "lack_percentile", "contact_rate_drop"):
        if facts[key] not in text:
            return False, f"{key} missing: {facts[key]!r}"

    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks != 3:
        return False, f"paragraph structure invalid: {paragraph_breaks} breaks (expected 3)"

    return True, ""
