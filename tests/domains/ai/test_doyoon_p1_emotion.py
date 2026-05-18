"""도윤 P-1 1-3 감정 곡선 합성 테스트."""

import pytest

from app.domains.ai.domain.templates.doyoon_p1_emotion import compose_doyoon_p1_emotion
from app.domains.ai.domain.value_object.doyoon_p1_data import (
    DOYOON_P1_DATA,
    VALID_DOYOON_P1_ILGAN,
)


def test_user_name_required() -> None:
    with pytest.raises(ValueError, match="user_name"):
        compose_doyoon_p1_emotion(user_name="", ilgan="임수")


def test_unknown_ilgan_raises() -> None:
    with pytest.raises(KeyError):
        compose_doyoon_p1_emotion(user_name="홍길동", ilgan="모름")


def test_html_dummy_imsu_case() -> None:
    out = compose_doyoon_p1_emotion(user_name="홍길동", ilgan="임수")
    # 위기 95%, 1.8배, 회복 60%, 표현 효과 32%
    assert "95%" in out
    assert "1.8배" in out
    assert "60%" in out
    assert "32%" in out
    # 3단락
    assert out.count("\n\n") == 2


def test_length_range_10_ilgans() -> None:
    for ilgan in VALID_DOYOON_P1_ILGAN:
        out = compose_doyoon_p1_emotion(user_name="홍길동", ilgan=ilgan)
        length = len(out)
        assert 230 <= length <= 330, f"ilgan={ilgan} length={length}"
        data = DOYOON_P1_DATA[ilgan]
        # 위기 % 박힘
        assert f"{data.emotion_curve[2]}%" in out
        assert data.crisis_multiplier in out
        assert ilgan in out
