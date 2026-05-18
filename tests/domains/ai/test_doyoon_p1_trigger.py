"""도윤 P-1 1-2 트리거 메커니즘 합성 테스트."""

import pytest

from app.domains.ai.domain.templates.doyoon_p1_trigger import compose_doyoon_p1_trigger
from app.domains.ai.domain.value_object.doyoon_p1_data import (
    DOYOON_P1_DATA,
    VALID_DOYOON_P1_ILGAN,
)


def test_user_name_required() -> None:
    with pytest.raises(ValueError, match="user_name"):
        compose_doyoon_p1_trigger(user_name="", ilgan="임수")


def test_unknown_ilgan_raises() -> None:
    with pytest.raises(KeyError):
        compose_doyoon_p1_trigger(user_name="홍길동", ilgan="모름")


def test_html_dummy_imsu_case() -> None:
    out = compose_doyoon_p1_trigger(user_name="홍길동", ilgan="임수")
    assert "홍길동님" in out
    assert "88%" in out  # 임계점 도달
    assert "17%" in out  # 자기조절
    data = DOYOON_P1_DATA["임수"]
    assert data.trigger_1 in out
    assert data.trigger_2 in out
    # 2단락 구조
    assert out.count("\n\n") == 1


def test_length_range_10_ilgans() -> None:
    for ilgan in VALID_DOYOON_P1_ILGAN:
        out = compose_doyoon_p1_trigger(user_name="홍길동", ilgan=ilgan)
        length = len(out)
        assert 180 <= length <= 280, f"ilgan={ilgan} length={length}"
        data = DOYOON_P1_DATA[ilgan]
        assert str(data.self_control_pct) in out
        assert data.trigger_1 in out
        assert data.trigger_2 in out
