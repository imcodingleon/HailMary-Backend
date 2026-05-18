"""도윤 P-1 일간 10셀 데이터 풀 snapshot/완전성 테스트."""

import pytest

from app.domains.ai.domain.value_object.doyoon_p1_data import (
    DOYOON_P1_DATA,
    VALID_DOYOON_P1_ILGAN,
    DoyoonP1IlganData,
)

EXPECTED_ILGANS = {"갑목", "을목", "병화", "정화", "무토", "기토", "경금", "신금", "임수", "계수"}


def test_10_data_present() -> None:
    assert set(DOYOON_P1_DATA.keys()) == EXPECTED_ILGANS
    assert frozenset(EXPECTED_ILGANS) == VALID_DOYOON_P1_ILGAN


def test_each_data_has_all_fields() -> None:
    for key, d in DOYOON_P1_DATA.items():
        assert isinstance(d, DoyoonP1IlganData)
        assert d.love_type
        assert 1 <= d.pct_value <= 30
        assert 5.0 <= d.distribution_pct <= 20.0
        assert d.trigger_1 and d.trigger_2 and d.trigger_3
        # 트리거 3개 서로 달라야
        assert len({d.trigger_1, d.trigger_2, d.trigger_3}) == 3, key
        # 감정 곡선 4 포인트 — 위기(3번째)가 최대값
        assert len(d.emotion_curve) == 4
        crisis = d.emotion_curve[2]
        assert crisis == max(d.emotion_curve), f"{key} crisis not max"
        assert all(0 <= p <= 100 for p in d.emotion_curve)
        assert "배" in d.crisis_multiplier
        assert 10 <= d.self_control_pct <= 50
        assert 20 <= d.expression_effect_pct <= 50


def test_data_is_frozen() -> None:
    import dataclasses

    d = DOYOON_P1_DATA["임수"]
    with pytest.raises(dataclasses.FrozenInstanceError):
        d.pct_value = 99  # type: ignore[misc]


def test_html_dummy_imsu_data() -> None:
    """HTML 도윤_final.html 임수 더미 케이스 매칭 — 8%, 12.4%, 1.8배, 자기조절 17%, 표현 효과 32%."""
    d = DOYOON_P1_DATA["임수"]
    assert d.pct_value == 8
    assert d.distribution_pct == 12.4
    assert d.crisis_multiplier == "1.8배"
    assert d.self_control_pct == 17
    assert d.expression_effect_pct == 32
    assert d.emotion_curve == (45, 85, 95, 60)
