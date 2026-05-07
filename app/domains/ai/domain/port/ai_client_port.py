from abc import ABC, abstractmethod


class AIClientError(Exception):
    """AI 호출 실패 일반 에러. Adapter에서 SDK 에러 → 이 타입으로 변환."""


class AIClientRateLimitError(AIClientError):
    """레이트 리밋 초과 — 재시도 가능."""


class AIClientPort(ABC):
    """AI 챕터 생성 클라이언트 포트.

    실 구현은 adapter/outbound/external/claude_client.py.
    system/user 분리: prompt caching 활성화 위해 system 별도 인자.
    """

    @abstractmethod
    async def generate_chapter(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.85,
    ) -> str: ...
