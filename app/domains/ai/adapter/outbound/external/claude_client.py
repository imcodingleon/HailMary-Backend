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
    - Prompt caching: system 블록에 cache_control={"type": "ephemeral"} 마킹
    - SDK 에러는 도메인 에러로 변환하여 application 레이어로 노출
    """

    def __init__(self, *, api_key: str, model: str) -> None:
        self._client = AsyncAnthropic(api_key=api_key)
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
                system=[
                    {
                        "type": "text",
                        "text": system_prompt,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
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
