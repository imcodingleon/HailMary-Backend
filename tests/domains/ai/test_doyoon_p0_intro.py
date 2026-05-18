"""도윤 P-0 0-5 4단락 합성 단위 테스트.

분량 범위 + 변수 박힘 + 250 조합 KeyError-free + 가드 케이스.
"""

import pytest

from app.domains.ai.domain.templates.doyoon_p0_intro import (
    OHANG_EXCESS_IMPACT,
    VALID_DOYOON_P0_ILGAN,
    VALID_DOYOON_P0_OHANG,
    compose_doyoon_p0_intro,
)


def test_user_name_required() -> None:
    with pytest.raises(ValueError, match="user_name"):
        compose_doyoon_p0_intro(
            user_name="", ilgan="임수", ohang_excess="수", ohang_lack="토"
        )


def test_unknown_ilgan_raises() -> None:
    with pytest.raises(KeyError):
        compose_doyoon_p0_intro(
            user_name="홍길동", ilgan="모름", ohang_excess="수", ohang_lack="토"
        )


def test_unknown_ohang_raises() -> None:
    with pytest.raises(KeyError):
        compose_doyoon_p0_intro(
            user_name="홍길동", ilgan="임수", ohang_excess="모름", ohang_lack="토"
        )


def test_html_dummy_case() -> None:
    """HTML 도윤_final 더미: 홍길동 + 임수 + 수 과다 + 토 부족."""
    out = compose_doyoon_p0_intro(
        user_name="홍길동", ilgan="임수", ohang_excess="수", ohang_lack="토"
    )
    assert "홍길동님" in out
    assert "임수(壬水)" in out
    assert "수(水)" in out
    assert "토(土)" in out
    assert "36%" in out  # 수 과다 IMPACT
    # 4단락 구조
    assert out.count("\n\n") == 3


def test_length_range_in_dummy_case() -> None:
    out = compose_doyoon_p0_intro(
        user_name="홍길동", ilgan="임수", ohang_excess="수", ohang_lack="토"
    )
    # HTML 명세: 220~300자. 단락 사이 \\n\\n 4 글자 포함.
    length = len(out)
    assert 220 <= length <= 350, f"out length={length}, expected 220~350"


def test_250_combinations_all_compose() -> None:
    """10 일간 × 5 과다 × 5 부족 = 250 조합 KeyError 없음."""
    for ilgan in VALID_DOYOON_P0_ILGAN:
        for excess in VALID_DOYOON_P0_OHANG:
            for lack in VALID_DOYOON_P0_OHANG:
                out = compose_doyoon_p0_intro(
                    user_name="테스트",
                    ilgan=ilgan,
                    ohang_excess=excess,
                    ohang_lack=lack,
                )
                assert "테스트님" in out
                # 단락 4개 분리
                assert out.count("\n\n") == 3


def test_impact_per_excess() -> None:
    """과다 오행 5종 IMPACT 문구가 단락 3에 박힘."""
    for excess in VALID_DOYOON_P0_OHANG:
        out = compose_doyoon_p0_intro(
            user_name="테스트",
            ilgan="임수",
            ohang_excess=excess,
            ohang_lack="토",
        )
        assert OHANG_EXCESS_IMPACT[excess] in out


def test_length_range_10_spot_check() -> None:
    """일간 10종 × 임의 오행 조합 분량 범위 검증."""
    for ilgan in VALID_DOYOON_P0_ILGAN:
        out = compose_doyoon_p0_intro(
            user_name="홍길동",
            ilgan=ilgan,
            ohang_excess="수",
            ohang_lack="토",
        )
        length = len(out)
        assert 220 <= length <= 360, f"ilgan={ilgan} length={length}"
