"""도윤 호명용 이름 분류 — parse + usecase 단위 테스트."""

from __future__ import annotations

import pytest

from app.domains.ai.application.usecase.determine_doyoon_name_address_usecase import (
    DetermineDoyoonNameAddressUseCase,
)
from app.domains.ai.domain.port.ai_client_port import AIClientError, AIClientPort
from app.domains.ai.domain.service.doyoon_name_address_prompt import (
    build_name_address_prompt,
    parse_name_address_response,
)


class _FakeAIClient(AIClientPort):
    def __init__(self, *, response_text=None, raise_exc=None):
        self.response_text = response_text
        self.raise_exc = raise_exc

    async def generate_chapter(self, *, system_prompt, user_prompt, max_tokens=1024, temperature=0.85, model=None):
        if self.raise_exc:
            raise self.raise_exc
        return self.response_text


# ── parse ────────────────────────────────────────────────


def test_parse_korean_realname() -> None:
    resp = '{"name_for_address": "성현", "is_korean_real_name": true, "reasoning": "..."}'
    assert parse_name_address_response(resp, "배성현") == "성현"


def test_parse_복성() -> None:
    resp = '{"name_for_address": "성현", "is_korean_real_name": true, "reasoning": "복성"}'
    assert parse_name_address_response(resp, "남궁성현") == "성현"


def test_parse_nickname() -> None:
    resp = '{"name_for_address": "곰돌이푸", "is_korean_real_name": false, "reasoning": "닉네임"}'
    assert parse_name_address_response(resp, "곰돌이푸") == "곰돌이푸"


def test_parse_english() -> None:
    resp = '{"name_for_address": "John", "is_korean_real_name": false, "reasoning": "영문"}'
    assert parse_name_address_response(resp, "John") == "John"


def test_parse_invalid_json_falls_back() -> None:
    """JSON 깨짐 → 풀네임 fallback."""
    assert parse_name_address_response("not json at all", "배성현") == "배성현"


def test_parse_substring_check_falls_back() -> None:
    """출력이 입력의 부분 문자열이 아니면 → 풀네임 fallback (변형/생성 차단)."""
    resp = '{"name_for_address": "다른이름", "is_korean_real_name": true, "reasoning": "..."}'
    assert parse_name_address_response(resp, "배성현") == "배성현"


def test_parse_empty_candidate_falls_back() -> None:
    resp = '{"name_for_address": "", "is_korean_real_name": false, "reasoning": "..."}'
    assert parse_name_address_response(resp, "배성현") == "배성현"


def test_parse_with_surrounding_text() -> None:
    """JSON 앞뒤에 다른 텍스트 있어도 추출."""
    resp = '응답입니다:\n{"name_for_address": "성현", "is_korean_real_name": true, "reasoning": "..."}\n끝.'
    assert parse_name_address_response(resp, "배성현") == "성현"


# ── prompt builder ───────────────────────────────────────


def test_build_prompt_basic() -> None:
    sys, user = build_name_address_prompt("배성현")
    assert "한국 이름 분류" in sys
    assert '"배성현"' in user
    assert "JSON" in sys


def test_build_prompt_empty_name_raises() -> None:
    with pytest.raises(ValueError):
        build_name_address_prompt("")


# ── usecase ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_usecase_success() -> None:
    fake = _FakeAIClient(
        response_text='{"name_for_address": "성현", "is_korean_real_name": true, "reasoning": "한국 실명"}'
    )
    result = await DetermineDoyoonNameAddressUseCase(ai_client=fake).execute(user_name="배성현")
    assert result == "성현"


@pytest.mark.asyncio
async def test_usecase_ai_failure_falls_back() -> None:
    fake = _FakeAIClient(raise_exc=AIClientError("simulated"))
    result = await DetermineDoyoonNameAddressUseCase(ai_client=fake).execute(user_name="배성현")
    assert result == "배성현"


@pytest.mark.asyncio
async def test_usecase_empty_name_returns_empty() -> None:
    fake = _FakeAIClient(response_text="never called")
    result = await DetermineDoyoonNameAddressUseCase(ai_client=fake).execute(user_name="")
    assert result == ""


@pytest.mark.asyncio
async def test_usecase_nickname_preserved() -> None:
    fake = _FakeAIClient(
        response_text='{"name_for_address": "곰돌이푸", "is_korean_real_name": false, "reasoning": "닉네임"}'
    )
    result = await DetermineDoyoonNameAddressUseCase(ai_client=fake).execute(user_name="곰돌이푸")
    assert result == "곰돌이푸"
