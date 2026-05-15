"""P-0 0-5 첫인사 22조각 템플릿 합성 검증."""

import pytest

from app.domains.ai.domain.templates.yeonwoo_p0_intro import (
    ILGAN_PARA_2,
    OHANG_EXCESS_PARA_3,
    OHANG_LACK_PARA_4,
    PARA_1_OPENING,
    PARA_5_CLOSING,
    VALID_ILGAN,
    VALID_OHANG,
    compose_p0_intro,
)

# 일간 10종 + 오행 5종 키 검증
EXPECTED_ILGAN = {
    "갑목", "을목", "병화", "정화", "무토",
    "기토", "경금", "신금", "임수", "계수",
}

EXPECTED_OHANG = {"목", "화", "토", "금", "수"}


def test_ilgan_dict_has_exactly_10_keys() -> None:
    assert set(ILGAN_PARA_2.keys()) == EXPECTED_ILGAN
    assert len(ILGAN_PARA_2) == 10


def test_ohang_excess_dict_has_exactly_5_keys() -> None:
    assert set(OHANG_EXCESS_PARA_3.keys()) == EXPECTED_OHANG
    assert len(OHANG_EXCESS_PARA_3) == 5


def test_ohang_lack_dict_has_exactly_5_keys() -> None:
    assert set(OHANG_LACK_PARA_4.keys()) == EXPECTED_OHANG
    assert len(OHANG_LACK_PARA_4) == 5


def test_valid_constants_match_dict_keys() -> None:
    assert VALID_ILGAN == EXPECTED_ILGAN
    assert VALID_OHANG == EXPECTED_OHANG


def test_para1_and_para5_are_fixed() -> None:
    assert "촛불 앞에 앉으니까" in PARA_1_OPENING
    assert "다음 장부터" in PARA_5_CLOSING


@pytest.mark.parametrize("ilgan", sorted(EXPECTED_ILGAN))
def test_each_ilgan_text_contains_hanja(ilgan: str) -> None:
    text = ILGAN_PARA_2[ilgan]
    # 강연우 톤: "갑목(甲木) 일간이라..." 형태로 한자 병기.
    assert "(" in text and ")" in text
    assert "일간이라" in text


@pytest.mark.parametrize("ohang", sorted(EXPECTED_OHANG))
def test_each_ohang_excess_text_contains_hanja(ohang: str) -> None:
    text = OHANG_EXCESS_PARA_3[ohang]
    assert "(" in text and ")" in text


@pytest.mark.parametrize("ohang", sorted(EXPECTED_OHANG))
def test_each_ohang_lack_text_mentions_emptiness(ohang: str) -> None:
    text = OHANG_LACK_PARA_4[ohang]
    assert "비어 있어서" in text
    assert "흘러내리는" in text


# 합성 함수 검증
def test_compose_returns_5_paragraphs_separated_by_blank_line() -> None:
    result = compose_p0_intro(
        ilgan="임수", ohang_excess="수", ohang_lack="토"
    )
    paragraphs = result.split("\n\n")
    assert len(paragraphs) == 5


def test_compose_html_dummy_case_matches_html_phrases() -> None:
    """HTML 더미 케이스(임수 + 수 과다 + 토 부족) 합성 결과 검증.

    HTML line 1669~1675의 더미 응답과 같은 핵심 문구가 들어가야 함.
    """
    result = compose_p0_intro(
        ilgan="임수", ohang_excess="수", ohang_lack="토"
    )
    assert "촛불 앞에 앉으니까" in result
    assert "임수(壬水) 일간이라" in result
    assert "수(水)가 너무 넘쳐서" in result
    assert "토(土)가 비어 있어서" in result
    assert "다음 장부터" in result


@pytest.mark.parametrize(
    "ilgan,excess,lack",
    [
        ("갑목", "화", "금"),
        ("을목", "수", "토"),
        ("병화", "토", "수"),
        ("정화", "토", "수"),
        ("무토", "수", "목"),
        ("기토", "금", "목"),
        ("경금", "목", "화"),
        ("신금", "화", "수"),
        ("임수", "수", "토"),  # HTML 더미
        ("계수", "금", "목"),
    ],
)
def test_compose_length_within_html_spec(
    ilgan: str, excess: str, lack: str
) -> None:
    """HTML 명세 분량(공백 포함 200~350자) 범위 검증 (10종 spot check).

    문단 구분 \\n\\n은 제거하고 본문 길이만 확인 (분리 표기는 분량에 포함 X).
    상한 갱신: 2026-05-15 "키우다" 표현 정리 + 함께 성장하다 등 카피 다양화로
    의도적으로 330자대까지 늘어남. 일간/오행 조합에 따라 자연 변동, 운영 정상.
    """
    result = compose_p0_intro(
        ilgan=ilgan, ohang_excess=excess, ohang_lack=lack
    )
    # 문단 구분 개행만 제거, 본문 공백은 유지.
    body_len = len(result.replace("\n", ""))
    assert 200 <= body_len <= 350, (
        f"분량 범위 벗어남: {ilgan}+{excess}+{lack} = {body_len}자"
    )


def test_unknown_ilgan_raises_keyerror() -> None:
    with pytest.raises(KeyError, match="ilgan"):
        compose_p0_intro(ilgan="없는일간", ohang_excess="수", ohang_lack="토")


def test_unknown_ohang_excess_raises_keyerror() -> None:
    with pytest.raises(KeyError, match="ohang_excess"):
        compose_p0_intro(ilgan="임수", ohang_excess="X", ohang_lack="토")


def test_unknown_ohang_lack_raises_keyerror() -> None:
    with pytest.raises(KeyError, match="ohang_lack"):
        compose_p0_intro(ilgan="임수", ohang_excess="수", ohang_lack="X")
