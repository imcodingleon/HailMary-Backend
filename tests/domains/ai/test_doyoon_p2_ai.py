"""도윤 P-2 2박스 AI 단위 테스트 — 원본 구조 재설계 (2026-05-21).

10 일간 KeyError-free + 임수 케이스 facts/validate/usecase fallback.
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
    DOYOON_P2_DATA,
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


# ── 데이터 완전성 ─────────────────────────────────────────────────


def test_all_10_ilgan_have_data() -> None:
    assert len(DOYOON_P2_DATA) == 10
    for ilgan in VALID_DOYOON_P2_ILGAN:
        d = DOYOON_P2_DATA[ilgan]
        assert d.hurt_type_1.keyword
        assert d.hurt_type_1.risk_pct.endswith("%")
        assert len(d.meters) == 4
        assert d.meters[0].label == "직후"
        assert d.meters[3].label == "6개월"
        assert d.sd_avatar_asset


def test_all_10_ilgan_compose_hurt() -> None:
    for ilgan in VALID_DOYOON_P2_ILGAN:
        out = compose_doyoon_p2_hurt(user_name="홍길동", ilgan=ilgan)
        assert "두 유형" in out["ai_hurt"]


def test_all_10_ilgan_compose_recovery() -> None:
    for ilgan in VALID_DOYOON_P2_ILGAN:
        out = compose_doyoon_p2_recovery(user_name="홍길동", ilgan=ilgan)
        assert "홍길동님" in out["ai_recovery"]


# ── HURT ─────────────────────────────────────────────────────────


def test_hurt_facts_imsu() -> None:
    f = get_doyoon_p2_hurt_facts(user_name="홍길동", ilgan="임수")
    assert f["hurt_type_1_keyword"] == "무관심 신호 인지"
    assert f["hurt_type_1_risk_pct"] == "78%"
    assert f["hurt_type_2_keyword"] == "의도 미독해"
    assert f["hurt_type_2_risk_pct"] == "64%"
    assert f["intervention_drop_pct"] == "41%"
    assert f["ilgan_hanja"] == "壬水"


def _hurt_valid_text(facts: dict[str, str]) -> str:
    return (
        f"두 유형이 {facts['ilgan_full']}({facts['ilgan_hanja']}) 일간 표본에서 가장 빈번한 변수입니다. "
        "차단율 가장 높은 두 케이스를 측정한 결과예요.\n\n"
        f"첫 번째는 {facts['hurt_type_1_keyword']}예요. 위험도 {facts['hurt_type_1_risk_pct']}로 측정됩니다. "
        f"{facts['user_name']}님 케이스에서 가장 큰 감정 손실 변수로 잡혀요. "
        "평균 대비 차단율이 높고 누적 손실도 큰 패턴입니다.\n\n"
        f"두 번째는 {facts['hurt_type_2_keyword']}예요. 위험도 {facts['hurt_type_2_risk_pct']}. "
        "신호 인지 실패 변수가 같이 들어오면 두 케이스 모두 발화돼요.\n\n"
        f"신호 해석 전 24시간 텀을 두시면 두 패턴 모두 발생률이 {facts['intervention_drop_pct']} 떨어집니다. "
        "통제 가능한 영역이에요. 조금만 의식해보세요."
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
    assert "hurt_type_1_risk_pct" in reason


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
    assert "무관심 신호 인지" in out
    assert "78%" in out


# ── RECOVERY ─────────────────────────────────────────────────────


def test_recovery_facts_imsu() -> None:
    f = get_doyoon_p2_recovery_facts(user_name="홍길동", ilgan="임수")
    assert f["recovery_lag_multiplier"] == "1.4배"
    assert f["meter_pct_0"] == "20%"
    assert f["meter_pct_1"] == "40%"
    assert f["meter_pct_2"] == "65%"
    assert f["meter_pct_3"] == "90%"


def _recovery_valid_text(facts: dict[str, str]) -> str:
    return (
        f"회복 데이터 정리해 드릴게요. {facts['ilgan_full']}({facts['ilgan_hanja']}) 일간의 평균 회복 곡선 분석입니다. "
        "4단계로 나누어 살펴봅니다.\n\n"
        f"진행률을 보면, 직후 {facts['meter_pct_0']} / 1개월 {facts['meter_pct_1']} / "
        f"3개월 {facts['meter_pct_2']} / 6개월 {facts['meter_pct_3']} 회복으로 측정돼요. "
        f"{facts['user_name']}님 케이스의 잔여 인덱스가 평균보다 길게 유지되는 패턴입니다. "
        "각 단계 임계점이 다른 일간보다 깊게 잡혀요.\n\n"
        f"평균 대비 회복 지연이 {facts['recovery_lag_multiplier']} 수준입니다. "
        "자연 인덱스 감소가 가장 안전한 회복 경로예요. 강제 삭제는 곡선을 오히려 늦춥니다. "
        "회복 구간 내 새 매칭 시도는 충돌 확률을 높입니다."
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
async def test_recovery_usecase_falls_back_on_error() -> None:
    fake = _FakeAIClient(raise_exc=AIClientError("simulated"))
    out = await GenerateP2RecoveryUseCase(ai_client=fake).execute(
        user_name="홍길동", ilgan="임수"
    )
    assert "1.4배" in out
