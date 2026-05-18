"""캐릭터 페르소나 value object snapshot 테스트.

YEONWOO_PERSONA / DOYOON_PERSONA 4 필드가 변경되면 P-10 system prompt 톤이
바뀌므로 의도적 변경만 허용 (테스트 갱신과 함께).
"""

from app.domains.ai.domain.value_object.character_persona import (
    DOYOON_PERSONA,
    YEONWOO_PERSONA,
    CharacterPersona,
)


def test_yeonwoo_persona_shape() -> None:
    assert isinstance(YEONWOO_PERSONA, CharacterPersona)
    assert YEONWOO_PERSONA.name == "강연우"
    assert YEONWOO_PERSONA.role == "사주 명리 상담사"
    assert "결" in YEONWOO_PERSONA.signature_phrase
    assert "매듭" in YEONWOO_PERSONA.signature_phrase


def test_doyoon_persona_shape() -> None:
    assert isinstance(DOYOON_PERSONA, CharacterPersona)
    assert DOYOON_PERSONA.name == "한도윤"
    assert DOYOON_PERSONA.role == "사주 데이터 분석가"
    assert "표본" in DOYOON_PERSONA.signature_phrase
    assert "분포" in DOYOON_PERSONA.signature_phrase
    assert "존댓말" in DOYOON_PERSONA.tone_hint


def test_personas_are_frozen() -> None:
    """value object — 불변성 보장 (@dataclass(frozen=True))."""
    import dataclasses

    import pytest

    with pytest.raises(dataclasses.FrozenInstanceError):
        YEONWOO_PERSONA.name = "해킹"  # type: ignore[misc]
