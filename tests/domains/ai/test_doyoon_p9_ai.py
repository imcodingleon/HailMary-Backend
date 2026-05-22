"""도윤 P-9 3박스 AI 단위 테스트 — ohang + risk + optimize."""

from __future__ import annotations

import pytest

from app.domains.ai.application.usecase.generate_p9_ohang_usecase import (
    GenerateP9OhangUseCase,
)
from app.domains.ai.application.usecase.generate_p9_optimize_usecase import (
    GenerateP9OptimizeUseCase,
)
from app.domains.ai.application.usecase.generate_p9_risk_usecase import (
    GenerateP9RiskUseCase,
)
from app.domains.ai.domain.port.ai_client_port import AIClientError, AIClientPort
from app.domains.ai.domain.service.doyoon_p9_ohang_prompt import validate_p9_ohang
from app.domains.ai.domain.service.doyoon_p9_optimize_prompt import validate_p9_optimize
from app.domains.ai.domain.service.doyoon_p9_risk_prompt import validate_p9_risk
from app.domains.ai.domain.templates.doyoon_p9_optimize import (
    compose_doyoon_p9_ohang,
    compose_doyoon_p9_optimize,
    compose_doyoon_p9_risk,
    get_doyoon_p9_ohang_facts,
    get_doyoon_p9_optimize_facts,
    get_doyoon_p9_risk_facts,
)
from app.domains.ai.domain.value_object.doyoon_p9_data import (
    DOYOON_P9_DATA,
    RISK_CARDS,
    VALID_DOYOON_P9_ILGAN,
    get_ohang_methods,
)


class _FakeAIClient(AIClientPort):
    def __init__(self, *, response_text=None, raise_exc=None):
        self.response_text = response_text
        self.raise_exc = raise_exc

    async def generate_chapter(self, *, system_prompt, user_prompt, max_tokens=1024, temperature=0.85, model=None):
        if self.raise_exc:
            raise self.raise_exc
        return self.response_text


# ── 데이터 ─────────────────────────────────────────────────


def test_all_10_p9_data() -> None:
    assert len(DOYOON_P9_DATA) == 10


def test_risk_cards_3() -> None:
    assert len(RISK_CARDS) == 3
    assert RISK_CARDS[0].tone == "warn"
    assert RISK_CARDS[2].tone == "amber"


def test_get_ohang_methods_all_5() -> None:
    for ohang in ["목", "화", "토", "금", "수"]:
        methods = get_ohang_methods(ohang)
        assert len(methods) == 3


def test_compose_ohang_all_ilgan() -> None:
    for ilgan in VALID_DOYOON_P9_ILGAN:
        text = compose_doyoon_p9_ohang(user_name="홍길동", ilgan=ilgan, ohang_lack="수")
        assert "23%" in text


def test_compose_risk_all_ilgan() -> None:
    for ilgan in VALID_DOYOON_P9_ILGAN:
        text = compose_doyoon_p9_risk(user_name="홍길동", ilgan=ilgan)
        assert "36%" in text


def test_compose_optimize_all_ilgan() -> None:
    for ilgan in VALID_DOYOON_P9_ILGAN:
        text = compose_doyoon_p9_optimize(user_name="홍길동", ilgan=ilgan)
        assert "홍길동" in text


# ── OHANG ──────────────────────────────────────────────────


def _ohang_valid(facts):
    return (
        f"{facts['ilgan_full']}({facts['ilgan_hanja']}) 일간은 {facts['ohang_lack']}({facts['ohang_lack_hanja']}) "
        f"보완에 유독 민감하게 반응해요. 보완 적용 전후 인연 접촉률이 평균 {facts['boost_pct']} 차이가 납니다. "
        f"일반 케이스보다 {facts['response_multiplier']} 높은 반응성으로 측정돼요.\n\n"
        f"세 가지를 30일간 유지하시면 누적 효과가 강하게 나타나요. 상호작용 효과까지 포함하면 "
        f"최대 {facts['max_boost_pct']}까지 부스트됩니다.\n\n"
        f"{facts['user_name']}님께서는 가벼운 것부터 시작하시면 됩니다. 색채 노출이 가장 진입 장벽 낮아요."
    )


def test_ohang_validate() -> None:
    f = get_doyoon_p9_ohang_facts(user_name="홍길동", ilgan="임수", ohang_lack="화")
    ok, reason = validate_p9_ohang(_ohang_valid(f), f)
    assert ok, reason


@pytest.mark.asyncio
async def test_ohang_usecase_falls_back() -> None:
    fake = _FakeAIClient(raise_exc=AIClientError("x"))
    out = await GenerateP9OhangUseCase(ai_client=fake).execute(
        user_name="홍길동", ilgan="임수", ohang_lack="화"
    )
    assert "23%" in out


# ── RISK ────────────────────────────────────────────────────


def _risk_valid(facts):
    return (
        f"세 개 중에 즉시 변수가 임팩트가 가장 큽니다. 이것 하나만 정리해도 새 인연 진입률이 "
        f"{facts['immediate_impact_pct']} 올라가요. 단기·중기는 차차 진행 가능합니다.\n\n"
        f"{facts['user_name']}님이 동시에 셋 다 진행하시면 효과가 합산이 아닌 {facts['combined_multiplier']} 수준으로 수렴해요. "
        f"즉 192가 아니라 약 {facts['combined_value']} 수준입니다. 우선순위 명확화가 효율적이에요."
    )


def test_risk_validate() -> None:
    f = get_doyoon_p9_risk_facts(user_name="홍길동", ilgan="임수")
    ok, reason = validate_p9_risk(_risk_valid(f), f)
    assert ok, reason


@pytest.mark.asyncio
async def test_risk_usecase_falls_back() -> None:
    fake = _FakeAIClient(raise_exc=AIClientError("x"))
    out = await GenerateP9RiskUseCase(ai_client=fake).execute(user_name="홍길동", ilgan="임수")
    assert "36%" in out


# ── OPTIMIZE ───────────────────────────────────────────────


def _optimize_valid(facts):
    return (
        f"{facts['current_score']}에서 {facts['target_score']}까지 격차 분석해드릴게요. "
        "이 격차는 침묵 활용, 시선 안정, 표현 빈도 세 가지에서 발생해요. "
        "각각 별도 변수로 작동합니다.\n\n"
        f"{facts['ilgan_full']} 일간은 침묵 활용 하나만 올려도 매력 발현 효율이 "
        f"{facts['gap_per_action']}씩 상승해요. 30일 의식 시 6~8점 부스트됩니다. "
        f"목표 넘기면 전체 호감 유발 효율이 {facts['overall_boost_pct']} 상승해요.\n\n"
        f"별거 없습니다. 시작만 하시면 됩니다. 분석은 끝났고 공은 {facts['user_name']}님께 있어요."
    )


def test_optimize_validate() -> None:
    f = get_doyoon_p9_optimize_facts(user_name="홍길동", ilgan="임수")
    ok, reason = validate_p9_optimize(_optimize_valid(f), f)
    assert ok, reason


@pytest.mark.asyncio
async def test_optimize_usecase_falls_back() -> None:
    fake = _FakeAIClient(raise_exc=AIClientError("x"))
    out = await GenerateP9OptimizeUseCase(ai_client=fake).execute(
        user_name="홍길동", ilgan="임수"
    )
    assert "21%" in out
