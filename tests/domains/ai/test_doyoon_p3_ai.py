"""도윤 P-3 2박스 AI 단위 테스트 — blockade + pattern."""

from __future__ import annotations

import pytest

from app.domains.ai.application.usecase.generate_p3_blockade_usecase import (
    GenerateP3BlockadeUseCase,
)
from app.domains.ai.application.usecase.generate_p3_pattern_usecase import (
    GenerateP3PatternUseCase,
)
from app.domains.ai.domain.port.ai_client_port import (
    AIClientError,
    AIClientPort,
)
from app.domains.ai.domain.service.doyoon_p3_blockade_prompt import (
    validate_p3_blockade,
)
from app.domains.ai.domain.service.doyoon_p3_pattern_prompt import (
    validate_p3_pattern,
)
from app.domains.ai.domain.templates.doyoon_p3_blocking import (
    compose_doyoon_p3_blockade,
    compose_doyoon_p3_pattern,
    get_doyoon_p3_blockade_facts,
    get_doyoon_p3_pattern_facts,
)
from app.domains.ai.domain.value_object.doyoon_p3_data import (
    BLOCKADE_BY_OHANG,
    DOYOON_P3_DATA,
    VALID_DOYOON_P3_ILGAN,
    VALID_DOYOON_P3_OHANG,
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


def test_all_5_ohang_blockade() -> None:
    assert len(BLOCKADE_BY_OHANG) == 5
    for oh in VALID_DOYOON_P3_OHANG:
        b = BLOCKADE_BY_OHANG[oh]
        assert b.ohang_hanja
        assert b.blockade_multiplier.endswith("배")


def test_all_10_ilgan_p3_data() -> None:
    assert len(DOYOON_P3_DATA) == 10
    for ilgan in VALID_DOYOON_P3_ILGAN:
        d = DOYOON_P3_DATA[ilgan]
        assert len(d.patterns) == 3
        assert len(d.strategies) == 2


def test_all_50_combos_compose_blockade() -> None:
    """10 일간 × 5 오행 = 50 조합 KeyError-free."""
    for ilgan in VALID_DOYOON_P3_ILGAN:
        for oh in VALID_DOYOON_P3_OHANG:
            text = compose_doyoon_p3_blockade(
                user_name="홍길동", ilgan=ilgan, ohang_excess=oh
            )
            assert "홍길동님" in text
            assert text.count("\n\n") == 2


def test_all_10_compose_pattern() -> None:
    for ilgan in VALID_DOYOON_P3_ILGAN:
        text = compose_doyoon_p3_pattern(user_name="홍길동", ilgan=ilgan)
        assert "홍길동님" in text


# ── BLOCKADE ─────────────────────────────────────────────────────


def test_blockade_facts_imsu_su() -> None:
    f = get_doyoon_p3_blockade_facts(user_name="홍길동", ilgan="임수", ohang_excess="수")
    assert f["ohang_excess_hanja"] == "水"
    assert f["blockade_pct"] == "상위 15%"
    assert f["blockade_multiplier"] == "1.7배"
    assert f["blockage_rate_drop"] == "36%"
    assert f["recovery_after_clearing_pct"] == "24%"


def _blockade_valid_text(facts: dict[str, str]) -> str:
    return (
        f"데이터부터 정리할게요. {facts['user_name']}님의 사주 구조에서 "
        f"{facts['ohang_excess']}({facts['ohang_excess_hanja']}) 기운이 평균 대비 "
        f"{facts['blockade_multiplier']}로 측정됩니다. 단순 강조 수준이 아니라 구조적으로 과다인 상태예요.\n\n"
        f"이게 새 인연 진입을 차단해요. 같은 결의 사람이 들어올 자리가 부족합니다. "
        f"동일 일간 표본에서 이 케이스의 신규 접촉률이 평균 대비 {facts['blockage_rate_drop']} 낮게 잡혀요. "
        "구조적 변수 누적이 원인이라 우연이 아니에요.\n\n"
        f"비우는 게 해법이에요. 사람이든 미련이든 답 안 오는 연락이든 하나만 정리해도 "
        f"진입률이 {facts['recovery_after_clearing_pct']} 회복돼요. "
        "기존 변수 감소가 신규 변수 추가보다 효율적인 영역입니다."
    )


def test_blockade_validate_passes() -> None:
    f = get_doyoon_p3_blockade_facts(user_name="홍길동", ilgan="임수", ohang_excess="수")
    ok, reason = validate_p3_blockade(_blockade_valid_text(f), f)
    assert ok, f"unexpected fail: {reason}"


def test_blockade_validate_fails_multiplier_mutated() -> None:
    f = get_doyoon_p3_blockade_facts(user_name="홍길동", ilgan="임수", ohang_excess="수")
    text = _blockade_valid_text(f).replace("1.7배", "1.6배")
    ok, reason = validate_p3_blockade(text, f)
    assert not ok
    assert "blockade_multiplier" in reason


@pytest.mark.asyncio
async def test_blockade_usecase_falls_back() -> None:
    fake = _FakeAIClient(raise_exc=AIClientError("simulated"))
    out = await GenerateP3BlockadeUseCase(ai_client=fake).execute(
        user_name="홍길동", ilgan="임수", ohang_excess="수"
    )
    assert "1.7배" in out
    assert "36%" in out


# ── PATTERN ──────────────────────────────────────────────────────


def test_pattern_facts_imsu() -> None:
    f = get_doyoon_p3_pattern_facts(user_name="홍길동", ilgan="임수")
    assert f["pattern_1_keyword"] == "초기 과진입"
    assert f["pattern_1_pct"] == "81%"
    assert f["pattern_2_keyword"] == "중반 무표현"
    assert f["pattern_3_keyword"] == "위기 일괄 폭발"
    assert f["stability_boost_pct"] == "41%"


def _pattern_valid_text(facts: dict[str, str]) -> str:
    return (
        f"{facts['user_name']}님의 반복 실수 패턴을 3단계로 분석해드릴게요.\n\n"
        f"1단계 — {facts['pattern_1_keyword']} (발생률 {facts['pattern_1_pct']}). "
        "첫 한 달 안에 감정 자원 과투입이 집중되는 구간입니다. "
        "평균 케이스보다 빠른 진입 속도가 잡혀요.\n\n"
        f"2단계 — {facts['pattern_2_keyword']} (발생률 {facts['pattern_2_pct']}). "
        "표현 빈도가 떨어지는 침묵 구간이에요. "
        f"3단계 — {facts['pattern_3_keyword']} (발생률 {facts['pattern_3_pct']}). 누적 감정 폭발 구간입니다.\n\n"
        f"{facts['ilgan_full']} 일간 특유의 패턴이에요. "
        f"1단계 속도만 평균선까지 조정해도 전체 안정성이 {facts['stability_boost_pct']} 향상됩니다."
    )


def test_pattern_validate_passes() -> None:
    f = get_doyoon_p3_pattern_facts(user_name="홍길동", ilgan="임수")
    ok, reason = validate_p3_pattern(_pattern_valid_text(f), f)
    assert ok, f"unexpected fail: {reason}"


@pytest.mark.asyncio
async def test_pattern_usecase_falls_back() -> None:
    fake = _FakeAIClient(raise_exc=AIClientError("simulated"))
    out = await GenerateP3PatternUseCase(ai_client=fake).execute(
        user_name="홍길동", ilgan="임수"
    )
    assert "초기 과진입" in out
    assert "81%" in out
