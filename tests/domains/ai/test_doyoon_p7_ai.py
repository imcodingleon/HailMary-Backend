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
    """facts — 카드 라벨 (모든 일간 공통)만 노출, 별도 메타 수치는 제외."""
    f = get_doyoon_p7_ending_facts(user_name="홍길동", ilgan="임수")
    assert f["sc1_label"] == "소멸 65%"
    assert f["sc2_label"] == "좋은 결말 78%"
    assert f["sc3_label"] == "좋은 결말 91%"
    # 별도 메타 수치는 facts에 없음
    assert "sc1_six_month_pct" not in f
    assert "initiative_multiplier" not in f


def _valid(facts):
    """카드 풀이 톤 — 65%/78%/91% 직접 인용, 별도 메타 수치 X."""
    return (
        "세 갈래 시나리오, 카드로 정리해드렸어요. 각 분기의 의미를 풀어드릴게요.\n\n"
        "시나리오 1 — 지금 이대로 두면 소멸 65%. 양쪽 모두 정체된 채 흐름이 약해지는 패턴이에요. "
        "가장 흔하지만 가장 위험한 경로입니다. 이 분기를 선택하면 시간이 흐를수록 가능성은 더 낮아집니다.\n\n"
        f"시나리오 2 — {facts['user_name']}님이 먼저. 좋은 결말 78%. "
        f"{facts['ilgan_full']}({facts['ilgan_hanja']}) 일간 표본 능동 분기로 권장됩니다. "
        f"{facts['user_name']}님이 지금 통제 가능한 변수라는 점이 핵심이에요. 작은 신호 한 번이 결정점입니다.\n\n"
        "시나리오 3 — 상대가 먼저. 좋은 결말 91% — 수치는 가장 높습니다. "
        "단 상대 움직임을 대기해야 하는 조건부 경로라 시간 비용이 큰 분기예요. 통제 변수 밖에 있는 분기입니다.\n\n"
        f"{facts['user_name']}님, 결정은 본인 것이에요. "
        f"다만 78%는 {facts['user_name']}님이 지금 통제 가능한 분기이고, 91%는 대기 시간 위에 놓인 조건부 분기입니다. "
        "능동 분기를 추천드립니다."
    )


def test_validate() -> None:
    f = get_doyoon_p7_ending_facts(user_name="홍길동", ilgan="임수")
    ok, reason = validate_p7_ending(_valid(f), f)
    assert ok, reason


@pytest.mark.asyncio
async def test_usecase_falls_back() -> None:
    """fallback 시 카드 라벨 (65/78/91) 포함, 별도 메타 수치 (22%, 71%, 38%) 미포함."""
    fake = _FakeAIClient(raise_exc=AIClientError("x"))
    out = await GenerateP7EndingUseCase(ai_client=fake).execute(
        user_name="홍길동", ilgan="임수"
    )
    assert "65%" in out
    assert "78%" in out
    assert "91%" in out
    # 카드에 없는 별도 수치는 룰 텍스트에도 없어야
    assert "71%" not in out
    assert "22%" not in out
    assert "38%" not in out
