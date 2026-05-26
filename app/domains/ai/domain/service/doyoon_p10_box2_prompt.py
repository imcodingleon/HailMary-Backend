"""도윤 P-10 box2 — 사용자 알고싶은 영역 분석 AI prompt + validate.

동적 글자수: 선택 옵션 수에 비례 (1개 → ~450자, 4개 → ~900자).
페이지 라벨 언급 금지 — answer_data에 박힌 수치/keyword 직접 인용.
"""

from __future__ import annotations

from app.domains.ai.domain.templates.doyoon_p10_box_letter import (
    calc_box_length_range,
)

_BASE_MIN = 400
_BASE_MAX = 550


_SYSTEM_PROMPT_TPL = """\
당신은 도화선 캐릭터 한도윤 — 사주 데이터 분석가.

[페르소나]
- 존댓말, "{user_name}님" 호명 (자연스러운 분포)
- 어휘: 질문, 측정값, 변수, 답할 수 있는 영역, 데이터
- 분석적이되 답을 *지금 박스 안에서* 직접 풀어줄 것

[금지어]
- 신안, 기운, 살, 거머리, 결, 매듭, 명줄, 뿌리
- "네가" 반말 금지

[페이지 언급 절대 금지]
- "X장에서", "다음 장에서", "뒤에서 풀어드려요", "다음 페이지에서" 등 외부 참조 금지
- answer_data 블록에 박힌 사실값을 *지금 이 박스 안에서 직접 풀어줄 것*
- "다음에 알려드려요" 식의 약속도 금지

[사실값 보존]
- 사용자 이름: {user_name}
- 일간: {ilgan_full}({ilgan_hanja})
- 질문 영역 라벨: {step2_labels}
- 오행 보완: {ohang_lack}({ohang_lack_hanja})
- answer_data: 옵션별 답 데이터 (수치·시기·키워드 그대로 인용)

[구성] {step2_count}개 옵션 → {min_len}~{max_len}자, 단락 {min_para}~{max_para}개
1. 도입 — {user_name}님 호명 + 질문 영역 정리
2+. 옵션별 답 데이터 *지금 박스 안에서* 직접 풀이 (선택한 옵션 수에 비례)
N. 데이터 한계 + {user_name}님 클로징

[출력] 본문 텍스트만.
"""


_USER_PROMPT_TPL = """\
[사실값]
- user_name: {user_name}
- ilgan_full: {ilgan_full}
- ilgan_hanja: {ilgan_hanja}
- step2_count: {step2_count}
- step2_labels: {step2_labels}
- ohang_lack: {ohang_lack}
- ohang_lack_hanja: {ohang_lack_hanja}

[answer_data — 옵션별 답 사실값 (페이지 언급 X, 지금 박스 안에서 직접 풀이)]
{answer_data}

[룰 기반 텍스트]
{rule_text}

[요청] {min_len}~{max_len}자, {min_para}~{max_para}단락.
"""


_REQUIRED_KEYS = {
    "user_name", "ilgan_full", "ilgan_hanja",
    "step2_labels", "step2_count",
    "ohang_lack", "ohang_lack_hanja", "answer_data", "rule_text",
}


def _para_range(option_count: int) -> tuple[int, int]:
    return (3, 4) if option_count <= 2 else (4, 5)


def build_p10_box2_prompt(facts: dict[str, str]) -> tuple[str, str]:
    missing = _REQUIRED_KEYS - set(facts.keys())
    if missing:
        raise KeyError(f"missing facts keys: {sorted(missing)}")
    option_count = int(facts.get("step2_count", "1"))
    min_len, max_len = calc_box_length_range(option_count, base_min=_BASE_MIN, base_max=_BASE_MAX)
    min_para, max_para = _para_range(option_count)

    fmt_keys = {
        **{k: facts[k] for k in _REQUIRED_KEYS},
        "min_len": str(min_len),
        "max_len": str(max_len),
        "min_para": str(min_para),
        "max_para": str(max_para),
    }
    system = _SYSTEM_PROMPT_TPL.format(**fmt_keys)
    user = _USER_PROMPT_TPL.format(**fmt_keys)
    return system, user


def validate_p10_box2(text: str, facts: dict[str, str]) -> tuple[bool, str]:
    option_count = int(facts.get("step2_count", "1"))
    min_len, max_len = calc_box_length_range(option_count, base_min=_BASE_MIN, base_max=_BASE_MAX)
    soft_min = int(min_len * 0.85)
    soft_max = int(max_len * 1.15)

    length = len(text)
    if length < soft_min or length > soft_max:
        return False, f"length out of range: {length} (expected {soft_min}~{soft_max} for {option_count} options)"
    if facts["user_name"] not in text:
        return False, "user_name missing"
    if facts["ilgan_full"] not in text:
        return False, "ilgan_full missing"

    forbidden_page_terms = ["다음 장", "뒤 장", "앞 장", "장에서 풀", "장에서 알려", "다음 페이지", "뒤에서 풀"]
    for term in forbidden_page_terms:
        if term in text:
            return False, f"forbidden page reference: {term!r}"

    min_para, _ = _para_range(option_count)
    paragraph_breaks = text.count("\n\n")
    if paragraph_breaks < min_para - 1:
        return False, f"paragraph structure invalid: {paragraph_breaks} (expected >= {min_para - 1})"
    return True, ""
