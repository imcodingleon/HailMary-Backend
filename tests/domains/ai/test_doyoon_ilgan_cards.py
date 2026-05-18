"""도윤 일간 카드 10종 snapshot/완전성 테스트."""

import pytest

from app.domains.ai.domain.value_object.doyoon_ilgan_cards import (
    DOYOON_ILGAN_CARDS,
    VALID_DOYOON_ILGAN,
    DoyoonIlganCard,
)

EXPECTED_ILGANS = {"갑목", "을목", "병화", "정화", "무토", "기토", "경금", "신금", "임수", "계수"}


def test_10_cards_present() -> None:
    assert set(DOYOON_ILGAN_CARDS.keys()) == EXPECTED_ILGANS
    assert frozenset(EXPECTED_ILGANS) == VALID_DOYOON_ILGAN


def test_each_card_has_all_fields() -> None:
    for key, card in DOYOON_ILGAN_CARDS.items():
        assert isinstance(card, DoyoonIlganCard)
        assert card.name_kor == key
        assert len(card.name_han) == 2  # 한자 2글자
        assert card.subtitle
        assert len(card.data_traits) == 3
        assert all(t for t in card.data_traits)
        assert len(card.love_variables) == 3
        assert all(v for v in card.love_variables)
        assert card.main_conflict


def test_cards_are_frozen() -> None:
    import dataclasses

    card = DOYOON_ILGAN_CARDS["임수"]
    with pytest.raises(dataclasses.FrozenInstanceError):
        card.name_kor = "해킹"  # type: ignore[misc]


def test_html_dummy_imsu_card_shape() -> None:
    """HTML 도윤_final 더미 임수 카드와 정확히 일치."""
    card = DOYOON_ILGAN_CARDS["임수"]
    assert card.name_kor == "임수"
    assert card.name_han == "壬水"
    assert "큰 물" in card.subtitle
    assert "1.7배" in card.data_traits[0]
    assert "0.4배" in card.data_traits[1]
