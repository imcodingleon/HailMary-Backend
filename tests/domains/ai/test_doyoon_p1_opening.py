"""도윤 P-1 1-1 오프닝 합성 단위 테스트."""

import pytest

from app.domains.ai.domain.templates.doyoon_p1_opening import compose_doyoon_p1_opening
from app.domains.ai.domain.value_object.doyoon_p1_data import VALID_DOYOON_P1_ILGAN


def test_user_name_required() -> None:
    with pytest.raises(ValueError, match="user_name"):
        compose_doyoon_p1_opening(
            user_name="", ilgan="임수", ilju="임술(壬戌)"
        )


def test_unknown_ilgan_raises() -> None:
    with pytest.raises(KeyError):
        compose_doyoon_p1_opening(
            user_name="홍길동", ilgan="모름", ilju="임술(壬戌)"
        )


def test_html_dummy_imsu_case() -> None:
    out = compose_doyoon_p1_opening(
        user_name="홍길동", ilgan="임수", ilju="임술(壬戌)"
    )
    assert "홍길동님" in out
    assert "상위 8%" in out
    assert "임수" in out
    assert "12.4%" in out
    assert "정보 처리형" in out  # love_type
    assert "임술(壬戌)" in out
    # 4단락 구조
    assert out.count("\n\n") == 3


def test_length_range_10_ilgans() -> None:
    for ilgan in VALID_DOYOON_P1_ILGAN:
        out = compose_doyoon_p1_opening(
            user_name="홍길동", ilgan=ilgan, ilju="임술(壬戌)"
        )
        length = len(out)
        assert 300 <= length <= 450, f"ilgan={ilgan} length={length}"
        assert "홍길동님" in out
