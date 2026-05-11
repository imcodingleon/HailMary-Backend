"""compose_paid_report_usecase 회귀 테스트.

end-to-end: saju_raw → PaidChaptersResponse (P-0~P-5).
백엔드 templates·service 직접 변경 없이 orchestrator만 검증.
"""

from __future__ import annotations

from typing import Any

from app.domains.ai.application.usecase.compose_paid_report_usecase import (
    ComposePaidReportUseCase,
)


def _imsu_saju() -> dict[str, Any]:
    """임수(壬) 일간 + 수 과다 + 토 부족 fixture.

    spouse_avoid (yongSin 없음, day.stemElement="수"→상극 "화"): female →
    slot_id = 'm-fire-yang' (gender 'female' → opposite 'm', stemElement '수'→상극 '화', day.yinYang '양').
    """
    return {
        "year": {"stem": "임", "branch": "신", "stemElement": "수", "yinYang": "양"},
        "month": {"stem": "임", "branch": "자", "stemElement": "수", "yinYang": "양"},
        "day": {"stem": "임", "branch": "술", "stemElement": "수", "yinYang": "양"},
        "hour": {"stem": "임", "branch": "인", "stemElement": "수", "yinYang": "양"},
        "wuxingCount": {"목": 1, "화": 0, "토": 1, "금": 1, "수": 5},
        "gender": "female",
        "sinSals": [],
        "tenGodsDistribution": {},
    }


def test_compose_returns_p0_to_p5() -> None:
    usecase = ComposePaidReportUseCase()
    res = usecase.execute(_imsu_saju())

    # P-0
    assert res.p0 is not None
    assert res.p0.ilgan == "임수"
    assert res.p0.saju_pillars.il_g == "壬"
    assert res.p0.saju_pillars.il_j == "戌"
    assert res.p0.ohang_excess == "su"
    assert res.p0.ohang_lack == "hwa"
    assert res.p0.ohang_strength.su == max(
        res.p0.ohang_strength.mok,
        res.p0.ohang_strength.hwa,
        res.p0.ohang_strength.to,
        res.p0.ohang_strength.geum,
        res.p0.ohang_strength.su,
    )
    assert res.p0.ilgan_card.name_han == "壬水"
    assert res.p0.ai_intro  # non-empty 5문단

    # P-1
    assert res.p1 is not None
    assert res.p1.ilgan == "임수(壬水)"
    assert res.p1.ilju == "임술(壬戌)"
    assert len(res.p1.candle_rows) == 3
    assert any(r.is_peak for r in res.p1.candle_rows)
    assert res.p1.ai_opening and res.p1.ai_trigger and res.p1.ai_emotion

    # P-2
    assert res.p2 is not None
    assert res.p2.scenario_1_when and res.p2.scenario_2_when
    assert len(res.p2.recovery_timeline) == 3
    assert res.p2.recovery_accel.value

    # P-3
    assert res.p3 is not None
    assert "水" in res.p3.ohang_excess  # 한자 포함
    assert res.p3.reverse_card_1.value and res.p3.reverse_card_2.value

    # P-4 (spouse_avoid slotId = 'm-fire-yang' → VALID_SLOTID)
    assert res.p4 is not None
    assert res.p4.akyon_slot_id == "m-fire-yang"
    assert len(res.p4.akyon_keyword_tags) == 5
    assert len(res.p4.akyon_info_rows) == 6
    assert len(res.p4.illusion_signals) == 3
    assert res.p4.illusion_good_card.value

    # P-5
    assert res.p5 is not None
    assert 0 <= res.p5.charm_score <= 100
    assert 0 <= res.p5.charm_percentile <= 100
    assert res.p5.ai_charm and res.p5.ai_mechanism and res.p5.ai_sense
    assert len(res.p5.stage_cards) == 4
    assert len(res.p5.point_cards) == 3


def test_compose_neutral_slot_returns_p4_none() -> None:
    """yongSin/stemElement 모두 없으면 slotId='neutral' → P-4 None."""
    saju = _imsu_saju()
    saju["day"].pop("stemElement", None)  # spouse_avoid가 neutral 반환
    res = ComposePaidReportUseCase().execute(saju)
    assert res.p0 is not None
    assert res.p4 is None  # P-4만 빠지고 나머지는 채워짐


def test_compose_returns_empty_when_ilgan_missing() -> None:
    """일간 추출 실패 시 모든 chapters None."""
    saju = _imsu_saju()
    saju["day"] = {}  # day 비움 → ILGAN/ILJU 빈 문자열
    res = ComposePaidReportUseCase().execute(saju)
    assert res.p0 is None
    assert res.p1 is None
    assert res.p5 is None
