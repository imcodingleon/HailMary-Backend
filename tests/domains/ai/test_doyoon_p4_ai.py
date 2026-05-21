"""도윤 P-4 2박스 AI 단위 테스트 — akyon + illusion."""

from __future__ import annotations

import pytest

from app.domains.ai.application.usecase.generate_p4_akyon_usecase import (
    GenerateP4AkyonUseCase,
)
from app.domains.ai.application.usecase.generate_p4_illusion_usecase import (
    GenerateP4IllusionUseCase,
)
from app.domains.ai.domain.port.ai_client_port import (
    AIClientError,
    AIClientPort,
)
from app.domains.ai.domain.service.doyoon_p4_akyon_prompt import (
    validate_p4_akyon,
)
from app.domains.ai.domain.service.doyoon_p4_illusion_prompt import (
    validate_p4_illusion,
)
from app.domains.ai.domain.templates.doyoon_p4_blocking2 import (
    compose_doyoon_p4_akyon,
    compose_doyoon_p4_illusion,
    get_doyoon_p4_akyon_facts,
    get_doyoon_p4_illusion_facts,
)
from app.domains.ai.domain.value_object.doyoon_p4_data import (
    DOYOON_AKYON_BY_SLOT,
    DOYOON_P4_DATA,
    VALID_DOYOON_P4_ILGAN,
)


class _FakeAIClient(AIClientPort):
    def __init__(self, *, response_text: str | None = None, raise_exc: Exception | None = None) -> None:
        self.response_text = response_text
        self.raise_exc = raise_exc

    async def generate_chapter(
        self, *, system_prompt, user_prompt, max_tokens=1024, temperature=0.85, model=None
    ) -> str:
        if self.raise_exc is not None:
            raise self.raise_exc
        assert self.response_text is not None
        return self.response_text


# ── 데이터 완전성 ─────────────────────────────────────────────────


def test_all_22_slots_have_akyon_data() -> None:
    """20 slot (성별 2 × 오행 5 × 음양 2) + 2 neutral."""
    assert len(DOYOON_AKYON_BY_SLOT) == 22


def test_all_10_ilgan_p4_data() -> None:
    assert len(DOYOON_P4_DATA) == 10
    for ilgan in VALID_DOYOON_P4_ILGAN:
        d = DOYOON_P4_DATA[ilgan]
        assert len(d.illusion_signs) == 3


def test_all_22_slots_compose_akyon() -> None:
    for slot in DOYOON_AKYON_BY_SLOT:
        text = compose_doyoon_p4_akyon(
            user_name="홍길동", ilgan="임수", akyon_slot_id=slot
        )
        assert "홍길동님" in text


def test_compose_illusion_all_ilgan() -> None:
    for ilgan in VALID_DOYOON_P4_ILGAN:
        text = compose_doyoon_p4_illusion(user_name="홍길동", ilgan=ilgan)
        assert "홍길동님" in text


def test_compose_akyon_unknown_slot_fallback() -> None:
    """unknown slot은 m-water-yang으로 fallback."""
    text = compose_doyoon_p4_akyon(
        user_name="홍길동", ilgan="임수", akyon_slot_id="m-unknown-yang"
    )
    assert "64%" in text  # m-water-yang의 height_distribution_pct


# ── AKYON ────────────────────────────────────────────────────────


def test_akyon_facts_imsu() -> None:
    f = get_doyoon_p4_akyon_facts(
        user_name="홍길동", ilgan="임수", akyon_slot_id="m-water-yang"
    )
    assert f["impression_first"] == "91"
    assert f["impression_6m"] == "14"
    assert f["impression_gap"] == "77"
    assert f["height_distribution_pct"] == "64%"
    assert f["common_signal_pct"] == "71%"


def _akyon_valid_text(facts: dict[str, str]) -> str:
    return (
        "데이터가 분류한 비호환 프로파일이에요. 외형부터 정리해드릴게요.\n\n"
        f"키 분포 — 평균보다 +5cm 이상 표본이 {facts['height_distribution_pct']}. "
        f"체형은 마른 골격에 어깨가 좁은 편. 얼굴 데이터는 광대 도드라짐, 턱선 각짐. "
        f"동일 비호환 사례의 {facts['common_signal_pct']}를 차지하는 패턴입니다.\n\n"
        f"문제는 인상 점수 격차예요. 첫인상 {facts['impression_first']}점, "
        f"6개월 호감 {facts['impression_6m']}점, 격차 {facts['impression_gap']}점. "
        "평균 격차 32점 대비 두 배 이상입니다.\n\n"
        f"{facts['ilgan_full']} 일간과의 감정 주파수 불일치율이 87%로 측정돼요. "
        "초기 신호 두 개 이상 보이면 즉시 거리 조정 권장. "
        f"{facts['user_name']}님 매력을 낭비하기엔 아까운 유형입니다."
    )


def test_akyon_validate_passes() -> None:
    f = get_doyoon_p4_akyon_facts(
        user_name="홍길동", ilgan="임수", akyon_slot_id="m-water-yang"
    )
    ok, reason = validate_p4_akyon(_akyon_valid_text(f), f)
    assert ok, f"unexpected fail: {reason}"


def test_akyon_validate_fails_gap_mutated() -> None:
    f = get_doyoon_p4_akyon_facts(
        user_name="홍길동", ilgan="임수", akyon_slot_id="m-water-yang"
    )
    text = _akyon_valid_text(f).replace("77점", "76점")
    ok, reason = validate_p4_akyon(text, f)
    assert not ok
    assert "impression_gap" in reason


@pytest.mark.asyncio
async def test_akyon_usecase_falls_back() -> None:
    fake = _FakeAIClient(raise_exc=AIClientError("simulated"))
    out = await GenerateP4AkyonUseCase(ai_client=fake).execute(
        user_name="홍길동", ilgan="임수", akyon_slot_id="m-water-yang"
    )
    assert "91" in out
    assert "77" in out


# ── ILLUSION ─────────────────────────────────────────────────────


def test_illusion_facts_imsu() -> None:
    f = get_doyoon_p4_illusion_facts(user_name="홍길동", ilgan="임수")
    assert f["illusion_multiplier"] == "1.3배"
    assert f["sign_1_keyword"] == "첫 만남 점수 90+"
    assert f["sign_1_pct"] == "78%"
    assert f["real_growth_pct"] == "+18%"
    assert f["fake_drop_pct"] == "-38%"
    assert f["accuracy_multiplier"] == "9배"


def _illusion_valid_text(facts: dict[str, str]) -> str:
    return (
        f"{facts['ilgan_full']} 일간 표본에서 착각 인연 발생률이 평균보다 "
        f"{facts['illusion_multiplier']} 높게 측정됩니다. "
        "초기 강한 끌림을 운명으로 오인하는 경향이 통계적으로 유의미해요.\n\n"
        f"핵심은 3개월차 기울기예요. 진짜 인연은 호감도 {facts['real_growth_pct']} 상승, "
        f"착각 인연은 {facts['fake_drop_pct']} 하락. 이 기울기가 첫 만남 점수보다 "
        f"{facts['accuracy_multiplier']} 더 정확한 지표입니다.\n\n"
        f"오인 신호 — {facts['sign_1_keyword']} (발생률 {facts['sign_1_pct']}), "
        f"{facts['sign_2_keyword']} (발생률 {facts['sign_2_pct']}), "
        f"{facts['sign_3_keyword']} (발생률 {facts['sign_3_pct']}). 두 가지 이상이면 검증 진입.\n\n"
        f"{facts['user_name']}님, 3개월 기다리는 게 가장 정확한 검증법입니다."
    )


def test_illusion_validate_passes() -> None:
    f = get_doyoon_p4_illusion_facts(user_name="홍길동", ilgan="임수")
    ok, reason = validate_p4_illusion(_illusion_valid_text(f), f)
    assert ok, f"unexpected fail: {reason}"


@pytest.mark.asyncio
async def test_illusion_usecase_falls_back() -> None:
    fake = _FakeAIClient(raise_exc=AIClientError("simulated"))
    out = await GenerateP4IllusionUseCase(ai_client=fake).execute(
        user_name="홍길동", ilgan="임수"
    )
    assert "+18%" in out
    assert "-38%" in out
