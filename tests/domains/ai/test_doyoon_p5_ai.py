"""도윤 P-5 3박스 AI 단위 테스트 — charm_index + conversion + appeal."""

from __future__ import annotations

import pytest

from app.domains.ai.application.usecase.generate_p5_appeal_usecase import (
    GenerateP5AppealUseCase,
)
from app.domains.ai.application.usecase.generate_p5_charm_index_usecase import (
    GenerateP5CharmIndexUseCase,
)
from app.domains.ai.application.usecase.generate_p5_conversion_usecase import (
    GenerateP5ConversionUseCase,
)
from app.domains.ai.domain.port.ai_client_port import (
    AIClientError,
    AIClientPort,
)
from app.domains.ai.domain.service.doyoon_p5_appeal_prompt import (
    validate_p5_appeal,
)
from app.domains.ai.domain.service.doyoon_p5_charm_index_prompt import (
    validate_p5_charm_index,
)
from app.domains.ai.domain.service.doyoon_p5_conversion_prompt import (
    validate_p5_conversion,
)
from app.domains.ai.domain.templates.doyoon_p5_charm import (
    compose_doyoon_p5_appeal,
    compose_doyoon_p5_charm_index,
    compose_doyoon_p5_conversion,
    get_doyoon_p5_appeal_facts,
    get_doyoon_p5_charm_index_facts,
    get_doyoon_p5_conversion_facts,
)
from app.domains.ai.domain.value_object.doyoon_p5_data import (
    DOYOON_P5_DATA,
    VALID_DOYOON_P5_ILGAN,
)


class _FakeAIClient(AIClientPort):
    def __init__(self, *, response_text=None, raise_exc=None):
        self.response_text = response_text
        self.raise_exc = raise_exc

    async def generate_chapter(self, *, system_prompt, user_prompt, max_tokens=1024, temperature=0.85, model=None):
        if self.raise_exc:
            raise self.raise_exc
        return self.response_text


def test_all_10_p5_data() -> None:
    assert len(DOYOON_P5_DATA) == 10
    for ilgan in VALID_DOYOON_P5_ILGAN:
        d = DOYOON_P5_DATA[ilgan]
        assert len(d.radar) == 6
        assert len(d.appeal_meters) == 4


def test_all_10_compose() -> None:
    for ilgan in VALID_DOYOON_P5_ILGAN:
        assert "홍길동님" in compose_doyoon_p5_charm_index(
            user_name="홍길동", ilgan=ilgan, charm_pct=12
        )
        assert "홍길동님" in compose_doyoon_p5_conversion(user_name="홍길동", ilgan=ilgan)
        assert "홍길동님" in compose_doyoon_p5_appeal(user_name="홍길동", ilgan=ilgan)


# ── charm_index ──


def test_charm_index_facts_imsu() -> None:
    f = get_doyoon_p5_charm_index_facts(user_name="홍길동", ilgan="임수", charm_pct=8)
    assert f["charm_pct"] == "8%"
    assert f["strength_axis_1"] == "존재감"
    assert f["strength_axis_2"] == "깊이감"
    assert f["strength_multiplier"] == "1.7배"
    assert f["conscious_gap_multiplier"] == "2.4배"


def _ci_valid(facts):
    return (
        f"상위 {facts['charm_pct']} 케이스로 측정됐어요. 일반적인 분포에서 벗어난 수치입니다. "
        "동일 일간 표본 안에서도 흔치 않은 구간이에요.\n\n"
        f"6축 중 강점이 둘이에요. {facts['strength_axis_1']}과 {facts['strength_axis_2']} — "
        f"평균 대비 {facts['strength_multiplier']}로 나오네요. 나머지 축들은 평균~약상위 구간입니다. "
        "약점이 있는 게 아니라 강점이 분명한 구조예요. 분포 특성상 두 축 모두 이만큼 나오기 쉽지 않습니다.\n\n"
        f"다만 {facts['user_name']}님은 의식적 발현과 무의식 발현 차이가 {facts['conscious_gap_multiplier']}예요. "
        "잠재력 활용도가 낮은 상태입니다. 조금만 의식하셔도 측정값이 더 올라갈 여지가 큽니다."
    )


def test_charm_index_validate() -> None:
    f = get_doyoon_p5_charm_index_facts(user_name="홍길동", ilgan="임수", charm_pct=8)
    ok, reason = validate_p5_charm_index(_ci_valid(f), f)
    assert ok, reason


@pytest.mark.asyncio
async def test_charm_index_usecase_falls_back() -> None:
    fake = _FakeAIClient(raise_exc=AIClientError("x"))
    out = await GenerateP5CharmIndexUseCase(ai_client=fake).execute(
        user_name="홍길동", ilgan="임수", charm_pct=8
    )
    assert "8%" in out
    assert "1.7배" in out


# ── conversion ──


def test_conversion_facts_imsu() -> None:
    f = get_doyoon_p5_conversion_facts(user_name="홍길동", ilgan="임수")
    assert f["step_1_pct"] == "30%"
    assert f["step_4_pct"] == "88%"
    assert f["second_meeting_multiplier"] == "1.4배"
    assert f["final_gap_pct"] == "38%p"


def _cv_valid(facts):
    return (
        f"첫 인상 {facts['step_1_pct']}에서 시작해서 끌림 {facts['step_4_pct']}까지 도달하는 4단계 전환율입니다. "
        f"중간 단계 {facts['step_2_pct']}와 {facts['step_3_pct']}로 올라가요.\n\n"
        f"두 번째 만남에서 평균의 {facts['second_meeting_multiplier']}로 효율이 뛰어요. "
        f"첫 만남 종료 vs 두 번째 진행 케이스의 호감도 격차가 {facts['final_gap_pct']} 벌어집니다.\n\n"
        f"{facts['user_name']}님 전략은 두 번째 약속 사전 확보예요."
    )


def test_conversion_validate() -> None:
    f = get_doyoon_p5_conversion_facts(user_name="홍길동", ilgan="임수")
    ok, reason = validate_p5_conversion(_cv_valid(f), f)
    assert ok, reason


@pytest.mark.asyncio
async def test_conversion_usecase_falls_back() -> None:
    fake = _FakeAIClient(raise_exc=AIClientError("x"))
    out = await GenerateP5ConversionUseCase(ai_client=fake).execute(
        user_name="홍길동", ilgan="임수"
    )
    assert "1.4배" in out
    assert "38%p" in out


# ── appeal ──


def test_appeal_facts_imsu() -> None:
    f = get_doyoon_p5_appeal_facts(user_name="홍길동", ilgan="임수")
    assert f["meter_1_name"] == "존재감"
    assert f["meter_1_value"] == "92"
    assert f["weakness_axis_1"] == "표현 일관성"
    assert f["appeal_boost_pct"] == "26%"


def _ap_valid(facts):
    return (
        "4개 변수 점수 정리해드릴게요. 핵심 호감 유발 지표 측정값입니다. "
        "각 변수마다 가중치가 다르게 작동해요.\n\n"
        f"{facts['meter_1_name']} {facts['meter_1_value']}, "
        f"{facts['meter_2_name']} {facts['meter_2_value']}, "
        f"{facts['meter_3_name']} {facts['meter_3_value']}, "
        f"{facts['meter_4_name']} {facts['meter_4_value']}. "
        f"{facts['weakness_axis_1']}과 {facts['weakness_axis_2']}가 약점 변수입니다. "
        "이 두 축이 통제 가능한 영역이라 가장 효율적인 개선 포인트예요.\n\n"
        f"{facts['user_name']}님 케이스에서 두 변수만 올리면 호감 유발 효율이 {facts['appeal_boost_pct']} 상승해요. "
        "강점 보완보다 약점 보완이 효율 높은 영역입니다. 우선순위 정해서 진입하세요."
    )


def test_appeal_validate() -> None:
    f = get_doyoon_p5_appeal_facts(user_name="홍길동", ilgan="임수")
    ok, reason = validate_p5_appeal(_ap_valid(f), f)
    assert ok, reason


@pytest.mark.asyncio
async def test_appeal_usecase_falls_back() -> None:
    fake = _FakeAIClient(raise_exc=AIClientError("x"))
    out = await GenerateP5AppealUseCase(ai_client=fake).execute(
        user_name="홍길동", ilgan="임수"
    )
    assert "표현 일관성" in out
    assert "26%" in out
