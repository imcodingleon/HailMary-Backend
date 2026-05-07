"""일간 10종 카드 정적 풀 단위 테스트.

검증 포인트:
- 10종 모두 dict에 존재
- 각 카드 필드 비어있지 않음
- 연애 불릿 정확히 3개
- 합산 분량 130~150자 가이드 (약간 여유 ±10자 허용)
"""

import pytest

from app.domains.ai.domain.value_object.ilgan_cards import (
    ILGAN_CARDS,
    VALID_ILGAN_NAMES,
    get_ilgan_card,
)

EXPECTED_ILGAN: tuple[str, ...] = (
    "갑목", "을목", "병화", "정화",
    "무토", "기토", "경금", "신금",
    "임수", "계수",
)


def test_all_ten_ilgan_present() -> None:
    assert set(ILGAN_CARDS.keys()) == set(EXPECTED_ILGAN)
    assert frozenset(EXPECTED_ILGAN) == VALID_ILGAN_NAMES


@pytest.mark.parametrize("ilgan", EXPECTED_ILGAN)
def test_card_fields_non_empty(ilgan: str) -> None:
    card = get_ilgan_card(ilgan)
    assert card.name_kor == ilgan
    assert card.name_han, "한자 표기 비어있음"
    assert card.subtitle, "부제 비어있음"
    assert card.essence, "결 본문 비어있음"
    assert card.caution, "주의 본문 비어있음"


@pytest.mark.parametrize("ilgan", EXPECTED_ILGAN)
def test_in_love_has_exactly_three_bullets(ilgan: str) -> None:
    card = get_ilgan_card(ilgan)
    assert len(card.in_love) == 3
    for bullet in card.in_love:
        assert bullet, "불릿 비어있음"


@pytest.mark.parametrize("ilgan", EXPECTED_ILGAN)
def test_total_length_within_guide(ilgan: str) -> None:
    """결 + 3불릿 + 주의 합산 약 130~150자 (가이드).

    HTML 임수 더미 기준 ~130자. 일간별 결 차이로 ±10자 허용.
    """
    card = get_ilgan_card(ilgan)
    total = card.total_length()
    assert 110 <= total <= 170, f"{ilgan} 분량 {total}자 — 가이드 130~150자 벗어남"


def test_get_unknown_ilgan_raises() -> None:
    with pytest.raises(KeyError):
        get_ilgan_card("토끼")
