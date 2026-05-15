from anthropic import (
    APIConnectionError,
    APIStatusError,
    AsyncAnthropic,
    RateLimitError,
)

from app.domains.ai.domain.port.ai_client_port import (
    AIClientError,
    AIClientPort,
    AIClientRateLimitError,
)


class ClaudeClient(AIClientPort):
    """Anthropic SDK 기반 Claude 클라이언트.

    - 모델: settings.claude_model (기본 claude-sonnet-4-6)
    - Prompt caching: 현재 미적용. sonnet-4-6 최소 cacheable prefix=2048 tokens인데
      P-10 system prompt가 약 670 tokens으로 미달. 트래픽 늘면 system을 2048+ tokens로
      확장한 후 cache_control 재도입. (CODE_ANALYSIS_2026-05-15.md 참조)
    - SDK 에러는 도메인 에러로 변환하여 application 레이어로 노출
    """

    def __init__(self, *, api_key: str, model: str) -> None:
        # max_retries=5: 기본 2회로는 Anthropic 529(Overloaded) 지속 시 부족.
        # SDK가 5xx/429/408에 expo backoff(retry-after 헤더 우선) 적용.
        # frontend TIMEOUT_MS=90s 와 정합 (SDK retry 누적 ~60s 흡수).
        self._client = AsyncAnthropic(api_key=api_key, max_retries=5)
        self._model = model

    async def generate_chapter(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.85,
    ) -> str:
        try:
            message = await self._client.messages.create(
                model=self._model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt},
                ],
            )
        except RateLimitError as exc:
            raise AIClientRateLimitError("Claude API rate limit") from exc
        except APIConnectionError as exc:
            raise AIClientError("Claude API 연결 실패") from exc
        except APIStatusError as exc:
            raise AIClientError(f"Claude API status error: {exc.status_code}") from exc

        text_parts: list[str] = []
        for block in message.content:
            block_text = getattr(block, "text", None)
            if isinstance(block_text, str):
                text_parts.append(block_text)
        if not text_parts:
            raise AIClientError("Claude 응답에 text block이 없습니다")
        return "".join(text_parts).strip()
