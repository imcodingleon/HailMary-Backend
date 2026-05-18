"""P-10 system prompt dispatcher 단위 테스트.

build_p10_system_prompt가 persona.name으로 yeonwoo / doyoon builder에
정확히 위임하는지 + 도윤 user_name 가드 검증.
"""

import pytest

from app.domains.ai.domain.service.p10_letter_prompt import build_p10_system_prompt
from app.domains.ai.domain.value_object.character_persona import (
    DOYOON_PERSONA,
    YEONWOO_PERSONA,
)

_COMMON_KWARGS = {
    "ilgan": "병화(丙火)",
    "ilju": "병인(丙寅)",
    "ohang_excess": "화(火)",
    "ohang_lack": "토(土)",
    "box1_body": "박스 1 본문 샘플",
    "box2_body": "박스 2 본문 샘플",
    "step3": "테스트 고민 한 줄",
    "emphasis": "강조구 한 줄",
}


def test_yeonwoo_dispatcher_includes_natural_metaphor() -> None:
    system, user = build_p10_system_prompt(
        persona=YEONWOO_PERSONA, **_COMMON_KWARGS
    )
    # 연우는 자연 비유 키워드가 system에 박혀있어야
    assert "결" in system
    assert "매듭" in system
    # user에도 사용자 인용이 박힘
    assert "테스트 고민 한 줄" in user


def test_doyoon_dispatcher_includes_statistics_vocab() -> None:
    system, user = build_p10_system_prompt(
        persona=DOYOON_PERSONA, user_name="홍길동", **_COMMON_KWARGS
    )
    # 도윤은 통계 어휘가 박혀있어야
    assert "표본" in system
    assert "분포" in system
    # 호명이 user에 들어감
    assert "홍길동" in user


def test_doyoon_dispatcher_requires_user_name() -> None:
    with pytest.raises(ValueError, match="user_name"):
        build_p10_system_prompt(persona=DOYOON_PERSONA, **_COMMON_KWARGS)


def test_unknown_persona_raises() -> None:
    from app.domains.ai.domain.value_object.character_persona import CharacterPersona

    unknown = CharacterPersona(
        name="알수없음",
        role="테스트",
        signature_phrase="x",
        tone_hint="x",
    )
    with pytest.raises(ValueError, match="unknown persona"):
        build_p10_system_prompt(persona=unknown, **_COMMON_KWARGS)
