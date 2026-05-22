"""도윤 P-8 ai_intro 단위 테스트."""

from __future__ import annotations

from typing import Any

import pytest

from app.domains.ai.application.usecase.generate_p8_intro_usecase import (
    GenerateP8IntroUseCase,
)
from app.domains.ai.domain.port.ai_client_port import AIClientError, AIClientPort
from app.domains.ai.domain.service.doyoon_p8_intro_prompt import validate_p8_intro
from app.domains.ai.domain.templates.doyoon_p8_timing import (
    compose_doyoon_p8_timing,
    get_doyoon_p8_facts,
)


class _FakeAIClient(AIClientPort):
    def __init__(self, *, response_text: str | None = None, raise_exc: Exception | None = None) -> None:
        self.response_text = response_text
        self.raise_exc = raise_exc

    async def generate_chapter(self, *, system_prompt, user_prompt, max_tokens=1024, temperature=0.85, model=None):
        if self.raise_exc:
            raise self.raise_exc
        assert self.response_text is not None
        return self.response_text


def _fake_raw_months(peak_indices: tuple[int, int] = (3, 8)) -> list[dict[str, Any]]:
    """12 row, peak 2개 score 90, 나머지 점진 분포."""
    months: list[dict[str, Any]] = []
    for i in range(12):
        if i in peak_indices:
            score = 90
        elif i in (2, 4, 7, 9):
            score = 60  # hearts 4
        elif i in (1, 5, 11):
            score = 50  # hearts 3
        elif i in (0, 6, 10):
            score = 35  # hearts 2
        else:
            score = 20  # hearts 1
        months.append({"romanceScore": score})
    return months


def test_compose_basic() -> None:
    out = compose_doyoon_p8_timing(
        user_name="홍길동", ilgan="임수",
        raw_months=_fake_raw_months(), start_year=2026, start_month=5,
    )
    assert len(out["months"]) == 12
    peaks = [m for m in out["months"] if m["is_peak"]]  # type: ignore[index]
    assert len(peaks) == 2
    # 피크는 hearts 5
    assert all(p["hearts"] == 5 for p in peaks)  # type: ignore[index]


def test_compose_all_ilgan() -> None:
    for ilgan in ["갑목", "을목", "병화", "정화", "무토", "기토", "경금", "신금", "임수", "계수"]:
        out = compose_doyoon_p8_timing(
            user_name="홍길동", ilgan=ilgan,
            raw_months=_fake_raw_months(), start_year=2026, start_month=5,
        )
        assert "12개월" in str(out["ai_intro"]) or "피크" in str(out["ai_intro"])


def test_compose_invalid_ilgan() -> None:
    with pytest.raises(KeyError):
        compose_doyoon_p8_timing(
            user_name="홍길동", ilgan="모름",
            raw_months=_fake_raw_months(), start_year=2026, start_month=5,
        )


def test_compose_wrong_month_count() -> None:
    with pytest.raises(ValueError):
        compose_doyoon_p8_timing(
            user_name="홍길동", ilgan="임수",
            raw_months=_fake_raw_months()[:5], start_year=2026, start_month=5,
        )


def test_facts_imsu() -> None:
    f = get_doyoon_p8_facts(
        user_name="홍길동", ilgan="임수",
        raw_months=_fake_raw_months((3, 8)),
        start_year=2026, start_month=5,
    )
    # peak idx 3 == 8월, idx 8 == '27. 1월
    assert "8월" in f["peak_1_label"]
    assert "1월" in f["peak_2_label"]


def _valid(facts):
    return (
        "향후 12개월 접촉 확률 분포 정리해드릴게요. 이번 달부터 1년이에요.\n\n"
        f"연간 평균 대비 피크 구간이 두 곳이에요. {facts['peak_1_label']}과 {facts['peak_2_label']}. "
        "이 두 달은 신규 인연 접촉 확률이 평균 대비 2.3배까지 올라가요. "
        "그 사이 구간은 변수 정리·매력 변수 보완에 효율적인 충전 구간입니다.\n\n"
        "임수 일간 표본에서 흐름 거스르는 행동의 ROI가 가장 낮게 측정돼요. "
        "피크에 적극 움직이고, 정체기엔 변수 정리에 집중하시는 게 가장 효율적입니다."
    )


def test_validate() -> None:
    f = get_doyoon_p8_facts(
        user_name="홍길동", ilgan="임수",
        raw_months=_fake_raw_months(), start_year=2026, start_month=5,
    )
    ok, reason = validate_p8_intro(_valid(f), f)
    assert ok, reason


@pytest.mark.asyncio
async def test_usecase_falls_back() -> None:
    fake = _FakeAIClient(raise_exc=AIClientError("x"))
    out = await GenerateP8IntroUseCase(ai_client=fake).execute(
        user_name="홍길동", ilgan="임수",
        raw_months=_fake_raw_months(), start_year=2026, start_month=5,
    )
    assert "12개월" in out
    assert "피크" in out
