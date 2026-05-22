"""도윤 P-10 box1/box2 AI 단위 테스트."""

from __future__ import annotations

import pytest

from app.domains.ai.application.usecase.generate_p10_box1_usecase import (
    GenerateP10Box1UseCase,
)
from app.domains.ai.application.usecase.generate_p10_box2_usecase import (
    GenerateP10Box2UseCase,
)
from app.domains.ai.domain.port.ai_client_port import AIClientError, AIClientPort
from app.domains.ai.domain.service.doyoon_p10_box1_prompt import validate_p10_box1
from app.domains.ai.domain.service.doyoon_p10_box2_prompt import validate_p10_box2
from app.domains.ai.domain.templates.doyoon_p10_box_letter import (
    compose_doyoon_box1_body,
    compose_doyoon_box2_body,
    get_doyoon_box1_facts,
    get_doyoon_box2_facts,
)


class _FakeAIClient(AIClientPort):
    def __init__(self, *, response_text=None, raise_exc=None):
        self.response_text = response_text
        self.raise_exc = raise_exc

    async def generate_chapter(self, *, system_prompt, user_prompt, max_tokens=1024, temperature=0.85, model=None):
        if self.raise_exc:
            raise self.raise_exc
        return self.response_text


def test_compose_box1_all_ilgan() -> None:
    for ilgan in ["갑목", "을목", "병화", "정화", "무토", "기토", "경금", "신금", "임수", "계수"]:
        text = compose_doyoon_box1_body(
            user_name="홍길동", ilgan=ilgan, step1=("crushing", "in_relationship"),
        )
        assert "홍길동" in text


def test_compose_box2_all_ilgan() -> None:
    for ilgan in ["갑목", "을목", "병화", "정화", "무토", "기토", "경금", "신금", "임수", "계수"]:
        text = compose_doyoon_box2_body(
            user_name="홍길동", ilgan=ilgan, step2=("soulmate", "timing"),
        )
        assert "홍길동" in text


def test_box1_facts() -> None:
    f = get_doyoon_box1_facts(user_name="홍길동", ilgan="임수", step1=("crushing",))
    assert "썸 진행 중" in f["step1_labels"]


def test_box2_facts() -> None:
    f = get_doyoon_box2_facts(
        user_name="홍길동", ilgan="임수",
        step2=("soulmate", "patterns"), ohang_lack="화",
    )
    assert "운명의 상대" in f["step2_labels"]
    assert "연애 패턴의 본질" in f["step2_labels"]
    assert f["ohang_lack_hanja"] == "火"


def _box1_valid(facts):
    return (
        f"{facts['user_name']}님이 선택해주신 상황 변수, 데이터로 차근차근 정리해드릴게요. "
        "분류 자체는 어렵지 않은 케이스입니다.\n\n"
        f"입력값: {facts['step1_labels']}. {facts['ilgan_full']}({facts['ilgan_hanja']}) 일간 표본에서 "
        "이 조합은 일관된 분류 패턴으로 잡혀요. 변수가 한 곳으로 쏠려 감정 활성도가 "
        "평균보다 1.4배 높게 측정되는 상태입니다. 흔하지만 가벼운 이슈는 아니에요.\n\n"
        f"{facts['user_name']}님께서 당장 결정 내리지 않으셔도 됩니다. 데이터부터 보고 그다음에 움직이시는 게 효율적이에요."
    )


def test_box1_validate() -> None:
    f = get_doyoon_box1_facts(user_name="홍길동", ilgan="임수", step1=("crushing",))
    ok, reason = validate_p10_box1(_box1_valid(f), f)
    assert ok, reason


@pytest.mark.asyncio
async def test_box1_usecase_falls_back() -> None:
    fake = _FakeAIClient(raise_exc=AIClientError("x"))
    out = await GenerateP10Box1UseCase(ai_client=fake).execute(
        user_name="홍길동", ilgan="임수", step1=("crushing",),
    )
    assert "홍길동" in out


def _box2_valid(facts):
    return (
        f"{facts['user_name']}님이 알고 싶다고 표시하신 질문 영역, 데이터 측면에서 정리해드릴게요. "
        "분류 자체가 답 가능 영역에 포함됩니다.\n\n"
        f"질문 영역: {facts['step2_labels']}. {facts['ilgan_full']}({facts['ilgan_hanja']}) 일간 표본에서 "
        "가장 자주 잡히는 질문 셋이에요. 답변 가능한 변수는 이미 측정돼 있고, 다음 장에서 차례로 풀어드리겠습니다. "
        "여기서 다루지 못하는 영역은 명확히 표시해드릴 거예요.\n\n"
        f"데이터가 답할 수 있는 영역과 그렇지 않은 영역이 분명하게 나뉩니다. "
        f"{facts['ohang_lack']}({facts['ohang_lack_hanja']}) 보완 효율도 답 가능 영역 안에 포함돼요."
    )


def test_box2_validate() -> None:
    f = get_doyoon_box2_facts(
        user_name="홍길동", ilgan="임수",
        step2=("soulmate",), ohang_lack="화",
    )
    ok, reason = validate_p10_box2(_box2_valid(f), f)
    assert ok, reason


@pytest.mark.asyncio
async def test_box2_usecase_falls_back() -> None:
    fake = _FakeAIClient(raise_exc=AIClientError("x"))
    out = await GenerateP10Box2UseCase(ai_client=fake).execute(
        user_name="홍길동", ilgan="임수",
        step2=("soulmate",), ohang_lack="화",
    )
    assert "홍길동" in out
