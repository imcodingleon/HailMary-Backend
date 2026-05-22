"""도윤 P-7 ai_ending 단위 테스트."""

from __future__ import annotations

import pytest

from app.domains.ai.application.usecase.generate_p7_ending_usecase import (
    GenerateP7EndingUseCase,
)
from app.domains.ai.domain.port.ai_client_port import AIClientError, AIClientPort
from app.domains.ai.domain.service.doyoon_p7_ending_prompt import validate_p7_ending
from app.domains.ai.domain.templates.doyoon_p7_ending import (
    compose_doyoon_p7_ending,
    get_doyoon_p7_ending_facts,
)
from app.domains.ai.domain.value_object.doyoon_p7_data import (
    DOYOON_P7_DATA,
    VALID_DOYOON_P7_ILGAN,
)


class _FakeAIClient(AIClientPort):
    def __init__(self, *, response_text=None, raise_exc=None):
        self.response_text = response_text
        self.raise_exc = raise_exc

    async def generate_chapter(self, *, system_prompt, user_prompt, max_tokens=1024, temperature=0.85, model=None):
        if self.raise_exc:
            raise self.raise_exc
        return self.response_text


def test_all_10_p7_data() -> None:
    assert len(DOYOON_P7_DATA) == 10
    for ilgan in VALID_DOYOON_P7_ILGAN:
        d = DOYOON_P7_DATA[ilgan]
        assert len(d.scenarios) == 3


def test_compose_all_ilgan() -> None:
    for ilgan in VALID_DOYOON_P7_ILGAN:
        text = compose_doyoon_p7_ending(user_name="홍길동", ilgan=ilgan)
        assert "홍길동님" in text


def test_facts_imsu() -> None:
    f = get_doyoon_p7_ending_facts(user_name="홍길동", ilgan="임수")
    assert f["sc1_six_month_pct"] == "22%"
    assert f["sc2_six_month_pct"] == "71%"
    assert f["sc3_six_month_pct"] == "38%"
    assert f["initiative_multiplier"] == "1.4배"
    assert f["wait_cost_multiplier"] == "2.7배"
    assert f["expected_value_ratio"] == "3배"


def _valid(facts):
    return (
        "세 시나리오 분석 결과를 정리해드릴게요.\n\n"
        f"시나리오 1 — 지금 이대로. 6개월 후 관계 성립 확률 {facts['sc1_six_month_pct']}로 측정됩니다. "
        "양쪽 모두 정체된 채 흐름이 약해지는 패턴이에요. 기대값 기준 가장 낮은 구간입니다.\n\n"
        f"시나리오 2 — {facts['user_name']}님이 먼저. 6개월 후 관계 성립 확률 {facts['sc2_six_month_pct']}로 가장 권장됩니다. "
        f"신호 보냈을 때 상대 호응률이 평균보다 {facts['initiative_multiplier']} 높게 측정. "
        "이게 분기 권장 근거입니다.\n\n"
        f"시나리오 3 — 상대가 먼저. 6개월 후 관계 성립 확률 {facts['sc3_six_month_pct']}로 측정. "
        f"가능성은 있지만 시간 비용이 평균 {facts['wait_cost_multiplier']} 더 든다는 점이 단점이에요.\n\n"
        f"{facts['user_name']}님 결정이에요. 다만 기대값 기준 시나리오 2가 압도적입니다 — "
        f"{facts['sc2_six_month_pct']} vs {facts['sc1_six_month_pct']} {facts['expected_value_ratio']} 차이예요."
    )


def test_validate() -> None:
    f = get_doyoon_p7_ending_facts(user_name="홍길동", ilgan="임수")
    ok, reason = validate_p7_ending(_valid(f), f)
    assert ok, reason


@pytest.mark.asyncio
async def test_usecase_falls_back() -> None:
    fake = _FakeAIClient(raise_exc=AIClientError("x"))
    out = await GenerateP7EndingUseCase(ai_client=fake).execute(
        user_name="홍길동", ilgan="임수"
    )
    assert "71%" in out
    assert "22%" in out
