"""도윤 P-1 3박스 AI 단위 테스트 — facts/prompt/validate/usecase.

각 박스(opening/trigger/emotion)에 대해:
  - facts 추출 가드
  - prompt 박힘
  - validate 통과/실패
  - usecase AI 성공 / AI 에러 fallback / 검증 실패 fallback
"""

from __future__ import annotations

import pytest

from app.domains.ai.application.usecase.generate_p1_emotion_usecase import (
    GenerateP1EmotionUseCase,
)
from app.domains.ai.application.usecase.generate_p1_opening_usecase import (
    GenerateP1OpeningUseCase,
)
from app.domains.ai.application.usecase.generate_p1_trigger_usecase import (
    GenerateP1TriggerUseCase,
)
from app.domains.ai.domain.port.ai_client_port import (
    AIClientError,
    AIClientPort,
)
from app.domains.ai.domain.service.doyoon_p1_emotion_prompt import (
    build_p1_emotion_prompt,
    validate_p1_emotion,
)
from app.domains.ai.domain.service.doyoon_p1_opening_prompt import (
    build_p1_opening_prompt,
    validate_p1_opening,
)
from app.domains.ai.domain.service.doyoon_p1_trigger_prompt import (
    build_p1_trigger_prompt,
    validate_p1_trigger,
)
from app.domains.ai.domain.templates.doyoon_p1_emotion import (
    get_doyoon_p1_emotion_facts,
)
from app.domains.ai.domain.templates.doyoon_p1_opening import (
    get_doyoon_p1_opening_facts,
)
from app.domains.ai.domain.templates.doyoon_p1_trigger import (
    get_doyoon_p1_trigger_facts,
)

# ─────────────────────────────────────────────────────────────────
# Fake AI client
# ─────────────────────────────────────────────────────────────────


class _FakeAIClient(AIClientPort):
    def __init__(
        self,
        *,
        response_text: str | None = None,
        raise_exc: Exception | None = None,
    ) -> None:
        self.response_text = response_text
        self.raise_exc = raise_exc
        self.calls: list[dict[str, object]] = []

    async def generate_chapter(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.85,
        model: str | None = None,
    ) -> str:
        self.calls.append({"model": model, "max_tokens": max_tokens})
        if self.raise_exc is not None:
            raise self.raise_exc
        assert self.response_text is not None
        return self.response_text


# ─────────────────────────────────────────────────────────────────
# P-1 OPENING
# ─────────────────────────────────────────────────────────────────


def test_opening_facts_html_dummy() -> None:
    f = get_doyoon_p1_opening_facts(
        user_name="홍길동", ilgan="임수", ilju_hanja="임술(壬戌)"
    )
    assert f["user_name"] == "홍길동"
    assert f["ilgan_full"] == "임수"
    assert f["ilgan_hanja"] == "壬水"
    assert f["ilju_hanja"] == "임술(壬戌)"
    assert f["pct_value"] == "8%"
    assert f["distribution_pct"] == "12.4%"
    assert f["love_type"] == "정보 처리형 신중 진입자"
    assert "홍길동님" in f["rule_text"]


def test_opening_facts_user_name_required() -> None:
    with pytest.raises(ValueError, match="user_name"):
        get_doyoon_p1_opening_facts(user_name="", ilgan="임수", ilju_hanja="임술(壬戌)")


def test_opening_prompt_substitutes_facts() -> None:
    f = get_doyoon_p1_opening_facts(
        user_name="홍길동", ilgan="임수", ilju_hanja="임술(壬戌)"
    )
    system, user = build_p1_opening_prompt(f)
    assert "한도윤" in system
    assert "홍길동" in system
    assert "8%" in system
    assert "12.4%" in system
    assert "user_name: 홍길동" in user
    assert "壬水" in user
    assert "임술(壬戌)" in user
    assert f["rule_text"] in user


def _opening_valid_text(facts: dict[str, str]) -> str:
    return (
        f"솔직히 말씀드릴게요. {facts['user_name']}님은 상위 {facts['pct_value']} 케이스로 분류돼요. "
        "동일 일간 안에서 이렇게 분명한 패턴은 흔치 않거든요.\n\n"
        f"{facts['ilgan_full']}({facts['ilgan_hanja']}) 일간 분포가 {facts['distribution_pct']}인데, "
        f"그 안에서 '{facts['love_type']}'로 분류되는 케이스는 더 좁아요. "
        f"{facts['ilju_hanja']} 일주까지 결합하면 세분화가 한 단계 더 들어갑니다.\n\n"
        "특징은 처리량은 많은데 외부로 출력되는 비율이 평균보다 낮은 구조입니다. "
        "그래서 주변에서 읽어내는 데 시간이 더 걸려요.\n\n"
        "딱 하나 바꿔보세요. 표현 빈도를 주 1회만 의식적으로 늘려보시면, 읽는 방식이 달라질 거예요."
    )


def test_opening_validate_passes() -> None:
    f = get_doyoon_p1_opening_facts(
        user_name="홍길동", ilgan="임수", ilju_hanja="임술(壬戌)"
    )
    ok, reason = validate_p1_opening(_opening_valid_text(f), f)
    assert ok, f"unexpected fail: {reason}"


def test_opening_validate_fails_pct_mutated() -> None:
    f = get_doyoon_p1_opening_facts(
        user_name="홍길동", ilgan="임수", ilju_hanja="임술(壬戌)"
    )
    text = _opening_valid_text(f).replace("8%", "7%")
    ok, reason = validate_p1_opening(text, f)
    assert not ok
    assert "pct_value" in reason


@pytest.mark.asyncio
async def test_opening_usecase_returns_ai_on_success() -> None:
    f = get_doyoon_p1_opening_facts(
        user_name="홍길동", ilgan="임수", ilju_hanja="임술(壬戌)"
    )
    ai_text = _opening_valid_text(f)
    fake = _FakeAIClient(response_text=ai_text)
    out = await GenerateP1OpeningUseCase(ai_client=fake).execute(
        user_name="홍길동", ilgan="임수", ilju_hanja="임술(壬戌)"
    )
    assert out == ai_text
    assert fake.calls[0]["model"] == "claude-sonnet-4-6"


@pytest.mark.asyncio
async def test_opening_usecase_falls_back_on_ai_error() -> None:
    fake = _FakeAIClient(raise_exc=AIClientError("simulated"))
    out = await GenerateP1OpeningUseCase(ai_client=fake).execute(
        user_name="홍길동", ilgan="임수", ilju_hanja="임술(壬戌)"
    )
    assert "홍길동님" in out
    assert "상위 8%" in out


# ─────────────────────────────────────────────────────────────────
# P-1 TRIGGER
# ─────────────────────────────────────────────────────────────────


def test_trigger_facts_html_dummy() -> None:
    f = get_doyoon_p1_trigger_facts(user_name="홍길동", ilgan="임수")
    assert f["trigger_completion_pct"] == "88%"
    assert f["peak_window_days"] == "30일"
    assert f["self_control_pct"] == "17%"
    assert f["trigger_1"] == "공유된 지적 발견"
    assert f["trigger_2"] == "답 빠른 메시지 응답"
    assert "홍길동님" in f["rule_text"]


def test_trigger_prompt_substitutes_facts() -> None:
    f = get_doyoon_p1_trigger_facts(user_name="홍길동", ilgan="임수")
    system, user = build_p1_trigger_prompt(f)
    assert "88%" in system
    assert "30일" in system
    assert "17%" in system
    assert "공유된 지적 발견" in user


def _trigger_valid_text(facts: dict[str, str]) -> str:
    return (
        f"흥미로운 케이스입니다. 트리거 셋이 순서대로 발화하면 임계점 도달이 {facts['trigger_completion_pct']}로 잡혀요. "
        "거의 자동에 가까운 수준이에요.\n\n"
        f"특히 {facts['peak_window_days']} 안에 '{facts['trigger_1']}'과 '{facts['trigger_2']}'가 같이 잡히면, "
        f"{facts['user_name']}님이 스스로 멈추기가 어려워집니다. "
        f"{facts['ilgan_full']} 일간의 이 구간 자기조절 성공률이 {facts['self_control_pct']}거든요. "
        "알고 들어가는 게 안전합니다."
    )


def test_trigger_validate_passes() -> None:
    f = get_doyoon_p1_trigger_facts(user_name="홍길동", ilgan="임수")
    ok, reason = validate_p1_trigger(_trigger_valid_text(f), f)
    assert ok, f"unexpected fail: {reason}"


def test_trigger_validate_fails_88_mutated() -> None:
    f = get_doyoon_p1_trigger_facts(user_name="홍길동", ilgan="임수")
    text = _trigger_valid_text(f).replace("88%", "87%")
    ok, reason = validate_p1_trigger(text, f)
    assert not ok
    assert "trigger_completion_pct" in reason


@pytest.mark.asyncio
async def test_trigger_usecase_returns_ai_on_success() -> None:
    f = get_doyoon_p1_trigger_facts(user_name="홍길동", ilgan="임수")
    ai_text = _trigger_valid_text(f)
    fake = _FakeAIClient(response_text=ai_text)
    out = await GenerateP1TriggerUseCase(ai_client=fake).execute(
        user_name="홍길동", ilgan="임수"
    )
    assert out == ai_text


@pytest.mark.asyncio
async def test_trigger_usecase_falls_back_on_validation_fail() -> None:
    fake = _FakeAIClient(response_text="짧고 사실값 없는 응답. " * 10)
    out = await GenerateP1TriggerUseCase(ai_client=fake).execute(
        user_name="홍길동", ilgan="임수"
    )
    # 룰 fallback (사실값 모두 포함)
    assert "88%" in out
    assert "30일" in out
    assert "17%" in out


# ─────────────────────────────────────────────────────────────────
# P-1 EMOTION
# ─────────────────────────────────────────────────────────────────


def test_emotion_facts_html_dummy() -> None:
    f = get_doyoon_p1_emotion_facts(user_name="홍길동", ilgan="임수")
    assert f["crisis_pct"] == "95%"
    assert f["recovery_pct"] == "60%"
    assert f["crisis_multiplier"] == "1.8배"
    assert f["expression_effect_pct"] == "32%"


def test_emotion_prompt_substitutes_facts() -> None:
    f = get_doyoon_p1_emotion_facts(user_name="홍길동", ilgan="임수")
    system, user = build_p1_emotion_prompt(f)
    assert "95%" in system
    assert "1.8배" in system
    assert "32%" in system


def _emotion_valid_text(facts: dict[str, str]) -> str:
    return (
        f"그래프를 보시면, 위기 구간에서 진폭이 {facts['crisis_pct']}까지 튀어요. "
        f"평균의 {facts['crisis_multiplier']} 수준입니다. "
        f"회복 구간도 {facts['recovery_pct']}대에 한참 머무는 패턴이에요.\n\n"
        f"{facts['ilgan_full']} 일간이 원래 그런 구조입니다. 초반엔 차분해 보이다가 어느 순간 한꺼번에 쏟아져요. "
        "회복 구간도 평균보다 깊고 길게 잡힙니다.\n\n"
        f"미리 조금씩 꺼내두면 폭발 강도가 줄어요. 작은 표현을 의식적으로 노출하시면 "
        f"위기 구간 강도가 평균 {facts['expression_effect_pct']} 떨어집니다. "
        "어렵게 생각 마시고 자주 표현하시면 됩니다."
    )


def test_emotion_validate_passes() -> None:
    f = get_doyoon_p1_emotion_facts(user_name="홍길동", ilgan="임수")
    ok, reason = validate_p1_emotion(_emotion_valid_text(f), f)
    assert ok, f"unexpected fail: {reason}"


def test_emotion_validate_fails_multiplier_mutated() -> None:
    f = get_doyoon_p1_emotion_facts(user_name="홍길동", ilgan="임수")
    text = _emotion_valid_text(f).replace("1.8배", "1.7배")
    ok, reason = validate_p1_emotion(text, f)
    assert not ok
    assert "crisis_multiplier" in reason


@pytest.mark.asyncio
async def test_emotion_usecase_returns_ai_on_success() -> None:
    f = get_doyoon_p1_emotion_facts(user_name="홍길동", ilgan="임수")
    ai_text = _emotion_valid_text(f)
    fake = _FakeAIClient(response_text=ai_text)
    out = await GenerateP1EmotionUseCase(ai_client=fake).execute(
        user_name="홍길동", ilgan="임수"
    )
    assert out == ai_text


@pytest.mark.asyncio
async def test_emotion_usecase_falls_back_on_ai_error() -> None:
    fake = _FakeAIClient(raise_exc=AIClientError("rate limit"))
    out = await GenerateP1EmotionUseCase(ai_client=fake).execute(
        user_name="홍길동", ilgan="임수"
    )
    # 룰 fallback
    assert "95%" in out
    assert "1.8배" in out
    assert "32%" in out
