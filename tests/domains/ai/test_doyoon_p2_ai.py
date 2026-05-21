"""도윤 P-2 2박스 AI 단위 테스트 (hurt + recovery).

임수 케이스 중심 (모범 셀). 나머지 9 셀은 압축 데이터라 가벼운 sanity check만.
"""

from __future__ import annotations

import pytest

from app.domains.ai.application.usecase.generate_p2_hurt_usecase import (
    GenerateP2HurtUseCase,
)
from app.domains.ai.application.usecase.generate_p2_recovery_usecase import (
    GenerateP2RecoveryUseCase,
)
from app.domains.ai.domain.port.ai_client_port import (
    AIClientError,
    AIClientPort,
)
from app.domains.ai.domain.service.doyoon_p2_hurt_prompt import (
    validate_p2_hurt,
)
from app.domains.ai.domain.service.doyoon_p2_recovery_prompt import (
    validate_p2_recovery,
)
from app.domains.ai.domain.templates.doyoon_p2_hurt import (
    compose_doyoon_p2_hurt,
    get_doyoon_p2_hurt_facts,
)
from app.domains.ai.domain.templates.doyoon_p2_recovery import (
    compose_doyoon_p2_recovery,
    get_doyoon_p2_recovery_facts,
)
from app.domains.ai.domain.value_object.doyoon_p2_data import (
    VALID_DOYOON_P2_ILGAN,
)


class _FakeAIClient(AIClientPort):
    def __init__(
        self,
        *,
        response_text: str | None = None,
        raise_exc: Exception | None = None,
    ) -> None:
        self.response_text = response_text
        self.raise_exc = raise_exc

    async def generate_chapter(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.85,
        model: str | None = None,
    ) -> str:
        if self.raise_exc is not None:
            raise self.raise_exc
        assert self.response_text is not None
        return self.response_text


# ── 데이터 완전성 (10 일간 모두 KeyError 없음) ────────────────────


def test_all_10_ilgan_compose_hurt() -> None:
    for ilgan in VALID_DOYOON_P2_ILGAN:
        out = compose_doyoon_p2_hurt(user_name="홍길동", ilgan=ilgan)
        assert "홍길동님" in out["ai_hurt"]
        assert out["scenario_1_when"]
        assert out["scenario_2_when"]


def test_all_10_ilgan_compose_recovery() -> None:
    for ilgan in VALID_DOYOON_P2_ILGAN:
        out = compose_doyoon_p2_recovery(user_name="홍길동", ilgan=ilgan)
        assert "홍길동님" in str(out["ai_recovery"])
        timeline = out["timeline"]
        assert isinstance(timeline, list) and len(timeline) == 3


# ── HURT ─────────────────────────────────────────────────────────


def test_hurt_facts_imsu() -> None:
    f = get_doyoon_p2_hurt_facts(user_name="홍길동", ilgan="임수")
    assert f["vulnerability_pct"] == "78%"
    assert f["common_pattern_pct"] == "64%"
    assert f["ilgan_hanja"] == "壬水"
    assert "홍길동님" in f["rule_text"]


def _hurt_valid_text(facts: dict[str, str]) -> str:
    return (
        f"{facts['user_name']}님의 약점 트리거 분석입니다. "
        f"{facts['ilgan_full']}({facts['ilgan_hanja']}) 일간 표본에서 두 가지 위험 변수 케이스가 발견됐어요. "
        "둘 다 표본 발현률이 높은 패턴입니다.\n\n"
        f"첫 번째는 무시 입력 케이스 — 표본 발현률이 {facts['vulnerability_pct']}로 측정되고 "
        f"동일 패턴 비율은 {facts['common_pattern_pct']}예요. 정보 처리량 케이스라 내부 침잠으로 잡히는 구조입니다. "
        "외부 표현 빈도가 낮아 인지 자체가 어려워요.\n\n"
        "두 번째는 명시 표현 부족 케이스로 신호 인지 실패가 누적되는 패턴이에요. "
        "작은 출력 빈도를 의식적으로 늘리시면 변동성이 줄어듭니다. 차단율도 같이 떨어져요."
    )


def test_hurt_validate_passes() -> None:
    f = get_doyoon_p2_hurt_facts(user_name="홍길동", ilgan="임수")
    ok, reason = validate_p2_hurt(_hurt_valid_text(f), f)
    assert ok, f"unexpected fail: {reason}"


def test_hurt_validate_fails_pct_mutated() -> None:
    f = get_doyoon_p2_hurt_facts(user_name="홍길동", ilgan="임수")
    text = _hurt_valid_text(f).replace("78%", "77%")
    ok, reason = validate_p2_hurt(text, f)
    assert not ok
    assert "vulnerability_pct" in reason


@pytest.mark.asyncio
async def test_hurt_usecase_success() -> None:
    f = get_doyoon_p2_hurt_facts(user_name="홍길동", ilgan="임수")
    fake = _FakeAIClient(response_text=_hurt_valid_text(f))
    out = await GenerateP2HurtUseCase(ai_client=fake).execute(
        user_name="홍길동", ilgan="임수"
    )
    assert out == _hurt_valid_text(f)


@pytest.mark.asyncio
async def test_hurt_usecase_falls_back_on_error() -> None:
    fake = _FakeAIClient(raise_exc=AIClientError("simulated"))
    out = await GenerateP2HurtUseCase(ai_client=fake).execute(
        user_name="홍길동", ilgan="임수"
    )
    assert "홍길동님" in out
    assert "78%" in out


# ── RECOVERY ─────────────────────────────────────────────────────


def test_recovery_facts_imsu_slow() -> None:
    f = get_doyoon_p2_recovery_facts(user_name="홍길동", ilgan="임수")
    assert f["recovery_lag_multiplier"] == "1.4배"
    assert f["time_label_0"] == "직후"
    assert f["time_label_1"] == "3개월 후"
    assert f["time_label_2"] == "6개월 후"


def _recovery_valid_text(facts: dict[str, str]) -> str:
    return (
        f"{facts['user_name']}님의 회복 곡선 분석입니다. "
        f"{facts['ilgan_full']}({facts['ilgan_hanja']}) 일간 표본 기준으로 "
        f"회복 지연이 평균 대비 {facts['recovery_lag_multiplier']} 수준으로 측정돼요. "
        "정보 처리량이 많은 케이스의 전형적인 특징이에요.\n\n"
        f"{facts['time_label_0']} 구간에서는 일상 모든 입력에 옛 데이터가 결합되는 패턴이 잡혀요. "
        f"{facts['time_label_1']} 구간에서는 외부 표현은 정상화되지만 내부 처리량 잔여가 평균보다 길게 유지됩니다. "
        f"{facts['time_label_2']} 구간에 와야 새 매칭을 받을 임계점에 도달해요.\n\n"
        "강제로 옛 인덱스를 삭제하려는 시도는 회복 곡선을 오히려 늦춥니다. "
        "자연 인덱스 감소를 기다리는 게 가장 안전한 회복 경로입니다. 데이터가 그렇게 권합니다."
    )


def test_recovery_validate_passes() -> None:
    f = get_doyoon_p2_recovery_facts(user_name="홍길동", ilgan="임수")
    ok, reason = validate_p2_recovery(_recovery_valid_text(f), f)
    assert ok, f"unexpected fail: {reason}"


def test_recovery_validate_fails_multiplier_mutated() -> None:
    f = get_doyoon_p2_recovery_facts(user_name="홍길동", ilgan="임수")
    text = _recovery_valid_text(f).replace("1.4배", "1.3배")
    ok, reason = validate_p2_recovery(text, f)
    assert not ok
    assert "recovery_lag_multiplier" in reason


@pytest.mark.asyncio
async def test_recovery_usecase_success() -> None:
    f = get_doyoon_p2_recovery_facts(user_name="홍길동", ilgan="임수")
    fake = _FakeAIClient(response_text=_recovery_valid_text(f))
    out = await GenerateP2RecoveryUseCase(ai_client=fake).execute(
        user_name="홍길동", ilgan="임수"
    )
    assert "1.4배" in out


@pytest.mark.asyncio
async def test_recovery_usecase_falls_back_on_error() -> None:
    fake = _FakeAIClient(raise_exc=AIClientError("simulated"))
    out = await GenerateP2RecoveryUseCase(ai_client=fake).execute(
        user_name="홍길동", ilgan="임수"
    )
    assert "홍길동님" in out
    assert "1.4배" in out
