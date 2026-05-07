"""P-0 첫인사 프롬프트 빌더 단위 테스트.

검증 포인트:
- (system, user) 튜플 반환
- 입력 변수가 user prompt에 그대로 박힘
- system prompt에 강연우 페르소나 핵심 단어 존재
- 분량 제약 220~280자가 user prompt에 명시
"""

from app.domains.ai.domain.service.prompts.yeonwoo_p0_intro import (
    YEONWOO_SYSTEM_PROMPT,
    build_p0_intro_prompt,
)


def test_returns_system_user_pair() -> None:
    system, user = build_p0_intro_prompt(
        ilgan="임수", ohang_excess="수", ohang_lack="토"
    )
    assert system == YEONWOO_SYSTEM_PROMPT
    assert isinstance(user, str)
    assert len(user) > 0


def test_user_prompt_contains_input_variables() -> None:
    system, user = build_p0_intro_prompt(
        ilgan="갑목", ohang_excess="목", ohang_lack="금"
    )
    assert "갑목" in user
    assert "목" in user
    assert "금" in user
    assert "ILGAN" in user
    assert "OHANG_EXCESS" in user
    assert "OHANG_LACK" in user


def test_user_prompt_specifies_length_constraint() -> None:
    _, user = build_p0_intro_prompt(
        ilgan="병화", ohang_excess="화", ohang_lack="수"
    )
    assert "220" in user
    assert "280" in user


def test_system_prompt_carries_yeonwoo_persona() -> None:
    system, _ = build_p0_intro_prompt(
        ilgan="정화", ohang_excess="화", ohang_lack="수"
    )
    assert "강연우" in system
    assert "반말" in system


def test_user_prompt_describes_4_section_structure() -> None:
    _, user = build_p0_intro_prompt(
        ilgan="무토", ohang_excess="토", ohang_lack="목"
    )
    for marker in ("①", "②", "③", "④"):
        assert marker in user
