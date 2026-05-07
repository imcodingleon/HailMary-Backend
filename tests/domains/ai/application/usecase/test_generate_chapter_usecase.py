"""GenerateChapterUseCase 단위 테스트.

Fake AIClientPort로 외부 호출 격리.
"""

import pytest

from app.domains.ai.application.usecase.generate_chapter_usecase import (
    GenerateChapterUseCase,
    MissingChapterVariableError,
    UnknownChapterError,
)
from app.domains.ai.domain.port.ai_client_port import AIClientPort


class FakeAIClient(AIClientPort):
    def __init__(self, response: str) -> None:
        self._response = response
        self.calls: list[dict[str, object]] = []

    async def generate_chapter(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.85,
    ) -> str:
        self.calls.append(
            {
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
        )
        return self._response


async def test_p0_intro_returns_template_without_ai_call() -> None:
    """p0_intro는 템플릿 합성으로 전환됨 — AI 호출 X, 정적 합성 결과 반환."""
    fake = FakeAIClient(response="should-not-be-used")
    usecase = GenerateChapterUseCase(ai_client=fake)

    result = await usecase.execute(
        chapter_key="p0_intro",
        variables={"ilgan": "임수", "ohang_excess": "수", "ohang_lack": "토"},
    )

    # 템플릿 합성: 1문단 도입 + 2문단 임수 + 3문단 수 과다 + 4문단 토 부족 + 5문단 클로징.
    assert "촛불 앞에 앉으니까" in result
    assert "임수(壬水)" in result
    assert "수(水)가 너무 넘쳐서" in result
    assert "토(土)가 비어 있어서" in result
    assert "다음 장부터" in result
    # AI 호출은 절대 안 일어남.
    assert fake.calls == [], "p0_intro는 템플릿이라 AI 호출 금지"


async def test_unknown_chapter_raises() -> None:
    fake = FakeAIClient(response="x")
    usecase = GenerateChapterUseCase(ai_client=fake)

    with pytest.raises(UnknownChapterError):
        await usecase.execute(chapter_key="p99_xxx", variables={})


async def test_missing_variable_raises() -> None:
    fake = FakeAIClient(response="x")
    usecase = GenerateChapterUseCase(ai_client=fake)

    with pytest.raises(MissingChapterVariableError):
        await usecase.execute(
            chapter_key="p0_intro",
            variables={"ilgan": "임수"},  # ohang_excess, ohang_lack 누락
        )
    assert fake.calls == [], "변수 검증 실패 시 ai_client 호출 금지"
