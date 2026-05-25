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
    """카드 풀이 톤 — 81% (즉시 위험도) + 130 (실제 임팩트) 포함."""
    for ilgan in VALID_DOYOON_P9_ILGAN:
        text = compose_doyoon_p9_risk(user_name="홍길동", ilgan=ilgan)
        assert "81%" in text
        assert "130" in text


def test_compose_optimize_all_ilgan() -> None:
    for ilgan in VALID_DOYOON_P9_ILGAN:
        text = compose_doyoon_p9_optimize(user_name="홍길동", ilgan=ilgan)
        assert "홍길동" in text


# ── OHANG ──────────────────────────────────────────────────


def _ohang_valid(facts):
    """카드 풀이 톤 — 카드 라벨 (9%/7%/7%/23%)만 인용. 별도 메타 수치 X."""
    return (
        f"{facts['ilgan_full']}({facts['ilgan_hanja']}) 일간 {facts['user_name']}님께 "
        f"{facts['ohang_lack']}({facts['ohang_lack_hanja']}) 보완 효과를 카드로 정리해드렸어요. "
        f"세 가지 방법 합산 평균 {facts['boost_pct']} 인연 접촉 확률 상승.\n\n"
        "보완 방법 1 (+9%) 색채 노출이 가장 진입 장벽 낮습니다. 옷차림부터 시작 가능. "
        "방법 2 (+7%) 공간 변수와 방법 3 (+7%) 행동 변수는 누적 시간 필요.\n\n"
        f"세 가지 30일 유지 시 {facts['boost_pct']} 효과 안정. "
        f"{facts['user_name']}님께 효과 +9% 색채 노출부터 권장합니다."
    )


def test_ohang_validate() -> None:
    f = get_doyoon_p9_ohang_facts(user_name="홍길동", ilgan="임수", ohang_lack="화")
    ok, reason = validate_p9_ohang(_ohang_valid(f), f)
    assert ok, reason


@pytest.mark.asyncio
async def test_ohang_usecase_falls_back() -> None:
    """fallback 시 카드 합산 23% + 카드 라벨 풀이."""
    fake = _FakeAIClient(raise_exc=AIClientError("x"))
    out = await GenerateP9OhangUseCase(ai_client=fake).execute(
        user_name="홍길동", ilgan="임수", ohang_lack="화"
    )
    assert "23%" in out
    assert "+9%" in out  # 카드 라벨 풀이 확인
    # 카드에 없는 별도 수치는 룰 텍스트에도 없어야
    assert "28%" not in out
    assert "1.6배" not in out


# ── RISK ────────────────────────────────────────────────────


def _risk_valid(facts):
    """카드 풀이 톤 — 81%/64%/47% 카드 라벨 + 192·130 합산 패턴만."""
    return (
        "리스크 카드 세 장 정리해드렸어요. 즉시 81%·단기 64%·중기 47% 위험도가 그대로 우선순위. "
        "라벨 자체가 진행 순서를 가리킵니다.\n\n"
        f"{facts['user_name']}님이 셋 다 진행하시면 단순 합산 192가 아니라 "
        f"{facts['combined_multiplier']} 수준으로 수렴해 약 {facts['combined_value']}가 실제 임팩트입니다. "
        "즉시(81%)부터 우선 처리하시는 게 효율적이에요."
    )


def test_risk_validate() -> None:
    f = get_doyoon_p9_risk_facts(user_name="홍길동", ilgan="임수")
    ok, reason = validate_p9_risk(_risk_valid(f), f)
    assert ok, reason


@pytest.mark.asyncio
async def test_risk_usecase_falls_back() -> None:
    """fallback 시 카드 라벨 (81%) + 합산 패턴 (130). 36% 같은 별도 수치 X."""
    fake = _FakeAIClient(raise_exc=AIClientError("x"))
    out = await GenerateP9RiskUseCase(ai_client=fake).execute(user_name="홍길동", ilgan="임수")
    assert "81%" in out
    assert "130" in out
    assert "36%" not in out  # 카드에 없는 별도 수치 X


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
